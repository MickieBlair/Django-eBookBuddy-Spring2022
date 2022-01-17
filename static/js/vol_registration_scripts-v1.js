console.log("Loading Volunteer Registration Scripts");

//elements
const vol_reg_form = document.getElementById('volunteer_registration_form');
const additional_interests_options = document.getElementsByName("additional_interests");
const volunteer_other_areas_options = document.getElementsByName("volunteer_other_areas");
const device_type_options = document.getElementsByName("device_type");
const computer_options = document.getElementsByName("computer");
const social_media_source_options = document.getElementsByName("social_media_source");
const opportunity_source_options = document.getElementsByName("opportunity_source");
const previously_paired_options = document.getElementsByName("previously_paired");
const in_school_options = document.getElementsByName("in_school");
const returning_options = document.getElementsByName("volunteer_type");
const notifyModalButton= document.getElementById('notifyModalButton');
const convicted_options = document.getElementsByName("convicted");
const charges_pending_options = document.getElementsByName("charges_pending");
const refused_participation_options = document.getElementsByName("refused_participation");
const program_semester = document.getElementById("id_program_semester");
const dob_element = document.getElementById('id_dob');
const fieldWrapper_device_type = document.getElementById('fieldWrapper_device_type');
const fieldWrapper_computer = document.getElementById('fieldWrapper_computer');
const fieldWrapper_additional_interests = document.getElementById('fieldWrapper_additional_interests');
const fieldWrapper_volunteer_other_areas = document.getElementById('fieldWrapper_volunteer_other_areas');
const fieldWrapper_previously_paired = document.getElementById('fieldWrapper_previously_paired');
const fieldWrapper_student_name = document.getElementById('fieldWrapper_student_name');
const fieldWrapper_teamleader_name = document.getElementById('fieldWrapper_teamleader_name');
const fieldWrapper_returning_referred = document.getElementById('fieldWrapper_returning_referred');
const fieldWrapper_parent_name = document.getElementById('fieldWrapper_parent_name');
const fieldWrapper_parent_email = document.getElementById('fieldWrapper_parent_email');
const parent_name_input = document.getElementById('id_parent_name');
const parent_email_input = document.getElementById('id_parent_email');
const fieldWrapper_opportunity_source = document.getElementById('fieldWrapper_opportunity_source');
const fieldWrapper_social_media_source = document.getElementById('fieldWrapper_social_media_source');
const fieldWrapper_person_referral = document.getElementById('fieldWrapper_person_referral');
const fieldWrapper_web_source = document.getElementById('fieldWrapper_web_source');
const person_referral_input = document.getElementById('id_person_referral');
const web_source_input = document.getElementById('id_web_source');
const student_name_input = document.getElementById('id_student_name');
const teamleader_name_input = document.getElementById('id_teamleader_name');
const returning_referred_input = document.getElementById('id_returning_referred');
const fieldWrapper_current_education_level = document.getElementById('fieldWrapper_current_education_level');
const fieldWrapper_current_education_class = document.getElementById('fieldWrapper_current_education_class');
const fieldWrapper_current_school = document.getElementById('fieldWrapper_current_school');
const fieldWrapper_highest_education_level = document.getElementById('fieldWrapper_highest_education_level');
const highest_education_level = document.getElementById('id_highest_education_level');
const current_education_level = document.getElementById('id_current_education_level');
const current_education_class = document.getElementById('id_current_education_class');
const current_school_e = document.getElementById('id_current_school');
const chosen_start_date = document.getElementById('chosen_start');
const too_young = document.getElementById('too_young');
const volunteer_email = document.getElementById('volunteer_email');



