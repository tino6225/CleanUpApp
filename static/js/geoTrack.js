 /**
 * raw javascript and jquery ajax for geoTrack html page.
 */
 
watchID = null;
function resetWatch(){
    if (watchID != null){
        navigator.geolocation.clearWatch(watchID);
    }
    watchID = null;
}

window.onload = function(){
    var startButton = document.querySelector("button.btn.btn-info");
    var endButton = document.querySelector("button.btn.btn-danger");
    document.getElementById("btn2").disabled = true;
    document.getElementById("btn3").disabled = true;
    document.getElementById("btn4").disabled = true;

    startButton.onclick = function(eventObj){
        eventObj.preventDefault();
        if (startButton.innerHTML === "Start Geolocation"){
            document.getElementById("btn2").disabled = false;
            watchID = navigator.geolocation.watchPosition(function(position){
                var newLat = position.coords.latitude;
                var newLong = position.coords.longitude;
                document.getElementById("idCoordinates").value = newLat + " , " + newLong;
                document.getElementById("btn1").disabled = true;
            });
        }
    };

    endButton.onclick = function(eventObj){
        eventObj.preventDefault();
        if (endButton.innerHTML === "End Tracking"){
            document.getElementById("idCoordinates").disabled = true;
            resetWatch();
            document.getElementById("btn2").disabled = true;
            document.getElementById("btn3").disabled = false;
        }
    };
};



//Grab form input and transform to JSON before submitting to app for processing
//jQuery $method.val() sets or returns the value of form fields
$('#btn3').on('click',function(event) {
    event.preventDefault();
    var coordLength = document.getElementById('idCoordinates').value.length;
    var commentsLength = document.getElementById('idComments').value.length;
    var zipLength = document.getElementById('idZipcode').value.length;

    if (coordLength === 0 || commentsLength === 0 || zipLength === 0) {
        //msg = 'There is one or more empty input field. All fields are required to submit.';
        //$('#result').text(msg);
        alert('There is one or more empty input. All fields are required to Save');
    }
    else {
        var formData = {
            coordinates: $('#idCoordinates').val(),
            comments: $('#idComments').val(),
            zipCode: $('#idZipcode').val()};


        $.ajax({
                contentType: "application/json",
                dataType: 'json',
                type: 'POST',
                url: 'apiAddRecord',
                data: JSON.stringify(formData),
                success: function(data,status,jsonObject){
                    var jstring = JSON.stringify(jsonObject);
                    var srvResponse = JSON.parse(jstring);
                    $('#result').html(srvResponse.responseText);
                    document.getElementById("btn3").disabled = true;
                    document.getElementById("btn4").disabled = false;
                },
                error: function(data,status,error){
                    $('#result').html(data + error);

                }
        });
    } 
});
