console.log("Loading Session Scripts");

const room_view = JSON.parse(document.getElementById('room_view').textContent);
// console.log("room_view", room_view);

const staff_outer_div_presence = document.getElementById('outer_div_staff');
const jitsi_div = document.getElementById('jitsi_meeting_div');
let last_width_monitoring;
let last_width_video;
const todays_session_button = document.getElementById('todays_session_btn');
const todays_sessions_div = document.getElementById('todays_session_btn_show')
const all_monitoring_divs = document.getElementsByClassName('monitoring_type');
const all_side_bar_buttons = document.getElementsByName('btn_sidebar');
const all_sessions_div = document.getElementById('all_sessions_div');
const matches_in_session_div = document.getElementById('matches_in_session');
const all_type_room_divs = document.getElementsByClassName('room_call_divs');
const show_ws_rooms = document.getElementById('show_ws_rooms_btn');
// console.log('all_side_bar_buttons',all_side_bar_buttons)

function display_room_divs(element_id){
  // let outer_session_div = document.getElementById('outer_session_div');
  // outer_session_div.style.display = 'block';
  // console.log("div to display", element_id)
  let div_to_display_id = "show_" + element_id
  // console.log("div_to_display_id", div_to_display_id)
  for(let item of all_type_room_divs){
    // console.log("item", item)
      if(item.id == div_to_display_id){
        item.classList.remove('d-none')
      } else{
        item.classList.add('d-none')
      }
    }

  if(div_to_display_id == "show_this_room_btn"){
      get_room_participants();
    }
  else if (div_to_display_id == "show_all_rooms_btn"){
    get_jitsi_rooms();
  } else if (div_to_display_id == "show_one_by_one_btn"){
    all_rooms_one_by_one()
  }

}

function all_rooms_one_by_one(){
  // console.log("ONE BY ONE");

    $.ajax({
      type: 'GET',
      url: "/testing/check_all_rooms/",
      success: function (response) {
        // console.log("Success")
        // console.log(response)
        for(let item of response['updated_info']){
          // console.log(item)
          let j_part_count = document.getElementById('one_by_jitsi_room_count_' + item.room_id)
          if(j_part_count){
            j_part_count.innerHTML = item.count;
          }          

          let ws_part_count = document.getElementById('one_by_ws_room_count_' + item.room_id)
          if(ws_part_count){
            ws_part_count.innerHTML = item.ws_count;
          }
          
          let jitsi_parts = document.getElementById('one_by_room_j_participants_' + item.room_id)
          if(jitsi_parts){
            jitsi_parts.innerHTML = "";
            
            for(let inner_item of item.participants){
              let new_div = document.createElement('div');
              new_div.innerHTML = inner_item.display_name;
              jitsi_parts.appendChild(new_div)


            }
          }

          let ws_parts = document.getElementById('one_by_room_ws_participants_' + item.room_id)
          if(ws_parts){
            ws_parts.innerHTML = "";
            
            for(let inner_item of item.ws_users){
              let new_div = document.createElement('div');
              new_div.innerHTML = inner_item;
              ws_parts.appendChild(new_div)
            }
          }
        }
      },
      error: function (response) {
        console.log("Fail")
          console.log(response)
      }
    });

}

function get_jitsi_rooms() {
    // const numberOfParticipants = api.getNumberOfParticipants();
    // console.log("\n\n\nNumber In Room", numberOfParticipants);

    // let participants = api.getParticipantsInfo();
    // // console.log("Room participants", participants, typeof(participants));
    // let people_in_room = JSON.stringify(participants)
    // for (let item of participants){
    //   console.log("Participant ", item.displayName)
    // }
    let string_list  = ""
    $.ajax({
        type: 'GET',
        url: "https://sessions.goebookbuddy.org/all-rooms",
        success: function (response) {
          // console.log("\n all-rooms call success for user_id", user_id)
          // console.log("all-rooms response", response) 

        },
        error: function (response) {
          console.log("Fail")
            // console.log(response)
        }
       }).done(function( response ) {
          let json_rooms = JSON.parse(response)
          // console.log("\n\n\n\n\njson_rooms", json_rooms, typeof(json_rooms))

          let room_list = {}
          for (let item of json_rooms.rooms){
            // console.log("item", item)


            //console.log("room", item.jid)
            let slug = item.jid.split('@')[0].replaceAll('%20', '-')
            // console.log("\n\nslug", slug)

            let room_parts = []
            let participants = item.participants
            for (let item of participants){
              // console.log("participants", item.display_name)
              room_parts.push(item.display_name)
            }
            j_info = {}
            j_info['participants'] = room_parts
            j_info['j_count'] = item.participant_count
            room_list[slug] = j_info

            // console.log("Room List", room_list, typeof(room_list))
            string_list  = JSON.stringify(room_list)
             
          }

          // console.log("Room List", room_list, typeof(room_list))
           let all_rooms_room_rows = document.getElementsByClassName('all_rooms_room')
          for(let room_row of all_rooms_room_rows){
            // console.log('room_row id', room_row.id)
            let this_room_slug = room_row.id.split('_')[3]
            // let all_rooms_ws_count = document.getElementById('all_rooms_ws_room_count_' + this_room_slug)
            // if(all_rooms_ws_count){
            //   all_rooms_ws_count.innerHTML = 0;
            // }
            let all_rooms_js_count = document.getElementById('all_rooms_jitsi_room_count_' + this_room_slug);
            if(all_rooms_js_count){
              let j_part_div = document.getElementById('all_rooms_room_j_participants_' + this_room_slug); 
              
              // console.log("row slug", this_room_slug)
              let place = room_list[this_room_slug]
              

              // console.log("place", place)
              if (place){                
                let new_count = place.j_count;
                all_rooms_js_count.innerHTML = new_count;
                let jr_parts = place.participants
                j_part_div.innerHTML = "";
                for(let jp of jr_parts){
                  let r_person = document.createElement('div');
                  r_person.innerHTML = jp;
                  j_part_div.appendChild(r_person);
                }
              } else{
                j_part_div.innerHTML = "";
                all_rooms_js_count.innerHTML = 0;
              }

            }

            // console.log("row slug", this_room_slug)
            
            // console.log("Index", index)

            
          } 

 



      });

  }

