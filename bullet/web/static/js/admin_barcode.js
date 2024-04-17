document.body.addEventListener("htmx:afterSwap", () => {
    document.getElementById("js-scanform").reset()
    document.getElementById("js-scanfield").focus()
})

let scanning = true;
const error_audio = new Audio('/static/sound/barcode_error.mp3');
const success_audio = new Audio('/static/sound/barcode_success.mp3');

document.body.addEventListener("scan-complete", async (evt) => {
    scanning = true;
    document.getElementById("success-indicator").animate({opacity: "0"}, {duration: 100, fill: "forwards"})

    if (evt.detail.result === 0) {
        await success_audio.play();
    } else {
        await error_audio.play();
    }
})


let audio = new Audio('/static/sound/barcode_scanner.mp3');


document.getElementById("js-open-reader").addEventListener("click", (ev) => {
    ev.preventDefault()
    document.getElementById("reader-wrapper").classList.remove("hidden")
    document.getElementById("js-open-reader").classList.add("hidden")
    document.getElementById("js-scanform").classList.add("hidden")
    let successElement = document.getElementById("success-indicator")

    let lastCode = ""
    let codeScanner = new Html5Qrcode("js-reader")
    let config = {
        fps: 10,
        experimentalFeatures: {
            useBarCodeDetectorIfSupported: true
        },
        rememberLastUsedCamera: true,
        supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_CAMERA],
        formatsToSupport: [Html5QrcodeSupportedFormats.QR_CODE, Html5QrcodeSupportedFormats.CODE_128],
    }
    codeScanner.start({ facingMode: "environment" }, config, (text, result) => {
        if (text !== lastCode && scanning) {
            lastCode = text
            scanning = false
            document.getElementById("js-scanfield").value = text
            htmx.trigger("#js-scanform", "submit")
            navigator.vibrate(200)
            audio.play()
            successElement.animate({boxShadow: "inset 0 0 0 8px rgb(34 197 94 / 100)"}, {duration: 500, iterations: 1})
            successElement.animate({opacity: "0.8"}, {duration: 100, fill: "forwards"})
        }
    })
})
