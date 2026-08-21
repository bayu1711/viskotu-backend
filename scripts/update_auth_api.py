import re

with open('apps/users/views.py', 'r') as f:
    content = f.read()

import_reqs = "import requests\nfrom google.oauth2 import id_token"

if "import requests" not in content:
    content = content.replace("from google.oauth2 import id_token", import_reqs)

# Replace the verification block
old_verification = """        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                settings.GOOGLE_CLIENT_ID
            )
            
            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
        except ValueError:
            return Response({'error': 'Invalid Google token'}, status=status.HTTP_400_BAD_REQUEST)"""

new_verification = """        try:
            # Verify the access token by fetching user info
            response = requests.get(f'https://www.googleapis.com/oauth2/v3/userinfo?access_token={token}')
            if response.status_code != 200:
                return Response({'error': 'Invalid Google access token'}, status=status.HTTP_400_BAD_REQUEST)
            
            idinfo = response.json()
            email = idinfo.get('email')
            if not email:
                return Response({'error': 'Google account has no email'}, status=status.HTTP_400_BAD_REQUEST)

            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
        except Exception as e:
            return Response({'error': 'Invalid Google token'}, status=status.HTTP_400_BAD_REQUEST)"""

content = content.replace(old_verification, new_verification)

with open('apps/users/views.py', 'w') as f:
    f.write(content)

