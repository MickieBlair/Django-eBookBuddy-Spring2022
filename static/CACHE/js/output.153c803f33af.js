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
let vol_role_options=document.getElementsByName("roles");for(let option of vol_role_options){option.addEventListener('change',(event)=>{let the_option=document.getElementById(event.target.id);let the_value=the_option.value;let the_label=the_option.parentElement.textContent.trim();console.log("the_option the_value the_label",the_option,the_value,the_label)});}}
$('#id_video_uploaded').click(function(e){e.preventDefault();});;