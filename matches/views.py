from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from users.models import CustomUser, Role, User_Note
from buddy_program_data.models import Program_Semester, Daily_Session
from buddy_program_data.models import Program_Status
from buddy_program_data.models import Session_Day_Option
from buddy_program_data.models import Session_Time_Option
from buddy_program_data.models import Session_Meeting_Option
from buddy_program_data.models import Reading_Session_Day_Time
from matches.models import Scheduled_Match, Match_Note
from matches.models import Temporary_Match
from matches.models import Match_Type
from matches.models import Reader_Match_Profile, Student_Match_Profile
from matches.models import Match_Attendance_Record
from matches.forms import Create_Scheduled_Match_Form, Edit_Scheduled_Match_Form
from reading_sessions.models import Match_Session_Status


def post_create_match_student_for_meeting(sch_match):
	pass

def post_create_match_reader_for_meeting(sch_match):
	pass

def post_create_match_for_meeting(sch_match):
	pass

def get_sessions_in_the_future():
	time_now = timezone.localtime(timezone.now())
	qs = Daily_Session.objects.filter(session_start_date_time__gte=time_now)
	print("In the future Count", qs.count())
	return qs

def edit_scheduled_match_view(request, match_id, **kwargs):
	context = {}
	context['page_title'] = "Edit Scheduled Match"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:
				context['time_options'] = Session_Time_Option.objects.filter(active=True)
				context['day_options'] = Session_Day_Option.objects.filter(active=True)
				context['meeting_options'] = convert_session_meeting_choices()
				context['reading_session_options'] = Reading_Session_Day_Time.objects.filter(active=True)

				context = additional_context_all(context)

				match = Scheduled_Match.objects.get(id=match_id)
				context['match'] = match
				match_type=Match_Type.objects.get(name="Scheduled")

				original_match_times = match.day_times
				context['original_match_times'] = original_match_times
				

				if request.method == "POST":
					form = Edit_Scheduled_Match_Form(request.POST, instance=match, label_suffix='')
					if form.is_valid():
						print("Valid")
						obj = form.save()
						# # form.save_m2m()						
						note = Match_Note.objects.create(match_type=match_type,
														name="Scheduled Match Edited",
														created_user=request.user)
						obj.notes.add(note)
						attendance_note = Match_Note.objects.create(match_type=match_type,
														name="Scheduled Match Attendance Records Updated",
														created_user=request.user)						
						obj.notes.add(attendance_note)
						obj.post_edit_match(original_match_times)
						for session in obj.sessions_scheduled.all():
							match_session_status, created = Match_Session_Status.objects.get_or_create(
															match_type = match_type,
															sch_match = obj,
															session=session,
															)
						post_create_match_student_for_meeting(obj)
						post_create_match_reader_for_meeting(obj)
						post_create_match_for_meeting(obj)

						
						return redirect('site_admin:view_scheduled', match_type="Active")
					else:
						print("errors", form.errors)
						
				else:
					print("Student", match.student)
					print("Reader", match.reader)
					form = Edit_Scheduled_Match_Form(label_suffix='',
						instance=match,)

				context['form'] = form

				return render(request, "matches/edit_scheduled_match.html", context)

				
			return redirect('access_denied')

		else:
			return redirect('login')

def deactivate_scheduled_match_view(request, match_id, **kwargs):
	context = {}
	context['page_title'] = "Deactivate Scheduled Match"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:
				match = Scheduled_Match.objects.get(id=match_id)
				print("Deactivating This Match", match)
				match.set_match_inactive()
				note = Match_Note.objects.create(match_type=match.match_type,
												name="Scheduled Match Set Inactive",
												created_user=request.user)
				match.notes.add(note)
				attendance_note = Match_Note.objects.create(match_type=match.match_type,
												name="Scheduled Match Future Attendance Records Deleted",
												created_user=request.user)						
				match.notes.add(attendance_note)


				return redirect('site_admin:view_scheduled', match_type="Active")

				
			return redirect('access_denied')

		else:
			return redirect('login')

def display_match_notes_view(request, match_id, **kwargs):
	context = {}
	context['page_title'] = "Match Notes"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:							
				context = additional_context_all(context)
				match = Scheduled_Match.objects.get(id=match_id)
				context['match'] = match
				
				return render(request, "matches/match_notes.html", context)				
			else:
				return redirect('access_denied')

		else:
			return redirect('login')

