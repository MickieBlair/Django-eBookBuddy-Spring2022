from django.core.serializers.python import Serializer
from django.contrib.humanize.templatetags.humanize import naturaltime
from staff_chat.utils import calculate_timestamp, calculate_date_time
from rest_framework import serializers
from reading_sessions.models import Redirect
from matches.models import Temporary_Match
from users.models import CustomUser
from buddy_program_data.models import Room


class LazyMatchStatusEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'match_status_id': int(obj.id)})
		dump_object.update({'get_type': str(obj.get_type())})
		dump_object.update({'match_status_active': bool(obj.match_status_active)})
		dump_object.update({'session_id': int(obj.session.id)})
		dump_object.update({'session_slot': str(obj.session.day_time.session_slot)})
		dump_object.update({'student_id': int(obj.get_student().id)})
		dump_object.update({'student_online': bool(obj.get_student().session_status.online_ws)})
		dump_object.update({'display_student_location': bool(obj.display_student_location)})
		dump_object.update({'buddy_id': int(obj.get_buddy().id)})
		dump_object.update({'buddy_online': bool(obj.get_buddy().session_status.online_ws)})
		dump_object.update({'display_buddy_location': bool(obj.display_reader_location)})
		if obj.get_student().session_status.room:
			dump_object.update({'student_room_name': str(obj.get_student().session_status.room.name)})
			dump_object.update({'student_room_slug': str(obj.get_student().session_status.room.slug)})
		if obj.get_buddy().session_status.room:
			dump_object.update({'reader_room_name': str(obj.get_buddy().session_status.room.name)})
			dump_object.update({'reader_room_slug': str(obj.get_buddy().session_status.room.slug)})
		if(obj.match_type):
			dump_object.update({'match_type': str(obj.match_type.name)})
		else:
			dump_object.update({'match_type': "Broken"})
		dump_object.update({'complete': bool(obj.both_online)})
		dump_object.update({'status': str(obj.status.name)})
		if obj.room:
			dump_object.update({'status_room_name': str(obj.room.name)})
			dump_object.update({'status_room_slug': str(obj.room.slug)})

		dump_object.update({'student_username': str(obj.get_student().username)})
		dump_object.update({'student_full_name': str(obj.get_student().full_name())})
		dump_object.update({'reader_username': str(obj.get_buddy().username)})
		dump_object.update({'reader_full_name': str(obj.get_buddy().full_name())})
		return dump_object

class UserSerializer(serializers.ModelSerializer):	
	full_name = serializers.SerializerMethodField()
	class Meta:
		model = CustomUser
		fields = (
		'id',
		'username',
		'full_name',
		)

	def get_full_name(self, obj):  # "get_" + field name
		return obj.first_name + " " + obj.last_name

class RoomSerializer(serializers.ModelSerializer):
	class Meta:
		model = Room
		fields = (
		'id',
		'name',
		'slug',
		)

class TemporaryMatchSerializer(serializers.ModelSerializer):
	class Meta:
		model = Temporary_Match
		fields = '__all__'

class RedirectSerializer(serializers.ModelSerializer):
	to_room = RoomSerializer(many=False, read_only=True)
	to_user = UserSerializer(many=False, read_only=True)
	user_to_redirect = UserSerializer(many=False, read_only=True)
	class Meta:
		model = Redirect
		fields = (
		'user_to_redirect',
		'to_room',
		'to_user',
		'auto_send',
		)


class LazyUserSessionStatusEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'user_id': int(obj.user.id)})
		dump_object.update({'username': str(obj.user.username)})
		dump_object.update({'full_name': str(obj.user.full_name())})
		dump_object.update({'online_ws': bool(obj.online_ws)})
		dump_object.update({'online_jitsi': bool(obj.online_jitsi)})
		dump_object.update({'has_redirect': bool(obj.has_redirect)})
		return dump_object


class LazyRoomParticipantsEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'room_id': int(obj.id)})
		dump_object.update({'room_name': str(obj.name)})
		dump_object.update({'ws_count': int(obj.ws_count)})
		dump_object.update({'jitsi_count': int(obj.jitsi_count)})
		ws_participants = obj.ws_users.all()
		s = LazyMeetingParticipantsEncoder()
		dump_object.update({'ws_participants': s.serialize(ws_participants)})
		jitsi_participants = obj.jitsi_users.all()
		s = LazyMeetingParticipantsEncoder()
		dump_object.update({'jitsi_participants': s.serialize(jitsi_participants)})
		
		return dump_object

class LazyMeetingParticipantsEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'member_id': str(obj.id)})
		dump_object.update({'username': str(obj.username)})
		dump_object.update({'full_name': str(obj.full_name())})
		return dump_object

class LazyRedirectEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'redirect_id': int(obj.id)})
		dump_object.update({'user_to_redirect_id': int(obj.user_to_redirect.id)})
		dump_object.update({'user_to_redirect_name': str(obj.user_to_redirect.full_name())})
		dump_object.update({'auto_send': bool(obj.auto_send)})
		dump_object.update({'to_room_id': int(obj.to_room.id)})
		dump_object.update({'to_room_name': str(obj.to_room.name)})
		dump_object.update({'to_room_slug': str(obj.to_room.slug)})
		dump_object.update({'redirect_url': str(obj.redirect_url)})
		return dump_object


class LazyHelpEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'request_id': int(obj.id)})
		dump_object.update({'from_user_id': int(obj.from_user.id)})
		dump_object.update({'username': str(obj.from_user.username)})
		dump_object.update({'full_name': str(obj.from_user.full_name())})
		dump_object.update({'from_room_id': int(obj.from_room.id)})
		dump_object.update({'from_room': str(obj.from_room.name)})
		dump_object.update({'from_room_slug': str(obj.from_room.slug)})
		dump_object.update({'created': calculate_timestamp(obj.created)})
		dump_object.update({'message': str(obj.message)})
		dump_object.update({'user_message': str(obj.user_message)})
		dump_object.update({'room_url': str(obj.room_url)})
		dump_object.update({'done': bool(obj.done)})
		if obj.visited_by:
			dump_object.update({'visited_by_id': int(obj.visited_by.id)})
			dump_object.update({'visited_by_username': str(obj.visited_by.username)})
			dump_object.update({'visited_by_full_name': str(obj.visited_by.full_name())})
			dump_object.update({'visited_time': calculate_timestamp(obj.visited_time)})
		# print(dump_object)
		return dump_object