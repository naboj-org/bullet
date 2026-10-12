# Tearoff upload, generation and printing

Tearoffs contain the problem statements and the barcodes that identify each team and problem. Upload the source PDFs once for the competition, then generate printable PDFs for each venue.

Keep these files private before the competition. Use "Tearoff upload", not the public file browser.

## Preparing and uploading source PDFs

Country and branch administrators can upload source files while the competition is unlocked.

Prepare one PDF per language. Name it with the exact language code, such as `sk.pdf`, `cs.pdf` or `en.pdf`. Use lowercase `.pdf` filenames, as the generator looks for those names.

Each source PDF must have one page per problem, in problem order, plus one final page for the team's summary tearoff. For 50 problems, the PDF must have 51 pages. Each page should contain a single tearoff, with the page size cropped to the strip rather than a full sheet of paper. The generator uses the primary-language PDF's first page height to calculate how many strips fit on an A4 sheet.

1. Select the correct competition.
2. Open "Upload tearoffs" in the sidebar.
3. Upload a language PDF, or a ZIP containing several language PDFs.
4. Review the uploaded file list and any error messages.

Put PDFs at the ZIP's top level, without enclosing folders. Files whose names are not recognised language codes are rejected; non-PDF files in the ZIP are ignored. A ZIP can upload valid files even if other filenames are rejected.

Uploading the same filename replaces the existing file. The source files belong to the whole competition, so a replacement affects subsequent generation for all venues using that language.

## Assigning team numbers

Once registration closes, assign team numbers before generating tearoffs:

1. Open "Teams" and click "Assign numbers".
2. Select the venue.
3. Leave forced reassignment off unless you intend to replace all existing numbers.
4. Submit the form.

Venue, country and branch administrators can assign numbers. The system numbers competing teams within the venue starting at 001, 002, 003 and so on. Waiting and unconfirmed teams are not included in numbering or tearoff generation.

If the team list changes, you can run assignment again. By default, existing numbers stay unchanged and teams without numbers fill gaps in the sequence.

Forced reassignment clears the existing numbers and assigns them again. Do not use it after printing unless you also replace the printed sets: the new numbers can differ from those on the paper barcodes.

For individual changes, such as assigning a backup set's number or resolving a conflict after moving venues, see [changing team numbers](/admin/documentation/teams/#changing-team-numbers).

## Generating a venue PDF

Open "Venues", select your venue and open "Tearoffs".

- Leave "Selected teams" blank to include all eligible teams, or enter team numbers such as `1-4, 5, 7`. These are assigned numbers, not the IDs prefixed with `#`.
- Check "First problem". It defaults to the category's first problem.
- Choose the primary venue language and a language print option.
- Choose the problem ordering.
- Set the number and language of backup teams if you need spare sets.
- Leave "Include QR code" selected if you want QR codes alongside the barcodes.

Backup sets use numbers starting at 999, then 998, and so on. They do not create teams in the database. Before giving a backup set to a team, an administrator must assign that number to the team and check that it is not already in use.

### Language options

"Mixed" includes all selected teams, with statements in each team's chosen language.

"Monolingual" includes only teams whose language matches the primary venue language.

"Bilingual" includes only teams whose language differs from the primary venue language. It creates a double-sided document with the primary language on one side and the team's language on the other. Generate a separate monolingual document for teams using the primary language.

Upload source PDFs for every language you will print, including the primary venue language and any backup-team language.

### Problem ordering

"Aligned" groups teams so that their problems line up through the stack of printed sheets. Cutting the stack gives you strips already grouped by team.

"Sequential" puts consecutive problems for one team on the same sheet. You will need to sort the strips after cutting.

## Printing

Download the generated PDF and inspect a few pages before printing the full batch. Check the venue prefix, team numbers, languages and problem numbers.

Print on A4 at actual size rather than using "Fit to page". For bilingual documents, print a small duplex sample first and check that both sides belong to the same team and problem and face the right way. Test a barcode with the scanner you will use at the venue.

Keep each team's set together after cutting. If you change a team number or replace a source PDF, regenerate the affected sets rather than mixing old and new copies.

## Generation problems

### Missing tearoff file

The error names the missing language. Ask a country or branch administrator to upload that language's PDF. Check the filename, including its case, and the selected competition.

### Wrong page count

The error shows the expected and actual page counts. Generation uses the number of problem records in the competition and expects one extra summary page. Ask the competition organisers to check both the source PDF and the configured problems.

### A team is missing

Check that the team is competing at this venue and has a number. Then check "Selected teams" and the language option. Monolingual and bilingual generation deliberately exclude teams outside their language group.
