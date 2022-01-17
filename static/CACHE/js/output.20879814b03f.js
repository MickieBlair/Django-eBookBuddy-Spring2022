console.log("Loading Site Scripts")
const ws_scheme=window.location.protocol=="https:"?"wss":"ws";console.log(ws_scheme)
const clock_div=document.getElementById('server_clock')
if(clock_div){setInterval(showTime,1000);function showTime(){var dt=new Date();dt.setTime(dt.getTime()+dt.getTimezoneOffset()*60*1000);var offset=JSON.parse(document.getElementById('offset').textContent);var estDate=new Date(dt.getTime()+offset*60*1000);let time=estDate;let hour=time.getHours();let base_hour=time.getHours();let min=time.getMinutes();let base_min=time.getMinutes();let sec=time.getSeconds();let base_sec=time.getSeconds();am_pm="AM";if(hour>12){hour-=12;am_pm="PM";}
else if(hour==0){hr=12;am_pm="AM";}
else if(hour==12){am_pm="PM";}
hour=hour<10?"0"+hour:hour;min=min<10?"0"+min:min;sec=sec<10?"0"+sec:sec;let currentTime=hour+":"
+min+":"+sec+" "+am_pm;document.getElementById("server_clock").innerHTML=currentTime;if(base_hour==entry_start_hour){if(base_min==entry_start_min){if(base_sec==entry_start_sec){}}}
if(base_hour==entry_end_hour){if(base_min==entry_end_min){if(base_sec==entry_end_sec){}}}}
showTime();};console.log("Loading Session Scripts");const staff_outer_div_presence=document.getElementById('staff_outer_div');let last_width_monitoring;let last_width_video;const todays_session_button=document.getElementById('todays_session_btn');const todays_sessions_div=document.getElementById('todays_session_btn_show')
const all_monitoring_divs=document.getElementsByClassName('monitoring_type');const all_side_bar_buttons=document.getElementsByName('btn_sidebar');console.log('all_side_bar_buttons',all_side_bar_buttons)
function determine_div_to_display(target){console.log("div to display",target)}
if(staff_outer_div_presence){window.addEventListener('load',(event)=>{for(let item of all_monitoring_divs){if(item==todays_sessions_div){item.classList.remove('d-none')}else{item.classList.add('d-none')}}
for(let item of all_side_bar_buttons){console.log("item",item)
item.addEventListener('click',(event)=>{console.log("event.target",event.target)
determine_div_to_display(event.target)},true);}});}
function close_monitoring(element){console.log("close_monitoring",element)
let monitoring_pane_div=document.getElementById('monitoring_pane');monitoring_pane_div.classList.add('d-none');let staff_drag_bar=document.getElementById('staff_drag');staff_drag_bar.classList.add('d-none');let staff_sidebar_div=document.getElementById('staff_sidebar');let staff_sidebar_div_width=staff_sidebar_div.offsetWidth;let staff_outer_div_presence_width=staff_outer_div_presence.offsetWidth;let new_width_of_meeting=staff_outer_div_presence_width-staff_sidebar_div_width
let video_div=document.getElementById('staff_meeting_div');video_div.style.width=new_width_of_meeting+"px";}
function open_monitoring(){console.log("open_monitoring")
let monitoring_pane_div=document.getElementById('monitoring_pane');let new_width_of_monitoring=last_width_monitoring+'px';monitoring_pane_div.style.width=new_width_of_monitoring;monitoring_pane_div.classList.remove('d-none');let staff_drag_bar=document.getElementById('staff_drag');staff_drag_bar.classList.remove('d-none');let staff_sidebar_div=document.getElementById('staff_sidebar');let new_width_of_meeting=last_width_video+'px';let video_div=document.getElementById('staff_meeting_div');video_div.style.width=new_width_of_meeting;}
const help_request_modal=document.getElementById('helpModal');const help_request_input=document.getElementById('help_message_content');if(help_request_modal){help_request_modal.addEventListener('shown.bs.modal',function(){help_request_input.focus();})}
const open_full_screen_btn=document.getElementById('open_full_screen');const close_full_screen_btn=document.getElementById('close_full_screen');var elem=document.documentElement;function open_full_screen(){if(elem.requestFullscreen){elem.requestFullscreen();}else if(elem.webkitRequestFullscreen){elem.webkitRequestFullscreen();}else if(elem.msRequestFullscreen){elem.msRequestFullscreen();}
open_full_screen_btn.style.display="none";close_full_screen_btn.style.display="inline-grid";}
function close_full_screen(){if(document.exitFullscreen){document.exitFullscreen();}else if(document.webkitExitFullscreen){document.webkitExitFullscreen();}else if(document.msExitFullscreen){document.msExitFullscreen();}
open_full_screen_btn.style.display="inline-grid";close_full_screen_btn.style.display="none";}
document.addEventListener('fullscreenchange',exitHandler);document.addEventListener('webkitfullscreenchange',exitHandler);document.addEventListener('mozfullscreenchange',exitHandler);document.addEventListener('MSFullscreenChange',exitHandler);function exitHandler(){if(!document.fullscreenElement&&!document.webkitIsFullScreen&&!document.mozFullScreen&&!document.msFullscreenElement){open_full_screen_btn.style.display="inline-grid";close_full_screen_btn.style.display="none";}}
if(staff_outer_div_presence){let isResizing=false;let lastDownX=0;$(function(){let handle=$('#staff_drag')
let container=$('#staff_outer_div')
let staff_sidebar=$('#staff_sidebar')
let staff_left_panel=$('#monitoring_pane')
let staff_right_panel=$('#staff_meeting_div')
var window_width=$(window).width();var handle_width=handle.width();var container_width=container.width()-handle_width;var sidebar_width=staff_sidebar.width();let half_width=(container_width-sidebar_width)/2;last_width_monitoring=half_width
last_width_video=half_width
staff_left_panel.css('width',half_width+"px");staff_right_panel.css('width',half_width+"px");var staff_left_panel_width=staff_left_panel.width();var staff_right_panel_width=staff_right_panel.width();if(container){handle.on('mousedown touchstart',function(e){isResizing=true;lastDownX=e.clientX;if(e.type=='touchstart'){isResizing=true;lastDownX=e.originalEvent.touches[0].pageX;}else if(e.type=='mousedown'){isResizing=true;lastDownX=e.clientX;}});$(document).on('mousemove touchmove',function(e){if(!isResizing)
return;if(e.type=='touchmove'){lastDownX=e.changedTouches[0].clientX;}else if(e.type=='mousemove'){lastDownX=e.clientX;}
var container_width=container.width();var sidebar_width=staff_sidebar.width();let width_of_left_now=lastDownX-sidebar_width
let width_of_right_now=container_width-width_of_left_now
let total_width=width_of_right_now+width_of_left_now+sidebar_width
last_width_monitoring=width_of_left_now
last_width_video=width_of_right_now
let str_width_left=width_of_left_now+"px"
let str_width_right=width_of_right_now+"px"
if(width_of_right_now>245){if(width_of_left_now>0){staff_sidebar.css('width',"75px");staff_left_panel.css('width',str_width_left);staff_right_panel.css('width',str_width_right);}else{isResizing=false;}}else{isResizing=false;}}).on('mouseup touchend',function(e){isResizing=false;});};});};;