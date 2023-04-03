var xhttp = new XMLHttpRequest();
var output = document.getElementById('output');
function log () {
    fetch("logstream")
    .then(response => {
        response.text().then(t => {output.innerHTML = t})
    });
    /*
    xhttp.open('GET', "http://192.168.1.243:7777/logstream");
    
    document.addEventListener('readystatechange', event => {
      if (event.target.readyState === 'interactive' || event.target.readyState === 'complete') {
        xhttp.send();
        output.textContent = xhttp.responseText;
      }
      else {
        document.addEventListener("DOMContentLoaded", fn);
      }    
    }); */
}

setInterval(log, 1000);

function goFwd () {
  // takes user input from text box and makes it into varible here
  // might want to take this outside and use it as param
  var userInput = document.getElementById("userInput").value;

  // use the http request thing to execute URL; concatenate URL with variable userInput -> should work
  var urlBase = "http://192.168.1.243:7777/fwd?d=";
  var fullURL = urlBase.concat(userInput.toString());
  // open(method, url, async)
  xhttp.open("GET", fullURL, true);
  xhttp.send();
}

function goBwd () {
  var userInput = document.getElementById("userInput").value;

  var urlBase = "http://192.168.1.243:7777/bwd?d=";
  var fullURL = urlBase.concat(userInput.toString());

  xhttp.open("GET", fullURL, true);
  xhttp.send();
}

function goRight () {
  var userInput = document.getElementById("userInput").value;

  var urlBase = "http://192.168.1.243:7777/right?a=";
  var fullURL = urlBase.concat(userInput.toString());

  xhttp.open("GET", fullURL, true);
  xhttp.send();
}

function goLeft () {
  var userInput = document.getElementById("userInput").value;

  var urlBase = "http://192.168.1.243:7777/left?a=";
  var fullURL = urlBase.concat(userInput.toString());

  xhttp.open("GET", fullURL, true);
  xhttp.send();
}

function goMaze () {
  var fullURL = "http://192.168.1.243:7777/run";

  xhttp.open("GET", fullURL, true);
  xhttp.send();
}
