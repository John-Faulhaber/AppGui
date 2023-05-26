@echo off
:run
:: Navigate to th directory containing the .exe
call cd appgui
:: Run the .exe, closing the .exe with /C afterwards so the rest of this batch file can run
call CMD /C appgui.exe
:: Return to original directory
call cd ..
:: Pause so user may review printed statements
pause