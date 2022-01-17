from django.core.serializers.python import Serializer
from django.contrib.humanize.templatetags.humanize import naturaltime
from staff_chat.utils import calculate_timestamp, calculate_date_time
from staff_chat.staff_chat_constants import *

class LazyStaffRoomChatMessageEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'msg_type': STAFF_MSG_TYPE_MESSAGE})
		dump_object.update({'msg_id': int(obj.id)})
		dump_object.update({'user_id': int(obj.user.id)})
		dump_object.update({'username': str(obj.user.username)})
		dump_object.update({'full_name': str(obj.user.full_name())})
		dump_object.update({'message': str(obj.content)})
		dump_object.update({'meeting_room_id': int(obj.meeting_room.id)})
		dump_object.update({'meeting_room_name': str(obj.meeting_room.name)})
		dump_object.update({'natural_timestamp': calculate_timestamp(obj.timestamp)})
		dump_object.update({'date_time': calculate_date_time(obj.timestamp)})
		return dump_object

class LazyStaffEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'userID': int(obj.id)})
		dump_object.update({'staff_unread_count': int(obj.unread_staff.unread_count)})
		# print(dump_object)
		return dump_object

class LazyStaffInRoomEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'user_id': int(obj.id)})
		dump_object.update({'username': str(obj.username)})
		dump_object.update({'room': str(obj.session_status.room)})
		# print(dump_object)
		return dump_object