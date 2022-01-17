# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout

from users.models import Role
from users.models import Program
from users.models import CustomUser

import json
from json import dumps
from django.http import JsonResponse, HttpResponse

from django.conf import settings
from django.core.mail import send_mail



from users.forms import Create_User_Form, AccountAuthenticationForm, User_Update_Form

def get_program_status(name):
	program = Program.objects.get(name=name)
	updating_now = program.program_status.updating
	return updating_now


# Create your views here.
def login_view(request):
	context = {}
	context['page_title'] = "Login"
	context['display_login_logout']= False
	context['user_role']= "None"


	# updating_now = get_program_status()
	# if updating_now:
	# 	return redirect('update_in_progress')

	# else:	

	if not request.user.is_anonymous:
		user = request.user
		if user.is_authenticated:
			if user.is_approved:
				return redirect('landing')				
			else:
				return redirect('pending_approval')

	if request.POST:
		form = AccountAuthenticationForm(request.POST)
		
		# print("username password", username, password)
		# if '@' in username:
		# 	print("HAS @")
		# 	user = CustomUser.objects.get(email=username)
		# 	print("user", user)
		# 	username = user.username

		# else:
		# 	print("NO @")

		if form.is_valid():
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)

			if user:
				login(request, user)
				if user.is_approved:
					return redirect('landing')				
				else:
					return redirect('pending_approval')
		else:
			print('form errors', form.errors)

	else:
		form = AccountAuthenticationForm()

	context['login_form'] = form

	return render(request, "users/login.html", context)

def logout_view(request):
	print("Logging out")
	logout(request)
	return redirect('/')

def must_authenticate_view(request):
	context['display_login_logout']= True
	return render(request, 'users/must_authenticate.html', {})

def denied_view(request):
	context['display_login_logout']= True
	return render(request, 'users/access_denied.html', {})

def login_as_different_user(request):
	logout(request)
	return redirect('login')


def email_check(request):
  response = {}
  # request should be ajax and method should be GET.
  if request.is_ajax and request.method == "GET":
    # get from the client side.   
    email = request.GET.get("target_id", None)

    # check database.
    if CustomUser.objects.filter(email = email).exists():
      response['valid'] = True
      
      return HttpResponse(dumps(response), content_type="application/json")
    else:
      response['valid'] = False
      return HttpResponse(dumps(response), content_type="application/json")

  return JsonResponse({}, status = 400)