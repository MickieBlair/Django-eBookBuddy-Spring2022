console.log("Loading WS Reading Session JS");


let status_ws_path;

if (ws_scheme == "ws"){
	status_ws_path = ws_scheme + '://' + window.location.host + "/status/"; // development
} else if (ws_scheme == "wss"){
	status_ws_path = ws_scheme + '://' + window.location.host + ":8001/status/"; // production
} else {
	status_ws_path = "not working"
}

console.log("status_ws_path", status_ws_path)

let status_socket = null

	function getStatusSocket() {

	if (getStatusSocket.server && getStatusSocket.server.readyState < 2) {
		console.log("reusing the socket connection [state = " + getStatusSocket.server.readyState + "]: " + getStatusSocket.server.url);
		return Promise.resolve(getStatusSocket.server);
		}

		return new Promise(function (resolve, reject) {

		getStatusSocket.server = new WebSocket(status_ws_path);

	    getStatusSocket.server.onopen = function () {
	      console.log("Status socket connection is opened [state = " + getStatusSocket.server.readyState + "]: " + getStatusSocket.server.url);
	      status_socket=getStatusSocket.server;
	      resolve(getStatusSocket.server);
	      connect_to_status()
	    };

	    getStatusSocket.server.onerror = function (err) {
	      console.error("Status socket connection error : ", err);
	      // populate_websocket_error_modal("Staff Chat socket connection error : ", err, "getStatusSocket")
	      reject(err);
	    };

	    getStatusSocket.server.onclose = function (err) {
	      console.error("Status socket onclose : ", err);
	      // populate_websocket_error_modal("Staff Chat socket connection closed : ", err, "getStatusSocket")
	      status_socket=null;
	      reject(err);
	    };	

	    getStatusSocket.server.onmessage = function(message) {
        let server_data = JSON.parse(message.data);
          	try {
			  status_process_incoming_messages(server_data);
			} catch (error) {
			  console.error(error);
			}
        
      };


	  });
	}

function process_icons(this_user, room_name){
	// console.log('room_name', room_name)
	let ws_online_circle = document.getElementById('ws_online_' + this_user['user_id'])
	let jitsi_online_circle = document.getElementById('jitsi_online_' + this_user['user_id'])
	let online_jitsi = this_user['online_jitsi']
	let online_ws = this_user['online_ws']
	let status_icon = document.getElementById("status_icon_" + this_user['user_id']);
	let manual_user_location = document.getElementById('manual_user_location_' + this_user['user_id'])
	if(status_icon){
		// if(online_jitsi && online_ws){
		// 	status_icon.classList.remove('user_offline');
		// 	status_icon.classList.remove('user_limbo');
		// 	status_icon.classList.add('user_online');
		// 	if(ws_online_circle){
		// 		ws_online_circle.classList.remove('user_offline');
		// 		ws_online_circle.classList.add('user_online');
		// 	}
		// 	if(jitsi_online_circle){
		// 		jitsi_online_circle.classList.remove('user_offline');
		// 		jitsi_online_circle.classList.add('user_online');
		// 	}
		// 	// manual_user_location.innerHTML = room_name
		// } else 
		if(online_jitsi || online_ws){
			status_icon.classList.remove('user_offline');
			// status_icon.classList.add('user_limbo');
			status_icon.classList.add('user_online');
			// if(ws_online_circle){						
			// 	if(online_ws){
			// 		ws_online_circle.classList.remove('user_offline');
			// 		ws_online_circle.classList.add('user_online');	
			// 		// manual_user_location.innerHTML = "WS - " + room_name					
			// 	}else{
			// 		ws_online_circle.classList.add('user_offline');
			// 		ws_online_circle.classList.remove('user_online');
			// 		// manual_user_location.innerHTML = "WS - Offline"
			// 	}
				
			// }
			// if(jitsi_online_circle){
			// 	if(online_jitsi){
			// 		jitsi_online_circle.classList.remove('user_offline');
			// 		jitsi_online_circle.classList.add('user_online');	
			// 		// manual_user_location.innerHTML = "J - " + room_name					
			// 	}else{
			// 		jitsi_online_circle.classList.add('user_offline');
			// 		jitsi_online_circle.classList.remove('user_online');
			// 		// manual_user_location.innerHTML = "J - Offline"
			// 	}
			// }

			if(online_jitsi || online_ws){	
				
				let room_name_string = room_name
				if(online_jitsi && online_ws){
					room_name_string = room_name_string;
				}

				else if(online_ws && !online_jitsi){
					room_name_string = room_name_string;
					// room_name_string = room_name_string + " WS Only"
				}
				else if(!online_ws && online_jitsi){
					room_name_string = room_name_string
					// room_name_string = room_name_string + " Jitsi Only";
				}
				manual_user_location.innerHTML = room_name_string
			} else{
				manual_user_location.innerHTML = "Offline"
				
			}
		} else{
			status_icon.classList.add('user_offline');
			status_icon.classList.remove('user_limbo');
			status_icon.classList.remove('user_online');
			
			if(ws_online_circle){
				ws_online_circle.classList.add('user_offline');
				ws_online_circle.classList.remove('user_online');
			}
			if(jitsi_online_circle){
				jitsi_online_circle.classList.add('user_offline');
				jitsi_online_circle.classList.remove('user_online');
			}

			manual_user_location.innerHTML = "Offline";


		}
		let online_match_icon = document.getElementById('online_match_icon_' + this_user['user_id']);
		// console.log(online_jitsi, online_ws)
		if(online_jitsi || online_ws){	
			
			
			online_match_icon.classList.remove('d-none');

		} else{
			
			online_match_icon.classList.add('d-none');
		}
		
	} else{
		let online_match_icon = document.getElementById('online_match_icon_' + this_user['user_id'])

		if(online_jitsi || online_ws){	
			if(online_match_icon){		
				online_match_icon.classList.remove('d-none');
			}
			let room_name_string = room_name;
			if(online_jitsi && online_ws){
				room_name_string = room_name_string;
			}

			else if(online_ws && !online_jitsi){
				room_name_string = room_name_string;
				// room_name_string = room_name_string + " WS Only";
			}
			else if(!online_ws && online_jitsi){
				room_name_string = room_name_string;
				// room_name_string = room_name_string + " Jitsi Only";
			}
			manual_user_location.innerHTML = room_name_string;
		} else{
			if(online_match_icon){
				online_match_icon.classList.add('d-none');
			}
			manual_user_location.innerHTML = "Offline";
		}

	}
}

