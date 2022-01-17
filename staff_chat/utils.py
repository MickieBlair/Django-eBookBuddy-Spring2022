from datetime import datetime
from django.contrib.humanize.templatetags.humanize import naturalday
from django.core.serializers.python import Serializer
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