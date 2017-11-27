$(document).ready(function() {
  function log(val){
    $('div#log').prepend('<p>'+val+'</p>')
  }

  function get_judge_data(){
    return {
      'time':parseInt($("#time").val()),
      "judge_id":$("#judge_id").val(),
      "judger":$("#judger").val(),
      "memory":parseInt($("#memory").val()),
      "stack_limit":parseInt($("#stack_limit").val()),
      "lang":$("#lang").val(),
      "code":$("#code").val(),
    }
  }


  var socket = io.connect('http://103.73.48.21:5000/judge');

  socket.on('connect', function() {
    log('I connected!')
  });

  socket.on('judge_response', function(msg) {
    console.log(msg)
  });

  
  $('form#emit').submit(function(event) {
    //socket.emit('my_event', {data: $('#emit_data').val()});
    var data = get_judge_data()
    console.log(data)
    socket.emit('request_judge',data);
    return false;
  });


})
