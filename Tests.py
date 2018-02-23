import os, sys;

sModuleFolderPath = os.path.dirname(os.path.abspath(__file__));
sBaseFolderPath = os.path.dirname(sModuleFolderPath);
sys.path.extend([
  sBaseFolderPath,
  sModuleFolderPath,
  os.path.join(sModuleFolderPath, "modules"),
]);

from oConsole import oConsole;

for uBackground in xrange(0, 0x10):
  asLineOutput = [];
  for uForeground in xrange(0, 0x10, 1):
    uColor = uForeground + uBackground * 0x10;
    asLineOutput.extend([0xFF00 + uColor, "##"]);
  oConsole.fPrint(*asLineOutput);

uMax = oConsole.uWindowWidth or 100;
for uCurrent in xrange(uMax):
  nProgress = uCurrent / float(uMax);
  oConsole.fProgressBar(nProgress, "Screen width = %d" % uMax);

if oConsole.uWindowWidth is not None:
  # These tests apply to non-redirected output (to a window) only
  sTestMessage = "\t\tx\tTabs to spaces";
  uTestMessageLength = len(sTestMessage);
  oConsole.fStatus(sTestMessage);
  assert oConsole.uLastLineLength == uTestMessageLength, \
      "Expected last line to be %d chars, got %d" % (uTestMessageLength, oConsole.uLastLineLength);
  uTestMessageLength = len(sTestMessage.replace("\t\tx\t", "12341234x234"));
  oConsole.fStatus(sTestMessage, uConvertTabsToSpaces = 4);
  assert oConsole.uLastLineLength == uTestMessageLength, \
      "Expected last line to be %d chars, got %d" % (uTestMessageLength, oConsole.uLastLineLength);

oConsole.fPrint(0xFF1E, "Padding test", sPadding = " -");
oConsole.fPrint("This tests ", 0x10000, "underlined", 0, " text.");
if oConsole.bStdOutIsConsole:
  # Colors are only processed when outputting to a console. If you specify an invalid color, the code assumes you
  # accidentally output a number without first converting it to a string. If output is redirected, the color is not
  # processed and this error is not detected.
  try:
    oConsole.fPrint(0x20000);
  except:
    pass;
  else:
    raise AssertionFailure("Using a color number that is outside the value range did not cause an exception!");

oConsole.fPrint("Tests succeeded");
oConsole.fStatus("This should not be visible");
oConsole.fCleanup();

