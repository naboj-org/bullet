# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses the `YYYY.N` version format.

## 2024.7 - 2024-02-08

### Added

- Added a link to quickly edit a given page block right from the front-page.
- Added deprecation notes to content blocks and logos in the admin.
- Added an indicator in the archive that tells that a given competition year is only available to admins.
- Added an option to copy content and blocks from another page.

### Changed

- Title of a block is now displayed in block list.
- Competition name is now automatically generated from local branch name and the competition year.
- Upgraded Math homepage to page blocks.

### Removed

- Removed "official results" message from the results.

### Fixed

- Blocks with completely empty data no longer crash the site.
- Admin results did not persist when changing countries.

## 2024.6 - 2024-02-02

### Changed

- Improved logo cloud block template.

### Fixed

- Using file selector sometimes moved the whole page around.

## 2024.5 - 2024-02-01

### Fixed

- File selector did not work correctly inside forms with mupltiple entries.
- Changed translations to reflect new labels on homepage.

## 2024.4 - 2024-02-01

### Added

- Completely new way to manage homepage and other pages that require more than a markdown content (page blocks).

### Changed

- Upgraded Chemistry and Physics homepage to page blocks.

## 2024.3 - 2024-01-30

### Added

- Allow content administrators to manage files uploaded to the website's storage.
- Added an option for administrators to filter schools by countries in the school list.

### Changed

- Updated DE translations.

### Fixed

- Resolved issues with logging out of the system.
- Resolved a bug in which country fields did not work correctly or completely crash the website.

## 2024.2 - 2024-01-21

### Changed

- Images in archive are now scaled properly.
- Update missing translations for "Answer" in the problem archive.

## 2024.1 - 2024-01-15

### Changed

- Updated ET translations

## 2023.12.1 - 2023-12-14

### Fixed

- Actually updated DE translations

## 2023.12 - 2023-12-13

### Changed

- Updated HU translations
- Updated DE translations
- Photos in albums are now sorted by time of creation

## 2023.11 - 2023-11-20

### Changed

- Team export now contains `online_password`.
- Operators can now access admin results and results announcement.
- Public results now use infinite scrolling instead of pagination.
- Live results now scroll one team at a time, instead of 1/4 of page.

### Fixed

- `venue_timer` is now correctly passed to live results display.

## 2023.10.5 - 2023-10-31

### Fixed

- Emails about team deletion are being sent again.

## 2023.10.4 - 2023-10-26

### Fixed

- Fields with multiple checkboxes are now displaying normally.
- School edit form did not save school types.

## 2023.10.3 - 2023-10-17

### Added

- Added an option for selecting between short-lived and long-lived session on login (Remember me).

### Changed

- Reworked pages administration.
- Removed France from Náboj Junior homepage.
- Team lists now only show countries with at least one venue.
- Reworked problem scanner.

## 2023.10.2 - 2023-10-08

### Changed

- Updated translations for ES.
- Updated authorization field message in Spanish registration flow.
- Improved labels and help texts in category forms and tables.
- "Legacy" schools (that were imported from old system) are now not shown in the admin.

### Fixed

- Link between team list and waiting list now preserves selected country. 
- Category editing in admin did not use current competition.
- Fixed line wrapping in venue and school list.
- Album list did require admin permissions, not just photographer.

## 2023.10.1 - 2023-10-05

### Added

- Added a link between team list and waiting list on the site.
- Team registration confirm emails now contain list of contestants.

### Fixed

- Venues are now ordered correctly on the admin dashboard.
- Fixed an error when trying to edit teams that use normal registration flow.

## 2023.10 - 2023-10-03

### Changed

- Updated translations for CS, PL.

### Fixed

- Country administrator can now edit his venues.

## 2023.9.4 - 2023-09-29

### Added

- Added option to modify registration flow and hook special requirements into the
registration

### Changed

- Updated translations for SK, CS, ES, PL, NL languages

### Fixed

- Venue edit for country administrators caused a server error

## 2023.9.3 - 2023-09-24

### Added

- Added link to the old archive at the end of current archive
- Added date of the competition and registration start to the homepage
- Added option to view larger photos in albums
- Added option to upload PDF with problems to the archive

### Changed

- Moved venue related actions under Venues in the admin interface
- Results data is squashed after the competition ends

### Fixed

- Fixed edit links in content block admin
- Errors in admin's team edit form are now shown
- Fixed "Sever Error" when selecting a competition and changing branches

## 2023.9.2 - 2023-09-06

### Fixed

- Problem ordering in archive, finally
- Problem generation when problems already exist

## 2023.9.1 - 2023-09-05

### Fixed

- Problem ordering in archive
- Stats tried calculating data for non existent problems