getStatusSocket();

function status_process_incoming_messages(server_data){
		// console.log("Status process_incoming_messages : ", server_data);
		// manual_room_count-1
		// room_ws_participants_1
		// ws_participant_1
		// socket_status_{{part.id}}
		// status_icon_71
		// manual_user_location_74
		

		if(server_data.msg_type == "temp_match_redirect"){
			// console.log("temp_match_redirect: ", server_data);
			let redirect = server_data.redirect
			let user_to_redirect_temp_match = redirect.user_to_redirect.id
			if(redirect.user_to_redirect.id == parseInt(user_id.textContent)){
				// console.log("This is me")
				let link_to_click = create_link_to_click(redirect.to_room.slug, redirect.to_room.name)
				// console.log("link_to_click", link_to_click)
				link_to_click.click();
			} else{
				// console.log("not me")
			}      
        }

		if(server_data.msg_type == "manual_redirects"){
            let manual_redirects = JSON.parse(server_data['manual_redirects']).manual_redirects
            for(let item of manual_redirects) {
            	// console.log("redirect", item)
            	if (item.auto_send){
            		if(item.user_to_redirect_id == parseInt(user_id.textContent)){
                 	let link_to_click = create_link_to_click(item.to_room_slug, item.room_name)
                    link_to_click.click();
                  } 
              	}         
              }

             if(room_view == "Staff View"){
             	display_all_redirects(manual_redirects, server_data.not_auto_send_count)
             }
        }

        if(server_data.msg_type == "notify_all"){
			// console.log("notify_all: ", server_data);
			displayToAll(server_data);	     
        }

        if(server_data.msg_type == "session_stats"){
        	if(room_view == "Staff View"){
        		// console.log("Status process_incoming_messages : ", server_data);
        		let stats = JSON.parse(server_data.stats);
           		let unmatched_student_count = stats['unmatched_students'];
        		let pending_student_count = document.getElementById('pending_student_count');
        		pending_student_count.innerHTML = unmatched_student_count;

        		let unmatched_reader_count = stats['unmatched_readers'];
        		let available_reader_count = document.getElementById('available_reader_count');
        		available_reader_count.innerHTML = unmatched_reader_count;

        		let match_statuses = stats.match_statuses
        		// console.log("MATCH STATUSES", match_statuses)
        		process_match_statuses(match_statuses)

        	}

        }

		if (server_data.msg_type == "help_requests") {
			// console.log("Status process_incoming_messages : ", server_data);
			if(room_view == "Staff View"){
				let help_count = JSON.parse(server_data.help_count)
        		let help_requests = JSON.parse(server_data.all_help_requests).help_requests

        		display_help_requests(help_requests, help_count)  
			}
		}

		if (server_data.msg_type == "member_joining") {
			user_data = JSON.parse(server_data.status);
			let this_user = user_data.session_status;
			let pvt_chat_status = document.getElementById('msg_online_status-' + this_user['user_id']);
			if(pvt_chat_status){
				let new_option_string = this_user['username'] + ": " + this_user['full_name'] + " - ONLINE";
				pvt_chat_status.innerHTML = new_option_string
			}

			if(room_view == "Staff View"){
				
				// console.log("user_data", user_data);
				// let this_user = user_data.session_status;
				// console.log("this_user", this_user['user_id']);
				let div_for_room = document.getElementById("room_ws_participants_" + server_data.room_id);
				let part_div = document.getElementById("ws_participant_" + this_user['user_id']);
				process_icons(this_user, server_data.room_name)
				let ws_count = document.getElementById("ws_room_count_" + server_data.room_id);
				ws_count.innerHTML = user_data.room_ws_count;
				let jitsi_count = document.getElementById("jitsi_room_count_" + server_data.room_id);
				jitsi_count.innerHTML = user_data.jitsi_ws_count;
				let manual_room_string = "WS:(" + user_data.room_ws_count +") - J(" + user_data.jitsi_ws_count +")"
				let manual_room_count_div = document.getElementById('manual_room_count-' + server_data.room_id)
				if(manual_room_count_div){
					// manual_room_count_div.innerHTML = manual_room_string
					manual_room_count_div.innerHTML = user_data.room_ws_count
				}
				if(part_div){
					part_div.remove();
					let new_div = document.createElement('div');
					new_div.innerHTML = this_user.username;
					new_div.setAttribute('class', 'socket_status_' + this_user['user_id']);
					new_div.setAttribute('id', 'ws_participant_' + this_user['user_id']);
					div_for_room.appendChild(new_div);
				} else{
					let new_div = document.createElement('div');
					new_div.innerHTML = this_user.username;
					new_div.setAttribute('class', 'socket_status_' + this_user['user_id']);
					new_div.setAttribute('id', 'ws_participant_' + this_user['user_id']);
					div_for_room.appendChild(new_div);
				}			

			}

			let total_users = document.getElementById('total_users');
			if(total_users){
				total_users.innerHTML = server_data.ws_count
			}

			
			
				
		}

		if (server_data.msg_type == "member_left") {
			user_data = JSON.parse(server_data.status);
			let this_user = user_data.session_status;
			let pvt_chat_status = document.getElementById('msg_online_status-' + this_user['user_id']);
			
			if(pvt_chat_status){
				let new_option_string = this_user['username'] + ": " + this_user['full_name'] + " - OFFLINE";
				pvt_chat_status.innerHTML = new_option_string
			}


			if(room_view == "Staff View"){
				
				// console.log("user_data", user_data);
				// let this_user = user_data.session_status;
				let div_for_room = document.getElementById("room_ws_participants_" + server_data.room_id);
				let part_div = document.getElementById("ws_participant_" + this_user['user_id']);
				process_icons(this_user, server_data.room_name)
				// let status_icon = document.getElementById("status_icon_" + this_user['user_id']);
				// if(status_icon){
				// 	status_icon.classList.add('user_offline');
				// 	status_icon.classList.remove('user_online');
				// }
				// console.log("part_div", part_div);
				let ws_count = document.getElementById("ws_room_count_" + server_data.room_id);
				ws_count.innerHTML = user_data.room_ws_count;
				let jitsi_count = document.getElementById("jitsi_room_count_" + server_data.room_id);
				jitsi_count.innerHTML = user_data.jitsi_ws_count;
				let manual_room_string = "WS:(" + user_data.room_ws_count +") - J(" + user_data.jitsi_ws_count +")"
				let manual_room_count_div = document.getElementById('manual_room_count-' + server_data.room_id)
				if(manual_room_count_div){
					manual_room_count_div.innerHTML = manual_room_string
				}
				if(part_div){
					part_div.remove();
				}

			}	

			let total_users = document.getElementById('total_users');
			if(total_users){
				total_users.innerHTML = server_data.ws_count	
			}						
		}

		if(server_data.msg_type == "new_private_message"){
        	
        	
        	if(server_data.to_user == parseInt(user_id.textContent)){
        		// console.log("\n\n\n******A New private_messages for this user", server_data)
        		// console.log("privateChatSocket", privateChatSocket)
        		// console.log("current_room_id", current_room_id)
        		if(privateChatSocket){
        			if(privateChatSocket.readyState==1){
        				// console.log("Open and connected1")
        				clearPrivateChatLog()
        				getJustTheMessages(current_room_id)        				
        			}
        			
        		} else{
        			// console.log("Not Connected1")
        		}
        		
	                //console.log("new_private_message", status_data)
	                // play_notification_sound()
	                let unread_count_e = document.querySelectorAll('.new_private_messages-' + user_id.textContent)
	                // console.log("unread_count_e", unread_count_e)
	                for(let item of unread_count_e){
	                    item.innerHTML = server_data.total_unread
	                }

	                let btn_private = document.getElementById('private_messages_button');
	                if(btn_private){	                	
	                	if(btn_private.classList.contains("sidebar_btn")  || btn_private.classList.contains("sidebar_link_notification")){
                			// console.log("Staff")
                			if(server_data.total_unread == 0){
	                		// console.log("Count is zero");
	                		btn_private.classList.remove('sidebar_link_notification')
	                		btn_private.classList.add('sidebar_btn')
			                } else {
			                	// console.log("Still some left1");
			                	btn_private.classList.remove('sidebar_btn')
	                			btn_private.classList.add('sidebar_link_notification')
	                			play_notification_sound();
			                }
                		}else{
                			// console.log("Not Staff")  
                			if(server_data.total_unread == 0){
	                		// console.log("Count is zero");
	                		btn_private.classList.remove('btn_custom_messages_notification')
	                		btn_private.classList.add('btn_custom_messages')
			                } else {
			                	// console.log("Still some left1");
			                	btn_private.classList.remove('btn_custom_messages')
	                			btn_private.classList.add('btn_custom_messages_notification')
	                			play_notification_sound();
			                }
                		}	                	
	                }

	                

	                let no_unread_private = document.getElementById('no_unread_' + user_id.textContent)

	                if(no_unread_private){
	                    if(server_data.total_unread == 0){
	                        no_unread_private.style.display = "block"
	                    }else{
	                        no_unread_private.style.display = "none"
	                    }
	                }  

	                let no_read_private = document.getElementById('no_read_' + user_id.textContent)

	                if(no_read_private){
	                    if(server_data.total_unread == 0){
	                        no_read_private.style.display = "block"
	                    }else{
	                        no_read_private.style.display = "none"
	                    }
	                } 

	                get_private_rooms_for_user();
        	} else {
        		// console.log("\n\n\n******Not This User A New private_messages", server_data)
        	}
        }

        if(server_data.msg_type == "private_room_list"){
        	if(server_data.for_user == parseInt(user_id.textContent)){
        		if(privateChatSocket){
        			if(privateChatSocket.readyState==1){
        				// console.log("Open and connected2")
        				
        			}
        			
        		} else{
        			// console.log("Not Connected2")
        		}
        		let previous_rows = document.querySelectorAll('.private_room_row')
                for(let item of previous_rows){
                    item.remove()
                }
                // console.log("WS READING SESSION private_room server_data", server_data)
                let with_new_private_room_table = document.getElementById('new_tbody_private_rooms_for-' + user_id.textContent)
                let no_private_room_table = document.getElementById('no_new_tbody_private_rooms_for-' + user_id.textContent)
                // console.log("with_new_private_room_table", with_new_private_room_table)
                // console.log("no_private_room_table", no_private_room_table)
                let private_room_list = JSON.parse(server_data.pvt_rooms).private_rooms

                let unread_count_e = document.querySelectorAll('.new_private_messages-' + user_id.textContent)
                // console.log("unread_count_e", unread_count_e)
                for(let item of unread_count_e){
                    item.innerHTML = server_data.unread_count_for_user
                }
                let btn_private = document.getElementById('private_messages_button');
                if(btn_private){
                	if(btn_private.classList.contains("sidebar_btn")  || btn_private.classList.contains("sidebar_link_notification")){
                			// console.log("Staff")
                			if(server_data.unread_count_for_user == 0){
	                		// console.log("Count is zero");
	                		btn_private.classList.remove('sidebar_link_notification')
	                		btn_private.classList.add('sidebar_btn')
			                } else {
			                	// console.log("Still some left2");
			                	btn_private.classList.remove('sidebar_btn')
	                			btn_private.classList.add('sidebar_link_notification')
	                			// play_notification_sound();
			                }
                		} else{
                			// console.log("Not Staff")  
                			if(server_data.unread_count_for_user == 0){
	                		// console.log("Count is zero");
	                		btn_private.classList.remove('btn_custom_messages_notification')
	                		btn_private.classList.add('btn_custom_messages')
			                } else {
			                	// console.log("Still some left2");
			                	btn_private.classList.remove('btn_custom_messages')
	                			btn_private.classList.add('btn_custom_messages_notification')
	                			// play_notification_sound();
			                }

                		}

                }

                let no_unread_private = document.getElementById('no_unread_' + user_id.textContent)
                let no_read_private = document.getElementById('no_read_' + user_id.textContent)
                 if(no_unread_private){
	                    if(server_data.unread_count_for_user == 0){
	                        no_unread_private.classList.remove('d-none');
	                    }else{
	                        no_unread_private.classList.add('d-none');
	                    }
	                } 
	                
	                if(no_read_private){
	                	// console.log("server_data.pvt_room_count", server_data.pvt_room_count)
	                    if(server_data.pvt_room_count > 0){
	                        no_read_private.classList.add('d-none');
	                    }else{
	                        no_read_private.classList.remove('d-none');
	                    }
	                } 

	                for(let item of private_room_list){
                    // console.log(item)
                    let viewing_user = ""
                    let other_user = ""
                    let unread_count_for_self = ""
                    let other_user_name = ""


                    if(parseInt(user_id.textContent) == item.user1_id){
                        viewing_user = item.user1_id
                        other_user = item.user2_id
                        unread_count_for_self = item.user1_unread
                        other_user_name = item.user2_name

                    }else{
                        viewing_user = item.user2_id
                        other_user = item.user1_id
                        other_user_name = item.user1_name
                        unread_count_for_self = item.user2_unread
                    }

                    new_row = create_private_room_row(item, viewing_user, other_user_name, unread_count_for_self)
                    
                     if(unread_count_for_self == 0){
                        no_private_room_table.appendChild(new_row)
                    } else{
                        with_new_private_room_table.appendChild(new_row)
                    }
	               
                    
                    
                }


        	}else{
        		// console.log("Not this user")
        	}

        }


        if(server_data.msg_type == "unread_private_messages"){
        	
        	if(server_data.for_user == parseInt(user_id.textContent)){
        		if(privateChatSocket){
        			if(privateChatSocket.readyState==1){
        				// console.log("Open and connected3")        				
        			}
        			
        		} else{
        			// console.log("Not Connected3")
        		}
        		// console.log("\n\n\n******unread_private_messages", server_data)

        		// if(server_data.unread_by_room_total != 0){
        		// 	console.log("Here Sound")
        		// 	play_notification_sound()
        		// } 

                let unread_count_e = document.querySelectorAll('.new_private_messages-' + user_id.textContent)
                // console.log("unread_count_e", unread_count_e)
                for(let item of unread_count_e){
                    item.innerHTML = server_data.unread_by_room_total
                }

                let no_unread_private = document.getElementById('no_unread_' + user_id.textContent)
                let no_read_private = document.getElementById('no_read_' + user_id.textContent)
                 if(no_unread_private){
	                    if(server_data.unread_count_for_user == 0){
	                        no_unread_private.classList.remove('d-none');
	                    }else{
	                        no_unread_private.classList.add('d-none');

	                    }
	                } 
	                
	                if(no_read_private){
	                	// console.log("server_data.pvt_room_count", server_data.pvt_room_count)
	                    if(server_data.pvt_room_count > 0){
	                        no_read_private.classList.add('d-none');
	                    }else{
	                        no_read_private.classList.remove('d-none');
	                    }
	                } 

	            let btn_private = document.getElementById('private_messages_button');
                if(btn_private){
                	if(btn_private.classList.contains("sidebar_btn") || btn_private.classList.contains("sidebar_link_notification")){
                			// console.log("Staff")
                			if(server_data.unread_by_room_total == 0){
	                		// console.log("Count is zero");
	                		btn_private.classList.remove('sidebar_link_notification')
	                		btn_private.classList.add('sidebar_btn')
			                } else {
			                	// console.log("Still some left2");
			                	btn_private.classList.remove('sidebar_btn')
	                			btn_private.classList.add('sidebar_link_notification')
	                			// play_notification_sound();
			                }
                		} else{
                			// console.log("Not Staff")  
                			if(server_data.unread_by_room_total == 0){
	                		// console.log("Count is zero");
	                		btn_private.classList.remove('btn_custom_messages_notification');
	                		btn_private.classList.add('btn_custom_messages');
			                } else {
			                	// console.log("Still some left 3");
			                	btn_private.classList.remove('btn_custom_messages');
	                			btn_private.classList.add('btn_custom_messages_notification');
	                			// play_notification_sound();
			                }

                		}

                }

        	}
        }		


	}//end process_incoming_messages





