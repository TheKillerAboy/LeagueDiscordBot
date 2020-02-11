var socket = io.connect("http://102.39.33.86:8445")


$('#api-update-button').click(()=>{
    socket.emit('update-api-key',($('#api-update-input').val()))
})