def display_match_sessions_view(request, match_id, **kwargs):
	context = {}
	context['page_title'] = "Match Sessions"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:							
				context = additional_context_all(context)
				match = Scheduled_Match.objects.get(id=match_id)
				records = Match_Attendance_Record.objects.filter(sch_match=match)
				context['records'] = records
				context['match'] = match
				context['count'] = match.sessions_scheduled.all().count()				
				context['remaining_count'] = match.remaining_sessions().count()	
				context['successful_count'] = match.successful()	
				context['incomplete_count'] = match.incomplete()	
				
				return render(request, "matches/match_sessions.html", context)				
			else:
				return redirect('access_denied')

		else:
			return redirect('login')


def get_active_semester():
	return Program_Semester.objects.get(active_semester = True)

def students_with_match():
	semester = get_active_semester()
	qs = Student_Match_Profile.objects.filter(semester=semester,
												 match_needed=False)
	return qs

def students_without_match():
	semester = get_active_semester()
	qs = Student_Match_Profile.objects.filter(semester=semester,
												 match_needed=True)
	return qs

def student_users():
	stu_role = Role.objects.get(name="Student")
	qs = stu_role.user_roles.all().order_by('username')
	return qs

def readers_users():
	reader_role = Role.objects.get(name="Reader")
	qs = reader_role.user_roles.all().order_by('username')
	return qs

def open_slot_readers_users():
	semester = get_active_semester()
	qs = Reader_Match_Profile.objects.filter(semester=semester, open_slot_count__gt=0)
	return qs

def convert_session_meeting_choices():
	options = Session_Meeting_Option.objects.filter(active=True)
	count = 0
	list_options = []
	for item in options:
		list_options.append((count, item))
		count = count + 1
	return list_options


def convert_open_slot_readers_users():
	semester = Program_Semester.objects.get(active_semester = True)
	qs = Reader_Match_Profile.objects.filter(semester=semester, open_slot_count__gt=0).order_by('user__username')
	count = 0
	list_options = []

	for item in qs:
		list_options.append((count, item))
		count = count + 1
	return list_options

def convert_students_without_match():
	semester = Program_Semester.objects.get(active_semester = True)
	qs = Student_Match_Profile.objects.filter(semester=semester,
											match_needed=True).order_by('user__username')
	count = 0
	list_options = []

	for item in qs:
		list_options.append((count, item))
		count = count + 1
	return list_options

def create_scheduled_match_view(request, **kwargs):
	context = {}
	context['page_title'] = "Create Scheduled Match"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:
				context['time_options'] = Session_Time_Option.objects.filter(active=True)
				context['day_options'] = Session_Day_Option.objects.filter(active=True)
				context['meeting_options'] = convert_session_meeting_choices()
				context['reading_session_options'] = Reading_Session_Day_Time.objects.filter(active=True)
				all_students = student_users()
				context['all_students'] = all_students
				context['total_students'] = all_students.count()

				matched_students = students_with_match()
				context['matched_students'] = matched_students
				context['has_match_count'] = matched_students.count()

				unmatched_students = students_without_match()
				context['unmatched_students'] = convert_students_without_match()
				context['needs_match_count'] = unmatched_students.count()


				all_readers = readers_users()
				context['all_readers'] = all_readers
				context['total_readers'] = all_readers.count()

				readers_with_open_slots = open_slot_readers_users()
				context['readers_with_open_slots'] = convert_open_slot_readers_users()
				context['open_readers_count'] = readers_with_open_slots.count()

				context = additional_context_all(context)
				match_type=Match_Type.objects.get(name="Scheduled")

				if request.method == "POST":
					form = Create_Scheduled_Match_Form(request.POST, label_suffix='')
					if form.is_valid():
						obj = form.save()
						# form.save_m2m()						
						note = Match_Note.objects.create(match_type=match_type,
														name="Scheduled Match Created",
														created_user=request.user)
						obj.notes.add(note)
						attendance_note = Match_Note.objects.create(match_type=match_type,
														name="Scheduled Match Attendance Records Created",
														created_user=request.user)						
						obj.notes.add(attendance_note)
						obj.post_create_match()
						for session in obj.sessions_scheduled.all():
							match_session_status, created = Match_Session_Status.objects.get_or_create(
															match_type = match_type,
															sch_match = obj,
															session=session,
															)
						post_create_match_student_for_meeting(obj)
						post_create_match_reader_for_meeting(obj)
						post_create_match_for_meeting(obj)

						
						return redirect('site_admin:view_scheduled', match_type="Active")
					else:
						print("errors", form.errors)
						
				else:
					form = Create_Scheduled_Match_Form(label_suffix='',
						initial={
								'semester': context['active_semester'],
								'active': True,	
								'match_type': match_type,									
								})

				context['form'] = form

				return render(request, "matches/create_scheduled_match.html", context)

				
			return redirect('access_denied')

		else:
			return redirect('login')



def additional_context_all(context):
	active_semester = get_active_semester()
	context['active_semester'] = active_semester

	return context