function get_room_participants(){
  // console.log('room_name', room_name)


   let get_room_url =  "https://sessions.goebookbuddy.org/room" +"?" + "room=" + room_name.replaceAll("_"," ")
   // console.log('get_room_url', get_room_url)

    $.ajax({
      type: 'GET',
      url: get_room_url,
      success: function (response) {
        // console.log("Success ROOM")
        // console.log(response)
        let parse_room = JSON.parse(response)
        let this_room_name = document.getElementById('this_room_name');
        if(this_room_name){
          this_room_name.innerHTML = parse_room.room_name;
        }
        let this_room_count = document.getElementById('this_room_count');
        if(this_room_count){
          this_room_count.innerHTML = " - " + parse_room.count;
        }

        let this_room_participants = document.getElementById('this_room_participants');
        if(this_room_participants){
          this_room_participants.innerHTML = '';
          for(let item of parse_room.participants){
            // console.log('item', item)
            let new_js_part = document.createElement('div');
            new_js_part.classList.add('border');
            new_js_part.classList.add('p-1');

            new_js_part.innerHTML = item.display_name;
            this_room_participants.appendChild(new_js_part);

          }

        }

        
      },
      error: function (response) {
        console.log("Fail")
          console.log(response)
      }
    });


}

window.addEventListener('resize', function(event) {
    // console.log("resize", event )
    if(staff_outer_div_presence){
       let current_width = staff_outer_div_presence.offsetWidth;
        // console.log("current_width", current_width);
        // console.log("last_width_monitoring", last_width_monitoring);
        // console.log("last_width_video", last_width_video);
        let new_size_for_video = current_width - 80 - last_width_monitoring;
        last_width_video = new_size_for_video;
        jitsi_div.style.width = new_size_for_video + 'px'; 
    }
    


}, true);


function determine_div_to_display(target) {
  // console.log("div to display", target)
  let div_to_display_id = target.id + "_show"
  for(let item of all_monitoring_divs){
      if(item.id == div_to_display_id){
        item.classList.remove('d-none')
        if(target.id == "todays_session_btn"){
          all_sessions_div.style.display = "block"; 
          matches_in_session_div.classList.add('d-none')
          matches_in_session_div.style.display = "none";

        } else if (target.id == "rooms_participants_btn"){
            // console.log("rooms_participants_btn clicked")
            display_room_divs("ws_rooms_btn")

        } else if(target.id == "staff_chat_btn"){
          ajax_staff_reset();
        }
      } else{
        item.classList.add('d-none')
      }
    }
    open_monitoring()
}

function determine_session(element){
  // console.log("div to display", element)  
  all_sessions_div.style.display = "none"; 
  matches_in_session_div.classList.remove('d-none')
  matches_in_session_div.style.display = "block";

    const outer_session_divs = document.querySelectorAll('.outer_session_div');
    let id_for_outer_div_show = "outer_session_div_" + element.getAttribute("value")
     // console.log("div to id_for_outer_div_show", id_for_outer_div_show)
    for (let item of outer_session_divs) {
      // console.log("item outer_session_divs", item)
        if (item.id == id_for_outer_div_show){
         item.style.display = "block";
        } else {
         item.style.display = "none";
        }
    }
}

if(staff_outer_div_presence){
  window.addEventListener('load', (event) => {
    
    
    for(let item of all_monitoring_divs){
      if(item == todays_sessions_div){
        item.classList.remove('d-none');
        matches_in_session_div.classList.add('d-none');
      } else{
        item.classList.add('d-none')
      }
    }

  });
}


function close_monitoring(element) {
  // console.log("close_monitoring", element)
  let staff_left_panel = document.getElementById('staff_left_panel');
  staff_left_panel.classList.add('d-none');
  let drag_handle = document.getElementById('drag_handle');
  drag_handle.classList.add('d-none');
  let new_sidebar = document.getElementById('new_sidebar');
  let staff_sidebar_div_width = new_sidebar.offsetWidth;
  // console.log("staff_sidebar_div_width", staff_sidebar_div_width);
  let staff_outer_div_presence_width = staff_outer_div_presence.offsetWidth;
  // console.log("staff_outer_div_presence_width", staff_outer_div_presence_width);
  let new_width_of_meeting = staff_outer_div_presence_width - staff_sidebar_div_width
  let video_div = document.getElementById('jitsi_meeting_div');
  video_div.style.width = new_width_of_meeting + "px";
}

function open_monitoring() {
  // console.log("open_monitoring")
  // console.log("last_width_monitoring", last_width_monitoring)
  // console.log("last_width_video", last_width_video)
  let monitoring_pane_div = document.getElementById('staff_left_panel');
  let class_list = monitoring_pane_div.classList
  // console.log("class_list", class_list, typeof(class_list))
  if(class_list.value.search('d-none') != -1){
    // console.log("open_monitoring inner")
    let new_width_of_monitoring = last_width_monitoring +'px';
    monitoring_pane_div.style.width = new_width_of_monitoring;
    monitoring_pane_div.classList.remove('d-none');
    let staff_drag_bar = document.getElementById('drag_handle');
    staff_drag_bar.classList.remove('d-none');
    let staff_sidebar_div = document.getElementById('new_sidebar');
    let new_width_of_meeting = last_width_video +'px';  
    let video_div = document.getElementById('jitsi_meeting_div');
    video_div.style.width = new_width_of_meeting;
  }
  
  
}

//help request modal
const help_request_modal = document.getElementById('helpModal');
const help_request_input = document.getElementById('help_message_content');
if(help_request_modal){
	help_request_modal.addEventListener('shown.bs.modal', function () {
	  help_request_input.focus();
	})
}



