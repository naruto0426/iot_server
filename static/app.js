$(function(){
  $('form').submit(function(){
      $.ajax({
          type : "post",
          url : $(this).attr('action'),
          dataType : "json",
          data:{user: $('form').find('input[name="user"]').val(),
                password: $('form').find('input[name="password"]').val(),
                refer_url: $('input[name="refer_url"]').val()},
          global:false,
          success: function(data)
           {
            if (data['status']=='failed'){
              alert(data['text'])
            }else{
              window.location.href = data['text']
            }
           },
          error : function(data){
            console.log(data)
            alert('please try again later.')
          }
        });
      return false;
    })
})