@ECHO OFF
SETLOCAL

IF "%~1" == "--all" (
  REM If you can add the x86 and x64 binaries of python to the path, or add links to the local folder, tests will be run
  REM in both
  WHERE PYTHON_X86 >nul 2>&1
  IF NOT ERRORLEVEL 0 (
    ECHO - PYTHON_X86 was not found; not testing both x86 and x64 ISAs.
  ) ELSE (
    WHERE PYTHON_X64 >nul 2>&1
    IF NOT ERRORLEVEL 0 (
      ECHO - PYTHON_X64 was not found; not testing both x86 and x64 ISAs.
    ) ELSE (
      GOTO :RUN_PYTHON_FOR_BOTH_ISAS
    )
  )
)

IF DEFINED PYTHON (
  CALL :CHECK_PYTHON
  IF NOT ERRORLEVEL 1 GOTO :RUN_PYTHON
)
REM Try to detect the location of python automatically
FOR /F "usebackq delims=" %%I IN (`where "python" 2^>nul`) DO (
  SET PYTHON="%%~fI"
  CALL :CHECK_PYTHON
  IF NOT ERRORLEVEL 1 GOTO :RUN_PYTHON
)
REM Check if python is found in its default installation path.
FOR /D %%I IN ("%LOCALAPPDATA%\Programs\Python\*") DO (
  SET PYTHON="%%~fI\python.exe"
  CALL :CHECK_PYTHON
  IF NOT ERRORLEVEL 1 GOTO :RUN_PYTHON
)
ECHO - Cannot find python.exe, please set the "PYTHON" environment variable to the
ECHO   correct path, or add Python to the "PATH" environment variable.
EXIT /B 1

:CHECK_PYTHON
  REM Make sure path is quoted and check if it exists.
  SET PYTHON="%PYTHON:"=%"
  IF NOT EXIST %PYTHON% EXIT /B 1
  EXIT /B 0

:RUN_PYTHON
  ECHO + Testing with redirected output...
  CALL %PYTHON% "%~dpn0.py" %* >nul
  IF ERRORLEVEL 1 (
    ECHO   - Failed with error %ERRORLEVEL%!
    ENDLOCAL
    EXIT /B %ERRORLEVEL%
  )
  ECHO + Done.
  ENDLOCAL
  EXIT /B 0

:RUN_PYTHON_FOR_BOTH_ISAS
  ECHO + Testing with redirected output using Python for x86 ISA...
  CALL %PYTHON_X86% "%~dpn0.py" %* >nul
  IF NOT ERRORLEVEL 1 (
    ECHO + Testing with redirected output using Python for x64 ISA...
    CALL %PYTHON_X64% "%~dpn0.py" %* >nul
  )
  IF ERRORLEVEL 1 (
    ECHO   - Failed with error %ERRORLEVEL%!
    ENDLOCAL
    EXIT /B %ERRORLEVEL%
  )
  ECHO + Done.
  ENDLOCAL
  EXIT /B 0
