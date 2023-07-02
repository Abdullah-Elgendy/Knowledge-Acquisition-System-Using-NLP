from django.shortcuts import HttpResponse, render , redirect , get_object_or_404
import os , mimetypes
from django.http import Http404
from django.conf import settings
from . models import Project
from . forms import projectDataForm , fileUploadForm
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from . import utils

@login_required(login_url='login')
def renderCreateProject(request):
    
    form = projectDataForm()
    
    if request.method == 'POST':
            form = projectDataForm(request.POST)
    
            if form.is_valid():
              Project.objects.filter(User=request.user).delete()
              form.instance.User = request.user
              form.save()
              return redirect('myProjects')
            
    context = {'form':form}
    return render(request , 'Projects/usercreateproject.html' , context )


@login_required(login_url='login')
def renderMyProjects(request):
    try:
       project = get_object_or_404(Project, User=request.user)
    except:
       return redirect('userhome')
    else:
       project = get_object_or_404(Project, User=request.user) 
       context= { 'project': project }
       return render(request , 'Projects/usermyproject.html' , context )  
    
def createXML(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project = get_object_or_404(Project, User=request.user)
    url_list = []
    url1 = project._meta.get_field("Url_1")
    url1_value = url1.value_from_object(project)
    url2 = project._meta.get_field("Url_2")
    url2_value = url2.value_from_object(project)
    url3 = project._meta.get_field("Url_3")
    url3_value = url3.value_from_object(project)
    url4 = project._meta.get_field("Url_4")
    url4_value = url4.value_from_object(project)
    url_list.extend([url1_value,url2_value,url3_value,url4_value]) 
    utils.main(url_list)
    
    filename = '\output.xml'
    filepath = BASE_DIR + filename
    mime_type, _ = mimetypes.guess_type(filepath)
   
    path = open(filepath, 'r')
    response = HttpResponse(path, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response
        
        
        
@login_required(login_url='login')
def renderChooseSymptoms(request):
    
    media_path = settings.MEDIA_ROOT
    project_obj = get_object_or_404(Project, User=request.user)
    file_name = project_obj.XML.name
    file_path = os.path.join(media_path, file_name)
    with open(file_path, 'r') as file:
     list_of_symptoms = utils.extractSymptomsFromXML(file)
     
    context = { 'list': list_of_symptoms }
    
    if request.method == 'POST':
     check = request.POST.getlist('checks[]')
     with open(file_path, 'r') as open_file:
       result , perc = utils.xml_reasoning(open_file, check)
       context = { 'result': result , 'perc': perc }
       return render(request , 'Projects/result.html' , context )
        
    return render(request , 'Projects/choosesymptoms.html' , context )



@login_required(login_url='login')
def renderReasoning(request):
     if request.method == "POST":
        form = fileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES["file"]
            fs = FileSystemStorage()
            fs.save(uploaded_file.name , uploaded_file)
            project_obj = Project.objects.filter(User=request.user)
            project_obj.update(XML=request.FILES["file"])
            return redirect("choosesymptoms")
     else:
        form = fileUploadForm()
     return render(request, "Projects/Reasoning.html", {"form": form})

@login_required(login_url='login')
def renderUserProfile(request):
    
    return render(request , 'Projects/userprofile.html' ) 

