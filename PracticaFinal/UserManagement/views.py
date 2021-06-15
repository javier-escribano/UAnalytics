from django.shortcuts import render
from .forms import *
from UserManagement import models
from django.contrib import messages #import messages
from django.shortcuts import  render, redirect
from django.contrib.auth import login, authenticate, logout #add this
from django.contrib.auth.forms import AuthenticationForm #add this
from django.contrib.auth.decorators import login_required

# ----------------------------------------------------------------------------------------------------------------------------#
# ----------------------------------------------GESTIÓN DE USUARIOS-----------------------------------------------------------#
# ----------------------------------------------------------------------------------------------------------------------------#

# REGISTRO
# ----------------------------------------------------------#
def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
  
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("/")

		messages.error(request, "Unsuccessful registration. Invalid information.")
  
	form = NewUserForm
	return render (request=request, template_name="main/register.html", context={"register_form":form})

# LOGIN
# ----------------------------------------------------------#
def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
  
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
        
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("/")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
   
	form = AuthenticationForm()
	return render(request=request, template_name="main/login.html", context={"login_form":form})

# LOGOUT
# ----------------------------------------------------------#
def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
 
	return redirect("/")

# PAGINA DE MI CUENTA
# ----------------------------------------------------------#
@login_required
def myaccount(request):
    current_user = request.user
    data = models.History.objects.all().filter(username=current_user)
    return render(request=request, template_name="main/myaccount.html", context={'data': data})
