import os;

class cFileSystemItemStandIn(object):
  bSupportsZipFiles = False;
  def __init__(oSelf, sPath):
    oSelf.sPath = sPath;
  
  @property
  def sName(oSelf):
    return os.path.basename(oSelf.sPath);
  
  @property
  def sWindowsPath(oSelf):
    return oSelf.sPath;
  
  def fbIsFile(oSelf, bThrowErrors = True):
    assert bThrowErrors, \
        "Errors are always thrown by %s" % oSelf.__class__.__name__;
    return os.path.isfile(oSelf.sPath);
  
  def fbIsFolder(oSelf, bThrowErrors = True):
    assert bThrowErrors, \
        "Errors are always thrown by %s" % oSelf.__class__.__name__;
    return os.path.isdir(oSelf.sPath);
  
  def fbSetAsCurrentWorkingDirectory(oSelf):
    os.chdir(oSelf.sPath);
    assert os.getcwd().lower() == oSelf.sPath.lower(), \
        "Changed working directory to %s but got %s" % (repr(oSelf.sPath), repr(os.getcwd()));
  
  @property
  def oParent(oSelf):
    sParentPath = os.path.dirname(oSelf.sPath);
    return oSelf.__class__(sParentPath) if sParentPath != oSelf.sPath else None;
  
  def fsGetRelativePathTo(oSelf, oDescendant):
    return os.path.relpath(oDescendant.sPath, oSelf.sPath);
  
  def foGetChild(oSelf, sName, bMustBeFile = False, bMustBeFolder = False):
    return oSelf.foGetDescendant(
      sName,
      bMustBeFile = bMustBeFile,
      bMustBeFolder = bMustBeFolder,
    );
  def fo0GetChild(oSelf, sName, bMustBeFile = False, bMustBeFolder = False, bThrowErrors = True):
    assert bThrowErrors, \
        "Errors are always thrown by %s" % oSelf.__class__.__name__;
    return oSelf.foGetDescendant(
      sName,
      bMustBeFile = bMustBeFile,
      bMustBeFolder = bMustBeFolder,
    );
  
  def faoGetChildren(oSelf, bMustBeFile = False, bMustBeFolder = False):
    return oSelf.fa0oGetChildren(
      bMustBeFile = bMustBeFile,
      bMustBeFolder = bMustBeFolder,
      bThrowErrors = True,
    );
  def fa0oGetChildren(oSelf, bMustBeFile = False, bMustBeFolder = False, bThrowErrors = True):
    assert bThrowErrors, \
        "Errors are always thrown by %s" % oSelf.__class__.__name__;
    return [
      oChild for oChild in [
        oSelf.foGetChild(sName)
        for sName in os.listdir(oSelf.sPath)
      ] if (not bMustBeFile or oChild.fbIsFile()) and (not bMustBeFolder or oChild.fbIsFolder())
    ];
  
  def foGetDescendant(oSelf, sRelativePath, bMustBeFile = False, bMustBeFolder = False):
    return oSelf.fo0GetDescendant(
      sRelativePath,
      bMustBeFile = bMustBeFile,
      bMustBeFolder = bMustBeFolder,
      bThrowErrors = True,
    );
  def fo0GetDescendant(oSelf, sRelativePath, bMustBeFile = False, bMustBeFolder = False, bThrowErrors = True):
    assert bThrowErrors, \
        "Errors are always thrown by %s" % oSelf.__class__.__name__;
    oDescendant = oSelf.__class__(os.path.join(oSelf.sPath, sRelativePath));
    assert not bMustBeFile or oDescendant.fbIsFile(), \
        "%s is not a file!" % oDescendant;
    assert not bMustBeFolder or oDescendant.fbIsFolder(), \
        "%s is not a folder!" % oDescendant;
    return oDescendant;
  
  def faoGetDescendants(oSelf, bMustBeFile = False, bMustBeFolder = False):
    return oSelf.fa0oGetDescendants(
      bMustBeFile = bMustBeFile,
      bMustBeFolder = bMustBeFolder,
      bThrowErrors = True,
    );
  def fa0oGetDescendants(oSelf, bMustBeFile = False, bMustBeFolder = False, bThrowErrors = True):
    assert bThrowErrors, \
        "Errors are always thrown by %s" % oSelf.__class__.__name__;
    a0oChildren = oSelf.fa0oGetChildren(bThrowErrors = bThrowErrors);
    if a0oChildren is None:
      return None;
    aoDescendants = [];
    for oChild in a0oChildren:
      if oChild.fbIsFolder():
        if not bMustBeFile:
          aoDescendants.append(oChild);
        aoDescendants += oChild.fa0oGetDescendants(
          bMustBeFile = bMustBeFile,
          bMustBeFolder = bMustBeFolder,
          bThrowErrors = bThrowErrors,
        ) or [];
      elif not bMustBeFolder:
        aoDescendants.append(oChild);
    return aoDescendants;
  
  def fsbRead(oSelf, bThrowErrors = True):
    assert bThrowErrors, \
        "Errors are always thrown by %s" % oSelf.__class__.__name__;
    with open(oSelf.sPath, "rb") as oFile:
      return oFile.read();
  
  def fbWrite(oSelf, sbContent, bThrowErrors = True):
    assert bThrowErrors, \
        "Errors are always thrown by %s" % oSelf.__class__.__name__;
    with open(oSelf.sPath, "wb") as oFile:
      oFile.write(sbContent);
    return True;
  
  def fbDelete(oSelf, bThrowErrors = True):
    assert bThrowErrors, \
        "Errors are always thrown by %s" % oSelf.__class__.__name__;
    if oSelf.fbIsFile():
      os.remove(oSelf.sPath);
    else:
      os.rmdir(oSelf.sPath);
    return True;
  
  def __repr__(oSelf):
    return "<%s %s #%d>" % (oSelf.__class__.__name__, oSelf, id(oSelf));
  def fsToString(oSelf):
    return "%s{%s#%d}" % (oSelf.__class__.__name__, oSelf.sPath, id(oSelf));
  def __str__(oSelf):
    return oSelf.sPath;

gc0FileSystemItem = None;
def fcFileSystemItemLoader():
  global gc0FileSystemItem;
  if gc0FileSystemItem is None:
    try:
      from mFileSystemItem import cFileSystemItem;
    except Exception as oException:
      print("Using stand-in cFileSystemItem (%s)!" % oException);
      gcFileSystemItem = cFileSystemItemStandIn;
    else:
      gcFileSystemItem = cFileSystemItem;
  return gcFileSystemItem;
