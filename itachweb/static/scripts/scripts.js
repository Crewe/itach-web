

$.get("/api/v1/ip2cc/portstates?device_id=0", function( data ) {
    console.log( typeof data ); // string
    console.log( data ); // HTML content of the jQuery.ajax page
  });