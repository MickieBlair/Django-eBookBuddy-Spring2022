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
var element=document.getElementById('monitoring_pane');var resizer=document.createElement('staff_drag');resizer.addEventListener('mousedown',initResize,false);function initResize(e){console.log("INIT Resize",e)
window.addEventListener('mousemove',Resize,false);window.addEventListener('mouseup',stopResize,false);}
function Resize(e){element.style.width=(e.clientX-element.offsetLeft)+'px';element.style.height=(e.clientY-element.offsetTop)+'px';}
function stopResize(e){window.removeEventListener('mousemove',Resize,false);window.removeEventListener('mouseup',stopResize,false);}