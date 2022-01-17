console.log("Loading Volunteer Testing Scripts");

function clear_input_errors(input_name){
	let error_div = document.getElementById(input_name +"_errors");
	if(error_div){
		error_div.innerHTML = "";
	}	

	let email_input = document.getElementById('id_email');
	email_input.value="";
}