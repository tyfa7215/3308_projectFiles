var currentSlide = 0;
var numSlides;

function changeSlide(n){
  var highestTimeoutId = setTimeout(";");
  for (var i = 0 ; i < highestTimeoutId ; i++) {
      clearTimeout(i); 
  }
  currentSlide  = (currentSlide + document.getElementsByClassName('mySlides').length-2)%document.getElementsByClassName('mySlides').length;
  showSlides();
}


function showSlides(){
    var slides = document.getElementsByClassName('mySlides');
    numSlides = slides.length;
    currentSlide = (currentSlide+1)%3;

    for (var i = 0; i < numSlides; i++) {
      slides[i].style.display = "none";
    }

    slides[currentSlide].style.display='block';
    setTimeout(showSlides, 4000);
}