## 2023.9 - 2023-09-04

### Added

- Public archive with results, problems, stats and photos
- Current competition state
- School editing
- Option to hide school from public selector
- Option to hide language from country selector
- Competition and category editing
- Link to admin pages from frontpage when logged in
- Option to finalize competition - mark results as public, generate stats and prevent further changes
- Problem number generation

### Changed

- Venue editing interface
- Login session to the admin system is now shared between branches
- All emails are now sent asynchronously in the background
- Admin sidebar now scrolls only the menu part
- New and improved admin dashboard

### Fixed

- `web_start` is now honored when selecting current competition on the frontpage
- Admin now disallows you to create pages and blocks with invalid country-language combinations
- 

## 2023.4.6 - 2023-04-20

### Changed

- Updated translations for live view

## 2023.4.5 - 2023-04-20

### Added

- Math 2023 senior barcode fix

### Changed

- Redesigned live view

## 2023.4.4 - 2023-04-17

### Added

- Registration and confirmation date in admin
- Export school names and addresses separately
- Admin interface for manual team review
- Option for undoing a scan

## 2023.4.3 - 2023-04-14

### Added

- Link to admin dashboard
- Preparations for editing the result rows

### Changed

- Email sending now preloads some data to speed up the process
- Team numbers are assigned in random order

### Fixed

- Team list filtering

## 2023.4.2 - 2023-04-13

### Added

- Ability for admins to edit team numbers
- Link to number assignment page from team list
- Team export in admin

### Fixed

- Count of registered teams on admin dashboard
- Email campaign creation did not save selected venues

## 2023.4.1 - 2023-04-11

### Added

- Importer for legacy Romanian schools

### Fixed

- Admin can no longer create multiple pages with the same slug in the same country/langauge.

## 2023.4 - 2023-04-06

### Added

- Importer for Wales schools

### Changed

- Images on math homepage
- Table column names on admin homepage

### Fixed

- "Teams from school" number in waiting list

## 2023.3.2 - 2023-03-19

### Added

- Venue management interface in admin
- Cache busting for the CSS file

### Changed

- Estonian translations
- Math homepage map
- Schools are now indexed implicitly

## 2023.3.1 - 2023-03-18

### Added

- German translations
- Estonian translations
- Default team ordering
- Website analytics
- Team change history
- Generation of PDF team lists
- Support for RTL
- Language select field in team registration
- Import some schools from old website

### Changed

- Polish translations
- Wording of some texts in the admin interface

### Fixed

- Admin can now register teams at any time
- IntegrityError when creating content blocks

## 2023.3 - 2023-03-02

### Changed

- ?showblocks now also shows links for missing blocks

## 2023.2 - 2023-02-25

### Added

- Persian translations

### Changed

- Django admin titles

### Fixed

- Grade display in readonly team edit form
- Results view executing many SQL queries

## 2023.1 - 2023-01-18

### Added

- Add Django Silk

### Fixed

- Permission check in results announcement
- Disable autocomplete in problem scanner
- Page filtering by country

## 2022.12.1 - 2022-12-29

### Added

- Text wrapping on certificates

## 2022.12 - 2022-12-05

### Added

- Option to disqualify teams
- Support for certificate generation for team on demand

### Changed

- Ignore non-existent teams in scanning API
- New translations

- Results without `?venue_timer`

## 2022.11.11 - 2022-11-24

### Added

- Password reset form

## 2022.11.10 - 2022-11-24

### Fixed

- Problem scanning API response

## 2022.11.9 - 2022-11-24

### Added

- Support for offset result display
- API for online system problem scanning

## 2022.11.8 - 2022-11-23

### Added

- Improve phone scanner

### Changed

- Generate custom number of certificates

### Fixed

- Fix team school symbol assignment
- Send unregister notifications only to admin for this branch

## 2022.11.7 - 2022-11-20

### Added

- Generate passwords for online teams
- Support for team certificate generation
- Support for empty certificate generation

## 2022.11.6 - 2022-11-11

### Added

- Importer for schools in Belgium

### Changed

- Results announcement starts in hidden state
- Slower scrolling of live results

### Removed
### Fixed

## 2022.11.5 - 2022-11-08

### Fixed

- Team number assignment did not assign symbols correctly

## 2022.11.4 - 2022-11-06

### Added

- Link to team edit in admin waiting list
- Notify admins on team unregister
- Responsive results on mobile devices
- Responsive results on mobile devices

### Changed

- Redirect back to team search results after saving
- Change venue automatically on selector switch
- Number assignment will try to fill in gaps first
- Merger certificates into one PDF instead of zipping them

### Removed
### Fixed

