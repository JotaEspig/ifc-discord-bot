rm ifcbot.zip 2> /dev/null
zip -r ifcbot.zip discloud.config ifcbot main.py requirements.txt token.config -x venv\* -x .git\* -x **/__pycache__\* -x "*.db"