function display_message(notify_message){
    const display_to_all_btn = document.getElementById('display_to_all_btn')
    const notificationModalLabel = document.getElementById('notificationModalLabel')
    const sender_of = document.getElementById('sender')
    const this_msg = document.getElementById('this_msg')
    notificationModalLabel.innerHTML = "Session Notification"
    sender_of.innerHTML = notify_message.from
    this_msg.innerHTML = notify_message.message   
    display_to_all_btn.click();
}

function displayToAll(notify_group){
    // console.log("In display to all", notify_group)
    // console.log("room_view", room_view)
    if(notify_group.to_group == "All"){
        display_message(notify_group)        
    } else{
    	let group_notify = notify_group.to_group

    	// console.log("group_notify", group_notify)
        if(room_view == notify_group.to_group){
            display_message(notify_group) 
        }
    }   
}

function create_link_to_click(room_slug, room_name){
	let link = document.createElement('a')
	link.setAttribute('href', '/sessions/room/' + room_slug +'/')
	link.innerHTML = room_name;
	return link
}

function adjust_existing_row(item){
	// console.log("Match Status Just Adjust", item)
	let student_location_div_id = "id-match-user-location_" + item.match_status_id + "-" + item.student_id;
	let buddy_location_div_id = "id-match-user-location_" + item.match_status_id + "-" + item.buddy_id;
	let student_location_text = document.getElementById(student_location_div_id);
	let buddy_location_text = document.getElementById(buddy_location_div_id);

	if(item.display_student_location){
		if (item.student_online){
			if(student_location_text){
				student_location_text.innerHTML = "";
				let stu_link = create_link_to_click(item.student_room_slug, item.student_room_name);
				student_location_text.appendChild(stu_link);
				}				
			
		} else{
			if(student_location_text){
				student_location_text.innerHTML = "";
			}
		}
		
	} else{
		if(student_location_text){
			student_location_text.innerHTML = "";
		}
	}

	if(item.display_buddy_location){
		if (item.buddy_online){
			if(buddy_location_text){
				buddy_location_text.innerHTML = "";
				let reader_link = create_link_to_click(item.reader_room_slug, item.reader_room_name);
				buddy_location_text.appendChild(reader_link);
			}
	
		} else{;
			if(buddy_location_text){
				buddy_location_text.innerHTML = "";
			}
		}
		
	} else{
		if(buddy_location_text){
			buddy_location_text.innerHTML = "";
		}
	}

	let complete_icon = document.getElementById('match_status_complete_'+ item.match_status_id);
	if(complete_icon){
		if(item.complete){			
			complete_icon.setAttribute('class', 'fas fa-check match_check_green');
		} else{
			complete_icon.setAttribute('class', 'fas fa-times match_times_red');
		}
	}

	let match_status_info = document.getElementById('match_status_info_'+ item.match_status_id);
	let status_room_location = document.getElementById('in_room_status_' + item.match_status_id);
	if(match_status_info){
		match_status_info.innerHTML = item.status;
		if(item.status == "In Room"){
			status_room_location.innerHTML = "";
			let complete_room_link = create_link_to_click(item.status_room_slug, item.status_room_name);
			status_room_location.appendChild(complete_room_link);

		}else{
			status_room_location.innerHTML = "";
		}
	}

	let row = document.getElementById('match_status_row-' + item.match_status_id);

	let table_id = "tbody_" + item.session_id + '-' +item.session_slot + "-all";
	let table = document.getElementById(table_id);
	if(item.complete){		
		table.append(row);
	} 
}

