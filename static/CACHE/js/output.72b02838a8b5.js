console.log("Loading Site Scripts")
const ws_scheme=window.location.protocol=="https:"?"wss":"ws";console.log(ws_scheme)
const clock_div=document.getElementById('server_clock')
if(clock_div){setInterval(showTime,1000);function showTime(){var dt=new Date();dt.setTime(dt.getTime()+dt.getTimezoneOffset()*60*1000);var offset=JSON.parse(document.getElementById('offset').textContent);var estDate=new Date(dt.getTime()+offset*60*1000);let time=estDate;let hour=time.getHours();let base_hour=time.getHours();let min=time.getMinutes();let base_min=time.getMinutes();let sec=time.getSeconds();let base_sec=time.getSeconds();am_pm="AM";if(hour>12){hour-=12;am_pm="PM";}
else if(hour==0){hr=12;am_pm="AM";}
else if(hour==12){am_pm="PM";}
hour=hour<10?"0"+hour:hour;min=min<10?"0"+min:min;sec=sec<10?"0"+sec:sec;let currentTime=hour+":"
+min+":"+sec+" "+am_pm;document.getElementById("server_clock").innerHTML=currentTime;if(base_hour==entry_start_hour){if(base_min==entry_start_min){if(base_sec==entry_start_sec){}}}
if(base_hour==entry_end_hour){if(base_min==entry_end_min){if(base_sec==entry_end_sec){}}}}
showTime();};console.log("Loading Parent Registration Scripts")
const registration_lang_options=document.getElementsByName("registration_language");const parent_can_help_options=document.getElementsByName("parent_can_help");const fieldWrapper_help_name=document.getElementById('fieldWrapper_help_name');const fieldWrapper_help_phone=document.getElementById('fieldWrapper_help_phone');const fieldWrapper_help_relationship=document.getElementById('fieldWrapper_help_relationship');const help_name_input=document.getElementById('id_help_name');const help_phone_input=document.getElementById('id_help_phone');const help_relationship_input=document.getElementById('id_help_relationship');let lang_form;let span_select_one='(Seleccione uno)';let eng_select_one='(Select One)';let span_yes='  Sí';let other_specify_span='  Otro (por favor especifique)';window.addEventListener('load',(event)=>{let parent_form=document.getElementById('parent_form');if(parent_form){let choosen_registration_language=document.querySelector('input[name="registration_language"]:checked');if(choosen_registration_language){lang_form=choosen_registration_language.parentElement.textContent.trim();}
let country_select=document.getElementById('id_country')
let state_select=document.getElementById('id_state')
let all_registration_radios=document.querySelectorAll('.registration_radio');if(lang_form=="English"){country_select.options[0].text=eng_select_one;state_select.options[0].text=eng_select_one;}else{if(country_select){country_select.options[0].text=span_select_one;}
if(state_select){state_select.options[0].text=span_select_one;}
for(let item of all_registration_radios){let the_label=item.parentElement;let the_child_nodes=the_label.childNodes;for(let item of the_child_nodes){if(item.nodeName==='#text'){if(item.textContent.trim()=='Yes'){item.textContent=span_yes;}
else if(item.textContent.trim()=='Other (Please Specify)'){console.log(item)
item.textContent=other_specify_span;}}}}}
let choosen_parent_can_help=document.querySelector('input[name="parent_can_help"]:checked');if(choosen_parent_can_help){if(choosen_parent_can_help.value=="Yes"){set_help_divs("display_none");}else if(choosen_parent_can_help.value=="No"){set_help_divs("display_all");}}else{set_help_divs("display_none");}}});for(let option of parent_can_help_options){option.addEventListener('change',(event)=>{if(event.target.value=="No"){set_help_divs("display_all");}else if(event.target.value=="Yes"){set_help_divs("display_none");}});}
function set_help_divs(display_divs){if(display_divs=="display_none"){fieldWrapper_help_name.classList.add('d-none');fieldWrapper_help_phone.classList.add('d-none');fieldWrapper_help_relationship.classList.add('d-none');help_name_input.value='';help_phone_input.value='';help_relationship_input.value='';}else{fieldWrapper_help_name.classList.remove('d-none');fieldWrapper_help_phone.classList.remove('d-none');fieldWrapper_help_relationship.classList.remove('d-none');}}
function clear_input_errors(input_name){let error_div=document.getElementById(input_name+"_errors");if(error_div){error_div.innerHTML="";}}
function set_form_language(lang_id){console.log('lang_id',lang_id)
lang_options=document.getElementsByName('language')
for(let item of lang_options){if(item.value==parseInt(lang_id)){item.checked=true;}}
let pre_form=document.getElementById('pre_form')
pre_form.submit()}
function submit_parent_form(){let parent_reg=document.getElementById('parent_form');parent_reg.submit();}
function email_blur(ev,object){if(ev=="blur"){var email=object.value;if(email!=''){check_parent_email(email)}}}
function check_parent_email(email){payload={'email':email,'type_reg':"Parent",'reg_lang':"en"}
$.ajax({type:'GET',url:"/registration/registration_email_check/",data:payload,success:function(response){console.log("Success")
console.log(response)
if(!response['valid']){email_notifications()}},error:function(response){console.log("Fail")
console.log(response)}});}
function email_notifications(){console.log("Notify Email",)
if(notifyModalButton){const notifyModalButton=document.getElementById('notifyModalButton');notifyModalButton.click();}};