//event listeners
window.addEventListener('load', (event) => {
  if(vol_reg_form){
	var semester_value = program_semester.options[program_semester.selectedIndex].value;	
	let dob_value = dob_element.value;
	if(dob_value){
		let person_age = get_age(dob_value);
		set_parental_info_divs(person_age);
	} else {
		let person_age = 99;
		set_parental_info_divs(person_age);
	}	
	
	let checked_in_school = document.querySelector('input[name="in_school"]:checked');
	if(checked_in_school){
		if(checked_in_school.value == "Yes"){
			set_education_divs("in_school");
			
		} else if(checked_in_school.value == "No"){
			set_education_divs("not_in_school");
		}
	} else{
		set_education_divs("display_none");		
	}	

	let computer_choice = document.querySelector('input[name="computer"]:checked');

	if(computer_choice){
		if(computer_choice.value == "Yes"){
			fieldWrapper_device_type.classList.remove('d-none');		
		} else{
			fieldWrapper_device_type.classList.add('d-none');			
		}

	} else {
		fieldWrapper_device_type.classList.add('d-none');		
	}

	let interest_other_choice = document.querySelector('input[name="volunteer_other_areas"]:checked');	

	if(interest_other_choice){
		if(interest_other_choice.value == "Yes"){
			fieldWrapper_additional_interests.classList.remove('d-none');		
		} else{
			fieldWrapper_additional_interests.classList.add('d-none');			
		}

	} else {
		fieldWrapper_additional_interests.classList.add('d-none');		
	}

	let checked_returning = document.querySelector('input[name="volunteer_type"]:checked');	

	if(checked_returning){

		if(checked_returning.value == "New"){
			set_volunteer_type_divs("new");
			set_hear_about_us_divs("new");
			
		} else if(checked_returning.value == "Returning"){
			set_volunteer_type_divs("returning");
			set_hear_about_us_divs("display_none");	
		}
	} else{
			set_volunteer_type_divs("display_none");
			set_hear_about_us_divs("display_none");		
	}	
  	
  }//end volunteer form
});//end on window load

for(let option of convicted_options){
	option.addEventListener('change', (event) => {
		let the_option = document.getElementById(event.target.id);
		let the_value = the_option.value;
		clear_input_errors('convicted_text');
	});
}

for(let option of charges_pending_options){
	option.addEventListener('change', (event) => {
		let the_option = document.getElementById(event.target.id);
		let the_value = the_option.value;
		clear_input_errors('charges_pending_text');
	});
}

for(let option of charges_pending_options){
	option.addEventListener('change', (event) => {
		let the_option = document.getElementById(event.target.id);
		let the_value = the_option.value;
		clear_input_errors('charges_pending_text');
	});
}

for(let option of refused_participation_options){
	option.addEventListener('change', (event) => {
		let the_option = document.getElementById(event.target.id);
		let the_value = the_option.value;
		clear_input_errors('refused_participation_text')
	});
}


for(let option of volunteer_other_areas_options){
	option.addEventListener('change', (event) => {
	  	if(event.target.value == "Yes"){
	  		fieldWrapper_additional_interests.classList.remove('d-none');	  	
	  	} else if (event.target.value == "No"){
	  		fieldWrapper_additional_interests.classList.add('d-none');	 
	    	for(let item of additional_interests_options){
	    		item.checked = false;
	    	}
	  }
	});
}

for(let option of computer_options){
	option.addEventListener('change', (event) => {	  	
	  	if(event.target.value == "Yes"){
	  		fieldWrapper_device_type.classList.remove('d-none');
		} else if (event.target.value == "No"){
	  		fieldWrapper_device_type.classList.add('d-none');	  
	    	for(let item of device_type_options){
	    		item.checked = false;
	    	}
	  }
	});
}

for(let option of opportunity_source_options){
	option.addEventListener('change', (event) => {
		let the_option = document.getElementById(event.target.id);
		let the_label = the_option.parentElement.textContent.trim();
		display_source_divs(the_label);
	});
}

for(let option of previously_paired_options){
	option.addEventListener('change', (event) => {
		
	  	if(event.target.value == "Yes"){
	  		fieldWrapper_student_name.classList.remove('d-none');
	  	} else if (event.target.value == "No"){
	  		fieldWrapper_student_name.classList.add('d-none');
	  		student_name_input.value="";
	  }
	});
}