// Open-Close Full Screen
const open_full_screen_btn = document.getElementById('open_full_screen');
const close_full_screen_btn = document.getElementById('close_full_screen');

/* Get the documentElement (<html>) to display the page in fullscreen */
var elem = document.documentElement;

/* View in fullscreen */
function open_full_screen() {

  if (elem.requestFullscreen) {
    elem.requestFullscreen();
  } else if (elem.webkitRequestFullscreen) { /* Safari */
    elem.webkitRequestFullscreen();
  } else if (elem.msRequestFullscreen) { /* IE11 */
    elem.msRequestFullscreen();
  }

  open_full_screen_btn.style.display = "none";
  close_full_screen_btn.style.display = "inline-grid";
}

/* Close fullscreen */
function close_full_screen() {
  if (document.exitFullscreen) {
    document.exitFullscreen();
  } else if (document.webkitExitFullscreen) { /* Safari */
    document.webkitExitFullscreen();
  } else if (document.msExitFullscreen) { /* IE11 */
    document.msExitFullscreen();
  }

  open_full_screen_btn.style.display = "inline-grid";
  close_full_screen_btn.style.display = "none";
}

document.addEventListener('fullscreenchange', exitHandler);
document.addEventListener('webkitfullscreenchange', exitHandler);
document.addEventListener('mozfullscreenchange', exitHandler);
document.addEventListener('MSFullscreenChange', exitHandler);

function exitHandler() {
    if (!document.fullscreenElement && !document.webkitIsFullScreen && !document.mozFullScreen && !document.msFullscreenElement) {
        open_full_screen_btn.style.display = "inline-grid";
        close_full_screen_btn.style.display = "none";
    }
} 


//Resizing Staff panes
if(staff_outer_div_presence){

let isResizing = false;
let lastDownX = 0;

$(function () {
  let handle = $('#drag_handle')
  let container = $('#outer_div_staff')
  let staff_sidebar = $('#new_sidebar')
  let staff_left_panel = $('#staff_left_panel')
    // let room_header_inline_grid = $('#room_header_inline_grid')
    // let unmatched_row = $('#unmatched_row')
    // let monitoring_content = $('#monitoring_content')
  let staff_right_panel = $('#jitsi_meeting_div')
    

    var window_width = $(window).width();
    // console.log('window_width', window_width);

    var handle_width = handle.width();
    // console.log('handle_width', handle_width);

    var container_width = container.width() - handle_width;
    // console.log('container_width', container_width);

    var sidebar_width = staff_sidebar.width();
    // console.log('sidebar_width', sidebar_width);

    let half_width = (container_width - sidebar_width)/2;
    last_width_monitoring = half_width
    last_width_video = half_width
    staff_left_panel.css('width', half_width + "px");
    staff_right_panel.css('width', half_width + "px");

    var staff_left_panel_width = staff_left_panel.width();
    // console.log('staff_left_panel_width', staff_left_panel_width);   

    
    var staff_right_panel_width = staff_right_panel.width();
    // console.log('staff_right_panel_width', staff_right_panel_width);
    
    if(container){
        handle.on('mousedown touchstart', function (e) {
        isResizing = true;
        lastDownX = e.clientX;
            // console.log('e', e);
            if(e.type == 'touchstart'){
              isResizing = true;
              lastDownX = e.originalEvent.touches[0].pageX;
              // console.log('touchstart isResizing', isResizing);
              // console.log('touchstart lastDownX', lastDownX);

            }else if (e.type == 'mousedown'){
              isResizing = true;
              lastDownX = e.clientX;
              // console.log('Mouse down isResizing', isResizing);
              // console.log('mouse down lastDownX', lastDownX);
            }
            
        });

        $(document).on('mousemove touchmove', function (e) {
            // console.log("Doing something")
            
            // we don't want to do anything if we aren't resizing.
            if (!isResizing) 
                return;

            if(e.type == 'touchmove'){
               lastDownX = e.changedTouches[0].clientX;
              // console.log('touchstart isResizing', isResizing);
              // console.log('touchstart lastDownX', lastDownX);

            }else if (e.type == 'mousemove'){
              lastDownX = e.clientX;
              // console.log('Mouse down isResizing', isResizing);
              // console.log('mouse down lastDownX', lastDownX);
            }

            // console.log("lastDownX", lastDownX)

            // var room_header_inline_grid_height = room_header_inline_grid.height();
            // console.log('room_header_inline_grid_height', room_header_inline_grid_height);

            // var unmatched_row_height = unmatched_row.height();
            // console.log('unmatched_row_height', unmatched_row_height);

            // let header_height = room_header_inline_grid_height + unmatched_row_height + 5
            // console.log('header_height', header_height);

            // let height_str = "calc(100% - " + header_height + "px)"

            // monitoring_content.css('height', height_str);

            // console.log('mouse_moving', lastDownX);
            var container_width = container.width();
            // console.log('container_width', container_width);

            var sidebar_width = staff_sidebar.width();
            // console.log('sidebar_width', sidebar_width);

            let width_of_left_now = lastDownX - sidebar_width
            // console.log('width_of_left_now', width_of_left_now);

            let width_of_right_now = container_width - width_of_left_now
            // console.log('width_of_right_now', width_of_right_now);

            let total_width = width_of_right_now + width_of_left_now + sidebar_width
            // console.log("total_width", total_width)
            last_width_monitoring = width_of_left_now
            last_width_video = width_of_right_now

            let str_width_left = width_of_left_now + "px"
            let str_width_right = width_of_right_now + "px"

            if (width_of_right_now > 275 ){
              if(width_of_left_now > 0){
                staff_sidebar.css('width', "80px");
                staff_left_panel.css('width', str_width_left);
                staff_right_panel.css('width', str_width_right);
              }else{
                isResizing = false;
              }
              
            } else{
              isResizing = false;
            }

            
            
            // var left_width = lastDownX//- (e.clientX - container.offset().left);
            // adjusted_left_panel_width = left_width;
            // console.log('left_width', left_width);

            // var right_width = container_width -  lastDownX //- (e.clientX - container.offset().left);
            // adjusted_right_panel_width = right_width;
            // console.log('right_width', right_width);

            // if(right_width <= 225){
            //     let set_panel_width = container_width - 225;
            //     let width_str = set_panel_width + 'px'
            //     staff_left_panel.css('width', width_str);
            //     staff_right_panel.css('width', '225px');
            // } else {
            //     staff_left_panel.css('width', left_width);
            //     staff_right_panel.css('width', right_width);
            // }

        }).on('mouseup touchend', function (e) {
            // stop resizing
            isResizing = false;

            // console.log('End isResizing ', isResizing);
            //console.log('mouse up lastDownX', lastDownX);
        });
    };
});
};


