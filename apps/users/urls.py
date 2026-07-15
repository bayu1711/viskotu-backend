from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='auth-signup'),
    path('login/', views.LoginView.as_view(), name='auth-login'),
    path('logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('me/', views.MeView.as_view(), name='auth-me'),
    path('switch-role/', views.SwitchRoleView.as_view(), name='auth-switch-role'),
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='auth-password-reset'),
    path('password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='auth-verify-email'),
    path('resend-verification/', views.ResendVerificationView.as_view(), name='auth-resend-verification'),
]