for(let option of in_school_options){
	option.addEventListener('change', (event) => {
		if(event.target.value == "Yes"){
	  		set_education_divs("in_school");
	  	} else if (event.target.value == "No"){
	  		set_education_divs("not_in_school");
	  	}
	});
}

for(let option of returning_options){
	option.addEventListener('change', (event) => {
		if(event.target.value == "New"){
		  	set_volunteer_type_divs("new");
		  	set_hear_about_us_divs("new")	;
	  	} else if (event.target.value == "Returning"){
		  	set_volunteer_type_divs("returning");
		  	set_hear_about_us_divs("display_none");
		  }
	});
}

//functions

function get_age_at_start(dob_value, semester_start){
	console.log("Calculating age at semester_start")
	let dob_year = parseInt(dob_value.split("-")[0]);
	let dob_month = parseInt(dob_value.split("-")[1]) - 1;
	let dob_day = parseInt(dob_value.split("-")[2]);

	let start_year = parseInt(semester_start.split("-")[0]);
	let start_month = parseInt(semester_start.split("-")[1]) - 1;
	let start_day = parseInt(semester_start.split("-")[2]);
	var start_date = new Date(start_year, start_month, start_day); 

	var dob_date = new Date(dob_year, dob_month, dob_day);
	
	let year_age = 0;

	var diff_ms = start_date.getTime() - dob_date.getTime();
   var age_dt = new Date(diff_ms); 
  
   year_age = Math.abs(age_dt.getUTCFullYear() - 1970);
	return year_age;

}

function get_age(dob_value){
	console.log("Calculating age now")
	let dob_year = parseInt(dob_value.split("-")[0]);
	let dob_month = parseInt(dob_value.split("-")[1]) - 1;
	let dob_day = parseInt(dob_value.split("-")[2]);

	var dob_date = new Date(dob_year, dob_month, dob_day);
	
	let year_age = 0;

	var diff_ms = Date.now() - dob_date.getTime();
   var age_dt = new Date(diff_ms); 
  
   year_age = Math.abs(age_dt.getUTCFullYear() - 1970);
	
	return year_age;

}

function set_parental_info_divs(person_age){
	
	if(person_age < 18){
		fieldWrapper_parent_name.classList.remove('d-none');
		fieldWrapper_parent_email.classList.remove('d-none');

	} else {
		fieldWrapper_parent_name.classList.add('d-none');
		fieldWrapper_parent_email.classList.add('d-none');
		
		parent_name_input.value = "";
		parent_email_input.value= "";
	}
}

function findLabelForField(el) {
   var idVal = el.id;
   labels = document.getElementsByTagName('label');
   for( var i = 0; i < labels.length; i++ ) {
      if (labels[i].htmlFor == idVal)
           return labels[i];
   }
}

function set_hear_about_us_divs(display_divs){	
	let opportunity_choosen = document.querySelector('input[name="opportunity_source"]:checked');
	let social_media_choosen = document.querySelector('input[name="social_media_source"]:checked');

	if(display_divs == "display_none"){
		fieldWrapper_opportunity_source.classList.add('d-none');	
		fieldWrapper_social_media_source.classList.add('d-none');
		fieldWrapper_person_referral.classList.add('d-none');
		fieldWrapper_web_source.classList.add('d-none');
	 	for(let item of opportunity_source_options){
	 		item.checked = false;
	 	}

	 	for(let item of social_media_source_options){
	 		item.checked = false;
	 	} 

	 	web_source_input.value = "";

	 	person_referral_input.value = "";



	} else if(display_divs == "new"){
		fieldWrapper_opportunity_source.classList.remove('d-none');
		if (opportunity_choosen){
				let the_option = document.getElementById(opportunity_choosen.id);				
				let the_label = the_option.parentElement.textContent.trim();
				display_source_divs(the_label);
		} else {
			fieldWrapper_social_media_source.classList.add('d-none');
			fieldWrapper_person_referral.classList.add('d-none');
			fieldWrapper_web_source.classList.add('d-none');
		}
	}
}