function play_notification_sound(){
    let audio_element = document.getElementById('general_audio');
    audio_element.play();
}

//Redirects

function clear_existing_room(){
  let existing_room = document.querySelector('input[name="manual_room"]:checked')
  if(existing_room){
      existing_room.checked=false;
    }
}

function close_create_redirect(){
  let checkboxes_selected = document.querySelectorAll('input[name="user_in"]:checked');
    for (let checkbox of checkboxes_selected) {
        checkbox.checked = false;
    }
    let existing_room = document.querySelector('input[name="manual_room"]:checked')
    if(existing_room){
        existing_room.checked = false;
    }
}

function clear_redirect_error(){
    let error_div = document.getElementById('create_redirect_error');
    let error_div_text = document.getElementById('create_redirect_error_text');
    create_redirect_error_text.innerHTML = "";
    error_div.classList.add('d-none');
}

function create_and_send(){
    let close_manual_redirect_btn = document.getElementById('close_manual_redirect');
    let error_div = document.getElementById('create_redirect_error');
    let error_div_text = document.getElementById('create_redirect_error_text');
    let users_to_add = [];
    let existing_room = document.querySelector('input[name="manual_room"]:checked')
    let checkboxes_selected = document.querySelectorAll('input[name="user_in"]:checked');
    for (let checkbox of checkboxes_selected) {
        users_to_add.push(checkbox.value);
    }

    if(! existing_room || checkboxes_selected.length == 0){
        // console.log("something is empty")
        error_div.classList.remove('d-none');
        error_div_text.innerHTML = "Both a Room and Users are required.";

    } else {

        // console.log("existing_room", existing_room.value);
        // console.log("from_user", user_id.textContent);
        // console.log("users_to_add", users_to_add);
        let existing_room_value = existing_room.value;
        let from_user_value = user_id.textContent;
        send_redirect_data(existing_room_value, from_user_value, users_to_add);
        close_manual_redirect_btn.click();
        
    }
}

//help requests
function reply_to_help_request(request_id){
  // console.log("Request ID", request_id)
}
function ask_for_help(){
    let from_user_id = document.getElementById('from_user').value;
    let from_room_id = document.getElementById('from_room').value;
    let from_username = JSON.parse(document.getElementById('username').textContent);
    let from_room = JSON.parse(document.getElementById('room_name').textContent);
    let base_message = from_username + " needs help in " + from_room;
    let message_content = document.getElementById('help_message_content')
    // console.log(from_user_id)
    // console.log(from_room_id)
    // console.log(from_username)
    // console.log(from_room)
    // console.log(base_message)
    // console.log(message_content, message_content.value)
    let close_help = document.getElementById('close_send_help_request')

    ajax_create_help_request(base_message, message_content.value, from_user_id, from_room_id)
    message_content.value = "" ;
    close_help.click(); 
}

function ajax_create_help_request(base_message, message_content, from_user_id, from_room_id){
    payload = {
    // "csrfmiddlewaretoken": "{{ csrf_token }}",
    "message": base_message,
    "user_message": message_content,
    "from_user_id": from_user_id,
    "from_room_id": from_room_id
    }

    $.ajax({
      type: 'POST',
      dataType: "json",
      url: "/sessions/create_help_request/", // production
      data: payload,
      timeout: 5000,
      success: function (response) {
      if(response["valid"]){

      let the_response = response;

      }
      },
      error: function (response) {
      console.log(response)
      },
    });
}

function mark_as_done(request_id, send_to_staff){
    payload = {
    "user_id": JSON.parse(document.getElementById('user_id').textContent),
    "request_id": parseInt(request_id),
    "send_to_staff": send_to_staff,
          }

          $.ajax({
          type: 'POST',
          dataType: "json",
          url: "/sessions/ajax_help_mark_as_done/", // production
          data: payload,
          timeout: 5000,
          success: function (response) {
                 if(response["valid"]){
                  let help_none = document.getElementById('no_help_requests')
                  // console.log("Mark As Done", response);
                   let help_row_element = document.getElementById('help_row_' + request_id);
                    // console.log("help_row_element", help_row_element)
                    if(help_row_element){
                    help_row_element.remove();
                    if(response['not_done_count'] == 0){
                        help_none.classList.add('d-none')
                    }else{
                        help_none.classList.remove('d-none')
                    }
                  }

                 }
               },
               error: function (response) {
               console.log(response)
               },
        });
}

function mark_all_as_done(){
    // console.log("mark_all_as_done")
    var individual_buttons = document.querySelectorAll(".individual_help_request");
    // console.log("individual_buttons", individual_buttons)
    var individual_buttons_length = individual_buttons.length
    // console.log("individual_buttons_length", individual_buttons_length)

    for(let [index, item]  of individual_buttons.entries()){
        let individual_redirect_id = item.getAttribute('value');
        // mark_as_done(individual_redirect_id, true)
        // console.log(index, individual_redirect_id)
        if(index != individual_buttons_length -1){
          mark_as_done(individual_redirect_id, false)
        } else{
          mark_as_done(individual_redirect_id, true)
        }
    }

    close_help_modal.click()
}

