# Problem Scanning

The [“Problem scanning” page](/admin/scanning/problems/) of the administration interface is used to scan solved
problems during the competition.

We recommend using a hardware barcode scanner that supports keyboard emulation (that is most of them).
If you don’t have a barcode scanner, you can use your phone camera by pressing the “Phone scanner” button.
If everything else fails, you can enter the barcode manually using the keyboard.

When a team solves a problem, you scan the barcode into this page. After scanning the barcode, result of the scan will
appear on screen, this result will also be added to the scanning history (newest entries are at the top).
The result is colored to indicate status, and an error message is shown if available.

If you scan a problem by accident, you can undo the scan by clicking on the undo button in the history log. You can
also retry any failed scan by clicking on the retry button.

## Green

Green status means that the scanning was successful.

## Yellow

The yellow color indicates one of the following errors:

* **Barcode format is invalid.** The scanned barcode does not contain the required information. Try scanning again.
* **Check digit on the scanned barcode is not correct.** The scanned barcode does not contain valid check digit.
Try scanning again.
* **Could not find venue XXX.** / **Could not find team XXX in XXX.** / **Could not find problem XXX.**
The scanned barcode is malformed, try scanning again. If problem persists, contact IT.
* **You don't have the required permissions to scan problems in XXX.**
The scanned barcode belongs to another venue that you don’t have access to.

## Red

The red color indicates one of the following errors:

* **The competition did not start yet.**
The competition did not start yet, wait for the competition start.
* **The venue was already marked as reviewed.**
The venue was reviewed, and no more barcodes can be scanned. Contact us if this is an error.
* **The team was already marked as reviewed.**
The team was reviewed, and no more barcodes for this team can be scanned. This can be unlocked on
the [Review page](/admin/scanning/review).
* **Team should not have access to problem XXX.**
The team does not have enough solved problems to allow scanning of this problem. Check that you scanned and gave away
the problems in right order. This can be only fixed by scanning the missing problems.
* **Team already solved problem XXX.**
The team did already solve the problem, so this is a duplicate scan.

If you encounter any of the two last errors, always check whether the team has the correct number of problems and
whether they have the same problems as the system thinks they do (check using the [Review page](/admin/scanning/review)).
