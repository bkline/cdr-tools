@REM $Id$
@grep -v "zip as CDR" //bach/d$/cdr/log/Request4926.log | grep -v ": Processing CDR0" | grep -v ": saveDoc(" | grep -v "row 0: invalid literal for int" | grep -v "Docs examined" | grep -v "Docs changed" | grep -v "Versions changed" | grep -v "Time (hh:mm:ss)" | grep -v "Running in real mode" | grep -v "documents selected" | grep -v "new cwd = " | grep -v "new pub = " | grep -v "old cwd = " | grep -v "Specific versions saved:" | grep -v "new ver = " | grep -v "Could not lock   =" | grep -v "Errors           =" | grep -v ": Run completed" | grep -v "Purpose: Request 4926"
