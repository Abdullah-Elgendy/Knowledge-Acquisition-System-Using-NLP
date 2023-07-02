from django.db import models
from django.contrib.auth.models import User
from . import utils

class Project(models.Model):
    Title = models.CharField(max_length=100 , default= 'project' , verbose_name = 'Project Title') 
    Description = models.TextField(null=True, blank=True , verbose_name = 'Project Description')
    Url_1 = models.URLField(max_length=500 , null= True , blank= True , verbose_name = 'First Url')
    Url_2 = models.URLField(max_length=500 , null= True , blank= True , verbose_name = 'Second Url')
    Url_3 = models.URLField(max_length=500 , null= True , blank= True , verbose_name = 'Third Url')
    Url_4 = models.URLField(max_length=500 , null= True , blank= True , verbose_name = 'Fourth Url')
    XML = models.FileField(upload_to='uploads', null=True , blank=True , validators=[utils.validate_file_extension])
    User = models.OneToOneField(User, verbose_name= "Creator", on_delete=models.CASCADE)
    
    def __str__(self):
        return self.Title
    
    class Meta:
       verbose_name = 'Project' 
       