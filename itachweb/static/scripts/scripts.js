

$.get("/api/v1/ip2cc/0/portstates", function( data ) {
    console.log( typeof data ); // string
    console.log( data ); // HTML content of the jQuery.ajax page
  });