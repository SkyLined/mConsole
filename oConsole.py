import os, sys, threading;

# Augment the search path: look in main folder, parent folder or "modules" child folder, in that order.
sMainFolderPath = os.path.dirname(os.path.abspath(__file__));
sParentFolderPath = os.path.normpath(os.path.join(sMainFolderPath, ".."));
sModulesFolderPath = os.path.join(sMainFolderPath, "modules");
asOriginalSysPath = sys.path[:];
sys.path = [sMainFolderPath, sParentFolderPath, sModulesFolderPath] + sys.path;

# Load external dependecies to make sure they are available and shown an error
# if any one fails to load. This error explains where the missing component
# can be downloaded to fix the error.
for (sModuleName, sURL) in {
  "mWindowsAPI": "https://github.com/SkyLined/mWindowsAPI/",
}.items():
  try:
    __import__(sModuleName, globals(), locals(), [], -1);
  except ImportError as oError:
    if oError.message == "No module named %s" % sModuleName:
      print "*" * 80;
      print "%s depends on %s which you can download at:" % (os.path.filename(__file__), sModuleName);
      print "    %s" % sDownloadURL;
      print "After downloading, please save the code in this folder:";
      print "    %s" % os.path.join(sModuleFolderPath, sModuleName);
      print " - or -";
      print "    %s" % os.path.join(sParentFolderPath, sModuleName);
      print "Once you have completed these steps, please try again.";
      print "*" * 80;
    raise;

# Restore the search path
sys.path = asOriginalSysPath;

import mCP437;
from mWindowsAPI.mDLLs import KERNEL32;
from mWindowsAPI.mDefines import STD_OUTPUT_HANDLE;
from mWindowsAPI.mTypes import CONSOLE_SCREEN_BUFFER_INFO, DWORD;
from mWindowsAPI.mFunctions import POINTER;

