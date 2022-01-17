let max_upload_size = document.getElementById('max_upload_size').textContent
console.log("max_upload_size", max_upload_size)

let cropper;
// let imageFile;
// let base64ImageString;
// let cropX;
// let cropY;
// let cropW;
// let cropH;


/* return null if invalid or base64String if valid */
	function isImageSizeValid(image){
		console.log("max_upload_size", max_upload_size)
		// console.log(image)
		var startIndex = image.indexOf("base64,") + 7;
		var base64str = image.substr(startIndex);
		var decoded = atob(base64str);
		console.log("FileSize: " + decoded.length);
		if(decoded.length>= max_upload_size ){
			return null
		}
		return base64str
	}

	function cropImage(image, x, y, width, height){
		

	}

	// function cropImage(image, x, y, width, height){
	// 	base64ImageString = isImageSizeValid(image)

	// 	if(base64ImageString != null){
	// 		var requestData = {
	// 			"csrfmiddlewaretoken": "{{ csrf_token }}",
	// 			"image": base64ImageString,
	// 			"cropX": cropX,
	// 			"cropY": cropY,
	// 			"cropWidth": cropWidth,
	// 			"cropHeight": cropHeight
	// 		}
	// 		displayLoadingSpinner(true)
	// 		$.ajax({
	// 			type: 'POST',
	// 			dataType: "json",
	// 			url: "{% url 'account:crop_image' user_id=form.initial.id %}",
	// 			data: requestData,
	// 			timeout: 10000,
	// 			success: function(data) {
	// 				if(data.result == "success"){
	// 					document.getElementById("id_cancel").click()
	// 				}
	// 				else if(data.result == "error"){
	// 					alert(data.exception)
	// 					document.getElementById("id_cancel").click()
	// 				}
	// 			},
	// 			error: function(data) {
	// 				console.error("ERROR...", data)
	// 			},
	// 			complete: function(data){
	// 				displayLoadingSpinner(false)
	// 			}
	// 		});
	// 	}
	// 	else{
	// 		alert("Upload an image smaller than 10 MB");
	// 		document.getElementById("id_cancel").click()
	// 	}
	// }


function create_cropper(image, e, imageField){
	console.log("Creating Cropper")
	if (cropper){
		cropper.destroy()
	}
	cropper = new Cropper(imageField, {
					aspectRatio: 1/1,
					zoomable: false,
					// minContainerHeight: image_height,
					// minContainerWidth: image_width,
					// minCanvasHeight: image_height,
					// minCanvasWidth: image_width,
					crop(event) {
						// console.log("CROP START")
						// console.log("x: " + event.detail.x);
						// console.log("y: " + event.detail.y);
						// console.log("width: " + event.detail.width);
						// console.log("height: " + event.detail.height);				


						setImageCropProperties(
							image,
							event.detail.x,
							event.detail.y,
							event.detail.width,
							event.detail.height
						)
					},
				});

}


function readURL(input) {
		
        if (input.files && input.files[0]) {
            var reader = new FileReader();

            reader.onload = function (e) {
            	console.log("E.target", e.target)
               	var image = e.target.result
               	// console.log("Image", image, typeof(image))
            	var imageField = document.getElementById('id_profile_image_display')
            	imageField.src = image
            	create_cropper(image, e, imageField)				
            };
            reader.readAsDataURL(input.files[0]);
        }
    };


  function setImageCropProperties(image, x, y, width, height){ 
  	let input_X = document.getElementById('id_cropX')
  	let input_Y = document.getElementById('id_cropY')
  	let input_W = document.getElementById('id_cropW')
  	let input_H = document.getElementById('id_cropH')
  	let input_image_string = document.getElementById('id_image_string') 		

	let base64ImageString = isImageSizeValid(image)		

	if(base64ImageString != null){
		console.log("Good base64ImageString", )

		input_X.value = x
		input_Y.value = y
		input_W.value = width
		input_H.value = height
		input_image_string.value = base64ImageString


	}else{
		console.log("Bad base64ImageString", )
		alert("image too large")
	}	

  	


  	



  	

	// imageFile = image
	// cropX = x
	// cropY = y
	// cropW = width
	// cropH = height

	// console.log("setImageCropProperties", cropX, cropY, cropW, cropH)
	}

