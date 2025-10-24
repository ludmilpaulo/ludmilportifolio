from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('login/', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('logout/', views.user_logout, name='user_logout'),
    
    # Password management
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('change-password/', views.change_password, name='change_password'),
    
    # User profile
    path('profile/', views.get_user_profile, name='get_user_profile'),
    path('profile/update/', views.update_user_profile, name='update_user_profile'),
    
    # Activity logs
    path('login-history/', views.get_login_history, name='get_login_history'),
]
