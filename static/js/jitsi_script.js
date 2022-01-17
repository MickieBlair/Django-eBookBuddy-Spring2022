const username = JSON.parse(document.getElementById('username').textContent);
console.log("username", username)

const token = JSON.parse(document.getElementById('token').textContent);
console.log("Token", token)

const room_role = JSON.parse(document.getElementById('room_role').textContent);
console.log("Room Role", room_role)

const room_name = JSON.parse(document.getElementById('room_name').textContent);
console.log("room_name", room_name)

const domain = "sessions.goebookbuddy.org";
console.log("Domain", domain)

console.log("Room View", room_view)

const meeting_div = document.getElementById('meeting');
const meeting_spinner = document.getElementById('meeting_spinner');

// Select the node that will be observed for mutations
const targetNode = document.getElementById('meeting');

// Options for the observer (which mutations to observe)
const config = { attributes: true, childList: true, subtree: true };

// Callback function to execute when mutations are observed
const callback = function(mutationsList, observer) {
    // Use traditional 'for loops' for IE 11
    for(const mutation of mutationsList) {
        if (mutation.type === 'childList') {
            // console.error("mutation addedNodes", mutation.addedNodes, typeof(mutation.addedNodes))
            // console.error("mutation addedNodes NodeList", mutation.addedNodes[0].id)
            if(mutation.addedNodes[0].id ==="jitsiConferenceFrame0"){
              meeting_spinner.classList.add('d-none');
              observer.disconnect();
            }
            // console.error("mutation.type", mutation.type)
            // console.error('A child node has been added or removed.', mutation.type);
        }
        else if (mutation.type === 'attributes') {
            // console.error('The ' + mutation.attributeName + ' attribute was modified.');/
        }
    }
};

// Create an observer instance linked to the callback function
const observer = new MutationObserver(callback);

// Start observing the target node for configured mutations
observer.observe(targetNode, config);

// // Later, you can stop observing
// observer.disconnect();


let buttons = ""
let localRecoding_enabled = false;
let fileRecordingsServiceEnabled = false;
let fileRecordingsEnabled =false;
let startAudioMuted = false;
let startVideoMuted =  false;

// toolbarButtons: [
    //    'camera',
    //    'chat',
    //    'closedcaptions',
    //    'desktop',
    //    'download',
    //    'embedmeeting',
    //    'etherpad',
    //    'feedback',
    //    'filmstrip',
    //    'fullscreen',
    //    'hangup',
    //    'help',
    //    'invite',
    //    'livestreaming',
    //    'microphone',
    //    'mute-everyone',
    //    'mute-video-everyone',
    //    'participants-pane',
    //    'profile',
    //    'raisehand',
    //    'recording',
    //    'security',
    //    'select-background',
    //    'settings',
    //    'shareaudio',
    //    'sharedvideo',
    //    'shortcuts',
    //    'stats',
    //    'tileview',
    //    'toggle-camera',
    //    'videoquality',
    //    '__end'
    // ],

if(room_role == "Owner"){
  localRecoding_enabled = true;
  fileRecordingsServiceEnabled = true;
  fileRecordingsEnabled: true;
  buttons = [
       'camera',
       'chat',
       // 'closedcaptions',
       'desktop',
       // 'download',
       // 'embedmeeting',
       // 'etherpad',
       // 'feedback',
       'filmstrip',
       // 'fullscreen',
       // 'hangup',
       // 'help',
       // 'invite',
       // 'livestreaming',
       'microphone',
       'mute-everyone',
       'mute-video-everyone',
       'participants-pane',
       // 'profile',
       'raisehand',
       // 'recording',
       // 'security',
       // 'select-background',
       'settings',
       // 'shareaudio',
       // 'sharedvideo',
       'shortcuts',
       // 'stats',
       'tileview',
       'toggle-camera',
       // 'videoquality',
       // '__end',
       // 'localrecording',
    ];
} else{
  buttons =[
    'camera',
    'microphone',
    'chat',
    'desktop',
    'raisehand',
    'tileview', 
    'toggle-camera',
    'settings',

    // 'filmstrip', 
       
    ];
}

if(username == "Buddy_Admin" || username == "Mickie" || username == "Adolfo"){
  console.log("\n\nStart Muted/Video Off");
  startAudioMuted = true;
  startVideoMuted =  true;
} else{
  ("\n\nStart On/On");
  startAudioMuted = false;
  startVideoMuted =  false;
}

var options = {
  roomName: room_name,
  jwt: token,
  width: "100%",
  height: "100%",
  parentNode: meeting_div,
  configOverwrite: {
        toolbarButtons: buttons,
        localRecording: {
             enabled: localRecoding_enabled,
         },
         // fileRecordingsServiceEnabled: fileRecordingsServiceEnabled,
         // fileRecordingsEnabled: fileRecordingsEnabled,
         startWithAudioMuted: startAudioMuted,
         startWithVideoMuted: startVideoMuted,
  },
  interfaceConfigOverwrite: {
    filmStripOnly: true
  }
}

//console.log("USER ROLE", user_role, options)
console.error("Options", options)
var api = new JitsiMeetExternalAPI(domain, options);
// api.addEventListener("videoConferenceJoined", function(e){
//   observer.disconnect();
//   });

