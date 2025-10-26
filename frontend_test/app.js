// This code runs in the browser!
console.log("JavaScript file loaded.");

// 1. Find the button on the page
const button = document.getElementById("myButton");

// 2. Listen for a "click" event
button.addEventListener("click", () => {
    // 3. When clicked, run this code
    alert("You clicked the button! You are running JavaScript.");
});