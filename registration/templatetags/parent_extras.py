from django import template
from django.template.defaultfilters import stringfilter
from buddy_program_data.models import Question
from buddy_program_data.models import Form_Message
from buddy_program_data.models import Program_Semester

register = template.Library()

@register.filter(name='active_semester_title')
@stringfilter
def active_semester_title(lang_iso):
	form_message = Form_Message.objects.get(name="Active Semester", for_form__name="Parent Registration")
	print("\n\n\n\nMessage Title", form_message)

	if lang_iso == "en":
		message = form_message.message_content

	elif lang_iso == "es":
		message =  form_message.span_content

	else:
		message="Else"

	print("MESSAGE", lang_iso, message)
	return message

@register.filter(name='active_semester_dates')
@stringfilter
def active_semester_dates(lang_iso):
	message = Form_Message.objects.get(name="Active Semester Dates", for_form__name="Parent Registration")
	if lang_iso == "en":
		message = message.message_content
	elif lang_iso == "es":
		message =  message.span_content
	return message

@register.filter(name='button_text')
@stringfilter
def button_text(lang_iso):
	message = Form_Message.objects.get(name="Complete Form", for_form__name="Student Pre-Registration")
	if lang_iso == "en":
		 button_text = message.message_content
	elif lang_iso == "es":
		button_text =  message.span_content
	return button_text

@register.filter(name='question_number')
@stringfilter
def question_number(field_name):
	question = Question.objects.get(field_name=field_name, for_form__name="Parent Registration")
	if question.question_number:
		question_number_string = str(question.question_number) + ". "
	else:
		question_number_string = ""	
	return question_number_string

@register.filter(name='question_required')
@stringfilter
def question_required(field_name):
	question = Question.objects.get(field_name=field_name, for_form__name="Parent Registration")
	if question.required == "Yes":
		question_required_string = "*"
	else:
		question_required_string = " "
	return question_required_string


@register.filter(name='indent_question')
@stringfilter
def indent_question(field_name):
	question = Question.objects.get(field_name=field_name, for_form__name="Parent Registration")
	if question.question_number:
		field_indent = any(c.isalpha() for c in question.question_number)
		return field_indent
	else:
		return False