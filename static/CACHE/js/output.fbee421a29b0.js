console.log("Loading Session Scripts");const help_request_modal=document.getElementById('helpModal')
const help_request_input=document.getElementById('help_message_content')
if(help_request_modal){help_request_modal.addEventListener('shown.bs.modal',function(){help_request_input.focus()})}
const open_full_screen_btn=document.getElementById('open_full_screen');const close_full_screen_btn=document.getElementById('close_full_screen');var elem=document.documentElement;function open_full_screen(){if(elem.requestFullscreen){elem.requestFullscreen();}else if(elem.webkitRequestFullscreen){elem.webkitRequestFullscreen();}else if(elem.msRequestFullscreen){elem.msRequestFullscreen();}
open_full_screen_btn.style.display="none";close_full_screen_btn.style.display="inline-grid";}
function close_full_screen(){if(document.exitFullscreen){document.exitFullscreen();}else if(document.webkitExitFullscreen){document.webkitExitFullscreen();}else if(document.msExitFullscreen){document.msExitFullscreen();}
open_full_screen_btn.style.display="inline-grid";close_full_screen_btn.style.display="none";}
document.addEventListener('fullscreenchange',exitHandler);document.addEventListener('webkitfullscreenchange',exitHandler);document.addEventListener('mozfullscreenchange',exitHandler);document.addEventListener('MSFullscreenChange',exitHandler);function exitHandler(){if(!document.fullscreenElement&&!document.webkitIsFullScreen&&!document.mozFullScreen&&!document.msFullscreenElement){open_full_screen_btn.style.display="inline-grid";close_full_screen_btn.style.display="none";}};