function process_match_statuses(match_statuses){
	// console.log("\n\n\nThis is the match_statuses", match_statuses)
	for(let item of match_statuses){
		// console.log("\n\n\nThis is the Item", item)
		if(item.match_type == "Scheduled"){
			// console.log("Scheduled")
			adjust_existing_row(item);
		} else{
			// console.log("Temporary")
			let existing_row = document.getElementById('match_status_row-' + item.match_status_id)
			// existing_row.remove()
			// existing_row = document.getElementById('match_status_row-' + item.match_status_id)
			if(existing_row){
				// console.log("Row exists")
				adjust_existing_row(item)
			}else{
				// console.log("Match Status Create the TEMP ROW", item)
				let table_id = "tbody_" + item.session_id + '-' +item.session_slot + "-all"
				let table_to_add_to = document.getElementById(table_id)
				// console.log(table_id)
				let new_row = document.createElement('tr')
				new_row.setAttribute('class', 'all_match_row')
				new_row.setAttribute('id', 'match_status_row-'+item.match_status_id)
				table_to_add_to.append(new_row)

				let type_td=document.createElement('td')
				type_td.innerHTML = item.get_type

				let student_td = document.createElement('td')
				student_td.setAttribute('class', 'ps-1')
				let inner_student_div = document.createElement('div')
				inner_student_div.setAttribute('class', 'd-inline-flex w-100')
				inner_student_div.setAttribute('id', 'online_' + item.student_id)
				let student_profile_div = document.createElement('div')
				student_profile_div.setAttribute('type', 'button')
				student_profile_div.setAttribute('class', 'd-grid justify-content-center align-items-center px-1')
				student_profile_div.setAttribute('data-bs-toggle', 'modal')
				student_profile_div.setAttribute('data-bs-target', '#userprofileModal')
				let func_student = "show_only_profile('member_profile_" + item.student_id +"')"
				student_profile_div.setAttribute('onclick', func_student)
				inner_student_div.appendChild(student_profile_div)
				let stu_icon = document.createElement('i')
				let stu_icon_class = "fas fa-user profile_icon user_offline status_icon_" + item.student_id

				if(item.student_online){
					 stu_icon_class = "fas fa-user profile_icon user_online status_icon_" + item.student_id
				}else{
					 stu_icon_class = "fas fa-user profile_icon user_offline status_icon_" + item.student_id
				}
				
				stu_icon.setAttribute('class', stu_icon_class)
				student_profile_div.appendChild(stu_icon)

				let student_div_2 =document.createElement('div')
				let student_username_div = document.createElement('div')
				student_username_div.setAttribute('class', "username_small_bold")
				let s_text_username = document.createElement('text')				
				s_text_username.innerHTML = item.student_username + ":"
				student_username_div.appendChild(s_text_username)

				let s_text_location = document.createElement('text')
				s_text_location.setAttribute('class', "the_member_location-" +  item.student_id)
				let student_location_div_id = "id-match-user-location_" + item.match_status_id + "-" + item.student_id
				s_text_location.setAttribute('id', student_location_div_id)

				student_username_div.appendChild(s_text_location)
				let stu_link = create_link_to_click(item.student_room_slug, item.student_room_name);
				s_text_location.appendChild(stu_link)


				let student_name_div = document.createElement('div')
				student_name_div.setAttribute('class', "full_name")
				student_name_div.innerHTML = item.student_full_name


				student_div_2.appendChild(student_username_div)
				student_div_2.appendChild(student_name_div)
				inner_student_div.appendChild(student_div_2)
				student_td.appendChild(inner_student_div)



				let volunteer_td = document.createElement('td')
				volunteer_td.setAttribute('class', 'ps-1')
				let inner_volunteer_div = document.createElement('div')
				inner_volunteer_div.setAttribute('class', 'd-inline-flex w-100')
				inner_volunteer_div.setAttribute('id', 'online_' + item.buddy_id)
				let volunteer_profile_div = document.createElement('div')
				volunteer_profile_div.setAttribute('type', 'button')
				volunteer_profile_div.setAttribute('class', 'd-grid justify-content-center align-items-center px-1')
				volunteer_profile_div.setAttribute('data-bs-toggle', 'modal')
				volunteer_profile_div.setAttribute('data-bs-target', '#userprofileModal')
				let func_volunteer = "show_only_profile('member_profile_" + item.buddy_id +"')"
				volunteer_profile_div.setAttribute('onclick', func_volunteer)
				inner_volunteer_div.appendChild(volunteer_profile_div)
				let vol_icon = document.createElement('i')

				let vol_icon_class = "fas fa-user profile_icon user_offline status_icon_" + item.buddy_id
				if(item.buddy_online){
					vol_icon_class = "fas fa-user profile_icon user_online status_icon_" + item.buddy_id
				}else{
					vol_icon_class = "fas fa-user profile_icon user_offline status_icon_" + item.buddy_id
				}
				
				
				vol_icon.setAttribute('class', vol_icon_class)
				volunteer_profile_div.appendChild(vol_icon)

				let volunteer_div_2 =document.createElement('div')
				let volunteer_username_div = document.createElement('div')
				volunteer_username_div.setAttribute('class', "username_small_bold")
				let v_text_username = document.createElement('text')				
				v_text_username.innerHTML = item.reader_username + ":"
				volunteer_username_div.appendChild(v_text_username)

				let v_text_location = document.createElement('text')
				v_text_location.setAttribute('class', "the_member_location-" +  item.buddy_id)
				let buddy_location_div_id = "id-match-user-location_" + item.match_status_id + "-" + item.buddy_id
				v_text_location.setAttribute('id', buddy_location_div_id)

				volunteer_username_div.appendChild(v_text_location);
				let reader_link = create_link_to_click(item.reader_room_slug, item.reader_room_name);
				v_text_location.appendChild(reader_link)


				let volunteer_name_div = document.createElement('div')
				volunteer_name_div.setAttribute('class', "full_name")
				volunteer_name_div.innerHTML = item.reader_full_name


				volunteer_div_2.appendChild(volunteer_username_div)
				volunteer_div_2.appendChild(volunteer_name_div)
				inner_volunteer_div.appendChild(volunteer_div_2)
				volunteer_td.appendChild(inner_volunteer_div)


				let complete_td = document.createElement('td')
				complete_td.setAttribute('class', "text-center")
				let complete_icon = document.createElement('i')
				if(item.complete){					
					complete_icon.setAttribute('class', "fas fa-check match_check_green")		
				} else {
					complete_icon.setAttribute('class', "fas fa-check match_check_green")
				}
				complete_icon.setAttribute('id', "match_status_complete_" + item.match_status_id)
				complete_td.appendChild(complete_icon)

				let status_td = document.createElement('td');
				status_td.setAttribute('class', "text-center pe-3");
				let status_div = document.createElement('div');
				status_div.setAttribute('id', "match_status_info_" +item.match_status_id)
				status_div.innerHTML = item.status
				status_td.appendChild(status_div)

				

				let room_status_div = document.createElement('div');
				room_status_div.setAttribute('id', "in_room_status_" +item.match_status_id)
				if(item.status == "In Room"){
					let complete_room_link = create_link_to_click(item.status_room_slug, item.status_room_name);
					room_status_div.appendChild(complete_room_link);

				}else{
					room_status_div.innerHTML = "";
				}
				status_td.appendChild(room_status_div)

				new_row.appendChild(type_td)
				new_row.appendChild(student_td)
				new_row.appendChild(volunteer_td)
				new_row.appendChild(complete_td)
				new_row.appendChild(status_td)
			}
		}
	}
}



