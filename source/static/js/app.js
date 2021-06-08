$(document).ready(function(){

  var socket = io.connect('http://127.0.0.1:5000/');

  socket.on('message', function(msg){
      $("#cstat").html(msg);
      console.log("Received packet!");
  });

  $("#weather").on('click', function(){

    var country = document.getElementById("countryList").value;
    var city = document.getElementById("city_input").value;

    socket.emit('updateWeather', country, city, function(){
        console.log("Weather Update-Request has been sent");
      });
    });

  /*  $("#next").on('click', function(){
      socket.emit('nextTrack', function(){console.log("Next Track");});
    });

    $("#trackbutt").on('click', function(){
      socket.emit('trackTest', function(){console.log("Track Test");});
    });

    $("#pause").on('click', function(){
      socket.emit('pauseTrack', function(){console.log("Pause Track");});
    });

    $("#previous").on('click', function(){
      socket.emit('previousTrack', function(){console.log("Previous Track");});
    });

    $("#resume").on('click', function(){
      socket.emit('resumeTrack', function(){console.log("Resume Track");});
    }); */

    socket.on('updateTable', function(data){
        var json_data = JSON.parse(data);
        //$('#country').html(json_data.sys.country);
        $('#city').html(json_data.name);
        $('#humidity').html(json_data.main.humidity+"%");
        $('#temp').html(json_data.main.temp);
        //$('#weathertype').html(json_data.weather[0].main);
        //$('#windspeed').html(json_data.wind.speed);

    });


    socket.on('updateEmail', function(payload){
        console.log("Email Update");
        var json_payload = JSON.parse(payload);
        //console.log(json_payload);
        var index = 1;

        while(index != 6)
        {
          // convert the index to a string for string formating
          var strindex = index.toString();
          var subject = '#sub' + strindex;
          var snippet = '#snip' + strindex;
          var date = '#date' + strindex;
          var accessName = "email" + strindex;

          $(subject).html(json_payload[accessName]["subject"]);
          $(snippet).html(json_payload[accessName]["snippet"]);
          $(date).html(json_payload[accessName]["date"]);

          index++;
        }
    });

    socket.on('updateSpotify', function(payload){
      console.log("SpotifyUpdate");
      var json_payload = JSON.parse(payload);
      console.log(json_payload["img"])

      $('#artist').html(json_payload["artist"])
      $('#track').html(json_payload["track"])
      $('#img').attr('src', json_payload["img"]);
  });

  /*  $("#shutdown").on('click', function(){

      socket.emit('shutdown', function(){
        console.log("Shut Down!");
      });

    });*/



});
