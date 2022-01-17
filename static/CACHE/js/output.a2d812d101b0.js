const username=JSON.parse(document.getElementById('username').textContent);const token=JSON.parse(document.getElementById('token').textContent);const room_role=JSON.parse(document.getElementById('room_role').textContent);console.log("Role",room_role)
const room_name=JSON.parse(document.getElementById('room_name').textContent);const domain="sessions.goebookbuddy.org";const meeting_div=document.getElementById('meeting');const meeting_spinner=document.getElementById('meeting_spinner');const targetNode=document.getElementById('meeting');const config={attributes:true,childList:true,subtree:true};const callback=function(mutationsList,observer){for(const mutation of mutationsList){if(mutation.type==='childList'){if(mutation.addedNodes[0].id==="jitsiConferenceFrame0"){meeting_spinner.classList.add('d-none');observer.disconnect();}}
else if(mutation.type==='attributes'){}}};const observer=new MutationObserver(callback);observer.observe(targetNode,config);let buttons=""
let localRecoding_enabled=false;let fileRecordingsServiceEnabled=false;let fileRecordingsEnabled=false;let startAudioMuted=false;let startVideoMuted=false;if(room_role=="Owner"){localRecoding_enabled=true;fileRecordingsServiceEnabled=true;fileRecordingsEnabled:true;buttons=['camera','chat','desktop','download','etherpad','feedback','filmstrip','help','livestreaming','microphone','mute-everyone','mute-video-everyone','participants-pane','profile','raisehand','recording','settings','shareaudio','sharedvideo','shortcuts','stats','tileview','toggle-camera','videoquality','__end'];}else{buttons=['camera','microphone','chat','desktop','raisehand','tileview','toggle-camera','settings',];}
if(username=="Buddy_Admin"||username=="Mickie"||username=="Adolfo"){console.log("\n\nStart Muted/Video Off");startAudioMuted=true;startVideoMuted=true;}else{("\n\nStart On/On");startAudioMuted=false;startVideoMuted=false;}
var options={roomName:room_name,jwt:token,width:"100%",height:"100%",parentNode:meeting_div,configOverwrite:{toolbarButtons:buttons,localRecording:{enabled:localRecoding_enabled,},fileRecordingsServiceEnabled:fileRecordingsServiceEnabled,fileRecordingsEnabled:fileRecordingsEnabled,startWithAudioMuted:startAudioMuted,startWithVideoMuted:startVideoMuted,},interfaceConfigOverwrite:{filmStripOnly:true}}
console.error("Options",options)
var api=new JitsiMeetExternalAPI(domain,options);;