function close_view_help_requests(){

}

//Matches

function set_new_match_vol(element){
      // console.log("set_new_match_vol", element.id);
      const input_new_match_vol = document.getElementById('to_reader_id');
      
      let radio_id = "radio_vol_" + element.id.split("_")[3];
      const radio_input_vol = document.getElementById(radio_id);
      radio_input_vol.checked = true;

      // console.log('element', element);
      input_new_match_vol.value = radio_input_vol.value;
  }

  function set_new_match_stu (element){
        // console.log("set_new_match_stu", element.id);
      const input_new_match_stud = document.getElementById('reassign_student_id2');
      
      let radio_id = "stu_radio_" + element.id.split("_")[3];
      // console.log("RADIO_ID", radio_id)
      const radio_input_vol = document.getElementById(radio_id);
      // console.log("radio_input_vol", radio_input_vol);
      radio_input_vol.checked = true;

      // console.log('element', element);
      input_new_match_stud.value = radio_input_vol.value;
  }


function clear_error_create_match(){
  let error_div = document.getElementById('create_match_error');
  error_div.classList.add('d-none');
  error_div.innerHTML = "";

}


function close_create_manual_match(){
      // console.log("Closing manual match")
      var checkboxes_session = document.querySelectorAll(".session_radio");
      for(let item of checkboxes_session){
          item.checked = false;
      }
      var new_match_radios = document.querySelectorAll(".new_match_radio");

      for(let item of new_match_radios){
          item.checked = false;
      }
      clear_error_create_match();

  }

  function create_manual_match() {
      // console.log("create_manual_match",);
      let match_type = document.getElementById('input_temp_type')
      let student_new_match = document.querySelector('input[name="stu_choice"]:checked');
      let reader_new_match = document.querySelector('input[name="reader_choice"]:checked');
      let current_session = document.querySelector('input[name="ind_session"]:checked');
      let close_manual_match_modal = document.getElementById('close_create_manual_create_modal');
      let manual_match_error = document.getElementById('create_match_error');
      let send = true;
      let current_session_id = "";
      let vol_new_match_id = "";
      let student_new_match_id = "";

      // console.log("Student", student_new_match);
      // console.log("Reader", reader_new_match);
      // console.log("Current Session", current_session);

      if (current_session){
          current_session_id = current_session.value;
          // console.log("Current Session Value", current_session_id);

      } else {
          send = false;
          let session_error_div = document.createElement('div');
          session_error_div.innerHTML = " * Please add a Session.";
          manual_match_error.appendChild(session_error_div);
          manual_match_error.classList.remove('d-none');
      }

      if (reader_new_match){
          reader_new_match_id = reader_new_match.value;

      } else {
          send = false;
          let reader_error_div = document.createElement('div')
          reader_error_div.innerHTML = "* Please add a Reader."
          manual_match_error.appendChild(reader_error_div)
          manual_match_error.classList.remove('d-none');
      }

      if (student_new_match){
          student_new_match_id = student_new_match.value;
          // console.log("Current Stu Value", student_new_match_id);
      } else {
          let student_error_div = document.createElement('div')
          student_error_div.innerHTML = "* Please add a Student."
          manual_match_error.appendChild(student_error_div);
          send = false;
          manual_match_error.classList.remove('d-none');
      }


      if(send){
         let sent_by = JSON.parse(document.getElementById('user_id').textContent);
          // console.log("sent_by", sent_by)
          // console.log("current_session_id", current_session_id)
          // console.log("student_new_match_id", student_new_match_id)
          // console.log("reader_new_match_id", reader_new_match_id)

          create_new_match(sent_by, current_session_id, student_new_match_id, reader_new_match_id)

          close_manual_match_modal.click()   
      }             
  }

//Redirects
const close_redirects_btn = document.getElementById('close_redirects_modal');
function close_redirects(){
  // console.log("Closing redirects");
}


//Notify Users

var sendMessageModal = document.getElementById('sendMessageModal')
var to_all_message = document.getElementById('message_to_all')
if(sendMessageModal){
  sendMessageModal.addEventListener('shown.bs.modal', function () {
  to_all_message.focus()
  })

}
  
function send_msg_to_all(){
  // console.log("To All");
  let message_to_all = document.getElementById('message_to_all');
  let close_to_all = document.getElementById('close_to_all');
  let notify_from_user_id = document.getElementById('notify_from_user_id');
  let from = notify_from_user_id.value;
  let to_group = document.querySelector('input[name="to_group"]:checked');
  let msg_to_all = message_to_all.value;
  let notify_error = document.getElementById('notify_error');
  
  if(to_group && msg_to_all!=""){
    let for_group = to_group.getAttribute('value');

    websocket_send_notify_message(msg_to_all, for_group, from)
    
      
      close_to_all.click()
  } else{
    if(!to_group){
      notify_error.innerHTML = "To Group is Required."
    } else if(msg_to_all == ""){
      notify_error.innerHTML = "Message is Required."
    }else{
      notify_error.innerHTML = "To Group and Message are Required."
    }
    
  }

  
}

function clear_notify_error(){
  let notify_error = document.getElementById('notify_error');
  notify_error.innerHTML = ""
}

function close_notify_all(){
  let default_choice = document.getElementById('notify_all_default');
  default_choice.checked = true;
  let message_to_all = document.getElementById('message_to_all');
  message_to_all.value = '';


}