function connect_to_status(){
	status_socket.send(JSON.stringify({
		"command": "join",
		"user_id": user_id.textContent,
		"room_id": room_id.textContent,			
	}));
}

function display_all_redirects(all_redirects, redirect_count){
	// console.log("DISPLAY All Redirect", all_redirects, redirect_count)

	let current_redirect_rows = document.querySelectorAll('.redirect_row')
		  			// console.log("current_redirect_rows", current_redirect_rows)   
    for (item of current_redirect_rows) {
        // console.log("item.remove", item)  
        item.remove()
    }

    let no_pending_redirects_div = document.getElementById('no_pending_redirects')
    let redirect_modal_button = document.getElementById('redirect_modal_button');
    let number_pending_redirects = document.getElementById('number_pending_redirects')
    number_pending_redirects.innerHTML = redirect_count;

    if(no_pending_redirects_div){
    	if(redirect_count == 0){
    		// console.log("Count == 0")
    		no_pending_redirects_div.classList.remove('d-none');
    		redirect_modal_button.classList.remove('sidebar_link_notification');
    		redirect_modal_button.classList.add('sidebar_btn');
        }else{
        	// console.log("Count not 0")
    		no_pending_redirects_div.classList.add('d-none');
    		redirect_modal_button.classList.add('sidebar_link_notification');
    		redirect_modal_button.classList.remove('sidebar_btn');
    		play_notification_sound();

  		}
    } 


  		let table_body_all_redirects = document.getElementById('table_body_all_redirects')
  		// console.log("table_body_all_redirects", table_body_all_redirects)  

	  	if(table_body_all_redirects){
	    	for(let item of all_redirects){
	    		if(!item.auto_send){
	    			// console.log("let item of all_redirects", item)  
		      		let row = create_redirect_row(item)
		      		// console.log("row", row) 
		      		table_body_all_redirects.appendChild(row)
	    		}
	      		
	    	};
	  	};
}

