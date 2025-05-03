// var i = 0;
// var txt = 'Lorem ipsum typing effect!'; /* The text */
// var speed = 50; /* The speed/duration of the effect in milliseconds */

// function typeWriter() {
//   if (i < txt.length) {
//     document.getElementById("typed").innerHTML += txt.charAt(i);
//     i++;
//     setTimeout(typeWriter, speed);
//   }
// }





document.addEventListener("DOMContentLoaded", function () {
  const textToType = "Welcome to MoooD — your tastebuds’ new therapist. Feeling gloomy, fiery, or just kinda meh? We get it — moods are messy, but your food doesn’t have to be. Tell us how you feel, and we’ll serve up the perfect bite to match your vibe. From comfort carbs to spicy chaos, we’ve got flavors for every feeling. No overthinking, just good eats for good (or not-so-good) moods. What’s your MoooD today?";
  const typingEffectElement = document.getElementById("typed");

  function typeText(text, index) {
    if (index < text.length) {
      typingEffectElement.textContent += text.charAt(index);
      index++;
      setTimeout(function () {
        typeText(text, index);
      }, 10); 
    }
  }    
  typeText(textToType, 0);
});



document.getElementById('loginForm').addEventListener('submit', function(e) {
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value.trim();
  const error = document.getElementById('error');
  
  if (!username || !password) {
      e.preventDefault();
      error.textContent = 'Please fill in both fields.';
  } else {
      error.textContent = '';
  }
  });

  
  
  
  function log() {
      const popup = document.getElementById("login-popup");
      document.getElementById("menu").style.display = "none";
      popup.style.display = "flex"; 
  }
  
  function unlog() {
      const popup = document.getElementById("login-popup");
      popup.style.display = "none";
      document.getElementById("menu").style.display = "block";
  }


  function showsign() {
    document.getElementById("logg").style.display = "none";
    document.getElementById("pp").style.display = "none";
    document.getElementById("pu").style.display = "none";
    document.getElementById("sign").style.display = "block";
    document.getElementById("hh").style.display = "block";
}

function validateForm() {
  const signFormVisible = document.getElementById("sign").style.display !== "none";
  if (!signFormVisible) {
      return true; // No validation for login form
  }

  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("signup-password").value;
  const confirm = document.getElementById("confirm-password").value;

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!name || !email || !password || !confirm) {
      alert("Please fill all signup fields.");
      return false;
  }
  if (!emailRegex.test(email)) {
      alert("Please enter a valid email.");
      return false;
  }
  if (password.length < 6) {
      alert("Password must be at least 6 characters.");
      return false;
  }
  if (password !== confirm) {
      alert("Passwords do not match.");
      return false;
  }

  return true;
}