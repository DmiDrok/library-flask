try{
    const message = document.querySelector(".flash_msgs_here p")
    const close_message = document.querySelector(".flash_msgs_here p #close_flash_msg")


    close_message.addEventListener("click", function(){
        message.style.display = "none";
    })
}
catch(err){
    console.log(err);
}