function create_redirect_row(item){
		// console.log("create_redirect_row", item)
	  	// console.log(item.redirect_id)
	  	// console.log(item.user_to_redirect_id)
	  	// console.log(item.user_to_redirect_name)
	  	// console.log(item.to_room_id)
	  	// console.log(item.to_room_name)
	  	// console.log(item.redirect_url)

	  	let new_redirect_row = document.createElement('tr');
	  	new_redirect_row.classList.add('redirect_row');

	  	let td_student_name = document.createElement('td');
	  	td_student_name.innerHTML = item.user_to_redirect_name;
	 	new_redirect_row.appendChild(td_student_name);

	  	let td_send_to = document.createElement('td');
		td_send_to.classList.add('text-center');
		td_send_to.innerHTML = item.to_room_name;
		new_redirect_row.appendChild(td_send_to);

		let td_cancel_btn = document.createElement('td');
	  	td_cancel_btn.classList.add('text-center');
	  	let cancel_redirect = document.createElement('btn')
	  	cancel_redirect.innerHTML = "Cancel"
	  	cancel_redirect.setAttribute("class", "btn btn-sm btn-danger");
	  	let id_for_c_btn = "cancel_redirect_id-" + item.redirect_id;
	  	cancel_redirect.setAttribute("id", id_for_c_btn);
	  	cancel_redirect.setAttribute("value", item.redirect_id);
	  	cancel_redirect.setAttribute("onclick", "cancel_json_redirect(this)");
	  	td_cancel_btn.appendChild(cancel_redirect);
	  	new_redirect_row.appendChild(td_cancel_btn);


	  	let td_redirect_btn = document.createElement('td');
	  	td_redirect_btn.classList.add('text-center');

	  	let send_redirect = document.createElement('btn')
	  	send_redirect.innerHTML = "Redirect"
	  	send_redirect.setAttribute("class", "btn btn-sm btn-success individual_redirect");
	  	let id_for_btn = "redirect_id-" + item.redirect_id;
	  	send_redirect.setAttribute("id", id_for_btn);
	  	send_redirect.setAttribute("value", item.redirect_id);
	  	send_redirect.setAttribute("onclick", "send_json_redirect(this)");

	  	td_redirect_btn.appendChild(send_redirect);
	  	new_redirect_row.appendChild(td_redirect_btn);
	 
	  	new_redirect_row.appendChild(td_redirect_btn);

	  	return new_redirect_row;
	};


