//When a input is changed check all the inputs and if all are filled, enable the button
$('input,textarea,select').filter('[required]:visible').keyup(function() {
  var isValid = true;
  $('input,textarea,select').filter('[required]:visible').each(function() { 
    if ( $(this).val() === '' ) isValid = false;
  });
  if( isValid ) {
    $(this.form).find(':submit').prop('disabled', false);
  } else {
    $(this.form).find(':submit').prop('disabled', true);
  };
});