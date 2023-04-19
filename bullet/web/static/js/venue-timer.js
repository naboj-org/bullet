(() => {
    function animationInterval(ms, signal, callback) {
        const start = document.timeline ? document.timeline.currentTime : performance.now()

        function frame(time) {
            if (signal.aborted) return
            callback(time)
            scheduleFrame(time)
        }

        function scheduleFrame(time) {
            const elapsed = time - start
            const roundedElapsed = Math.round(elapsed / ms) * ms
            const targetNext = start + roundedElapsed + ms
            const delay = targetNext - performance.now()
            setTimeout(() => requestAnimationFrame(frame), delay)
        }

        scheduleFrame(start)
    }

    const controller = new AbortController()

    const DTF = new Intl.DateTimeFormat(document.documentElement.lang, {
        hour: 'numeric',
        minute: 'numeric',
        second: 'numeric',
        hourCycle: "h23",
        timeZone: 'UTC'
    })

    // Create an animation callback every second:
    document.querySelectorAll(".js-venue-timer").forEach(el => {
        let duration = parseInt(el.dataset.duration) * 1000
        let timeToStart = parseInt(el.dataset.start) * 1000 - new Date()

        animationInterval(1000, controller.signal, time => {
            let diff = timeToStart - time
            if (diff > 0) {
                el.innerText = DTF.format(diff)
                document.querySelectorAll(".js-venue-timer-before").forEach(e => e.classList.remove("hidden"))
            } else {
                el.innerText = DTF.format(diff + duration)
                document.querySelectorAll(".js-venue-timer-before").forEach(e => e.classList.add("hidden"))
            }
        })
    })
})()