function send_redirect_data(existing_room_value, from_user_value, users_to_add){
	status_socket.send(JSON.stringify({
		"command": "create_redirects",
		"to_room": existing_room_value,
		"created_by": from_user_value,	
		"users_to_send": users_to_add,		
	}));

}

function cancel_json_redirect(element){
    status_socket.send(JSON.stringify({
    "command": "delete_redirect",
    "user_id": parseInt(user_id.textContent),
    "redirect_id": parseInt(element.getAttribute('value')),
    }));
}

function send_json_redirect(element){
status_socket.send(JSON.stringify({
        "command": "redirect_autosend",
        "user_id": parseInt(user_id.textContent),
        "redirect_id": parseInt(element.getAttribute('value')),
    }));
}

function send_all_redirects(){
    // console.log("send_all_redirects")
    var individual_buttons = document.querySelectorAll(".individual_redirect");
    // console.log("individual_buttons", individual_buttons)
    for(let item of individual_buttons){
        let individual_redirect_id = item.getAttribute('value');

        status_socket.send(JSON.stringify({
        "command": "redirect_autosend",
        "user_id": parseInt(user_id.textContent),
        "redirect_id": individual_redirect_id,
        }));
    }
    close_redirects_btn.click()
}



function display_help_requests(help_requests, help_count){
	// console.log("DISPLAY Help Requests", help_requests, help_count)
	// if(help_requests && help_count){
	// 	console.log("DISPLAY Help Requests", help_requests, help_count)
		const help_count_display = document.getElementById('request_count')
		if (help_count_display){
	        help_count_display.innerHTML = help_count
	    }

	    let table_body = document.getElementById('table_body_all_help_requests')
	    // console.log("table_body", table_body)
	    let no_helps = document.getElementById('no_help_requests');
	    // console.log("no_helps", no_helps)
	    let view_help_request_button =document.getElementById('view_help_request_button')
	    if (help_count == 0){
	    	// console.log('help count 0', help_count)
	    	if(no_helps){
	    		no_helps.classList.add('d-none');
	    	}
	    	
	    	view_help_request_button.classList.remove('sidebar_link_notification');
	    	view_help_request_button.classList.add('sidebar_btn');

	    } else{
	    	// console.log('help count else', help_count)
	    	if(no_helps){
	    		no_helps.classList.remove('d-none');
	    	}
	    	view_help_request_button.classList.add('sidebar_link_notification');
	    	view_help_request_button.classList.remove('sidebar_btn');
	    	play_notification_sound()
	    }

	    // let requests = help_requests.help_requests;

		if(table_body){
			let current_helps =  document.querySelectorAll(".help_row");
			for (item of current_helps) {
				item.remove()
			}


			for (let item of help_requests) {
				// console.log(item)
				new_row = new_help_row(item);            
				table_body.appendChild(new_row);
			}
		}else{
			// console.log("No Table Body")
		}
		if (help_count == 0){
			no_helps.classList.remove('d-none');
		} else{
			no_helps.classList.add('d-none')
		}

}

