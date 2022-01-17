console.log("Loading Site Scripts")
const ws_scheme=window.location.protocol=="https:"?"wss":"ws";console.log(ws_scheme)
const clock_div=document.getElementById('server_clock')
if(clock_div){const entry_start=JSON.parse(document.getElementById('entry_start').textContent);const entry_end=JSON.parse(document.getElementById('entry_end').textContent);console.log("entry_start",entry_start)
console.log("entry_end",entry_end)
const entry_start_hour=entry_start.split(":")[0]
const entry_start_min=entry_start.split(":")[1]
const entry_start_sec=entry_start.split(":")[2]
const entry_end_hour=entry_end.split(":")[0]
const entry_end_min=entry_end.split(":")[1]
const entry_end_sec=entry_end.split(":")[2]
setInterval(showTime,1000);function showTime(){var dt=new Date();dt.setTime(dt.getTime()+dt.getTimezoneOffset()*60*1000);var offset=JSON.parse(document.getElementById('offset').textContent);var estDate=new Date(dt.getTime()+offset*60*1000);let time=estDate;let hour=time.getHours();let base_hour=time.getHours();let min=time.getMinutes();let base_min=time.getMinutes();let sec=time.getSeconds();let base_sec=time.getSeconds();am_pm="AM";if(hour>12){hour-=12;am_pm="PM";}
else if(hour==0){hr=12;am_pm="AM";}
else if(hour==12){am_pm="PM";}
hour=hour<10?"0"+hour:hour;min=min<10?"0"+min:min;sec=sec<10?"0"+sec:sec;let currentTime=hour+":"
+min+":"+sec+" "+am_pm;document.getElementById("server_clock").innerHTML=currentTime;if(base_hour==entry_start_hour){if(base_min==entry_start_min){if(base_sec==entry_start_sec){if(member_role=="Student"){landing_link.click()}else if(member_role=="Volunteer"){landing_link.click()}}}}
if(base_hour==entry_end_hour){if(base_min==entry_end_min){if(base_sec==entry_end_sec){if(member_role=="Student"){landing_link.click()}else if(member_role=="Volunteer"){landing_link.click()}}}}}
showTime();};