- Automatic mark venue as reviewed
- Live timer overflowed after competition end

## 2022.11.3 - 2022-11-05

### Changed

- Limit barcodes to 32 characters
- Allow only 3 digits for team number

### Fixed

- Dashboard typo
- Country flags in results shrinking
- Category name on certificates

## 2022.11.2 - 2022-11-03

### Changed

- Show venue capacity on dashboard

### Fixed

- Reviewed team count on dashboard

## 2022.11.1 - 2022-11-03

### Added

- Automatic team check-in after first problem scan
- Certificate generation
- Results announcement
- Team filtering in admin
- Admin dashboard

### Changed

- Increase gunicorn request timeout

### Removed
### Fixed

- Result position number on other pages

## 2022.11 - 2022-11-02

### Added

- Operator access level
- Mark venue as reviewed when all teams are reviewed
- Confirmation for team deletion
- Show link to results on the homepage
- Live results and countdown

### Changed

- Deny scanning problems for reviewed teams
- Allow searching for team by its code
- Show more teams in admin list
- Sort teams in admin list
- New translations

### Fixed

- Email content overflow in campaign detail view
- Email campaign permission checks for global campaigns

## 2022.10.13 - 2022-10-31

### Added

- Responsive tables in admin interface

### Changed

- Hide columns in team list that the admin can't see
- Show venue selector for admin with multiple venues assigned
- Hide teams without numbers from review
- Optimized images on the homepage
- Reset team number on school or venue change

### Removed
### Fixed

- Team number assignment
- Team contestant deletion in edit form

## 2022.10.12 - 2022-10-29

### Added

- Team number assignment
- Show team IDs in admin team list

### Changed

- Disallow scanning problems before competition and after venue review

### Fixed

- `None` in team names
- Disallow saving teams without school in admin

## 2022.10.11 - 2022-10-27

### Added

- Competition results generation
- Team deletion from admin interface
- Email campaign system
- Team school change in the admin interface
- Venue review interface

### Changed

- New translations

### Fixed

- Order of schools in search results
- Public waiting list ordering

## 2022.10.10 - 2022-10-23

### Added

- Automatic waiting list management after team unregister
- Photo consent in admin interface
- Importer for Spanish bachillerato schools
- Problem scanning interface in admin

### Changed

- Improved school search
- Team sorting in public team list

### Removed
### Fixed

## 2022.10.9 - 2022-10-20

### Added

- Option to ignore missing content blocks
- Empty content block to bottom of registration page
- Support for multiple venues/countries per admin user

### Changed

- Order of logos in the footer
- Display of timezone in the page footer
- New translations

### Fixed

- Display of school name in admin team list

## 2022.10.8 - 2022-10-17

### Added

- MŠMT notice to Junior footer
- User management in admin interface

### Changed

- Increased paddings on Junior homepage

## 2022.10.7 - 2022-10-14

### Added

- Email notification when team is moved from the waiting list

### Changed

- New translations

### Fixed

- From email address for server errors
- Country detection for some weird IP addresses
- Team edit page returned server error when accessed with invalid link

## 2022.10.6 - 2022-10-11

### Added

- Responsive navbar on mobile devices
- Menu items management in admin
- `hreflang` in country selector
- Importer for schools from Netherlands

## 2022.10.5 - 2022-10-11

### Added

- Error reporting emails
- Sponsor's and organizer's logo management in admin

### Fixed

- Team deregistration resulted in server error
- Remaining venue capacity was calculated with teams on waiting list

## 2022.10.4 - 2022-10-08

### Added

- Importer for high schools in Hungary
- Team editing to admin interface
- Checked in team status
- Button to move team from waiting list on edit page
- Button to re-send confirmation email
- Team search in admin
- Password change form in admin

### Changed

- Hide logo titles in footer when no logos are displayed

### Fixed

- GDPR link in registration page
- Czech schools importer

## 2022.10.3 - 2022-10-04

### Changed

- New translations
- Ordering of pages, content blocks and teams in admin interface
- Show venue category in venue selector

## 2022.10.2 - 2022-10-03

### Changed

- Show full names of branches in the top menu

### Fixed

- 404-page handler
- Waiting list calculation per category

## 2022.10.1 - 2022-10-03

### Added

- "From" email address is loaded from environment
- Validation of selected grade on registration
- Import tool for high schools in Poland
- Waiting list - admin and public views

### Changed

- Design for Chemistry homepage
- Design for Physics homepage
- Use SVG logos on frontend
- Merge logo models for partners and organizers

## 2022.10 - 2022-10-02

### Added

- GDPR link in footer

### Changed

- UI for Django messages

## 2022.9 - 2022-09-30

### Added

- Versioning scheme