function display_source_divs(display_divs){
	if(display_divs == "Social Media"){
		fieldWrapper_social_media_source.classList.remove('d-none');
		fieldWrapper_person_referral.classList.add('d-none');
		person_referral_input.value = "";
		fieldWrapper_web_source.classList.add('d-none');
		person_referral_input.value = "";
		web_source_input.value = "";
	} else if(display_divs == "Person"){
		fieldWrapper_social_media_source.classList.add('d-none');
		fieldWrapper_person_referral.classList.remove('d-none');
		fieldWrapper_web_source.classList.add('d-none');
		for(let item of social_media_source_options)
		{
			item.checked = false;
		}
		web_source_input.value = "";
	} else if(display_divs == "Web"){
		fieldWrapper_social_media_source.classList.add('d-none');
		fieldWrapper_person_referral.classList.add('d-none');
		fieldWrapper_web_source.classList.remove('d-none');		
		for(let item of social_media_source_options)
		{
			item.checked = false;
		}
		person_referral_input.value = "";
	} else{
		fieldWrapper_social_media_source.classList.add('d-none');
		fieldWrapper_person_referral.classList.add('d-none');
		fieldWrapper_web_source.classList.add('d-none');
		for(let item of social_media_source_options)
		{
			item.checked = false;
		}
		person_referral_input.value = "";
		web_source_input.value = "";
	}
}



function set_volunteer_type_divs(display_divs){	
	let selected_paired =  document.querySelector('input[name="previously_paired"]:checked');

	if(display_divs == "new"){
		fieldWrapper_previously_paired.classList.add('d-none');
		if(selected_paired){
			selected_paired.checked = false;
		}

		fieldWrapper_student_name.classList.add('d-none');
		student_name_input.value = "";

		fieldWrapper_teamleader_name.classList.add('d-none');
		teamleader_name_input.value = "";

		fieldWrapper_returning_referred.classList.add('d-none');
		returning_referred_input.value = "";			

	} else if(display_divs == "returning"){
		fieldWrapper_previously_paired.classList.remove('d-none');
		if(selected_paired){
			if(selected_paired.value == "Yes"){
				fieldWrapper_student_name.classList.remove('d-none');
			} else {
				fieldWrapper_student_name.classList.add('d-none');
				student_name_input.value = "";
			}
		} else{
			fieldWrapper_student_name.classList.add('d-none');
		}

		fieldWrapper_teamleader_name.classList.remove('d-none');
		fieldWrapper_returning_referred.classList.remove('d-none');

	} else if(display_divs =="display_none"){
		fieldWrapper_previously_paired.classList.add('d-none');
		if(selected_paired){
			selected_paired.checked = false
		}
		fieldWrapper_student_name.classList.add('d-none');
		student_name_input.value = "";

		fieldWrapper_teamleader_name.classList.add('d-none');
		teamleader_name_input.value = "";

		fieldWrapper_returning_referred.classList.add('d-none');
		returning_referred_input.value = "";	
	}
}

function set_education_divs(display_divs){
	let selected_highest = highest_education_level.options[highest_education_level.selectedIndex];	
	let selected_current = current_education_level.options[current_education_level.selectedIndex];	
	let selected_class = current_education_class.options[current_education_class.selectedIndex];
	

	if(display_divs == "in_school"){
		fieldWrapper_current_education_level.classList.remove('d-none');
		fieldWrapper_current_education_class.classList.remove('d-none');
		fieldWrapper_current_school.classList.remove('d-none');
		fieldWrapper_highest_education_level.classList.add('d-none');
		
		
		if(selected_highest){
			selected_highest.selected = false;
		}
		

	}else if(display_divs == "not_in_school"){
		fieldWrapper_current_education_level.classList.add('d-none');
		fieldWrapper_current_education_class.classList.add('d-none');
		fieldWrapper_current_school.classList.add('d-none');
		fieldWrapper_highest_education_level.classList.remove('d-none');
		
		if(selected_current){
			selected_current.selected = false;	
		}		
		
		if(selected_class){
			selected_class.selected = false;	
		}
		
		current_school_e.value = "";

	} else if(display_divs =="display_none"){
		fieldWrapper_current_education_level.classList.add('d-none');
		fieldWrapper_current_education_class.classList.add('d-none');
		fieldWrapper_current_school.classList.add('d-none');
		fieldWrapper_highest_education_level.classList.add('d-none');

		if(selected_highest){
			selected_highest.selected = false;
		}

		if(selected_current){
			selected_current.selected = false;
		}

		if(selected_class){
			selected_class.selected = false;
		}

		current_school_e.value = "";

	}
}

