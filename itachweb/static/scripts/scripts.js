
$(window).on('load', function() {
  // get the device ID from the URL

  // call the api to get the port statuses
  $.get("/api/v1/ip2cc/portstates?device_id=0", function( data ) {
    console.log( typeof data ); // string
    console.log( data ); // HTML content of the jQuery.ajax page
  });

  // update the UI

});
