console.log("Loading File Upload Scripts");
const error_url = document.getElementById('error_url').textContent
// console.log("error_url", error_url)


const uploadForm = document.getElementById('volunteer_video_form');
const email = document.getElementById('id_email');
const input_file = document.getElementById('id_videofile');
const progress_bar = document.getElementById('progress');
const top_div = document.getElementById('top_progress');
const spinner = document.getElementById('loading_spinner');
const title = document.getElementById('title');
const percent_div = document.getElementById('percent_div');
const percent = document.getElementById('percent');
const fieldWrapper_email = document.getElementById('fieldWrapper_email');
const fieldWrapper_videofile = document.getElementById('fieldWrapper_videofile');
const submit_btn_div = document.getElementById('submit_btn_div');
const email_input = document.getElementById('id_email');


$("#volunteer_video_form").submit(function(e){
    e.preventDefault();
    $form = $(this)

    var formData = new FormData(this);
    const media_data = input_file.files[0];
    let max_size = 1000000000
    let size = media_data.size
    console.log("Size", size)
    if(media_data != null && email.value !="" && size <= max_size){
        console.log(media_data);
        progress_bar.classList.remove("not-visible");
        fieldWrapper_email.classList.add('d-none');
        fieldWrapper_videofile.classList.add('d-none');
        submit_btn_div.classList.add('d-none');

        $.ajax({
        type: 'POST',
        url:'/registration/volunteer/video/upload/',
        data: formData,
        dataType: 'json',
        beforeSend: function(){

        },
        xhr:function(){
            const xhr = new window.XMLHttpRequest();
            xhr.upload.addEventListener('progress', e=>{
                if(e.lengthComputable){
                    const percentProgress = (e.loaded/e.total)*100;
                    //console.log(percentProgress);
                    top_div.classList.remove('d-none')
                    percent_div.classList.remove('d-none')
                    percent.innerHTML = Math.round(percentProgress) + " %";
                    progress_bar.innerHTML = `<div class="progress-bar progress-bar-striped bg-success progress-bar-animated" 
            role="progressbar" style="width: ${percentProgress}%" aria-valuenow="${percentProgress}" aria-valuemin="0" 
            aria-valuemax="100"></div>`
            if(percentProgress == 100){
                //console.log("Remove bar");
                progress_bar.classList.add('d-none');
                percent_div.classList.add('d-none');
                spinner.classList.remove('d-none');
                title.innerHTML = `<div>The file is now being attached to your registration application.</div><div>Please be patient.</div>`

                }
            }
            });
            return xhr
        },
        success: function(response){
            console.log("success",response);           
            progress_bar.classList.add('not-visible')
            window.location.replace(response['next_url']);
        },
        error: function(err){
            console.log(err);
             window.location.replace(response['next_url']);
        },
        cache: false,
        contentType: false,
        processData: false,
    });
    } else {
        let videofile_errors = document.getElementById('videofile_errors')
        if(media_data == null){
           // console.log("Video File required")        
        videofile_errors.innerHTML = `<div class="alert alert-danger mb-1">
                                    <strong id="{{field.name}}_error_text">This field is required</strong>
                                </div>` 
        }

        if (email.value == ""){
            // console.log("email required")
            let email_errors = document.getElementById('email_errors')
            email_errors.innerHTML = `<div class="alert alert-danger mb-1">
                                        <strong id="{{field.name}}_error_text">This field is required</strong>
                                    </div>` 
        } 

        if(size > max_size){

        videofile_errors.innerHTML = `<div class="alert alert-danger mb-1">
                                    <strong id="{{field.name}}_error_text">The file is too large.  Max size is 1000MB </strong>
                                </div>` 

        }      
        
    }

    
});

function clear_input_errors(input_name){
    let error_div = document.getElementById(input_name +"_errors");
    if(error_div){
        error_div.innerHTML = "";
    }   
}

function email_video_blur(ev, object) {
    if(ev == "blur"){
        var email = object.value;
        check_vol_video_email(email)
    } 
}

function check_vol_video_email(email){
    payload = {
        'email': email,
        'type_reg': "Volunteer Video",
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
        notifyModalButton.click();
        email_input.value = "";
    }
}

