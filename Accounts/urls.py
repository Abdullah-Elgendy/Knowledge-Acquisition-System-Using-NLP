from django.urls import path , include
from . import views

urlpatterns = [
    
    path('login',views.renderLoginPage , name="login"),
    path('signup',views.renderRegisterPage , name="signup"),
    path('forgotpassword',views.renderForgotPassword , name="forgotpassword"),
    path('logout', views.logoutUser, name='logout'),
    
]
