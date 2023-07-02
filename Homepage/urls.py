from django.urls import path , include
from . import views

urlpatterns = [
    
    path('',views.renderHome , name="Home"),
    path('userhome',views.renderUserhome , name="userhome")
]
