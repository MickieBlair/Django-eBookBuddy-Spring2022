$(function(){$('input').blur();});function allow_scroll(){let status_modal=document.getElementById('statusModal');status_modal.style.left="0px";status_modal.style.right="0px";document.body.style.overflow=null;}
function save_vol_changes(){let submit_changes=document.getElementById('submit_vol_changes');submit_changes.click();}
function save_vol_note(){let save_note=document.getElementById('add_vol_note');save_note.click();}
function save_student_changes(){let submit_changes=document.getElementById('submit_student_changes');submit_changes.click();}
function save_student_note(){let save_note=document.getElementById('add_student_note');save_note.click();}
function scroll_to_div(div_name){let scrolling_div=document.getElementById('scrolling_div');console.log('scrolling_div',scrolling_div)
let elmnt=document.getElementById(div_name);console.log('elmnt',elmnt)
let topPos=elmnt.offsetTop-60;console.log('topPos',topPos)
scrolling_div.scrollTop=topPos;}
const create_volunteer_user_form=document.getElementById('create_volunteer_user_form')
if(create_volunteer_user_form){console.log("Volunteer User Create Form")
let vol_role_options=document.getElementsByName("roles");for(let option of vol_role_options){option.addEventListener('click',(event)=>{let the_option=document.getElementById(event.target.id);let the_value=the_option.value;let the_label=the_option.parentElement.textContent.trim();if(the_label=="Volunteer"){event.preventDefault();}});}}
const create_staff_user_form=document.getElementById('create_staff_user_form')
if(create_staff_user_form){console.log("Staff User Create Form")
let staff_role_options=document.getElementsByName("roles");for(let option of staff_role_options){option.addEventListener('click',(event)=>{let the_option=document.getElementById(event.target.id);let the_value=the_option.value;let the_label=the_option.parentElement.textContent.trim();if(the_label=="Staff"){event.preventDefault();}});}}
$('#id_video_uploaded').click(function(e){e.preventDefault();});const edit_sch_match_form=document.getElementById('edit_sch_match')
if(edit_sch_match_form){const stu_errov_div=document.getElementById("student_errors");const reader_errov_div=document.getElementById("reader_errors");const day_times_errov_div=document.getElementById("day_times_errors");const reader_choices=document.getElementsByName("reader_choice");const student_choices=document.getElementsByName("student_choice");const new_meeting_choices=document.getElementsByName("new_meeting_choice");for(let option of new_meeting_choices){option.addEventListener('change',(event)=>{day_times_errov_div.innerHTML="";});}
for(let option of new_meeting_choices){option.addEventListener('click',(event)=>{let the_option=document.getElementById(event.target.id);let the_value=the_option.value;let coor_option=document.getElementById('id_new_day_times_'+the_value)
coor_option.click()});}}
window.addEventListener('load',(event)=>{if(edit_sch_match_form){const checked_day_times=document.querySelector('input[name="day_times"]:checked');console.log(checked_day_times)
const new_checked_day_times=document.querySelector('input[name="new_day_times"]:checked');if(checked_day_times){let checked_day_times_id=checked_day_times.id;console.log(checked_day_times_id)
let choice_to_check_id=checked_day_times_id.split('_')[3]+'_choice_day_times';console.log(choice_to_check_id)
let choice_to_check=document.getElementById(choice_to_check_id);console.log(choice_to_check)
if(choice_to_check){choice_to_check.checked=true;}}
if(new_checked_day_times){let new_checked_day_times_id=new_checked_day_times.id;let choice_to_check_id=new_checked_day_times_id.split('_')[4]+'_new_choice_day_times';let choice_to_check=document.getElementById(choice_to_check_id);if(choice_to_check){choice_to_check.checked=true;}}}})
const create_sch_match_form=document.getElementById('create_sch_match')
if(create_sch_match_form){const stu_errov_div=document.getElementById("student_errors");const reader_errov_div=document.getElementById("reader_errors");const day_times_errov_div=document.getElementById("day_times_errors");const reader_choices=document.getElementsByName("reader_choice");const student_choices=document.getElementsByName("student_choice");const meeting_choices=document.getElementsByName("meeting_choice");for(let option of reader_choices){option.addEventListener('change',(event)=>{reader_errov_div.innerHTML="";});}
for(let option of student_choices){option.addEventListener('change',(event)=>{stu_errov_div.innerHTML="";});}
for(let option of meeting_choices){option.addEventListener('change',(event)=>{day_times_errov_div.innerHTML="";});}
for(let option of reader_choices){option.addEventListener('click',(event)=>{let the_option=document.getElementById(event.target.id);let the_value=the_option.value;let coor_option=document.getElementById('id_reader_'+the_value);coor_option.click();});}
for(let option of student_choices){option.addEventListener('click',(event)=>{let the_option=document.getElementById(event.target.id);let the_value=the_option.value;let coor_option=document.getElementById('id_student_'+the_value);coor_option.click();});}
for(let option of meeting_choices){option.addEventListener('click',(event)=>{let the_option=document.getElementById(event.target.id);let the_value=the_option.value;let coor_option=document.getElementById('id_day_times_'+the_value)
coor_option.click()});}}
window.addEventListener('load',(event)=>{if(create_sch_match_form){const checked_student=document.querySelector('input[name="student"]:checked');const checked_reader=document.querySelector('input[name="reader"]:checked');const checked_day_times=document.querySelector('input[name="day_times"]:checked');if(checked_student){let checked_student_id=checked_student.id;let choice_to_check_id=checked_student_id.split('_')[2]+'_choice_student';let choice_to_check=document.getElementById(choice_to_check_id);choice_to_check.checked=true;}
if(checked_reader){let checked_reader_id=checked_reader.id;let choice_to_check_id=checked_reader_id.split('_')[2]+'_choice_reader';let choice_to_check=document.getElementById(choice_to_check_id);choice_to_check.checked=true;}
if(checked_day_times){let checked_day_times_id=checked_day_times.id;let choice_to_check_id=checked_day_times_id.split('_')[3]+'_choice_day_times';let choice_to_check=document.getElementById(choice_to_check_id);choice_to_check.checked=true;}}});