function check_status_for_user() {
  let all_connected = false
  if(room_view == "Staff View"){
    if(staff_chat_socket && status_socket){
      let connected_staff_chat = staff_chat_socket.readyState;
      let connected_status_ws = status_socket.readyState;
      // console.log(connected_status_ws, connected_staff_chat)
      if(connected_status_ws == 1 && connected_staff_chat ==1){
        all_connected = true
      } 
    }else{
        getStaffSocket();
        getStatusSocket();
      }    
  } else{
    if(status_socket){
      let connected_status_ws = status_socket.readyState;
      if(connected_status_ws == 1){
        all_connected = true
      } 
    }else{
        getStatusSocket();
      }
  }
  payload = {
    'user_id': user_id.textContent,
    'user_view': room_view,
    'all_connected': all_connected,
  }

  $.ajax({
      type: 'GET',
      dataType: "json",
      url: "/sessions/ajax_status/", // production
      data: payload,
      timeout: 5000,
      success: function (response) {
             if(response["valid"]){
              // console.log("Status Response", response);


             }
           },
           error: function (response) {
           console.log(response)
           },
    });

  // console.log("check_status_for_user Payload", payload);
}

const check_status_interval = setInterval(check_status_for_user, 30000);


//private messages/chat

const private_messages_button = document.getElementById('private_messages_button')
if(private_messages_button){
  private_messages_button.addEventListener('click', (event) => {  
    // console.log('Clicking Private Messages Button');
    get_private_rooms_for_user();

  });
}

function get_private_rooms_for_user_ajax(){
  let current_unread_count = document.getElementById('new_private_messages-' + user_id.textContent)
  // console.log("Get private rooms for user")
  payload = {
    'user_id': user_id.textContent,
    'current_unread_count': current_unread_count.innerHTML,
  }

  $.ajax({
      type: 'GET',
      dataType: "json",
      url: "/sessions/ajax_get_private_chats/", // production
      data: payload,
      timeout: 5000,
      success: function (response) {
             if(response["valid"]){
              // console.log("Status Response", response);


             }
           },
           error: function (response) {
           console.log(response)
           },
    });
}



let send_to_id = "";
let privateChatSocket = null;
let private_room_id = null;
let current_room_id = null;

function closeWebSocket(){
  if(privateChatSocket != null){
    privateChatSocket.close();
    privateChatSocket = null;
    current_room_id = null;
    clearPrivateChatLog();
    setPrivatePageNumber("1");
    disablePrivateChatLogScrollListener();
  }
}

function setupWebSocket(private_room_id){
  console.log("setupWebSocket: " + private_room_id);
  let private_room_ID = private_room_id
  current_room_id = private_room_ID
  // close previous socket if one is open
  closeWebSocket();
  let private_ws_path;
  if (ws_scheme == "ws"){
    private_ws_path = ws_scheme + '://' + window.location.host + "/private_chat/" + private_room_ID + "/"; // development
  } else if (ws_scheme == "wss"){
    private_ws_path = ws_scheme + '://' + window.location.host + ":8001/private_chat/" + private_room_ID + "/"; // production
  } else {
    console.log("Else ws_scheme", ws_scheme)
  }
  console.log("private_ws_path", private_ws_path)

  privateChatSocket = new WebSocket(private_ws_path);
  privateChatSocket.onmessage = function(message) {
  let private_message_data = JSON.parse(message.data);

  displayPrivateChatroomLoadingSpinner(private_message_data.display_progress_bar)

  if(private_message_data.to_user){
      // console.log("new chat message for user", private_message_data)
      // console.log("new chat message for user", private_message_data.to_user)
      if(private_message_data.to_user != parseInt(user_id.textContent)){
        status_socket.send(JSON.stringify({
            "command": "get_private_messages",
            "user_id": private_message_data.to_user,
            "for_private_room": "Not Sure",
            "action":"new_message",
          }));
        }
    }

  if (private_message_data.error) {
      console.error(private_message_data.error + ": " + private_message_data.message)
      showPrivateClientErrorModal(private_message_data.message)
      return;
    }

  // Handle joining (Client perspective)
    if (private_message_data.join) {
      // console.log("HERE Joining room " + private_message_data.join);
      // console.log(private_message_data)
      getUserInfo(private_room_ID)
      getPrivateRoomChatMessages(private_room_ID)
      enableChatLogScrollListener()
    }
    // Handle leaving (client perspective)
    if (private_message_data.leave) {
      // do nothing
      // console.log("Leaving room " + private_message_data.leave);
    }

    // user info coming in from backend
    if(private_message_data.user_info){
      // console.log("user info coming in from backend", private_message_data.user_info)
      handleOtherUserInfoPayload(private_message_data.user_info)
    }

    // Handle getting a message
    if (private_message_data.msg_type == 0 || private_message_data.msg_type == 1 || private_message_data.msg_type == 2) {
      // console.log("Handle getting a message", private_message_data)
      appendPrivateChatMessage(private_message_data, false, true)
    }

    // new payload of messages coming in from backend
    if(private_message_data.messages_payload){
      // console.log("new payload of messages coming in from backend", private_message_data.messages_payload)
      handlePrivateMessagesPayload(private_message_data.messages, private_message_data.new_page_number)
    }




  }

  privateChatSocket.addEventListener("open", function(e){
      console.log("privateChatSocket OPEN")
      // join chat room      
        privateChatSocket.send(JSON.stringify({
          "command": "join",
          "room": private_room_ID
        }));     

      let close_view_private_message_btn = document.getElementById('close_view_private_message');
      close_view_private_message_btn.value = private_room_ID;
    })

    privateChatSocket.onclose = function(e) {
      console.log('PRIVATE CHAT socket closed.');
      let close_view_private_message_btn = document.getElementById('close_view_private_message');
      close_view_private_message_btn.value = "";
    };

    privateChatSocket.onOpen = function(e){
      console.log("privateChatSocket onOpen", e)
    }

    privateChatSocket.onerror = function(e){
          console.log('privateChatSocket error', e)
      }

      if (privateChatSocket.readyState == WebSocket.OPEN) {
        console.log("privateChatSocket OPEN")
      } else if (privateChatSocket.readyState == WebSocket.CONNECTING){
          console.log("privateChatSocket connecting..")
      }
} //setup end

  document.getElementById('id_private_chat_message_input').focus();
  document.getElementById('id_private_chat_message_input').onkeyup = function(e) {
    if (e.keyCode === 13 && e.shiftKey) {  // enter + return
      // Handled automatically by textarea
    }
    else if(e.keyCode === 13 && !e.shiftKey){ // enter + !return
      document.getElementById('id_private_chat_message_submit').click();
    }
  };

    document.getElementById('id_private_chat_message_submit').onclick = function(e) {
      let close_view_private_message_btn = document.getElementById('close_view_private_message');
      let pvt_room_ID = close_view_private_message_btn.value;
      let to_user_ID = document.getElementById('conversation_other_user').value;
    const messageInputDom = document.getElementById('id_private_chat_message_input');
    const message = messageInputDom.value;
    privateChatSocket.send(JSON.stringify({
      "command": "send",
      "message": message,
      "room": pvt_room_ID,
      "room_id": pvt_room_ID,
      "to_user": to_user_ID,
      "from_user": user_id,
      "pvt_message": message,
    }));
    messageInputDom.value = '';

    // console.log("PRIVATE MESSAGE IN OPEN ROOM SENT")

  };

