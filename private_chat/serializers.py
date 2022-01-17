from django.core.serializers.python import Serializer
from django.contrib.humanize.templatetags.humanize import naturaltime
from private_chat.utils import calculate_timestamp, calculate_date_time
from private_chat.private_chat_constants import *

from private_chat.models import UnreadPrivateChatMessages

class LazyCustomUserEncoder(Serializer):
	def get_dump_object(self, obj):
		# print(obj.session_status.room)
		dump_object = {}
		dump_object.update({'user_id': str(obj.id)})
		dump_object.update({'username': str(obj.username)})
		# dump_object.update({'role': str(obj.role.name)})
		dump_object.update({'full_name': str(obj.full_name())})
		if obj.session_status.room:
			dump_object.update({'location_id': str(obj.session_status.room.id)})	
			dump_object.update({'location_name': str(obj.session_status.room.name)})	
			dump_object.update({'location_slug': str(obj.session_status.room.slug)})	
		# print(dump_object)
		return dump_object


class LazyMeetingParticipantsEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'member_id': str(obj.id)})
		dump_object.update({'username': str(obj.username)})
		# dump_object.update({'role': str(obj.role.name)})
		dump_object.update({'full_name': str(obj.full_name())})
		# dump_object.update({'needs_match': bool(obj.session_status.needs_session_match)})
		# print(dump_object)
		return dump_object

class LazyPrivateRoomChatMessageEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'msg_type': PRIVATE_MSG_TYPE_MESSAGE})
		dump_object.update({'msg_id': str(obj.id)})
		dump_object.update({'user_id': str(obj.user.id)})
		dump_object.update({'username': str(obj.user.username)})
		if obj.user.session_status.room:
			dump_object.update({'in_room_id': str(obj.user.session_status.room.id)})
			dump_object.update({'in_room_name': str(obj.user.session_status.room.name)})
			dump_object.update({'in_room_slug': str(obj.user.session_status.room.slug)})
		dump_object.update({'message': str(obj.content)})
		dump_object.update({'natural_timestamp': calculate_timestamp(obj.timestamp)})
		return dump_object


class LazyPrivateRoomEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'private_room_id': int(obj.id)})
		dump_object.update({'user1_id': int(obj.user1.id)})
		dump_object.update({'user1_name': str(obj.user1.full_name())})
		dump_object.update({'user1_unread': int(obj.unread_count_by_user(obj.user1))})
		dump_object.update({'user2_id': int(obj.user2.id)})
		dump_object.update({'user2_name': str(obj.user2.full_name())})
		dump_object.update({'user2_unread': int(obj.unread_count_by_user(obj.user2))})
		dump_object.update({'total': int(obj.total_message_count())})

		return dump_object