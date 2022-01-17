from django.conf import settings
import jwt
from django.utils import timezone
from datetime import datetime
import math

APP_ID=settings.APP_ID
APP_SUB=settings.APP_SUB
APP_SECRET=settings.APP_SECRET


def generateBaseTokenVolunteerTesting(username, email, role):
	token = "token"
	if role == "Staff":
		affiliation = "owner"
	elif role == "Volunteer":
		affiliation = "moderator"
	elif role == "Student":
		affiliation = "moderator"

	payload = {}
	payload['aud'] = APP_ID
	payload['iss'] = APP_ID
	payload['sub'] = APP_SUB
	payload['exp'] = math.ceil(datetime.timestamp(timezone.now() + timezone.timedelta(hours=4)))
	payload['room'] = "*"
	context = {}
	context['user'] = {
			  "name": username,
			  "email": email,		  
			  "affiliation": affiliation,
			  "session_role": role,
			}

	payload['context'] = context
	# print(payload)

	token = jwt.encode(
		payload, APP_SECRET, algorithm='HS256'
		)
	
	return token