def get_updating_status():
	updating_now = Program_Status.objects.filter(updating=True)
	if updating_now.count() == 0:
		return False
	else:
		return True

def get_matches_queryset(query=None):
	queryset = []
	queries = query.split(" ")

	for q in queries:
		matches = Scheduled_Match.objects.filter(
			Q(student__first_name__icontains=q)|
			Q(student__last_name__icontains=q)|
			Q(reader__first_name__icontains=q)|
			Q(reader__last_name__icontains=q)
			).order_by('date_created')

		for match in matches:
			queryset.append(match)

	return list(set(queryset))

def get_temp_matches_queryset(query=None):
	queryset = []
	queries = query.split(" ")

	for q in queries:
		matches = Temporary_Match.objects.filter(
			Q(student__first_name__icontains=q)|
			Q(student__last_name__icontains=q)|
			Q(reader__first_name__icontains=q)|
			Q(reader__last_name__icontains=q)
			).order_by('date_created')

		for match in matches:
			queryset.append(match)

	return list(set(queryset))

def all_scheduled_matches():
	qs = Scheduled_Match.objects.all().order_by('date_created')
	return qs

def active_scheduled_matches():
	qs = Scheduled_Match.objects.filter(active=True).order_by('date_created')
	return qs

def inactive_scheduled_matches():
	qs = Scheduled_Match.objects.filter(active=False).order_by('date_created')
	return qs

def all_temporary_matches():
	qs = Temporary_Match.objects.all().order_by('date_created')
	return qs

def active_temporary_matches():
	qs = Temporary_Match.objects.filter(active=True).order_by('date_created')
	return qs

def inactive_temporary_matches():
	qs = Temporary_Match.objects.filter(active=False).order_by('date_created')
	return qs

def display_temporary_matches_view(request, match_type, **kwargs):
	context = {}
	context['page_title'] = "Temporary Matches"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:							
				context = additional_context_all(context)				
				if request.GET:
					print("Get")
					query = request.GET.get('q', '')
					if query !='':
						context['matches'] = get_temp_matches_queryset(query)
						context['count'] = len(context['matches'])
						context['match_type'] = "Matching"
					else:
						context['matches'] = all_temporary_matches()
						context['count'] = all_temporary_matches().count()
						context['match_type'] = "All"


				else:					
					if match_type == "All":
						context['matches'] = all_temporary_matches()
						context['count'] = all_temporary_matches().count()
						context['match_type'] = "All"
					elif match_type == "Active":
						context['matches'] = active_temporary_matches()
						context['count'] = active_temporary_matches().count()
						context['match_type'] = "Active"

					elif match_type == "Inactive":
						context['matches'] = inactive_temporary_matches()
						context['count'] = inactive_temporary_matches().count()
						context['match_type'] = "Inactive"
					

				context['total_matches'] = all_temporary_matches().count()
				context['active_count'] = active_temporary_matches().count()
				context['inactive_count'] = inactive_temporary_matches().count()		
				
				return render(request, "matches/view_temporary_matches.html", context)				
			else:
				return redirect('access_denied')

		else:
			return redirect('login')

def display_scheduled_matches_view(request, match_type, **kwargs):
	context = {}
	context['page_title'] = "Scheduled Matches"
	updating_now = get_updating_status()
	user = request.user
	if updating_now:
		return redirect('update_in_progress')
	else:
		if user.is_authenticated:
			context['logged_in_user'] = user
			if user.access_site_admin:							
				context = additional_context_all(context)				
				if request.GET:
					print("Get")
					query = request.GET.get('q', '')
					if query !='':
						context['matches'] = get_matches_queryset(query)
						context['count'] = len(context['matches'])
						context['match_type'] = "Matching"
					else:
						context['matches'] = active_scheduled_matches()
						context['count'] = active_scheduled_matches().count()
						context['match_type'] = "Active"


				else:					
					if match_type == "Active":
						context['matches'] = active_scheduled_matches()
						context['count'] = active_scheduled_matches().count()
						context['match_type'] = "Active"
					elif match_type == "Inactive":
						context['matches'] = inactive_scheduled_matches()
						context['count'] = inactive_scheduled_matches().count()
						context['match_type'] = "Inactive"

					elif match_type == "All":
						context['matches'] = all_scheduled_matches()
						context['count'] = all_scheduled_matches().count()
						context['match_type'] = "All"
					

				context['total_matches'] = all_scheduled_matches().count()
				context['active_count'] = active_scheduled_matches().count()
				context['inactive_count'] = inactive_scheduled_matches().count()		
				
				return render(request, "matches/view_scheduled_matches.html", context)				
			else:
				return redirect('access_denied')

		else:
			return redirect('login')

