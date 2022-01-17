$(function(){$('input').blur();});function allow_scroll(){let status_modal=document.getElementById('statusModal');status_modal.style.left="0px";status_modal.style.right="0px";document.body.style.overflow=null;}
function save_vol_changes(){let submit_changes=document.getElementById('submit_vol_changes');submit_changes.click();}
function save_vol_note(){let save_note=document.getElementById('add_vol_note');save_note.click();}
$('#id_video_uploaded').click(function(e){e.preventDefault();});;