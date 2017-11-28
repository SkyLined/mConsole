@ECHO OFF

ECHO * Running unit-tests...


ECHO   * Test if oConsole can output to the console...
CALL PYTHON "Tests.py"
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test if oConsole can detect redirected output...
CALL PYTHON "Tests.py" >nul
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   + Passed unit-tests.
EXIT /B 0

:ERROR
  ECHO     - Failed with error level %ERRORLEVEL%
  ENDLOCAL & EXIT /B %ERRORLEVEL%
