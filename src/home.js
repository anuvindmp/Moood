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



function redirect(){
  window.location.href = "login.html";
}

function searchswitch(){
  document.getElementById('fade-wrap').style.opacity = '1';
  setTimeout(function(){
    window.location.href = "search.html";}, 300)
}