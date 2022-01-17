console.log("Loading Staff Chat JS");

const todays_staff_chat_room_id = JSON.parse(document.getElementById('todays_staff_chat_room_id').textContent);
// console.log("todays_staff_chat_room_id", todays_staff_chat_room_id);
// console.log("ws_scheme", ws_scheme);

let staff_ws_path;

if (ws_scheme == "ws"){
	staff_ws_path = ws_scheme + '://' + window.location.host + "/staff_chat/" + todays_staff_chat_room_id + "/"; // development
} else if (ws_scheme == "wss"){
	staff_ws_path = ws_scheme + '://' + window.location.host + ":8001/staff_chat/" + todays_staff_chat_room_id + "/"; // production
} else {
	staff_ws_path = "not working"
}

// console.log("Staff WS Path", staff_ws_path)

let staff_chat_socket = null

	function getStaffSocket() {

	if (getStaffSocket.server && getStaffSocket.server.readyState < 2) {
		console.log("reusing the socket connection [state = " + getStaffSocket.server.readyState + "]: " + getStaffSocket.server.url);
		return Promise.resolve(getStaffSocket.server);
		}

		return new Promise(function (resolve, reject) {

		getStaffSocket.server = new WebSocket(staff_ws_path);

	    getStaffSocket.server.onopen = function () {
	      console.log("Staff Chat socket connection is opened [state = " + getStaffSocket.server.readyState + "]: " + getStaffSocket.server.url);
	      staff_chat_socket=getStaffSocket.server;
	      resolve(getStaffSocket.server);
	      join_todays_chat()
	    };

	    getStaffSocket.server.onerror = function (err) {
	      console.error("Staff Chat socket connection error : ", err);
	      // populate_websocket_error_modal("Staff Chat socket connection error : ", err, "getStaffSocket")
	      reject(err);
	    };

	    getStaffSocket.server.onclose = function (err) {
	      console.error("Registration socket onclose : ", err);
	      // populate_websocket_error_modal("Staff Chat socket connection closed : ", err, "getStaffSocket")
	      staff_chat_socket=null;
	      reject(err);
	    };	

	    getStaffSocket.server.onmessage = function(message) {
        let server_data = JSON.parse(message.data);
          	try {
			  process_incoming_messages(server_data);
			} catch (error) {
			  console.error(error);
			}
        
      };


	  });
	}

	function process_incoming_messages(server_data){
		displayStaffChatroomLoadingSpinner(server_data.display_progress_bar);

		if (server_data.error) {
			console.error(server_data.error + ": " + server_data.message);
			showStaffClientErrorModal(server_data.message);
			return;
		}

		if (server_data.join) {
			// console.log("Joining Staff Chat " + server_data.join);
			getStaffRoomChatMessages(staff_chat_socket);
		}

		// Handle getting a message
		if (server_data.msg_type == 0) {
			// console.log("Staff DATA",server_data)
			appendStaffChatMessage(server_data, true, true);

		let all_unread_counts = JSON.parse(server_data.staff_msg_counts)
		// console.log("New Message", all_unread_counts, typeof(all_unread_counts))
		let data_counts = all_unread_counts.all_staff_counts
		// console.log("data_counts", data_counts, typeof(data_counts))
		let index = data_counts.findIndex(function (user) {
				let this_user_id = parseInt(user_id.textContent);
				return user.userID === this_user_id;
			});
		// console.log("Index", index)
		let user_new_count = data_counts[index].staff_unread_count;
		// console.log("Staff user_new_count line 94", user_new_count)
		adjust_staff_count_button(user_new_count)

		}

		// Handle getting the connected_user count
		if (server_data.msg_type == 1) {
			// console.log("STAFF", server_data['connected_user_count'])
			setStaffConnectedUsersCount(server_data['connected_user_count'], server_data['in_room'])
		}
		// new payload of messages coming in from backend
		if(server_data.messages_payload){
			handleStaffMessagesPayload(server_data.messages, server_data.new_page_number, server_data.unread_counts)
		}


	}//end process_incoming_messages

	function join_todays_chat(){
		// console.log("Joining today's chat")
		staff_chat_socket.send(JSON.stringify({
			"command": "join_staff",
			"room": todays_staff_chat_room_id
		}));
	}

	getStaffSocket();


function close_websocket_error(){
	console.log("Closing the Websocket Error Modal")
}

function take_action(){
	// console.log("Taking Action")
	let action_to_take = document.getElementById('action_to_take');
	if(action_to_take.value == "getStaffSocket"){
		getStaffSocket();
		getStatusSocket();
	}

	let close_websocket_error_btn = document.getElementById('close_websocket_error');
	close_websocket_error_btn.click()

}