function new_help_row(help_item){
    // console.log("help_item", help_item)
    let row = document.createElement('tr');
    row.setAttribute('id', 'help_row_' + help_item.request_id);
    row.classList.add('help_row');

    let from_td = document.createElement('td');
    from_td.setAttribute('class', 'ps-2 py-0');
    from_td.innerHTML = help_item.full_name;

    let message_td = document.createElement('td');
    let time_div = document.createElement('div');
    time_div.setAttribute('class', 'fw-bold text-decoration-underline');
    message_td.appendChild(time_div);
    time_div.innerHTML = help_item.created;

    let message_div = document.createElement('div');
    message_td.appendChild(message_div);
    message_div.innerHTML = help_item.user_message;

    let room_td = document.createElement('td');
    room_td.setAttribute('class', 'py-0');
    let link_div = document.createElement('div');
    room_td.appendChild(link_div);
    let link = create_link_to_click(help_item.from_room_slug, help_item.from_room)

	link.setAttribute('onclick', 'mark_as_done(' + help_item.request_id +', ' + false +')');
    link_div.appendChild(link);

    room_td.appendChild(link_div);

    let done_td = document.createElement('td');
    let button = document.createElement('button');
    button.setAttribute('value', help_item.request_id);
    button.setAttribute('class', 'btn btn-success btn-sm individual_help_request');
    button.setAttribute('onclick', 'mark_as_done(' + help_item.request_id +', ' + true +')');
    button.innerHTML = "Mark Done";
    done_td.appendChild(button);    

    row.appendChild(from_td);
    row.appendChild(message_td);
    row.appendChild(room_td);
    row.appendChild(done_td);

    return row
}


function create_new_match(sent_by, session, student_id, reader_id){
	status_socket.send(JSON.stringify({
          "command": "create_temp_match",
          "sent_by": sent_by,
          "session_id": session,
          "student_id": student_id,
          "reader_id": reader_id,
          
      }));

}

function websocket_send_notify_message(msg_to_all, for_group, from){
	status_socket.send(JSON.stringify({
          "command": "notify_all",
          "message": msg_to_all,
          "to_group": for_group,
          "user_id": from,
      }));
}



function send_message_to_reading_consumer(private_to_room, msg_to, msg_from, p_msg){
	status_socket.send(JSON.stringify({
		"command": "create_send_private_message",
		"room_id": private_to_room,
		"to_user": msg_to,
		"from_user": msg_from,
		"pvt_message": p_msg,
	}));
}


function get_private_rooms_for_user(){
	// console.log("Get private rooms for user")
	status_socket.send(JSON.stringify({
			"command": "get_private_rooms",
			"user_id": user_id.textContent,
		}));
}
          

function create_private_room_row(private_room_item, viewing_user, other_user, unread_count_for_self){
	// console.log("Creating ROW", private_room_item, viewing_user, other_user, unread_count_for_self)
	// console.log("THIS USER", viewing_user)
    let row = document.createElement('tr');
    row.setAttribute('id', 'private_room_row_' + private_room_item.private_room_id);
    row.classList.add('private_room_row');

    let from_td = document.createElement('td');
    from_td.setAttribute('class', 'ps-2');
    from_td.innerHTML = other_user;

    let count_td = document.createElement('td');
    count_td.setAttribute('class', '');
    if(unread_count_for_self !=0){
        count_td.innerHTML = unread_count_for_self;
    }else{
        count_td.innerHTML = private_room_item.total;
    }
    

    let read_td = document.createElement('td');
    read_td.setAttribute('class', 'ps-2');
    // let read_messages_btn = document.createElement('button')    
    // read_messages_btn.innerHTML = "View";
    // read_messages_btn.setAttribute('class', 'btn btn-sm btn-success m-1');
    // read_messages_btn.setAttribute('type', 'button');
    // read_messages_btn.setAttribute('value', parseInt(private_room_item.private_room_id));
    // read_messages_btn.setAttribute('onclick',"get_pvt_room_messages(this.value)");

    let modal_button =  document.createElement('button'); 
    modal_button.innerHTML = "View";
    modal_button.setAttribute('class', 'btn btn-sm btn-success m-1 private_chat_buttons');
    modal_button.setAttribute('type', 'button');
    modal_button.setAttribute('data-bs-toggle', 'modal');
    modal_button.setAttribute('data-bs-target', '#read_private_msg_Modal');
    modal_button.setAttribute('data-bs-dismiss', 'modal');
    modal_button.setAttribute('id', "modal_button_room_" + private_room_item.private_room_id);
    modal_button.setAttribute('value', parseInt(private_room_item.private_room_id));
    modal_button.setAttribute('onclick',"get_pvt_room_messages(this.value)");

    // read_td.appendChild(read_messages_btn);
    read_td.appendChild(modal_button);


   

    row.appendChild(from_td);
    row.appendChild(count_td);
    row.appendChild(read_td);
    // console.log("NEW ROW", row)
    return row

}


function get_pvt_room_messages(private_room_id){
	// console.log("Getting Private Messages for room", private_room_id)
	setupWebSocket(private_room_id)
	status_socket.send(JSON.stringify({
	  "command": "get_private_messages",
	  "user_id": user_id.textContent,
	  "for_private_room": private_room_id,
	  "action":"open",
	  })); 
}



function close_view_private_messages(){
		let close_view_private_message_btn = document.getElementById('close_view_private_message');
		let pvt_room_current_id = close_view_private_message_btn.value
		// console.log("close_view_private_messages", pvt_room_current_id)

		privateChatSocket.send(JSON.stringify({
			"command": "leave",
			"room": pvt_room_current_id
		}));

		closeWebSocket()

        get_private_rooms_for_user()

        status_socket.send(JSON.stringify({
		  "command": "get_private_messages",
		  "user_id": user_id.textContent,
		  "for_private_room": pvt_room_current_id,
		  "action":"close",
		  })); 

	}