function handlePrivateMessagesPayload(messages, new_page_number){
  // console.log("HERE NEW PRIVATE MESSAGES", messages, new_page_number)
  if(messages != null && messages != "undefined" && messages != "None"){
    setPrivatePageNumber(new_page_number)
    messages.forEach(function(message){
      appendPrivateChatMessage(message, true, false)
    })
  }
  else{
    setPrivatePaginationExhausted() // no more messages
  }
}

function setPrivatePaginationExhausted(){
    setPrivatePageNumber("-1")
  }

function appendPrivateChatMessage(data, maintainPosition, isNewMessage){

    // console.log('appendPrivateChatMessage', data, maintainPosition, isNewMessage)
    messageType = data['msg_type']
    msg_id = data['msg_id']
    message = data['message']
    uName = data['username']
    msg_user_id = data['user_id']
    // profile_image = data['profile_image']
    timestamp = data['natural_timestamp']
    // console.log("append chat message: " + messageType)
    
    var msg = "";
    var username = ""

    // determine what type of msg it is
    switch (messageType) {
      case 0:
        // new chatroom msg
        username = uName + ": "
        msg = message + '\n'
        createPrivateChatMessageElement(msg, msg_id, username, msg_user_id, timestamp, maintainPosition, isNewMessage)
        break;
      case 1:
        // User joined room
        // createPrivateConnectedDisconnectedElement(message, msg_id, msg_user_id)
        break;
      case 2:
        // User left room
        // createPrivateConnectedDisconnectedElement(message, msg_id, msg_user_id)
        break;
      default:
        console.log("Unsupported message type!");
        return;
    }
  }

  function createPrivateChatMessageElement(msg, msg_id, username, user_id, timestamp, maintainPosition, isNewMessage){
    // console.log("message",msg)


    var privateChatLog = document.getElementById("id_private_chat_log")

    var newMessageDiv = document.createElement("div")
    newMessageDiv.classList.add("message_container")
    // newMessageDiv.innerHTML = msg;
    var top_div = document.createElement("div")
    top_div.classList.add("top_div")

    var message_div = document.createElement("div")
    message_div.classList.add("message_div")
    var msg_p = document.createElement("p")
    msg_p.innerHTML = msg
    message_div.appendChild(msg_p)

    var name = document.createElement("div")
    name.classList.add("name")
    name.innerHTML = username
    var time = document.createElement("div")
    time.classList.add("time")
    time.innerHTML = timestamp
    top_div.appendChild(name)
    top_div.appendChild(time) 
    newMessageDiv.appendChild(top_div)
    newMessageDiv.appendChild(message_div)


    if(isNewMessage){
      // console.log("is new")
      privateChatLog.insertBefore(newMessageDiv, privateChatLog.firstChild)
    }
    else{
      // console.log("not new")
      privateChatLog.appendChild(newMessageDiv)
    }
    
    if(!maintainPosition){
      // console.log("maintainPosition", maintainPosition)
      privateChatLog.scrollTop = privateChatLog.scrollHeight
    }

  }


function getUserInfo(pvt_room_ID){
    privateChatSocket.send(JSON.stringify({
      "command": "get_user_info",
      "room_id": pvt_room_ID,
    }));
  }

  function handleOtherUserInfoPayload(user_info){
    let private_modal_title = document.getElementById('conversation_other_user');
    if(private_modal_title){
      private_modal_title.innerHTML = user_info.full_name;
      private_modal_title.value = user_info.user_id;
    }

  }

function getPrivateRoomChatMessages(private_room_ID){
  var privatePageNumber = document.getElementById("id_private_page_number").innerHTML

  if(privatePageNumber != "-1"){
    setPrivatePageNumber("-1") // loading in progress
    privateChatSocket.send(JSON.stringify({
      "command": "get_room_chat_messages",
      "room_id": private_room_ID,
      "page_number": privatePageNumber,
    }));
  }
}

function getJustTheMessages(private_room_ID){
    setPrivatePageNumber("-1") // loading in progress
    privateChatSocket.send(JSON.stringify({
      "command": "get_room_chat_messages",
      "room_id": private_room_ID,
      "page_number": 1,
    }));
}

  function showPrivateClientErrorModal(message){
    // console.log("ERROR CLIENT ERROR")
    // document.getElementById("id_client_error_modal_body").innerHTML = message
    // document.getElementById("id_trigger_client_error_modal").click()
  }


function close_private_messages(){
  // console.log("Closing Private Messages");

}

function clearPrivateChatLog(){
  document.getElementById("id_private_chat_log").innerHTML = ""
}

function setPrivatePageNumber(pageNumber){
  document.getElementById("id_private_page_number").innerHTML = pageNumber
}

