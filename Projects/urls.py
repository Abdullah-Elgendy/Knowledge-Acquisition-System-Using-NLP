from django.urls import path , include
from . import views

urlpatterns = [
    
    path('createProject',views.renderCreateProject , name="createProject"),
    path('myProjects',views.renderMyProjects , name="myProjects"),
    path('choosesymptoms',views.renderChooseSymptoms , name='choosesymptoms'),
    path('reasoning',views.renderReasoning , name='reasoning'),
    path('profile',views.renderUserProfile , name="profile"),
    path('createxml',views.createXML , name="createxml"),
    
]
