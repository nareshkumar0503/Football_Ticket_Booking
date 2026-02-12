const slides = document.querySelector('.carousel-slides');
const prev = document.querySelector('.prev');
const next = document.querySelector('.next');
const form = document.getElementById("contact-form");

let index = 0;

prev.addEventListener('click', () => {
    index = (index > 0) ? index - 1 : 3;
    slides.style.transform = `translateX(-${index * 25}%)`;
});

next.addEventListener('click', () => {
    index = (index < 3) ? index + 1 : 0;
    slides.style.transform = `translateX(-${index * 25}%)`;
});

form.addEventListener("submit",function(e) {
    e.preventDefault();

    let name = document.getElementById("name").value.trim();
    let email = document.getElementById("email").value.trim();
    let msg = document.getElementById("message").value.trim();
    let valid = true;

    document.getElementById("nameError").innerText="";
    document.getElementById("emailError").innerText="";
    document.getElementById("msgError").innerText="";
    document.getElementById("successmsg").innerText="";

    if(name==="") {
        document.getElementById("nameError").innerText="Name is Required";
        valid = false;
    }

    if(email==="") {
        document.getElementById("emailError").innerText="Email is Required";
        valid = false;
    }

    if(msg==="") {
        document.getElementById("msgError").innerText="Message is Required";
        valid = false;
    }

    if(valid) {
        document.getElementById("successmsg").innerText="Message Sent Successfully";
        form.reset();
    }
});

const bookBtns = document.querySelectorAll(".book-btn");

bookBtns.forEach(btn => {
    btn.addEventListener("click", function () {

        let matchName = this.getAttribute("data-match");
        let price = this.getAttribute("data-price");

        localStorage.setItem("matchName", matchName);
        localStorage.setItem("ticketPrice", price);

        window.location.href = "/cart/";
    });
});

