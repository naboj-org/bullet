# Live signage

Live signage displays the countdown and public results on a projector or venue screen. It runs on the public competition website and does not require an organiser login.

## Setting up a screen

1. Open the public website for the correct competition branch, country and language.
2. Open `live/` under the site's country and language URL prefix.
3. Fill in the display options and click "Start".
4. Put the browser in fullscreen mode and check the display from the contestants' seating area.

The page uses the website's current competition, not the competition selected in your admin session.

### Timer and result options

Select "Venue time" if your venue has a custom start time. Otherwise, leave it blank to use the global competition start. Include that venue in the "Venues" selection as well so its timer setting carries through to the embedded results.

Select the venues whose results you want to show. You can also choose country results and enable international results. The country and international tables use the categories of your selected venues.

Set "Country teams limit" and "International teams limit" to show only the leading teams in those tables. Leave a limit blank or set it to 0 to show all teams.

Use "Hide contestants" to omit contestant names, and "Hide squares" to omit the per-problem indicators. These options can make the tables easier to read on a smaller screen.

## What the screen shows

The display switches automatically according to the selected start time and competition duration:

- Before the start, it shows a countdown and a reminder not to open the problems.
- During the first three minutes, it shows the first recorded solution at each selected venue.
- During the main part of the competition, it shows results.
- During the last three minutes, it returns to the countdown.
- For the first two minutes after the end, it keeps the countdown screen, then returns to results.

The results display groups tables into pairs, scrolls through them and cycles between groups. It loads fresh results as it cycles.

These are public results, so the normal results freeze applies. Live signage does not show the unfrozen admin standings. See [Results](/admin/documentation/results/) for the difference.

## Before contestants arrive

Check the selected venues, categories and timer. Keep the screen computer connected to the internet, disable sleep and screensavers, and check that the browser's clock is correct: the automatic screen changes use the computer's current time.

Choose the options again from the setup page if you need to change the display. Starting signage submits the settings as a form; bookmarking the resulting browser address alone does not save that setup.

## Display problems

### The countdown or screen changes are wrong

Check the computer's clock and the "Venue time" selection. Ask an administrator to check the venue's custom start time if needed.

### Results are missing or have stopped changing

Check the internet connection and reload the page. If reloading returns you to setup, choose the options and click "Start" again.

Make sure you selected at least one venue. Country and international tables depend on the categories of those venues. Near the end, unchanged scores may be the expected results freeze rather than a connection problem.

### The text is too small

Check fullscreen mode and browser zoom. Reduce the country and international team limits, or hide contestant names and problem squares.
