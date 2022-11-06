(() => {
    const tick = () => {
        document.querySelectorAll(".js-venue-timer").forEach((elem) => {
            let startTime = parseInt(elem.dataset.start)
            let currentTime = Math.floor((new Date()).getTime() / 1000)
            let duration = parseInt(elem.dataset.duration)

            let diff
            if (currentTime > startTime) {
                diff = (startTime + duration) - currentTime
            } else {
                diff = startTime - currentTime
            }

            let seconds = Math.max(0, diff % 60)
            let minutes = Math.max(0, Math.floor(diff / 60) % 60)
            let hours = Math.max(0, Math.floor(diff / 3600))

            elem.innerText = (currentTime < startTime ? "-" : "") + hours.toString().padStart(2, "0") + ":" + minutes.toString().padStart(2, "0") + ":" + seconds.toString().padStart(2, "0")
        })
    }

    tick()
    setInterval(tick, 100)
})()
