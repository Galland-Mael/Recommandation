const profilContainer =document.querySelector('.profil-container');
const profil = document.querySelector('.profil');
const changeProfil = document.querySelector('.profil-span')

profilContainer.addEventListener('click',()=>{
   profil.click();
})

profilContainer.addEventListener('mouseover',()=>{
   changeProfil.classList.remove('opacity-null')
   changeProfil.classList.add('normal-opacity')
})

profilContainer.addEventListener('mouseout',()=>{
   changeProfil.classList.add('opacity-null')
   changeProfil.classList.remove('normal-opacity')
})




