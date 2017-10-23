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
    asLineOutput.extend([uColor, "X"]);
  oConsole.fStatus(*asLineOutput);

uMax = oConsole.uWindowWidth or 100;
for uCurrent in xrange(uMax):
  nProgress = uCurrent / float(uMax);
  oConsole.fProgressBar(nProgress, "Screen width = %d" % uMax);

oConsole.fPrint("Tests succeeded");
