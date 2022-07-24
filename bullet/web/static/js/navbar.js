document.addEventListener("scroll", () => document.getElementById("main-nav")
    .classList.toggle("-translate-y-full", document.body.scrollTop < 165 &&
        document.documentElement.scrollTop < 165))