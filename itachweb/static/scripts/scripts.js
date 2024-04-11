
$(window).on('load', function() {
  // call the api to get the port statuses
  $.get("/api/v1/ip2cc/portstates?device_id=0", function( data ) {
    //ports = $("#ccports").children();
    $.each(data, function(i, v) {
      if (v == 0) {
        $("#"+i).removeAttr('checked', 'checked');
      } else {
        $("#"+i).attr('checked', true);
      };
    });
  });

  // update the UI

  $('.form-check-input').click( function(data) {
    if ($(this)[0].checked == true) {
      //console.log( $(this).attr('id') + " -> CHECKED!" );
      setPortState($(this).parent().parent().data().deviceid, 
                   $(this).data().portid, 1);
      
    }
    else {
      //console.log( $(this).attr('id') + " -> UNchecked!" );
      setPortState($(this).parent().parent().data().deviceid, 
                   $(this).data().portid, 0);
    };
    // refresh the switch state

  });

});

function setPortState(deviceId, portId, state) {

  data = {
    'device_id': deviceId,
    'module': 1,
    'port': portId,
    'state': state,
  }

  $.ajax({
    type: "POST",
    url: "/state",
    data: JSON.stringify(data),
    dataType: "application/json",
    success: function (response) {
      $("#port"+portId).dispatchEvent(new Event("change"));
    },
    fail: function (response) {
      console.log("FALE");
    }
  });
};

function getPortStates(deviceId) {
  // call the api to get the port statuses
  $.get("/api/v1/ip2cc/portstates?device_id=" + deviceId, function( data ) {
    console.log( typeof data ); // string
    console.log( data ); // HTML content of the jQuery.ajax page
  });
};

function updateUIwitch(elem){
  $(elem).dispatchEvent(new Event("change"));
};