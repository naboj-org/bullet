# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses the `YYYY.MM[.PATCH]` version format.

## Unreleased

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
