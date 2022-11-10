(() => {
    const screens = JSON.parse(document.getElementById("js-screens").textContent)
    let currentScreen = -1
    let lastChange = null
    const iframe = document.getElementById("js-results")
    const venueTimer = new URLSearchParams(window.location.search).get("venue_timer")

    const nextScreen = () => {
        if (lastChange && (new Date() - lastChange) < 15000) {
            setTimeout(nextScreen, 1000)
            return
        }

        lastChange = new Date()
        currentScreen = (currentScreen + 1) % screens.length
        iframe.src = screens[currentScreen] + "?embed&venue_timer=" + venueTimer
        iframe.contentWindow.scrollTo(0, 0)
    }

    const scrollMore = () => {
        iframe.contentWindow.scrollBy(0, 2)
        const idoc = iframe.contentWindow.document.documentElement
        const remainingHeight = idoc.offsetHeight - (idoc.scrollTop + iframe.offsetHeight)

        if (remainingHeight > 0) {
            setTimeout(scrollMore, 35)
        } else {
            setTimeout(nextScreen, 1000)
        }
    }

    const startUp = () => {
        const start = new Date(document.querySelector(".js-venue-timer").dataset.start * 1000)
        const now = new Date()
        if (now > start) {
            document.getElementById("js-countdown").classList.add("hidden")
            iframe.classList.remove("hidden")
            setTimeout(nextScreen, 5000)
        } else {
            setTimeout(startUp, 5000)
        }
    }

    startUp()

    iframe.addEventListener("load", () => {
        if (!iframe.contentDocument) {
            setTimeout(nextScreen, 100)
        } else {
            setTimeout(scrollMore, 5000)
        }
    })
})()
