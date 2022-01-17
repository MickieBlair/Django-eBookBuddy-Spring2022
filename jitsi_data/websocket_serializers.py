from django.core.serializers.python import Serializer
from django.contrib.humanize.templatetags.humanize import naturaltime
import pytz
from django.utils import timezone
from django.conf import settings
from pytz import timezone

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


class LazyJitsiDataRoomEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'room_id': int(obj.id)})
		dump_object.update({'room_name': str(obj.room_name)})
		dump_object.update({'created_at': str(calculate_date_time(obj.created_at))})
		dump_object.update({'destroyed_at': str(calculate_date_time(obj.destroyed_at))})
		all_occupants = obj.all_occupants.all()
		s = LazyJitsiDataUserEncoder()
		dump_object.update({'occupants': s.serialize(all_occupants)})
		return dump_object


class LazyJitsiDataUserEncoder(Serializer):
	def get_dump_object(self, obj):
		dump_object = {}
		dump_object.update({'instance_id': str(obj.id)})
		dump_object.update({'name': str(obj.name)})
		dump_object.update({'jitsi_id': str(obj.jitsi_id)})
		dump_object.update({'joined_at': str(calculate_date_time(obj.joined_at))})
		dump_object.update({'left_at': str(calculate_date_time(obj.left_at))})
		# print(dump_object)
		return dump_object