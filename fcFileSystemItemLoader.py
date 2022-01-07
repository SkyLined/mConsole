import os;

class cFileSystemItemStandIn(object):
  bSupportsZipFiles = False;
  def __init__(oSelf, sPath):
    oSelf.sPath = os.path.normpath(sPath);
  
  @property
  def sName(oSelf):
    return os.path.basename(oSelf.sPath);
  
  @property
  def sWindowsPath(oSelf):
    return oSelf.sPath;
  
  def fbIsFile(oSelf, bThrowErrors = False):
    try:
      return os.path.isfile(oSelf.sPath);
    except Exception as oException:
      if bThrowErrors:
        raise;
      return False;
  
  def fbIsFolder(oSelf, bThrowErrors = False):
    try:
      return os.path.isdir(oSelf.sPath);
    except Exception as oException:
      if bThrowErrors:
        raise;
      return False;
  
  def foMustBeFile(oSelf):
    assert oSelf.fbIsFile(), \
        "%s is not a file" % oSelf.sPath;
    return oSelf;
  def foMustBeFolder(oSelf):
    assert oSelf.fbIsFolder(), \
        "%s is not a folder" % oSelf.sPath;
    return oSelf;
  
  def fSetAsCurrentWorkingDirectory(oSelf):
    assert oSelf.fbSetAsCurrentWorkingDirectory(bThrowErrors = True);
  def fbSetAsCurrentWorkingDirectory(oSelf, bThrowErrors = False):
    try:
      os.chdir(oSelf.sPath);
    except Exception:
      if bThrowErrors:
        raise;
      return False;
    assert os.getcwd().lower() == oSelf.sPath.lower(), \
        "Changed working directory to %s but got %s" % (repr(oSelf.sPath), repr(os.getcwd()));
    return True;
    
  @property
  def oParent(oSelf):
    sParentPath = os.path.dirname(oSelf.sPath);
    return oSelf.__class__(sParentPath) if sParentPath != oSelf.sPath else None;
  
  def fsGetRelativePathTo(oSelf, oDescendant):
    return os.path.relpath(oDescendant.sPath, oSelf.sPath);
  
  def fCreateAsFolder(oSelf, bCreateParents = False):
    assert oSelf.fbCreateAsFolder(
      bCreateParents = bCreateParents,
      bThrowErrors = True,
    );
  def fbCreateAsFolder(oSelf, bCreateParents = False, bThrowErrors = False):
    if oSelf.oParent and not oSelf.oParent.fbExists(bThrowErrors = bThrowErrors):
      if not bCreateParents:
        assert not bThrowErrors, \
            "Cannot create folder %s when its parent does not exist!" % oSelf.sPath;
        return False;
      if not oSelf.oParent.fbCreateAsParent(bThrowErrors = bThrowErrors):
        return False;
    try:
      os.makedirs(oSelf.sWindowsPath);
      if not os.path.isdir(oSelf.sWindowsPath):
        return False;
    except Exception as oException:
      if bThrowErrors:
        raise;
      return False;
    return True;
  
  def fCreateAsFile(oSelf, sbData = b"", bCreateParents = False):
    assert oSelf.fbCreateAsFile(
      sbData = sbData,
      bCreateParents = bCreateParents,
      bThrowErrors = True,
    );
  def fbCreateAsFile(oSelf, sbData = b"", bCreateParents = False, bThrowErrors = False):
    try:
      assert oSelf.oParent, \
          "Cannot create file %s as a root node!" % oSelf.sPath;
      assert not oSelf.fbIsFolder(bThrowErrors = bThrowErrors), \
          "Cannot create file %s if it already exists as a folder!" % oSelf.sPath;
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
    if not oSelf.oParent.fbExists(bThrowErrors = bThrowErrors):
      if not bCreateParents:
        assert not bThrowErrors, \
            "Cannot create file %s when its parent does not exist!" % oSelf.sPath;
        return False;
      if not oSelf.oParent.fbCreateAsParent(bThrowErrors = bThrowErrors):
        return False;
    try:
      with open(oSelf.sWindowsPath, "wb") as o0PyFile:
        o0PyFile.write(sbData);
    except Exception as oException:
      if bThrowErrors:
        raise;
      return False;
    return True;
  
  def foGetChild(oSelf, sName):
    return oSelf.fo0GetChild(sName, bThrowErrors = True);
  def fo0GetChild(oSelf, sName, bThrowErrors = False):
    sNormalizedName = os.path.normpath(sName);
    if (
      sNormalizedName != sName
      or os.sep in sName
      or os.altsep in sName
      or sName in [".", ".."]
      or sName.endswith(".")
    ):
      assert not bThrowErrors, \
          "Invalid child name %s!" % sName;
      return None;
    oChild = oSelf.__class__(os.path.join(oSelf.sPath, sName));
    return oChild;
  
  def faoGetChildren(oSelf):
    return oSelf.fa0oGetChildren(bThrowErrors = True);
  def fa0oGetChildren(oSelf, bThrowErrors = False):
    try:
      asChildNames = os.listdir(oSelf.sPath);
    except:
      if bThrowErrors:
        raise;
      return None;
    ao0Chilren = [
      oSelf.fo0GetChild(sChildName, bThrowErrors = bThrowErrors)
      for sChildName in asChildNames
    ];
    return [o0Child for o0Child in ao0Chilren if o0Child is not None];
  
  def foGetDescendant(oSelf, sRelativePath):
    return oSelf.fo0GetDescendant(
      sRelativePath,
      bThrowErrors = True,
    );
  def fo0GetDescendant(oSelf, sRelativePath, bThrowErrors = False):
    sNormalizedRelativePath= os.path.normpath(sRelativePath);
    if (
      sNormalizedRelativePath != sRelativePath
      or sRelativePath in [".", ".."]
      or sRelativePath.endswith(".")
    ):
      assert not bThrowErrors, \
          "Invalid descendant path %s!" % sRelativePath;
      return None;
    return oSelf.__class__(os.path.join(oSelf.sPath, sRelativePath));
  
  def faoGetDescendants(oSelf):
    return oSelf.fa0oGetDescendants(bThrowErrors = True);
  def fa0oGetDescendants(oSelf, bThrowErrors = False):
    assert bThrowErrors, \
        "Errors are always thrown by %s" % oSelf.__class__.__name__;
    a0oChildren = oSelf.fa0oGetChildren(bThrowErrors = bThrowErrors);
    if a0oChildren is None:
      return None;
    aoDescendants = [];
    for oChild in a0oChildren:
      aoDescendants.append(oChild);
      if oChild.fbIsFolder(bThrowErrors = bThrowErrors):
        aoDescendants += oChild.fa0oGetDescendants(bThrowErrors = bThrowErrors) or [];
    return aoDescendants;
  
  def fsbRead(oSelf):
    with open(oSelf.sPath, "rb") as oFile:
      return oFile.read();
  def fsb0Read(oSelf, bThrowErrors = False):
    assert bThrowErrors, \
        "Errors are always thrown by %s" % oSelf.__class__.__name__;
    with open(oSelf.sPath, "rb") as oFile:
      return oFile.read();
  
  def fWrite(oSelf, sbContent):
    return oSelf.fbWrite(sbContent, bThrowErrors = True);
  def fbWrite(oSelf, sbContent, bThrowErrors = False):
    assert bThrowErrors, \
        "Errors are always thrown by %s" % oSelf.__class__.__name__;
    with open(oSelf.sPath, "wb") as oFile:
      oFile.write(sbContent);
    return True;
  
  def fDeleteDescendants(oSelf):
    return oSelf.fbDeleteDescendants(bThrowErrors = True);
  def fbDeleteDescendants(oSelf, bThrowErrors = False):
    a0oChildren = oSelf.fa0oGetChildren(bThrowErrors = bThrowErrors);
    if a0oChildren is None:
      return False;
    for oChild in a0oChildren:
      if not oChild.fbDelete(bThrowErrors = bThrowErrors):
        return False;
    return True;
  
  def fDelete(oSelf):
    return oSelf.fbDelete(bThrowErrors = True);
  def fbDelete(oSelf, bThrowErrors = False):
    assert bThrowErrors, \
        "Errors are always thrown by %s" % oSelf.__class__.__name__;
    if oSelf.fbIsFile():
      os.remove(oSelf.sPath);
    else:
      if not oSelf.fbDeleteDescendants(bThrowErrors = bThrowErrors):
        return False;
      os.rmdir(oSelf.sPath);
    return True;
  
  def fuGetSize(oSelf):
    return oSelf.fu0GetSize(bThrowErrors = True);
  def fu0GetSize(oSelf, bThrowErrors = False):
    try:
      return os.path.getsize(oSelf.sWindowsPath);
    except Exception as oException:
      if bThrowErrors:
        raise;
      return None;
  
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
