from django import template
from django.template.defaultfilters import stringfilter
from django.utils import timezone
from matches.models import Scheduled_Match, Temporary_Match
from matches.models import Match_Attendance_Record, Match_Status_Option


register = template.Library()

@register.filter(name='status')
def status(match_record):
	if match_record.status:
		return match_record.status
	else:
		return ""
	



	
