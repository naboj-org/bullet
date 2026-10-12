# Review

After the competition, use [Review](/admin/scanning/review/) to check each team's problem records against the remaining tearoffs and mark the team as reviewed. Finish the venue review once all teams have been checked, before announcing final results.

This is different from [Table review](/admin/documentation/table-review/), which checks the problems on a team's table during the competition without marking the team as reviewed.

Operators can review teams at their assigned venues. Venue, country and branch administrators can also review teams within their scope. A venue administrator or higher must finish the venue review.

## Reviewing a team by barcode

1. Open "Review" in the sidebar and select the venue.
2. Find the first problem tearoff that the team did not receive.
3. Scan its barcode.
4. Check the response and the team's status in the list.

Use a hardware scanner, "Phone scanner", or enter the barcode manually and click "Scan".

The expected barcode is the problem immediately after the highest problem the team should have received. The system calculates this from the category's initial allocation and the number of recorded solutions.

For example, if teams start with six problems and a team has five recorded solutions, it should have received problems 1 through 11. Scan problem 12, the first unissued tearoff. Do not scan an unsolved problem still on the team's table for this check.

If the team should have received every problem, scan its "no more problems" card instead.

A successful scan after the venue's competition end marks the team as reviewed. A scan during the competition only checks the barcode and does not mark the team as reviewed. Before the venue's start time, the page rejects review scans.

## Correcting problem records

If the scanned problem does not match the expected number, check the remaining papers and accepted solutions before changing anything. The error reports the expected and scanned numbers.

For an unreviewed team, click "Edit problems" in the team list. The form shows each problem's "Solved?" flag and solution time.

1. Compare the entries with the accepted solutions and scanning records.
2. Correct the solved flags or times as needed.
3. For each solved problem, provide a time in `hh:mm:ss`, measured from the venue's competition start, not a wall-clock time.
4. Save, then return to the venue review and check the team again.

Saving recalculates the team's results. Make corrections only when you have evidence for them, as both the solved problems and their times can affect ranking.

Reviewed teams cannot have their problem records edited. While the venue is still unreviewed, use "Mark as unreviewed" on the team's card to reopen it.

You can also use "Mark as reviewed" manually after checking a team. This bypasses the barcode check, so use it only when you have completed the review another way.

## Finishing the venue review

The list shows unreviewed teams in red and reviewed teams in green. It includes competing teams with assigned numbers.

Once all teams are reviewed, the page offers a link to "finish the review". A venue administrator or higher must open it and confirm with "Finish review". Operators should ask their venue administrator to do this.

Finishing marks the venue as reviewed and queues calculation of its final venue ranks. Once all venues for that category and country are reviewed, the system also queues the country ranks.

Afterwards, normal problem scanning and problem-record editing are blocked for the venue. Finish only after resolving outstanding submissions and discrepancies.

## Reopening a finished review

If you need to correct a reviewed venue, ask a country or branch administrator to mark it as unreviewed. The Review page offers this link before the competition's results are public.

Reopening the venue does not clear individual teams' reviewed flags. Mark the affected team as unreviewed too, make the corrections, then review it and finish the venue review again.

See [Results](/admin/documentation/results/) for viewing rankings and announcing results.
