from rest_framework import serializers
import json
from jitsi_data.models import Jitsi_User_Status
from jitsi_data.models import Jitsi_User_Event
from jitsi_data.models import Jitsi_Room_Occupant
from jitsi_data.models import Jitsi_Room

from datetime import datetime
from django.utils.timezone import make_aware

def format_local_time_api(api_time):
	return make_aware(datetime.fromtimestamp(api_time))

class Jitsi_Room_Occupant_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Jitsi_Room_Occupant
		fields = ['name', 'email', 'occupant_jid', 
				'joined_at', 'left_at',]

class Jitsi_Room_Occupant_Create_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Jitsi_Room_Occupant
		fields = ['name', 'email', 'occupant_jid', 
				'joined_at', 'left_at',]

	def save(self):        
		try:
			data = self.validated_data
			name = self.validated_data['name']
			email = self.validated_data['email']
			occupant_jid = self.validated_data['occupant_jid']
			joined_at = self.validated_data['joined_at']
			left_at = self.validated_data['left_at']

			jitsi_user, created = Jitsi_Room_Occupant.objects.get_or_create(
									name = name,
									email = email,
									occupant_jid = occupant_jid,
									joined_at = joined_at,
									left_at = left_at,								
									)
			return jitsi_user, created

		except KeyError as e:
			str_e = 'KeyError:  ' + str(e)
			raise serializers.ValidationError({"response": str_e})
		except Exception as e:
			str_e = 'Exception:  ' + str(e)
			raise serializers.ValidationError({"response": str_e})

class Jitsi_Room_Serializer(serializers.ModelSerializer):
	all_occupants = Jitsi_Room_Occupant_Serializer(many=True)
	class Meta:
		model = Jitsi_Room
		fields = ['id','room_name', 'room_jid', 'event_name', 'created_at', 
				'destroyed_at','all_occupants',]


class Jitsi_Room_Create_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Jitsi_Room
		fields = ['event_name', 'room_name', 'room_jid', 'created_at']	

	def save(self):        
		try:
			data = self.validated_data
			print("data", data, type(data))
			event_name = self.validated_data['event_name']
			room_name = self.validated_data['room_name']
			room_jid = self.validated_data['room_jid']
			created_at = self.validated_data['created_at']

			jitsi_room_event, created = Jitsi_Room.objects.get_or_create(									
									room_name = room_name,
									room_jid = room_jid,
									created_at = created_at,								
									)
			if created:
				jitsi_room_event.event_name = event_name
				jitsi_room_event.save()

			return jitsi_room_event, created

		except KeyError as e:
			str_e = 'KeyError:  ' + str(e)
			raise serializers.ValidationError({"response": str_e})
		except Exception as e:
			str_e = 'Exception:  ' + str(e)
			raise serializers.ValidationError({"response": str_e})

class Jitsi_Room_Update_Serializer(serializers.ModelSerializer):
	all_occupants = Jitsi_Room_Occupant_Serializer(many=True)
	class Meta:
		model = Jitsi_Room
		fields = ['id','room_name', 'room_jid', 'event_name', 'created_at', 
				'destroyed_at','all_occupants']

	def create(self, validated_data):
		print("\n\n\n\nJitsi_Room_Update_Serializer create", validated_data)
		print
		try:
			occupants_data = validated_data.pop('all_occupants')

			jitsi_room_event, created = Jitsi_Room.objects.get_or_create(
									room_name = validated_data['room_name'],
									room_jid = validated_data['room_jid'],
									created_at = validated_data['created_at'],								
									)

			jitsi_room_event.event_name = validated_data['event_name']
			jitsi_room_event.destroyed_at = validated_data['destroyed_at']				
			jitsi_room_event.save()

			for occupant_data in occupants_data:
				j_user, created_u = Jitsi_Room_Occupant.objects.get_or_create(jitsi_room=jitsi_room_event, **occupant_data)
				j_user.fill_in_duration()

			return jitsi_room_event, created

		except KeyError as e:
			str_e = 'KeyError:  ' + str(e)
			raise serializers.ValidationError({"response": str_e})
		except Exception as e:
			str_e = 'Exception:  ' + str(e)
			raise serializers.ValidationError({"response": str_e})



class Jitsi_User_Event_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Jitsi_User_Event
		fields = ['id','event_name', 'room_name', 'room_jid', 'occupant_name', 
		'occupant_email','occupant_id', 'occupant_jid',
		'occupant_joined_at', 'occupant_left_at']

class Jitsi_User_Status_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Jitsi_User_Status
		fields = ['id','user', 'online', 'date_created', 'last_updated' ]


class Jitsi_User_Event_Create_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Jitsi_User_Event
		fields = ['event_name', 'room_name', 'room_jid', 'occupant_name', 
		'occupant_email', 'occupant_jid',
		'occupant_joined_at', 'occupant_left_at']

	def save(self):        
		try:
			data = self.validated_data
			print("data", data, type(data))
			event_name = self.validated_data['event_name']
			room_name = self.validated_data['room_name']
			room_jid = self.validated_data['room_jid']
			occupant_name = self.validated_data['occupant_name']
			occupant_email = self.validated_data['occupant_email']
			occupant_jid=self.validated_data['occupant_jid']
			occupant_joined_at=self.validated_data['occupant_joined_at']
			occupant_left_at=self.validated_data['occupant_left_at']


		
			user_status, created = Jitsi_User_Event.objects.get_or_create(
									event_name = event_name,
									room_name = room_name,
									room_jid = room_jid,
									occupant_name=occupant_name,
									occupant_email = occupant_email,
									occupant_jid=occupant_jid,
									occupant_joined_at=occupant_joined_at,
									occupant_left_at=occupant_left_at,
									)
			return user_status, created

		except KeyError as e:
			str_e = 'KeyError:  ' + str(e)
			raise serializers.ValidationError({"response": str_e})
		except Exception as e:
			str_e = 'Exception:  ' + str(e)
			raise serializers.ValidationError({"response": str_e})

class Jitsi_User_Event_Update_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Jitsi_User_Event
		fields = ['event_name', 'room_name', 'room_jid', 'occupant_name', 
		'occupant_email', 'occupant_jid',
		'occupant_joined_at', 'occupant_left_at']

	def save(self):        
		try:
			data = self.validated_data
			print("data", data, type(data))
			event_name = self.validated_data['event_name']
			room_name = self.validated_data['room_name']
			room_jid = self.validated_data['room_jid']
			occupant_name = self.validated_data['occupant_name']
			occupant_email = self.validated_data['occupant_email']
			occupant_jid=self.validated_data['occupant_jid']
			occupant_joined_at=self.validated_data['occupant_joined_at']
			occupant_left_at=self.validated_data['occupant_left_at']

		
			user_status, created = Jitsi_User_Event.objects.get_or_create(
									room_name = room_name,
									room_jid = room_jid,
									occupant_name=occupant_name,
									occupant_email = occupant_email,
									occupant_jid=occupant_jid,
									occupant_joined_at=occupant_joined_at,
									)
			
			user_status.occupant_left_at = occupant_left_at
			user_status.event_name = event_name
			user_status.save()
			print("\n\n\n\nuser_status", user_status)
			user_status.fill_in_duration()

			return user_status, created

		except KeyError as e:
			str_e = 'KeyError:  ' + str(e)
			print("KeyError", str_e)
			raise serializers.ValidationError({"response": str_e})
		except Exception as e:
			print("serializer", e)

			# str_e = str(e)
			
			raise serializers.ValidationError({"response": str_e})

