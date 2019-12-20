import json, os, sys;

# Augment the search path to make the test subject a package and have access to its modules folder.
sTestsFolderPath = os.path.dirname(os.path.abspath(__file__));
sMainFolderPath = os.path.dirname(sTestsFolderPath);
sParentFolderPath = os.path.dirname(sMainFolderPath);
sModulesFolderPath = os.path.join(sMainFolderPath, "modules");
asOriginalSysPath = sys.path[:];
sys.path = [sParentFolderPath, sModulesFolderPath] + asOriginalSysPath;
# Load product details
oProductDetailsFile = open(os.path.join(sMainFolderPath, "dxProductDetails.json"), "rb");
try:
  dxProductDetails = json.load(oProductDetailsFile);
finally:
  oProductDetailsFile.close();
# Save the list of names of loaded modules:
asOriginalModuleNames = sys.modules.keys();

__import__(dxProductDetails["sProductName"], globals(), locals(), [], -1);

# Sub-packages should load all modules relative, or they will end up in the global namespace, which means they may get
# loaded by the script importing it if it tries to load a differnt module with the same name. Obviously, that script
# will probably not function when the wrong module is loaded, so we need to check that we did this correctly.
asUnexpectedModules = list(set([
  sModuleName.lstrip("_").split(".", 1)[0] for sModuleName in sys.modules.keys()
  if not (
    sModuleName in asOriginalModuleNames # This was loaded before
    or sModuleName.lstrip("_").split(".", 1)[0] in (
      [dxProductDetails["sProductName"]] +
      dxProductDetails["asDependentOnProductNames"] +
      [
        # These built-in modules are expected:
        "collections", "ctypes", "gc", "heapq", "itertools", "keyword", "msvcrt",
        "platform", "string", "strop", "struct", "subprocess", "thread",
        "threading", "time",
      ]
    )
  )
]));
assert len(asUnexpectedModules) == 0, \
      "Module(s) %s was/were unexpectedly loaded!" % ", ".join(sorted(asUnexpectedModules));

#Import the test subject
from oConsole import oConsole;

# Restore the search path
sys.path = asOriginalSysPath;

for uBackground in xrange(0, 0x10):
  asLineOutput = [];
  for uForeground in xrange(0, 0x10, 1):
    uColor = uForeground + uBackground * 0x10;
    asLineOutput.extend([0xFF00 + uColor, "##"]);
  oConsole.fPrint(*asLineOutput);

# Use a large value, as this will be very slow unless the progress bar is not drawn when it's not changed as it should be.
uLoops = 10000;
for uCurrent in xrange(uLoops):
  nProgress = uCurrent / float(uLoops);
  oConsole.fProgressBar(nProgress, "Screen width = %d" % (oConsole.uWindowWidth or 100));

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
  except Exception:
    pass;
  else:
    raise AssertionFailure("Using a color number that is outside the value range did not cause an exception!");

oConsole.fPrint("Tests succeeded");
oConsole.fStatus("This should not be visible");
oConsole.fCleanup();

