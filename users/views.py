from distutils.log import error
from email import message
from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from .utils import paginatioProfiles, searchProfiles
from .forms import CustomUserCreationForm,ProfileForm,SkillForm,MessageForm
from. models import Profile,Message
# Create your views here.

def loginUser(request):
    page='login'
    context={'page':page}

    if request.user.is_authenticated:
        return redirect('profiles')

    if request.method=="POST":
        username=request.POST['username'].lower()
        password=request.POST['password']

        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request,'username does not exist')
        user=authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            messages.success(request,"logged in sucessfully")
            return redirect(request.GET['next'] if 'next' in request.GET else 'account')
        else:
            messages.error(request,'Username OR password is incorrect')

    return render(request,'users/login_register.html',context)

def logoutUser(request):
    logout(request)
    messages.info(request,'User was logged out')
    return redirect('login')

def registerUser(request):
    page='register'
    form=CustomUserCreationForm()
    context={'page':page,'form':form}
    if request.method=='POST':
        form=CustomUserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            messages.success(request,'User account was created')
            login(request,user)
            return redirect('edit-account')
        else:
            form=CustomUserCreationForm()
            messages.error(request,'An error has occured during registration')
    
    return render(request,'users/login_register.html',context)

def profiles(request):
    profile,search_query =searchProfiles(request)

    profile,custom_range=paginatioProfiles(request,profile,3)
    context={
        'profiles':profile , 
        'search_query':search_query,
        'custom_range':custom_range,
    }
    return render(request,'users/profiles.html',context)
def userProfile(request,pk):
    profile=Profile.objects.get(id=pk)

    topskills=profile.skill_set.exclude(description__exact="")
    otherskills=profile.skill_set.filter(description="")
    context={
        'profile':profile,
        'topskills':topskills,
        'otherskills':otherskills,
    }
    return render(request,'users/user-profile.html',context)

@login_required(login_url='login')
def userAccount(request):
    profile=request.user.profile
    skills=profile.skill_set.all()
    projects=profile.project_set.all()
    context={
        'profile':profile,
        'skills':skills,
        'projects':projects,
    }
    return render(request,'users/account.html',context)

@login_required(login_url='login')
def editAccount(request):
    profile=request.user.profile
    form=ProfileForm(instance=profile)
    
    if request.method=='POST':
        form=ProfileForm(request.POST,request.FILES,instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account')
    context={
        'form':form
    }
    return render(request,'users/profile_form.html',context)

@login_required(login_url='login')
def createSkill(request):
    profile=request.user.profile
    form=SkillForm()
    if request.method=="POST":
        form=SkillForm(request.POST)
        if form.is_valid():
            skill=form.save(commit=False)
            skill.owner=profile
            skill.save()
            messages.success(request,'Skill Added')
            return redirect('account')


    context={'form':form}
    return render(request,'users/skill_form.html',context)
@login_required(login_url='login')
def updateSkill(request,pk):
    profile=request.user.profile
    skill=profile.skill_set.get(id=pk)
    form=SkillForm(instance=skill)
    if request.method=="POST":
        form=SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request,'Skill Updated')
            return redirect('account')
    context={'form':form}
    return render(request,'users/skill_form.html',context)

@login_required(login_url='login')
def deleteSkill(request,pk):
    profile=request.user.profile
    skill=profile.skill_set.get(id=pk)
    if request.method=="POST":
        skill.delete()
        messages.info(request,'Skill deleted')
        return redirect('account')
    context={'object':skill}
    return render(request,'delete_template.html',context)

@login_required(login_url='login')
def inbox(request):
    profile=request.user.profile
    messageRequest= profile.messages.all()
    unreadCount=messageRequest.filter(is_read=False).count()

    context={
        "messageRequest":messageRequest,
        "unreadCount":unreadCount
    }
    return render(request,'users/inbox.html',context)

@login_required(login_url='login')
def viewMessage(request,pk):
    profile=request.user.profile
    messageRequest= profile.messages.get(id=pk)
    if messageRequest.is_read==False:
        messageRequest.is_read=True
        messageRequest.save()
    context={
        "messageRequest":messageRequest,
    }
    return render(request,'users/message.html',context)

@login_required(login_url='login')
def sendMessage(request,pk):
    profile=request.user.profile
    reciever=Profile.objects.get(id=pk)
    form= MessageForm()
    if request.method=='POST':
        form=MessageForm(request.POST)
        if form.is_valid():
            message_sent=form.save(commit=False)
            message_sent.sender=profile
            message_sent.recipient=reciever
            message_sent.name=profile.name
            message_sent.email=profile.email
            message_sent.save()
            messages.success(request,'Message sent')
            return redirect('user-profile', pk=reciever.id)
    context={
        "form":form,
        'profile':reciever
    }
    return render(request,'users/message_form.html',context)
