import re

with open('config/settings.py', 'r') as f:
    content = f.read()

if "GOOGLE_CLIENT_ID" not in content:
    content += "\n\nGOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')\n"
    
    with open('config/settings.py', 'w') as f:
        f.write(content)

with open('.env', 'r') as f:
    env_content = f.read()

if "GOOGLE_CLIENT_ID" not in env_content:
    env_content += "\nGOOGLE_CLIENT_ID=23482707320-oq0uk7gol6tufaqt8kc7pl14qek2ikf7.apps.googleusercontent.com\n"
    
    with open('.env', 'w') as f:
        f.write(env_content)

