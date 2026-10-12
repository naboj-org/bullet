# Managing teams

## Team list

Open "Teams" to view the teams within your access permissions. You can filter by country, venue or status, or use the full-text search.

Searching contestant names is not supported. Search by school or contact details instead.

The table shows:

* Number: the assigned team number used on printed barcodes and the database ID prefixed with `#`. Give IT support the database ID when reporting a problem.
* School: the school's name and address, plus an identifier such as A, B or C to distinguish teams from the same school.
* Contact information: the name, email and optional phone number of the person who registered the team. Operators cannot see the email or phone number.
* Contestants: the contestants' names.
* Venue / Category: the team's venue and category. This column may be omitted if you have access to only one venue.
* Status: the team's current status and its photo consent.

### Team statuses

* Unconfirmed: the team has not opened its email confirmation link yet.
* Waiting list: the team has confirmed but does not have a place. This can happen because the venue is full, the school limit has been reached or the team confirmed after registration closed.
* Registered: the team has a place in the competition.
* Checked in: the team has been marked as present at the venue.
* Reviewed: the team's problem tearoff has been reviewed.
* Disqualified: the team will not appear in results.

See [registration](/admin/documentation/registration/), [waiting lists](/admin/documentation/waiting-list/) and [check-in](/admin/documentation/check-in/) for those workflows.

## Editing teams

Open a team's edit page to correct its details and contestant list. Check that you have the right team, especially when a school has several entries.

### Operator permissions

Operators can edit contestant details, language, check-in and photo consent. They cannot edit:

* School
* Venue
* Contact name, email or phone number
* Team number
* Disqualification

Operators cannot see the contact email or phone number. Ask an administrator to handle changes outside these permissions.

### Changing team numbers

An administrator can change a team's number manually. For example, if you give a team a backup tearoff set numbered 999, change its saved number to 999 before it uses the set.

Numbers must be unique within a venue. The system rejects duplicates, so swapping two teams' numbers may require a temporary unused number.

Moving a team to another venue keeps its number. If that number is already in use at the destination, you must resolve the conflict before saving.

For initial assignment and reassignment before printing, see [assigning team numbers](/admin/documentation/tearoffs/#assigning-team-numbers).

### Changing team status

Administrators can move teams from the waiting list into the competition even when doing so exceeds capacity or the school limit. Use manual promotion only for an agreed exception. See [waiting lists](/admin/documentation/waiting-list/) for the automatic and manual options.

## Deleting teams and unregistration

Deleting a team removes its registration, contestant records and any recorded solutions and results. It is not the same as marking the team absent or disqualified, and there is no undo button. Check that you have the right team before confirming.

### When a team unregisters itself

A team can unregister through its private email link before the competition starts, provided it has not checked in. It must confirm the removal on the "Unregister team" page. After check-in or the competition start, self-service unregistration is blocked.

While registration is open, removing a team that is not on the waiting list can trigger promotion of the first waiting team at the same venue. The system checks that team's corrected school count against the current limit. If it passes, the waiting team gets a place and receives an email. Removing a waiting team does not trigger promotion.

If a team unregisters after registration closes, the system emails the venue administrators. It does not automatically promote a replacement at that point. Review the [waiting list](/admin/documentation/waiting-list/) and arrange any replacement with the organisers.

### When an administrator deletes a team

Venue, country and branch administrators can delete teams within their scope while the competition is unlocked. Operators cannot delete teams.

Open the team's edit page and choose the delete action. On the confirmation page, "Send mail to contact person" is selected by default. Leave it selected to notify the contact that their team has been deleted, or clear it if you have a reason not to send that email. Confirm with "Delete team".

Administrative deletion does not automatically promote a waiting team, even while registration is open. Check the venue's waiting list afterwards and use "Move automatically" if you want to fill the vacancy under the current rules.

Unlike self-service unregistration, administrative deletion is not blocked by check-in or the competition start. Be especially careful once a team has submitted solutions: deletion removes its recorded results too. For a team excluded under the competition rules, use disqualification rather than deleting its registration and solution records.

### Paper sets after a cancellation

Set aside any tearoffs already printed for the deleted team so they are not handed out by mistake. A replacement team needs its own assigned number matching the papers it receives. See [team number assignment](/admin/documentation/tearoffs/#assigning-team-numbers) before reusing or reprinting a set.

## Related tasks

Assign numbers and prepare printed sets using the [tearoffs guide](/admin/documentation/tearoffs/). To download team data, see [exporting teams](/admin/documentation/team-export/).
