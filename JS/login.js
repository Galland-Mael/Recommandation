const slidePage=document.querySelector('.slide-page')
const firsNext=document.querySelector('.next-1')
const circle = document.querySelectorAll(".step .circle");
const progressText = document.querySelectorAll(".step .name-step");
const progressCheck = document.querySelectorAll(".step .check");
let current =1;
firsNext.addEventListener('click',()=>{
   circle[current -1].classList.add("active");
    progressCheck[current - 1].classList.add("active");
    progressText[current - 1].classList.add("active");
   current+=1;
})