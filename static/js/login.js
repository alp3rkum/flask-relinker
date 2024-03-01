const login = document.getElementsByName('login')[0];
const signup = document.getElementsByName('login')[1];

const divlogin = document.getElementsByClassName('div-login')[0];
const divsignup = document.getElementsByClassName('div-signup')[0];

login.addEventListener('click', () => {
    divlogin.style.display = 'block';
    divsignup.style.display = 'none';
})
signup.addEventListener('click', () => {
    divlogin.style.display = 'none';
    divsignup.style.display = 'block';
})

window.onload = () => {
    login.checked = true;
    divlogin.style.display = 'block';
    divsignup.style.display = 'none';
}