class cConsole(object):
  uColumnsForRedirectedOutput = 80;
  
  def __init__(oSelf):
    oSelf.oLock = threading.RLock();
    oSelf.uLastLineLength = 0;
    oSelf.hStdOut = KERNEL32.GetStdHandle(STD_OUTPUT_HANDLE);
    dwMode = DWORD(0);
    oSelf.bStdOutIsConsole = KERNEL32.GetConsoleMode(oSelf.hStdOut, POINTER(dwMode));
    oSelf.bByteOrderMarkWritten = False;
    if oSelf.bStdOutIsConsole:
      oSelf.uOriginalColor = oSelf.uCurrentColor;
      oSelf.uDefaultColor = 0;
      oSelf.uDefaultBarColor = 0xFF00 | (oSelf.uOriginalColor & 0xFF);
      oSelf.uDefaultProgressColor = 0xFF00 | ((oSelf.uOriginalColor & 0xF0) >> 4) | ((oSelf.uOriginalColor & 0x0F) << 4);
      oSelf.bLastSetColorIsNotOriginal = False;
  
  def fLock(oSelf):
    oSelf.oLock.acquire();
  
  def fUnlock(oSelf):
    oSelf.oLock.release();
  
  def fCleanup(oSelf):
    # If we are outputting to a console and the last set color is not the original color, the user must have
    # interrupted Python: set the color back to the original color the console will look as expected.
    # Also, if the last output was a status message, we need to clean it up.
    if oSelf.bStdOutIsConsole:
      if oSelf.bLastSetColorIsNotOriginal:
        oSelf.__fSetColor(oSelf.uOriginalColor);
      if oSelf.uLastLineLength:
        oSelf.__fWriteOutput(u"\r" + u" " * oSelf.uLastLineLength + u"\r");
  
  def __foGetConsoleScreenBufferInfo(oSelf):
    assert oSelf.bStdOutIsConsole, \
        "Cannot get colors when output is redirected";
    oConsoleScreenBufferInfo = CONSOLE_SCREEN_BUFFER_INFO()
    assert KERNEL32.GetConsoleScreenBufferInfo(oSelf.hStdOut, POINTER(oConsoleScreenBufferInfo)), \
        "GetConsoleScreenBufferInfo(%d, ...) => Error %08X" % \
        (oSelf.hStdOut, KERNEL32.GetLastError());
    return oConsoleScreenBufferInfo;
  
  @property
  def uCurrentColor(oSelf):
    if not oSelf.bStdOutIsConsole: return None;
    oConsoleScreenBufferInfo = oSelf.__foGetConsoleScreenBufferInfo();
    uColor = oConsoleScreenBufferInfo.wAttributes & 0xFF;
    bUnderlined = oConsoleScreenBufferInfo.wAttributes & 0x8000;
    return (bUnderlined and 0x10000 or 0) | 0xFF00 | uColor;

  @property
  def uWindowWidth(oSelf):
    if not oSelf.bStdOutIsConsole: return None;
    oConsoleScreenBufferInfo = oSelf.__foGetConsoleScreenBufferInfo();
    return oConsoleScreenBufferInfo.srWindow.Right - oConsoleScreenBufferInfo.srWindow.Left;
  
  @property
  def uWidth(oSelf):
    if not oSelf.bStdOutIsConsole: return None;
    oConsoleScreenBufferInfo = oSelf.__foGetConsoleScreenBufferInfo();
    return oConsoleScreenBufferInfo.dwSize.X;
  
  def __fSetColor(oSelf, uColor):
    assert oSelf.bStdOutIsConsole, \
        "Cannot set colors when output is redirected";

    uMask = (uColor >> 8) & 0xFF;
    bUnderline = (uColor >> 16);
    assert bUnderline in [0, 1], \
        "You cannot use color 0x%X; maybe you are trying to print a number without converting it to a string?" % uColor;
    uAttribute = (oSelf.uCurrentColor & (uMask ^ 0xFF)) | (uColor & uMask) | (bUnderline and 0x8000 or 0);
    assert KERNEL32.SetConsoleTextAttribute(oSelf.hStdOut, uAttribute), \
        "SetConsoleTextAttribute(%d, %d) => Error %08X" % \
        (oSelf.hStdOut, uAttribute, KERNEL32.GetLastError());
    # Track if the current color is not the original, so we know when to set it back.
    oSelf.bLastSetColorIsNotOriginal = uAttribute != oSelf.uOriginalColor;
  
  def __fWriteOutput(oSelf, sMessage):
    dwCharsWritten = DWORD(0);
    if oSelf.bStdOutIsConsole:
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
      assert fbWriteFunction(oSelf.hStdOut, sMessage[:uCharsToWrite], uCharsToWrite, POINTER(dwCharsWritten), None), \
          "%s(%d, '...', %d, ..., NULL) => Error %08X" % \
          (sWriteFunctionName, oSelf.hStdOut, uCharsToWrite, KERNEL32.GetLastError());
      sMessage = sMessage[dwCharsWritten.value:];

  def __fOutputHelper(oSelf, axCharsAndColors, bIsStatusMessage, uConvertTabsToSpaces, sPadding):
    assert oSelf.bStdOutIsConsole or not bIsStatusMessage, \
        "Status messages should not be output when output is redirected.";
    oSelf.oLock.acquire();
    try:
      # Go to the start of the current line if needed
      if oSelf.uLastLineLength:
        oSelf.__fWriteOutput(oSelf.bStdOutIsConsole and u"\r" or "\r");
      uCharsOutput = 0;
      # setup colors if outputting to a console.
      if oSelf.bStdOutIsConsole:
        uColumns = oSelf.uWidth;
        if oSelf.uDefaultColor != -1:
          oSelf.__fSetColor(oSelf.uDefaultColor);
      else:
        uColumns = oSelf.uColumnsForRedirectedOutput;
      try:
        for xCharsOrColor in axCharsAndColors:
          if isinstance(xCharsOrColor, int) or isinstance(xCharsOrColor, long):
            if oSelf.bStdOutIsConsole: # If output is redirected, colors will not be set, so don't try
              if xCharsOrColor == -1:
                uColor = oSelf.uOriginalColor;
              else:
                uColor = xCharsOrColor;
              oSelf.__fSetColor(uColor);
          else:
            assert isinstance(xCharsOrColor, str) or isinstance(xCharsOrColor, unicode), \
                "You cannot print %s (type = %s) directly; it must be converted to a string" % (repr(xCharsOrColor), xCharsOrColor.__class__.__name__);
            if oSelf.bStdOutIsConsole:
              uCharsLeftOnLine = uColumns - uCharsOutput - 1;
            if uConvertTabsToSpaces:
              uCurrentColumn = uCharsOutput;
              sMessage = "";
              for sChar in xCharsOrColor:
                if bIsStatusMessage and uCharsLeftOnLine == 0: break;
                if ord(sChar) == ord('\t'):
                  sChar = " ";
                  uCount = (uConvertTabsToSpaces - (uCurrentColumn % uConvertTabsToSpaces)) or uConvertTabsToSpaces;
                  if bIsStatusMessage:
                    uCount = min(uCount, uCharsLeftOnLine);
                else:
                  uCount = 1;
                sMessage += sChar * uCount;
                uCurrentColumn += uCount;
                if oSelf.bStdOutIsConsole:
                  uCharsLeftOnLine -= uCount;
            else:
              sMessage = xCharsOrColor;
              if bIsStatusMessage and len(sMessage) > uCharsLeftOnLine:
                # Do not let a status message span multiple lines.
                sMessage = sMessage[:uCharsLeftOnLine];
            oSelf.__fWriteOutput(sMessage);
            uCharsOutput += len(sMessage);
            if bIsStatusMessage and uCharsOutput == uColumns - 1:
              # We've reached the end of the line and the remained of the arguments will not be output.
              break;
        if sPadding and uCharsOutput < uColumns:
          uPaddingColumns = uColumns - uCharsOutput - 1;
          sLinePadding = (sPadding * (uPaddingColumns / len(sPadding)))[:uPaddingColumns];
          oSelf.__fWriteOutput(sLinePadding);
          uCharsOutput += uPaddingColumns;
      finally:
        if oSelf.bStdOutIsConsole and oSelf.bLastSetColorIsNotOriginal:
          oSelf.__fSetColor(oSelf.uOriginalColor);
      if oSelf.bStdOutIsConsole:
        # Optionally output some padding if this is a status message that is smaller than the previous status message.
        # Then go back to the start of the line and move to the next line if this is not a status message.
        oSelf.__fWriteOutput("".join([
          uCharsOutput < oSelf.uLastLineLength and u" " * (oSelf.uLastLineLength - uCharsOutput) or "",
          bIsStatusMessage and u"\r" or u"\r\n",
        ]));
        oSelf.uLastLineLength = bIsStatusMessage and uCharsOutput or 0;
      else:
        oSelf.__fWriteOutput("\n");
        oSelf.uLastLineLength = 0;
    finally:
      oSelf.oLock.release();

  def fPrint(oSelf, *axCharsAndColors, **dxFlags):
    for sFlag in dxFlags.keys():
      assert sFlag in ["uConvertTabsToSpaces", "sPadding"], \
          "Unknown flag %s" % sFlag;
    oSelf.__fOutputHelper(
      axCharsAndColors,
      bIsStatusMessage = False,
      uConvertTabsToSpaces = dxFlags.get("uConvertTabsToSpaces", 0),
      sPadding = dxFlags.get("sPadding", None),
    );

  def fStatus(oSelf, *axCharsAndColors, **dxFlags):
    # Status messages are not shown if output is redirected.
    if oSelf.bStdOutIsConsole:
      for sFlag in dxFlags.keys():
        assert sFlag in ["uConvertTabsToSpaces", "sPadding"], \
            "Unknown flag %s" % sFlag;
      oSelf.__fOutputHelper(
        axCharsAndColors,
        bIsStatusMessage = True,
        uConvertTabsToSpaces = dxFlags.get("uConvertTabsToSpaces", 0),
        sPadding = dxFlags.get("sPadding", None),
      );
  
  def fProgressBar(oSelf, nProgress, sMessage = "", uProgressColor = None, uBarColor = None):
    # Converting tabs to spaces in sMessage is not possible because this requires knowning which column each character
    # is going to be located. However, sMessage will be centered, so the location of each character depends on its
    # length, which we cannot know until after converting the tabs to spaces. This is a Catch-22 type issue.
    if not oSelf.bStdOutIsConsole: return;
    if uBarColor is None:
      uBarColor = oSelf.uDefaultBarColor;
    if uProgressColor is None:
      uProgressColor = oSelf.uDefaultProgressColor;
    assert nProgress >=0 and nProgress <= 1, \
        "Progress must be [0, 1], not %s" % nProgress;
    uBarWidth = oSelf.uWindowWidth - 1;
    sBar = sMessage.center(uBarWidth);
    uProgress = long(oSelf.uWindowWidth * nProgress);
    oSelf.__fOutputHelper(
      [uProgressColor, sBar[:uProgress], uBarColor, sBar[uProgress:]],
      bIsStatusMessage = True,
      uConvertTabsToSpaces = 0,
      sPadding = None,
    );
  
  def fSetTitle(oSelf, sTitle):
    assert KERNEL32.SetConsoleTitleW(sTitle), \
        "SetConsoleTitleW(%s) => Error %08X" % \
        (repr(sTitle), KERNEL32.GetLastError());
  
oConsole = cConsole();