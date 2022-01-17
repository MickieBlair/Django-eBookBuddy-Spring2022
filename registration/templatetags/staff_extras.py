from django import template
from django.template.defaultfilters import stringfilter
from buddy_program_data.models import Question

register = template.Library()

@register.filter(name='question_number')
@stringfilter
def question_number(field_name):
	question = Question.objects.get(field_name=field_name, for_form__name="Staff Registration")
	if question.question_number:
		question_number_string = str(question.question_number) + ". "
	else:
		question_number_string = ""	
	return question_number_string

@register.filter(name='question_required')
@stringfilter
def question_required(field_name):
	question = Question.objects.get(field_name=field_name, for_form__name="Staff Registration")
	if question.required == "Yes":
		question_required_string = "*"
	else:
		question_required_string = " "
	return question_required_string


@register.filter(name='indent_question')
@stringfilter
def indent_question(field_name):
	question = Question.objects.get(field_name=field_name, for_form__name="Staff Registration")
	if question.question_number:
		field_indent = any(c.isalpha() for c in question.question_number)
		return field_indent
	else:
		return False