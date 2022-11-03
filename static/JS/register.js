const slidePage = document.querySelector('.slide-page');
const firstNext = document.querySelector('.next-1');
const secNext = document.querySelector('.next-2');
const secondPrevious = document.querySelector('.prev-2');
const thirdPrevious = document.querySelector('.prev-3');
const thirdNext = document.querySelector('.next-3');
const failInfo = document.querySelectorAll('.failInfo');
const fourthPrevious = document.querySelector('.prev-4');
const fourthNext = document.querySelector('.next-4');
const firstName = document.querySelector('.firstName');
const lastName = document.querySelector('.lastName');
const date = document.querySelector('.date');
const mail = document.querySelector('.mail');
const pwd1 = document.querySelector('.pwd1');
const pwd2 = document.querySelector('.pwd2');
const circle = document.querySelectorAll(".step .circle");
const progressText = document.querySelectorAll(".step .name-step");
const progressCheck = document.querySelectorAll(".step .check");
const item = document.querySelectorAll('.item');
let current = 1;


firstNext.addEventListener('click', () => {
        slidePage.style.marginLeft = "-25%";
                        circle[current - 1].classList.add("active");
                        progressCheck[current - 1].classList.add("active");
                        progressText[current - 1].classList.add("active");
                        current += 1;
})

secNext.addEventListener('click', () => {
    if (mail.value != "") {
         failInfo[3].textContent = "*Ce champs ne peut pas être vide";
        failInfo[3].classList.add('none');
    } else {
        showCLassTimer(failInfo[3], 2000, "none");
    }
    if (pwd1.value != "") {
        failInfo[4].classList.add('none');
    } else {
        showCLassTimer(failInfo[4], 2000, "none");
    }
    if (pwd2.value != "") {
        failInfo[5].classList.add('none');
    } else {
        showCLassTimer(failInfo[5], 2000, "none");
    }
    if ((/^[\w-.]+@([\w-]+.)+[\w-]{2,4}$/.test(mail.value))) {
        if (/^[\w$@%*+\-_!]{8,15}$/.test((pwd1.value))) {
            if (pwd1.value == pwd2.value) {
                failInfo[5].classList.add('none');
                slidePage.style.marginLeft = "-50%";
                circle[current - 1].classList.add("active");
                progressCheck[current - 1].classList.add("active");
                progressText[current - 1].classList.add("active");
                current += 1;
            } else {
                showCLassTimer(failInfo[5], 2000, "none")
            }
        } else {
            showCLassTimer(failInfo[4], 2000, "none");
        }
    }else
        {
            failInfo[3].textContent = "*Adresse mail introuvable";
            showCLassTimer(failInfo[3], 2000, "none");
        }

})

thirdNext.addEventListener('click', () => {
    slidePage.style.marginLeft = "-75%";
    circle[current - 1].classList.add("active");
    progressCheck[current - 1].classList.add("active");
    progressText[current - 1].classList.add("active");
    current += 1;
})
fourthNext.addEventListener('click', () => {
    console.log("end");
})
secondPrevious.addEventListener('click', () => {
    slidePage.style.marginLeft = "0%";
    circle[current - 2].classList.remove("active");
    progressCheck[current - 2].classList.remove("active");
    progressText[current - 2].classList.remove("active");
    current -= 1;
})
thirdPrevious.addEventListener('click', () => {
    slidePage.style.marginLeft = "-25%";
    circle[current - 2].classList.remove("active");
    progressCheck[current - 2].classList.remove("active");
    progressText[current - 2].classList.remove("active");
    current -= 1;
})

fourthPrevious.addEventListener('click', () => {
    slidePage.style.marginLeft = "-50%";
    circle[current - 2].classList.remove("active");
    progressCheck[current - 2].classList.remove("active");
    progressText[current - 2].classList.remove("active");
    current -= 1;
})

function showCLassTimer(selector, timer, type) {
    selector.classList.remove(type);
    setTimeout(function () {
        selector.classList.add(type)
    }, timer);
}

item.forEach((item, index) => {
    item.addEventListener('click', event => {
        if (item.firstElementChild.classList.contains("none")) {
            item.firstElementChild.classList.remove("none")
        } else {
            item.firstElementChild.classList.add("none")
        }
    })
})