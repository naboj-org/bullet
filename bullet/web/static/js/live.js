(() => {
    const data = JSON.parse(document.getElementById("js-data").textContent)
    const ifr = document.getElementById("js-frame")
    const minutes = 60*1000
    let lastSrc = ""

    const changeSrc = (newSrc) => {
        if (lastSrc !== newSrc) {
            ifr.src = newSrc
            lastSrc = newSrc
        }
    }

    const loop = () => {
        const start = new Date(data.start)
        const end = new Date(start.getTime() + data.duration*1000)
        const now = new Date()

        if (now < start) {
            // Before the competition
            changeSrc(data.countdown)
        } else if (now < end) {
            // During the competition
            if (now - start < 3*minutes) {
                // Just started
                changeSrc(data.first_problem)
            } else if (end - now < 3*minutes) {
                // Before end
                changeSrc(data.countdown)
            } else {
                changeSrc(data.results)
            }
        } else {
            // After the competition
            if (now - end < 2*minutes) {
                changeSrc(data.countdown)
            } else {
                changeSrc(data.results)
            }
        }
    }

    setInterval(loop, 5000)
    loop()
})()
