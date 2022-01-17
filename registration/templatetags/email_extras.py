from django import template
from django.template.defaultfilters import stringfilter
from registration.models import Parent_Registration

register = template.Library()

@register.filter(name='user_info')
@stringfilter
def user_info(reg_type, registration_id):
	if reg_type == "Parent":
		parent_reg = Parent_Registration.objects.get(id = registration_id)
	return parent_reg