function enableChatLogScrollListener(){
    document.getElementById("id_private_chat_log").addEventListener("scroll", privateChatLogScrollListener);
  }

function disablePrivateChatLogScrollListener(){
  document.getElementById("id_private_chat_log").removeEventListener("scroll", privateChatLogScrollListener)
}

function privateChatLogScrollListener(e) {
  var privatechatLog = document.getElementById("id_private_chat_log")
  let close_view_private_message_btn = document.getElementById('close_view_private_message');
  let pvt_room_ID = close_view_private_message_btn.value;
  if ((Math.abs(privatechatLog.scrollTop) + 2) >= (privatechatLog.scrollHeight - privatechatLog.offsetHeight)) {
    getPrivateRoomChatMessages(pvt_room_ID);
  }
}

function displayPrivateChatroomLoadingSpinner(isDisplayed){
  // console.log("displayPrivateChatroomLoadingSpinner: " + isDisplayed)
  var spinner = document.getElementById("id_private_chatroom_loading_spinner")
  if(isDisplayed){
    spinner.style.display = "block"
  }
  else{
    spinner.style.display = "none"
  }
}


function clear_send_message_error(){
  // console.log("clear_send_message_error");
  let send_p_msg_error_div = document.getElementById('send_private_message_error');
  if(send_p_msg_error_div){
    send_p_msg_error_div.classList.add('d-none');
    let inner_text = document.getElementById('private_message_error_text');
    if(inner_text){
      inner_text.innerHTML = "";
    }
    
  }
}


function create_new_private_message(){
  // program_semester.options[program_semester.selectedIndex].value;
  let send_p_msg_error_div = document.getElementById('send_private_message_error');
  let inner_text = document.getElementById('private_message_error_text');
  let private_from = document.getElementById('private_from');
  let to_user_select = document.getElementById('id_to_user');

  let private_content = document.getElementById('private_msg_content');

  let from_user = private_from.value
  let to_user = parseInt(to_user_select.options[to_user_select.selectedIndex].value);
  let content_value = private_content.value

  if(to_user == 0 && content_value == ""){
    if(send_p_msg_error_div){    
      let inner_text = document.getElementById('private_message_error_text');
      if(inner_text){
        inner_text.innerHTML = "Both Fields Are Required.";
      }
      send_p_msg_error_div.classList.remove('d-none');
      
    }
  }else if(to_user == 0 ){
    if(send_p_msg_error_div){    
      let inner_text = document.getElementById('private_message_error_text');
      if(inner_text){
        inner_text.innerHTML = "To User is Required.";
      }
      send_p_msg_error_div.classList.remove('d-none');
      
    }
  }else if(content_value == "" ){
    if(send_p_msg_error_div){    
      let inner_text = document.getElementById('private_message_error_text');
      if(inner_text){
        inner_text.innerHTML = "A Message is Required.";
      }
      send_p_msg_error_div.classList.remove('d-none');
      
    }
  } else{
    
    send_private_message(from_user, to_user, content_value)
    to_user_select.options[to_user_select.selectedIndex].selected = false;
    private_content.value = "";
    document.getElementById('close_pvt_btn').click()

  }


}

function send_private_message(msg_from, msg_to, p_msg){
  // console.log("send_private_message", msg_from, msg_to, p_msg);
    payload = {
    'user_id': msg_from,
    'msg_to': msg_to,
    'p_msg': p_msg,
  }

    $.ajax({
      type: 'GET',
      url: "/sessions/ajax_private_chat/", // production,
      data: payload,
      success: function (response) {
        if(response["valid"]){
          // console.log(response) 
          chatroomId = response['private_room_id'];
          let private_chat_room_id = document.getElementById('private_chat_room_id');
          private_chat_room_id.value = chatroomId;                        
        }
      },
      error: function (response) {
          // console.log(response)
          console.log(response)
      }
    }).done(function() {
      // console.log('done')

      let private_to_room = private_chat_room_id.value
      // console.log('private_to_room', private_to_room)
      // OnGetOrCreateChatroomSuccess(private_to_room, msg_to, msg_from, p_msg)
      send_message_to_reading_consumer(private_to_room, msg_to, msg_from, p_msg)

      // send_message_to_private_consumer(private_to_room, msg_to, msg_from, p_msg)
    });
    
  };

function createPrivateConnectedDisconnectedElement(msg, msd_id, user_id){
    var privateChatLog = document.getElementById("id_private_chat_log")

    var newMessageDiv = document.createElement("div")
    newMessageDiv.classList.add("d-flex")
    newMessageDiv.classList.add("flex-row")
    newMessageDiv.classList.add("message-container")



    var usernameSpan = document.createElement("span")
    usernameSpan.innerHTML = msg
    usernameSpan.classList.add("username-span")
    usernameSpan.addEventListener("click", function(e){
      selectUser(user_id)
    })
    newMessageDiv.appendChild(usernameSpan)

    privateChatLog.insertBefore(newMessageDiv, privateChatLog.firstChild)


  }

  function selectUser(user_id){
    // Weird work-around for passing arg to url
    // var url = "url 'account:view' user_id=53252623623632623 ".replace("53252623623632623", user_id)
    // var win = window.open(url, "_blank")
    // win.focus()
  }


  function createOrReturnPrivateChat(id){
    payload = {
      // "csrfmiddlewaretoken": "{{ csrf_token }}",
      "user2_id": id,
    }
    $.ajax({
      type: 'GET',
      dataType: "json",
      url: "url 'reading_sessions:create-or-return-private-chat' %}", // production
      data: payload,
      timeout: 5000,
      success: function(data) {
        // console.log("SUCCESS", data)
        if(data['response'] == "Successfully got the chat."){
          setupWebSocket(data['chatroom_id'])
        }
        else if(data['response'] != null){
          alert(data['response'])
        }
      },
      error: function(data) {
        console.error("ERROR...", data)
        alert("Something went wrong.")
      },
    });
  }
