@ECHO OFF
IF ".%1%." == ".." (
    ECHO Backing up all CDR directories that can be replaced in a deploy-all run
    ECHO Usage: backupDeploy outputdirname
    EXIT /B 1
)
SET ZIPNAME=%1%
zip -r %ZIPNAME% d:\Inetpub d:\cdr\Bin d:\cdr\ClientFiles d:\cdr\Database d:\cdr\lib d:\cdr\Mailers d:\cdr\Publishing d:\cdr\Utilities