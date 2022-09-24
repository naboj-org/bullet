const backup_nav = document.getElementById("backup-nav");
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if(!entry.isIntersecting && backup_nav.classList.contains("-translate-y-full")){
            backup_nav.classList.remove("-translate-y-full");
        } else {
            backup_nav.classList.add("-translate-y-full");
        }
    });
});
observer.observe(document.getElementById("default-nav"));
