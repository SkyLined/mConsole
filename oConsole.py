import threading;
import mCP437;
from mWindowsAPI import *;
from oVersionInformation import oVersionInformation;

class cConsole(object):
  oVersionInformation = oVersionInformation;
  
  def __init__(oConsole):
    oConsole.oLock = threading.Lock();
    oConsole.uLastLineLength = 0;
    oConsole.hStdOut = KERNEL32.GetStdHandle(STD_OUTPUT_HANDLE);
    dwMode = DWORD(0);
    oConsole.bStdOutIsConsole = KERNEL32.GetConsoleMode(oConsole.hStdOut, POINTER(dwMode));
    oConsole.bByteOrderMarkWritten = False;
    oConsole.uDefaultColor = -1;
  
  def __foGetConsoleScreenBufferInfo(oConsole):
    assert oConsole.bStdOutIsConsole, \
        "Cannot set colors when output is redirected";
    oConsoleScreenBufferInfo = CONSOLE_SCREEN_BUFFER_INFO()
    assert KERNEL32.GetConsoleScreenBufferInfo(oConsole.hStdOut, POINTER(oConsoleScreenBufferInfo)), \
        "GetConsoleScreenBufferInfo(%d, ...) => Error %08X" % \
        (oConsole.hStdOut, KERNEL32.GetLastError());
    return oConsoleScreenBufferInfo;
  
  @property
  def uCurrentColor(oConsole):
    oConsoleScreenBufferInfo = oConsole.__foGetConsoleScreenBufferInfo();
    return oConsoleScreenBufferInfo.wAttributes & 0xFF;

  @property
  def uWindowWidth(oConsole):
    oConsoleScreenBufferInfo = oConsole.__foGetConsoleScreenBufferInfo();
    return oConsoleScreenBufferInfo.srWindow.Right - oConsoleScreenBufferInfo.srWindow.Left;
  
  @property
  def uWidth(oConsole):
    oConsoleScreenBufferInfo = oConsole.__foGetConsoleScreenBufferInfo();
    return oConsoleScreenBufferInfo.dwSize.X;
  
  def __fSetColor(oConsole, uColor):
    assert oConsole.bStdOutIsConsole, \
        "Cannot set colors when output is redirected";

    uMask = uColor >> 8;
    assert uMask in xrange(0, 0x100), \
        "You cannot use color 0x%X; maybe you are trying to print a number without converting it to a string?" % uColor;
    uColor &= 0xFF;
    if uMask:
      uCurrentColor = oConsole.uCurrentColor;
      uColor = (uCurrentColor & (uMask ^ 0xFF)) + (uColor & uMask);
    assert KERNEL32.SetConsoleTextAttribute(oConsole.hStdOut, uColor), \
        "SetConsoleTextAttribute(%d, %d) => Error %08X" % \
        (oConsole.hStdOut, uColor, KERNEL32.GetLastError());
  
  def __fWriteOutput(oConsole, sMessage):
    dwCharsWritten = DWORD(0);
    if oConsole.bStdOutIsConsole:
      sWriteFunctionName = "WriteConsoleW";
      if isinstance(sMessage, str):
        sMessage = mCP437.fsutoUnicode(sMessage); # Convert CP437 to Unicode
    else:
      sWriteFunctionName = "WriteFile";
      if isinstance(sMessage, unicode):
        sMessage = mCP437.fsFromUnicode(sMessage); # Convert Unicode to CP437
    fbWriteFunction = getattr(KERNEL32, sWriteFunctionName);
    while sMessage:
      uCharsToWrite = min(len(sMessage), 10000);
      assert fbWriteFunction(oConsole.hStdOut, sMessage[:uCharsToWrite], uCharsToWrite, POINTER(dwCharsWritten), None), \
          "%s(%d, '...', %d, ..., NULL) => Error %08X" % \
          (sWriteFunctionName, oConsole.hStdOut, uCharsToWrite, KERNEL32.GetLastError());
      sMessage = sMessage[dwCharsWritten.value:];

  def __fOutputHelper(oConsole, axCharsAndColors, bIsStatusMessage):
    assert oConsole.bStdOutIsConsole or not bIsStatusMessage, \
        "Status messages should not be output when output is redirected.";
    oConsole.oLock.acquire();
    try:
      # Go to the start of the current line if needed
      if oConsole.uLastLineLength:
        oConsole.__fWriteOutput(oConsole.bStdOutIsConsole and u"\r" or "\r");
      uCharsOutput = 0;
      # setup colors if outputting to a console.
      bColorWasSet = False;
      if oConsole.bStdOutIsConsole:
        uColumns = oConsole.uWidth;
        uOriginalColor = oConsole.uCurrentColor;
        if oConsole.uDefaultColor != -1:
          oConsole.__fSetColor(oConsole.uDefaultColor);
          bColorWasSet = True;
      try:
        for xCharsOrColor in axCharsAndColors:
          if isinstance(xCharsOrColor, int) or isinstance(xCharsOrColor, long):
            if oConsole.bStdOutIsConsole: # If output is redirected, colors will not be set, so don't try
              if xCharsOrColor == -1: xCharsOrColor = uOriginalColor;
              oConsole.__fSetColor(xCharsOrColor);
              bColorWasSet = True;
          else:
            assert isinstance(xCharsOrColor, str) or isinstance(xCharsOrColor, unicode), \
                "You cannot print %s (type = %s) directly; it must be converted to a string" % (repr(xCharsOrColor), xCharsOrColor.__class__.__name__);
            if bIsStatusMessage and uCharsOutput + len(xCharsOrColor) >= uColumns:
              # Do not let a status message span multiple lines.
              xCharsOrColor = xCharsOrColor[:uColumns - uCharsOutput - 1];
            oConsole.__fWriteOutput(xCharsOrColor);
            uCharsOutput += len(xCharsOrColor);
            if bIsStatusMessage and uCharsOutput == uColumns - 1:
              # We've reached the end of the line and the remained of the arguments will not be output.
              break;
      finally:
        if bColorWasSet:
          oConsole.__fSetColor(uOriginalColor);
      if oConsole.bStdOutIsConsole:
        # Optionally output some padding if this is a status message that is smaller than the previous status message.
        # Then go back to the start of the line and move to the next line if this is not a status message.
        oConsole.__fWriteOutput("".join([
          uCharsOutput < oConsole.uLastLineLength and u" " * (oConsole.uLastLineLength - uCharsOutput) or "",
          bIsStatusMessage and u"\r" or u"\r\n",
        ]));
        oConsole.uLastLineLength = bIsStatusMessage and uCharsOutput or 0;
      else:
        oConsole.__fWriteOutput("\n");
        oConsole.uLastLineLength = 0;
    finally:
      oConsole.oLock.release();

  def fPrint(oConsole, *axCharsAndColors):
    oConsole.__fOutputHelper(axCharsAndColors, False);

  def fStatus(oConsole, *axCharsAndColors):
    # If output is redirected, do not output status messages
    if oConsole.bStdOutIsConsole:
      oConsole.__fOutputHelper(axCharsAndColors, True);
  
  def fProgressBar(oConsole, nProgress, sMessage = "", uProgressColor = None, uBarColor = None):
    if uBarColor is None:
      uBarColor = oConsole.uCurrentColor;
    if uProgressColor is None:
      uProgressColor = ((uBarColor & 0xF0) >> 4) | ((uBarColor & 0x0F) << 4);
    assert nProgress >=0 and nProgress <= 1, \
        "Progress must be [0, 1], not %s" % nProgress;
    if oConsole.bStdOutIsConsole:
      uBarWidth = oConsole.uWindowWidth - 1;
      sBar = sMessage.center(uBarWidth);
      uProgress = long(oConsole.uWindowWidth * nProgress);
      oConsole.__fOutputHelper([uProgressColor, sBar[:uProgress], uBarColor, sBar[uProgress:]], True);

oConsole = cConsole();