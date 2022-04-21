Del .\Main.exe
pyinstaller -F -w Main.py
Del .\Main.spec

rmdir /s /q __pycache__
rmdir /s /q build

