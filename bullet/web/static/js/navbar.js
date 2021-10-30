document.addEventListener("scroll", scrollFunction);

function scrollFunction() {
  if (document.body.scrollTop > 165 || document.documentElement.scrollTop > 165) {
    document.getElementById("main-nav").style.top = "0";
  } else {
    document.getElementById("main-nav").style.top = "-100px";
  }
}
