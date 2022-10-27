document.body.addEventListener("htmx:afterSwap", (evt) => {
    document.getElementById("js-scanform").reset()
    document.getElementById("js-scanfield").focus()
})

document.getElementById("js-open-reader").addEventListener("click", () => {
    document.getElementById("js-reader").classList.remove("hidden")
    document.getElementById("js-open-reader").style.display = "none"
    document.getElementById("js-scanform").classList.add("hidden")

    let lastCode = ""
    let codeScanner = new Html5QrcodeScanner("js-reader", {
        fps: 10,
        experimentalFeatures: {
            useBarCodeDetectorIfSupported: true
        },
        rememberLastUsedCamera: true,
        supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_CAMERA],
        formatsToSupport: [Html5QrcodeSupportedFormats.QR_CODE, Html5QrcodeSupportedFormats.CODE_128],
    }, false)
    codeScanner.render((text, result) => {
        if (text !== lastCode) {
            lastCode = text
            document.getElementById("js-scanfield").value = text
            htmx.trigger("#js-scanform", "submit")
        }
    })
})
