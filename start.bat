cd C:\GoogleDrive\earthshaker-aftershock
REM del *.pyc
ping -n 6 127.0.0.1 > nul
python earthshaker.py
pause