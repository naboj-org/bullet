(() => {
    const SCREENS = JSON.parse(document.getElementById("js-screens").textContent)
    let CURRENT_SCREEN = 0
    let lastChange = new Date()

    const loadScreens = () => {
        document.scrollingElement.scrollTop = 0
        let screens = SCREENS[CURRENT_SCREEN]

        for (let i = 0; i < 2; i++) {
            document.getElementById("js-screen-"+i).innerHTML = ""
            document.getElementById("js-title-"+i).innerText = ""
            if (i >= screens.length) {
                continue
            }

            document.getElementById("js-title-"+i).innerText = screens[i].title
            htmx.ajax("GET", screens[i].url, "#js-screen-"+i)
        }

        setTimeout(scrollMore, 5000)
    }

    const nextScreen = () => {
        if (lastChange && (new Date() - lastChange) < 20000) {
            setTimeout(nextScreen, 1000)
            return
        }
        lastChange = new Date()

        CURRENT_SCREEN = (CURRENT_SCREEN+1) % SCREENS.length
        loadScreens()
    }

    const scrollMore = () => {
        const oldScroll = document.scrollingElement.scrollTop

        const row = document.querySelector("#js-results-content tr")
        const offset = Math.max(Math.round(row.clientHeight / 40), 1)
        const divided = row.clientHeight / offset
        document.scrollingElement.scrollTop += offset

        if (oldScroll !== document.scrollingElement.scrollTop) {
            setTimeout(scrollMore, 1000/divided)
        } else {
            setTimeout(nextScreen, 1000)
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        loadScreens()
    })
})()
