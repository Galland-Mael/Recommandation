const slidePage=document.querySelector('.slide-page');
const firstNext=document.querySelector('.next-1');
const secNext=document.querySelector('.next-2');
const secondPrevious=document.querySelector('.prev-2');
const thirdPrevious=document.querySelector('.prev-3');
const thirdNext=document.querySelector('.next-3');
const fourthPrevious=document.querySelector('.prev-4');
const fourthNext=document.querySelector('.next-4');
const circle = document.querySelectorAll(".step .circle");
const progressText = document.querySelectorAll(".step .name-step");
const progressCheck = document.querySelectorAll(".step .check");
const test=document.getElementById('test');
let current =1;
let temp=0;
firstNext.addEventListener('click',()=>{
    slidePage.style.marginLeft = "-25%";
    circle[current -1].classList.add("active");
    progressCheck[current - 1].classList.add("active");
    progressText[current - 1].classList.add("active");
   current+=1;
})

secNext.addEventListener('click',()=>{
    slidePage.style.marginLeft = "-50%";
    circle[current -1].classList.add("active");
    progressCheck[current - 1].classList.add("active");
    progressText[current - 1].classList.add("active");
    current+=1;
})

thirdNext.addEventListener('click',()=>{
    slidePage.style.marginLeft = "-75%";
    circle[current -1].classList.add("active");
    progressCheck[current - 1].classList.add("active");
    progressText[current - 1].classList.add("active");
    current+=1;
})
fourthNext.addEventListener('click',()=>{
    if (temp%2==0) {
        test.classList.add('select');
    }else{
        test.classList.remove('select')
    }
    temp=temp+1;
    console.log(temp)
})
secondPrevious.addEventListener('click',()=>{
    slidePage.style.marginLeft = "0%";
    circle[current - 2].classList.remove("active");
    progressCheck[current - 2].classList.remove("active");
    progressText[current - 2].classList.remove("active");
    current -= 1;
})
thirdPrevious.addEventListener('click',()=>{
    slidePage.style.marginLeft = "-25%";
    circle[current - 2].classList.remove("active");
    progressCheck[current - 2].classList.remove("active");
    progressText[current - 2].classList.remove("active");
    current -= 1;
})
fourthPrevious.addEventListener('click',()=>{
    slidePage.style.marginLeft = "-50%";
    circle[current - 2].classList.remove("active");
    progressCheck[current - 2].classList.remove("active");
    progressText[current - 2].classList.remove("active");
    current -= 1;
})


