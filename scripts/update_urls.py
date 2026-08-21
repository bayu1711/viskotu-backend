import re

with open('apps/users/urls.py', 'r') as f:
    content = f.read()

if "GoogleLoginView" not in content:
    content = content.replace(
        "path('login/', views.LoginView.as_view(), name='auth-login'),",
        "path('login/', views.LoginView.as_view(), name='auth-login'),\n    path('google/', views.GoogleLoginView.as_view(), name='auth-google'),"
    )
    
    with open('apps/users/urls.py', 'w') as f:
        f.write(content)