function populate_websocket_error_modal(message, error, socket_name){
	// console.log("Populate Modal");
	let ws_error_title = document.getElementById('ws_error_title');
	ws_error_title.innerHTML = message;
	let ws_error_description = document.getElementById('ws_error_description');
	ws_error_description.innerHTML = error;
	let ws_error_action = document.getElementById('ws_error_action')
	ws_error_action.innerHTML = "You will need to reconnect to the Websocket.";
	let action_to_take = document.getElementById('action_to_take');
	action_to_take.value = socket_name;
	let websocket_error_button = document.getElementById('websocket_error_button');
	websocket_error_button.click();
}

function displayStaffChatroomLoadingSpinner(isDisplayed){
	// console.log("displayStaffChatroomLoadingSpinner", isDisplayed)
	var spinner = document.getElementById("id_staff_chatroom_loading_spinner")
	if(isDisplayed){
		spinner.style.display = "block"
	}
	else{
		spinner.style.display = "none"
	}
}

function showStaffClientErrorModal(message){
	// console.log("showClientErrorModal")
	document.getElementById("id_client_error_modal_body").innerHTML = message
	document.getElementById("staff_chat_error_button").click()
}

function close_staff_chat_error(){
	console.log("Closing the Staff Chat Error Modal")
}

function getStaffRoomChatMessages(staff_chat_socket){
	// console.log("getStaffRoomChatMessages")
	var pageNumber = document.getElementById("id_staff_page_number").innerHTML
	if(pageNumber != "-1"){
		setStaffPageNumber("-1") // Do not allow any other queries while one is in progress
		staff_chat_socket.send(JSON.stringify({
			"command": "get_room_chat_messages",
			"room_id": todays_staff_chat_room_id,
			"page_number": pageNumber,
		}));
	}
}

/*
	Get the next page of chat messages when scrolls to bottom
*/
document.getElementById("id_staff_chat_log").addEventListener("scroll", function(e){
	// console.log("Scrolling Log");
	var chatLog = document.getElementById("id_staff_chat_log")
	chatLog.addEventListener("scroll", function(e){
		if ((Math.abs(chatLog.scrollTop) + 2) >= (chatLog.scrollHeight - chatLog.offsetHeight)) {
			getStaffRoomChatMessages(staff_chat_socket)
		}
	});
})

function setStaffPageNumber(pageNumber){
	document.getElementById("id_staff_page_number").innerHTML = pageNumber
}


function ajax_staff_reset(){
	let url = "/sessions/ajax_staff_reset_count/"
	// console.log(url);
	    $.ajax({
	  type: 'GET',
	  url: url,
	  data: {"user_id": parseInt(user_id.textContent)},
	  success: function (response) {
	    if(response["valid"]){
	      // console.log(response) 
	      adjust_staff_count_button(response["unread_staff_count"])               
	    }
	  },
	  error: function (response) {
	      console.log(response)
	  }
	})
}



function adjust_staff_count_button(count){
	let new_staff_chat_messages =document.getElementById('new_staff_chat_messages');
	
	let staff_chat_btn_show = document.getElementById('staff_chat_btn_show')

	let staff_chat_btn = document.getElementById('staff_chat_btn');

	if(staff_chat_btn){ 
	  if(count == 0){
	  	staff_chat_btn.classList.remove('sidebar_link_notification');
	  	staff_chat_btn.classList.add('sidebar_btn');
	  	new_staff_chat_messages.innerHTML = count;

	  } else {
	  	

	  	let classlist_chat_div = staff_chat_btn_show.classList;
	  	let opened = classlist_chat_div.value.search('d-none');
	  	// console.log("opened", opened)
	  	if (opened != -1){
	  		new_staff_chat_messages.innerHTML = count;
	  		staff_chat_btn.classList.add('sidebar_link_notification');
	  		staff_chat_btn.classList.remove('sidebar_btn');
	  		play_notification_sound()
	  	}
	    

	  }
	} else{
	  // console.log("Else", inner_staff_chat_div)
	}
}

function setStaffConnectedUsersCount(count, in_room){
	let the_number_element = document.getElementById("id_staff_chat_connected_users");
	the_number_element.innerHTML = count;
	// console.log("IN ROOM", in_room, typeof(in_room))
	let in_room_users = JSON.parse(in_room).in_room;
	// console.log("in_room_users", in_room_users, typeof(in_room_users))
	let ul_element = document.getElementById('staff_in_room');
	ul_element.innerHTML = "";
	if(ul_element){
		for(let item of in_room_users){
			let li_person = document.createElement('li');
			li_person.innerHTML = item.username + " in " + item.room;
			ul_element.appendChild(li_person);
		}
	}
	
}


