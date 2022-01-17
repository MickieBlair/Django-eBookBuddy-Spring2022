from datetime import datetime
from django.contrib.humanize.templatetags.humanize import naturalday
from django.core.serializers.python import Serializer
import pytz
from django.utils import timezone
from django.conf import settings
from pytz import timezone

from private_chat.models import PrivateChatRoom, User_Private_Room_List, Private_Chat_Error
from private_chat.private_chat_constants import *

def find_or_create_private_chat(user1, user2):
	try:
		if PrivateChatRoom.objects.filter(user1=user1, user2=user2).exists():
			chat = PrivateChatRoom.objects.get(user1=user1, 
													user2=user2)
		elif PrivateChatRoom.objects.filter(user1=user2, user2=user1).exists():
			chat = PrivateChatRoom.objects.get(user1=user2, 
													user2=user1)
		else:
			chat, created = PrivateChatRoom.objects.get_or_create(user1=user1,
																user2=user2,
																last_use=timezone.now())

		user1_list, created = User_Private_Room_List.objects.get_or_create(user=user1)
		print(user1_list)
		user1_list.add_room(chat)

		user2_list, created = User_Private_Room_List.objects.get_or_create(user=user2)
		print(user2_list)
		user2_list.add_room(chat)

	except Exception as e:
		print("BROKEN find_or_create_private_chat", e)
		Private_Chat_Error.objects.create(file="utils.py",
						function_name="find_or_create_private_chat",
						location_in_function="try block for find_or_create_private_chat",
						occurred_for_user=user1.username,
						error_text=e)

	return chat

def calculate_timestamp(timestamp):

	timestamp = timestamp.astimezone(timezone('US/Eastern'))
	ts = ""
	if (naturalday(timestamp) == "today") or (naturalday(timestamp) == "yesterday"):
		str_time = datetime.strftime(timestamp, "%I:%M %p")
		str_time = str_time.strip("0")
		ts = f"{naturalday(timestamp)} at {str_time}"
	# other days
	else:
		str_time = datetime.strftime(timestamp, "%m/%d/%Y")
		ts = f"{str_time}"
	return str(ts)

def calculate_date_time(timestamp):

	timestamp = timestamp.astimezone(timezone('US/Eastern'))
	return str(timestamp)