function age_notifications(person_age){
	console.log("Notify", person_age)
	if(notifyModalButton){
		let notifyModalLabel = document.getElementById('notifyModalLabel');
		notifyModalLabel.innerHTML = "Registration Notification";
	}

	

	if (person_age < 14){
		too_young.classList.remove('d-none');
		notifyModalButton.click();
	}
}

function program_start_date_variables(){
	var value = program_semester.options[program_semester.selectedIndex].value;
	var text = program_semester.options[program_semester.selectedIndex].text;
	let input_start_date = document.getElementById('program_' + value);
	
	if(chosen_start_date.value){
		chosen_start_date.value = input_start_date.value;
		if(dob_element){
			let dob = dob_element.value;
			if(dob){
				let person_age_at_start = get_age_at_start(dob, chosen_start_date.value);
	    		age_notifications(person_age_at_start); 
			}
		}
	}	
}

document.getElementById('id_program_semester').addEventListener('change', (event) => {
	program_start_date_variables();
});

function elog(ev, object) {
  	if(ev == "blur"){
  		var dob = object.value;
    	
    	let person_age;
    	let person_age_at_start;
    	let program_start_date = chosen_start_date.value;

    	if(dob){
    		person_age = get_age(dob);  		
    		set_parental_info_divs(person_age);
    		age_notifications(person_age);
    	}
    	
    	if (dob && program_start_date){
    		person_age_at_start = get_age_at_start(dob, program_start_date);
    		age_notifications(person_age_at_start);
    	}
    } 
}

function email_blur(ev, object) {
  	if(ev == "blur"){
  		var email = object.value;
  		if (email != ''){
  			check_vol_email(email)
  		}
    } 
}

function check_vol_email(email){
	payload = {
		'email': email,
		'type_reg': "Volunteer",
		'reg_lang': "en"
	}

    $.ajax({
      type: 'GET',
      url: "/registration/registration_email_check/",
      data: payload,
      success: function (response) {
        console.log("Success")
        console.log(response)
        if (!response['valid']){
        	email_notifications()
        }
      },
      error: function (response) {
        console.log("Fail")
          console.log(response)
      }
    });

}

function email_notifications(){
	console.log("Notify Email", )
	if(notifyModalButton){
		let notifyModalLabel = document.getElementById('notifyModalLabel');
		notifyModalLabel.innerHTML = "Registration Notification";

		volunteer_email.classList.remove('d-none');
		notifyModalButton.click();
	}
}

function close_notify_modal(){
	too_young.classList.add('d-none');
	volunteer_email.classList.add('d-none');
}



function clear_input_errors(input_name){
	let error_div = document.getElementById(input_name +"_errors");
	if(error_div){
		error_div.innerHTML = "";
	}	
}

function show_english(){
	all_eng_text = document.querySelectorAll('.eng_text');
	for(let item of all_eng_text){
		item.setAttribute('class', 'eng_text');
	}

	all_span_text = document.querySelectorAll('.span_text');
	for(let item of all_span_text){
		item.setAttribute('class', 'span_text d-none');
	}
}

function show_spanish(){
	all_span_text = document.querySelectorAll('.span_text');
	for(let item of all_span_text){
		item.setAttribute('class', 'span_text');
	}
	all_eng_text = document.querySelectorAll('.eng_text');
	for(let item of all_eng_text){
		item.setAttribute('class', 'eng_text d-none');
	}
}


function submit_vol_reg_form(){
	let vol_reg = document.getElementById('volunteer_registration_form');
	vol_reg.submit();
}
