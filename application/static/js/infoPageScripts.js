$(document).ready(function(){
    if (!jQuery) {  
      // jQuery is not loaded
      alert("Error jQuery is not loaded");
      return;
    }

    initializations();
 });

 function initializations(){
    
     //click handlers
     document.getElementById("idBackToHomeButton").onclick = function(){
        window.location.href='/';
     }
     return;
 }