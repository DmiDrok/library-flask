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

try{
    const bottomNavBar = document.querySelector(".navigation_bottom");
    const blockText = document.querySelector(".book_text");

    if (blockText.clientHeight < window.screen.height){
        bottomNavBar.style.display = "none";
    }
}
catch(err){
    console.log(err);
}

// try{
//     let favourites = [];
//     let allBtns = document.querySelectorAll(".book_block .favourite_link");
//     let xmlhttp = XMLHttpRequest();

//     //Логика на добавление в массив избранных произведений
//     for (let btn of allBtns){
//         btn.onclick = function(){
//             nextElement = btn.nextElementSibling.textContent.trim().slice(0, btn.nextElementSibling.textContent.trim().length - 10);

//             if (btn.classList.contains("add")){
//                 favourites.push(nextElement);
//                 btn.innerHTML = "-";
//                 btn.nextElementSibling.classList.add("in_favourites");
//                 btn.classList.add("in_favourites");

//                 btn.classList.remove("add");
//                 btn.classList.add("remove");
//             }
//             else{
//                 favourites = favourites.filter(function(value) {return value != nextElement})
//                 btn.innerHTML = "+";
//                 btn.nextElementSibling.classList.remove("in_favourites");
//                 btn.classList.remove("in_favourites");

//                 btn.classList.remove("remove");
//                 btn.classList.add("add");
//             }

//             console.log(favourites);
//         }
//     }


//     //Логика AJAX - запроса
//     const requestURL = "https://localhost/favourites/upload";
// }
// catch(err){
//     console.error(err);
// }