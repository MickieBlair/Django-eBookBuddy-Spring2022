console.log("Loading Site Scripts")
const ws_scheme=window.location.protocol=="https:"?"wss":"ws";console.log(ws_scheme)
const clock_div=document.getElementById('server_clock')
if(clock_div){setInterval(showTime,1000);function showTime(){var dt=new Date();dt.setTime(dt.getTime()+dt.getTimezoneOffset()*60*1000);var offset=JSON.parse(document.getElementById('offset').textContent);var estDate=new Date(dt.getTime()+offset*60*1000);let time=estDate;let hour=time.getHours();let base_hour=time.getHours();let min=time.getMinutes();let base_min=time.getMinutes();let sec=time.getSeconds();let base_sec=time.getSeconds();am_pm="AM";if(hour>12){hour-=12;am_pm="PM";}
else if(hour==0){hr=12;am_pm="AM";}
else if(hour==12){am_pm="PM";}
hour=hour<10?"0"+hour:hour;min=min<10?"0"+min:min;sec=sec<10?"0"+sec:sec;let currentTime=hour+":"
+min+":"+sec+" "+am_pm;document.getElementById("server_clock").innerHTML=currentTime;if(base_hour==entry_start_hour){if(base_min==entry_start_min){if(base_sec==entry_start_sec){}}}
if(base_hour==entry_end_hour){if(base_min==entry_end_min){if(base_sec==entry_end_sec){}}}}
showTime();};console.log("Loading Session Scripts");const help_request_modal=document.getElementById('helpModal');const help_request_input=document.getElementById('help_message_content');if(help_request_modal){help_request_modal.addEventListener('shown.bs.modal',function(){help_request_input.focus();})}
const open_full_screen_btn=document.getElementById('open_full_screen');const close_full_screen_btn=document.getElementById('close_full_screen');var elem=document.documentElement;function open_full_screen(){if(elem.requestFullscreen){elem.requestFullscreen();}else if(elem.webkitRequestFullscreen){elem.webkitRequestFullscreen();}else if(elem.msRequestFullscreen){elem.msRequestFullscreen();}
open_full_screen_btn.style.display="none";close_full_screen_btn.style.display="inline-grid";}
function close_full_screen(){if(document.exitFullscreen){document.exitFullscreen();}else if(document.webkitExitFullscreen){document.webkitExitFullscreen();}else if(document.msExitFullscreen){document.msExitFullscreen();}
open_full_screen_btn.style.display="inline-grid";close_full_screen_btn.style.display="none";}
document.addEventListener('fullscreenchange',exitHandler);document.addEventListener('webkitfullscreenchange',exitHandler);document.addEventListener('mozfullscreenchange',exitHandler);document.addEventListener('MSFullscreenChange',exitHandler);function exitHandler(){if(!document.fullscreenElement&&!document.webkitIsFullScreen&&!document.mozFullScreen&&!document.msFullscreenElement){open_full_screen_btn.style.display="inline-grid";close_full_screen_btn.style.display="none";}}
let isResizing=false;let lastDownX=0;$(function(){let handle=$('#staff_drag')
let container=$('#staff_outer_div')
let staff_sidebar=$('#staff_sidebar')
let staff_left_panel=$('#monitoring_pane')
let staff_right_panel=$('#staff_meeting_div')
var window_width=$(window).width();console.log('window_width',window_width);var handle_width=handle.width();console.log('handle_width',handle_width);var container_width=container.width()-handle_width;console.log('container_width',container_width);var sidebar_width=staff_sidebar.width();console.log('sidebar_width',sidebar_width);let half_width=(container_width-sidebar_width)/2;staff_left_panel.css('width',half_width+"px");staff_right_panel.css('width',half_width+"px");var staff_left_panel_width=staff_left_panel.width();console.log('staff_left_panel_width',staff_left_panel_width);var staff_right_panel_width=staff_right_panel.width();console.log('staff_right_panel_width',staff_right_panel_width);if(container){handle.on('mousedown touchstart',function(e){isResizing=true;lastDownX=e.clientX;if(e.type=='touchstart'){isResizing=true;lastDownX=e.originalEvent.touches[0].pageX;}else if(e.type=='mousedown'){isResizing=true;lastDownX=e.clientX;}});$(document).on('mousemove touchmove',function(e){if(!isResizing)
return;if(e.type=='touchmove'){lastDownX=e.changedTouches[0].clientX;}else if(e.type=='mousemove'){lastDownX=e.clientX;}
var container_width=container.width();var sidebar_width=staff_sidebar.width();let width_of_left_now=lastDownX-sidebar_width
let width_of_right_now=container_width-width_of_left_now
let total_width=width_of_right_now+width_of_left_now+sidebar_width
let str_width_left=width_of_left_now+"px"
let str_width_right=width_of_right_now+"px"
if(width_of_right_now>245){if(width_of_left_now>0){staff_sidebar.css('width',"75px");staff_left_panel.css('width',str_width_left);staff_right_panel.css('width',str_width_right);}else{isResizing=false;}}else{isResizing=false;}}).on('mouseup touchend',function(e){isResizing=false;console.log('End isResizing ',isResizing);});};});;