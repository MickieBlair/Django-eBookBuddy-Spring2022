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
var window_width=$(window).width();console.log('window_width',window_width);var container_width=container.width();console.log('container_width',container_width);var sidebar_width=staff_sidebar.width();console.log('sidebar_width',sidebar_width);var staff_left_panel_width=staff_left_panel.width();console.log('staff_left_panel_width',staff_left_panel_width);var staff_right_panel_width=staff_right_panel.width();console.log('staff_right_panel_width',staff_right_panel_width);if(container){handle.on('mousedown touchstart',function(e){isResizing=true;lastDownX=e.clientX;console.log('e',e);console.log('Mouse down isResizing',isResizing);console.log('mouse down lastDownX',lastDownX);});$(document).on('mousemove touchmove',function(e){console.log("Doing something")
if(!isResizing)
return;lastDownX=e.clientX;var room_header_inline_grid_height=room_header_inline_grid.height();var unmatched_row_height=unmatched_row.height();let header_height=room_header_inline_grid_height+unmatched_row_height+5
let height_str="calc(100% - "+header_height+"px)"
monitoring_content.css('height',height_str);var container_width=container.width();var sidebar_width=staff_sidebar.width();var left_width=lastDownX
adjusted_left_panel_width=left_width;var right_width=container_width-lastDownX
adjusted_right_panel_width=right_width;if(right_width<=225){let set_panel_width=container_width-225;let width_str=set_panel_width+'px'
staff_left_panel.css('width',width_str);staff_right_panel.css('width','225px');}else{staff_left_panel.css('width',left_width);staff_right_panel.css('width',right_width);}}).on('mouseup',function(e){isResizing=false;});};});;