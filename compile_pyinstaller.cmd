del /f /s /q dist 1>nul
rmdir /s /q dist
pyinstaller.exe --uac-admin --onefile --noconsole --log-level=INFO gui.py --icon=graphics\icon.ico
pyinstaller.exe --uac-admin --onefile --log-level=INFO node.py --icon=graphics\icon.ico
pyinstaller.exe --uac-admin --onefile --log-level=INFO miner.py --icon=graphics\icon.ico
pyinstaller.exe --uac-admin --onefile --log-level=INFO explorer\explorer.py --icon=graphics\icon.ico --hidden-import=explorer
robocopy explorer\static dist\static
copy peers.txt dist\peers.txt
copy ledger.db dist\ledger.db
"C:\Program Files (x86)\Inno Setup 5\iscc" /q "setup.iss"
pause