function handleStaffMessagesPayload(messages, new_page_number, unread_counts){
	// console.log("handleMessagesPayload unread_counts",)
	if(messages != null && messages != "undefined" && messages != "None"){
		setStaffPageNumber(new_page_number)
		messages.forEach(function(message){
			// console.log("Message", message)
			appendStaffChatMessage(message, true, false)
		})
	}
	else{
		setStaffPaginationExhausted() // no more messages
	}

	
	let all_unread_counts = JSON.parse(unread_counts)
	// console.log("handleMessagesPayload", all_unread_counts, typeof(all_unread_counts))
	let data_counts = all_unread_counts.all_staff_counts
	// console.error("Here", data_counts)
	let index = data_counts.findIndex(function (user) {
			// console.log("User in function", user)
			// console.log("This user id", user_id.textContent)
			let this_user_id = parseInt(user_id.textContent);
			return user.userID === this_user_id;
		});
	// console.log("Index", index)
	let user_new_count = data_counts[index].staff_unread_count;
	// console.log("user_new_count", user_new_count)
	adjust_staff_count_button(user_new_count)
}


function appendStaffChatMessage(data, maintainPosition, isNewMessage){
	// console.log('appendStaffChatMessage', data, maintainPosition, isNewMessage)
	let message = data['message']
	let msg_id = data['msg_id']
	let uName = data['username']
	let user_id_chat = data['user_id']
	let timestamp = data['natural_timestamp']
	let date_time = data['date_time']
	let meeting_room = data['meeting_room_name']
	let meeting_room_id_msg =data['meeting_room_id']
	let  msg = message + '\n';
	let  username = uName + ": "
	createStaffChatMessageElement(msg, msg_id, username, user_id_chat, timestamp, date_time, meeting_room, meeting_room_id_msg, maintainPosition, isNewMessage)
}


function createStaffChatMessageElement(message, msg_id, username, user_id_chat, timestamp, date_time,  meeting_room, meeting_room_id_msg, maintainPosition, isNewMessage){
	// console.log('createStaffChatMessageElement')
	var chatLog = document.getElementById('id_staff_chat_log')

	var newMessageDiv = document.createElement("div")
	newMessageDiv.classList.add("message_container")
	var top_div = document.createElement("div")
	top_div.classList.add("top_div")
	var message_div = document.createElement("div")
	message_div.classList.add("message_div")
	var msg_p = document.createElement("p")
	msg_p.innerHTML = message
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

	let message_in_room = document.createElement('div');
	message_in_room.classList.add('in_room');
	message_in_room.innerHTML = "In: " + meeting_room
	newMessageDiv.appendChild(message_in_room)
	newMessageDiv.appendChild(message_div)


	if(isNewMessage){
		if(user_id_chat != user_id){

			// let staff_add_one = document.getElementById('staff_add_one')
			// staff_add_one.click()
		}
		
		chatLog.insertBefore(newMessageDiv, chatLog.firstChild)
	}
	else{
		chatLog.appendChild(newMessageDiv)
	}

	if(!maintainPosition){
		chatLog.scrollTop = chatLog.scrollHeight
	}        
}

function setStaffPaginationExhausted(){
	setStaffPageNumber("-1")
}


document.getElementById('staff_chat-message-input').onkeyup = function(e) {
	if (e.keyCode === 13 && e.shiftKey) {  // enter + return
		// Handled automatically by textarea
		// console.log("e.keyCode === 13 && e.shiftKey", e)
	}
	else if(e.keyCode === 13 && !e.shiftKey){ // enter + !return
		document.getElementById('staff_chat-message-submit').click();
		// console.log("e.keyCode === 13 && !e.shiftKey", e)
	}
};

document.getElementById('staff_chat-message-submit').onclick = function(e) {
	// console.log("Clicking send staff message", staff_chat_socket)
	// console.log("todays_staff_chat_room_id", todays_staff_chat_room_id)
	// console.log("room_name", room_name.textContent)
	// console.log("room_id", room_id.textContent)
	let room_name_jitsi = room_name.textContent.replaceAll('"',"")
	// console.log("room_name_jitsi", room_name_jitsi)

	const staffmessageInputDom = document.getElementById('staff_chat-message-input');
	const staffmessage = staffmessageInputDom.value;
	staff_chat_socket.send(JSON.stringify({
		"command": "send",
		"message": staffmessage,
		"room_id": todays_staff_chat_room_id,
		"meeting_room": room_name_jitsi,
		"meeting_room_id": room_id.textContent,

	}));
	staffmessageInputDom.value = '';
};