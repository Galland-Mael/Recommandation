const searchTerm = document.querySelector('.searchTerm')
const glider = document.querySelector('.glider-contain')

searchTerm.addEventListener('focus',()=>{
    glider.classList.add("flou")
})
searchTerm.addEventListener('focusout',()=>{
    glider.classList.remove("flou")
})