# Teams

## Team List

The system provides a list of all registered teams. You always see a list of teams that are determined by your access
permissions. Teams can be filtered based on country, venue, or status. There is also a full-text search available.

_Unfortunately, searching through contestant names is currently not possible._

The table offers the following columns:

* **Number:** This column contains the assigned team number (the number that will be printed on the barcodes, if
  assigned) and a team ID (number prefixed with #). When communicating with IT support, please provide them with the
  team ID.
* **School:** The name and address of the team's school. This column also contains the school team identifier (A, B, C…)
  used to identify different teams from the same school.
* **Contact information:** The name, phone number and email of the person who registered the team. Phone number is not a
  required field, so it may be omitted. _The phone number and email are not shown to operators._
* **Contestants:** The list of the contestants' names.
* **Venue / Category:** The venue and category of the team. This column may be omitted if you only have access to a
  single venue.
* **Status:** The current status of the team (see below). This column also indicates their consent to taking photos
  during the competition.

### Team Statuses

* **Unconfirmed:** The team did not confirm their registration yet. This is done by clicking a link that was delivered
  by email upon registering.
* **Waiting list:** The team was placed on the waiting list due to insufficient venue capacity or due to hitting the
  per-school team limit.
* **Checked in:** The team was marked as checked in at and is present at the venue.
* **Reviewed:** The team's problem tear-off was reviewed.
* **Registered:** The team is registered for the competition.
* **Disqualified:** The team was marked as disqualified and will not be shown in any results.

## Assigning Team Numbers

When the registration closes, and you want to start printing the problem tear-offs, you should assign team numbers using
the “Assign numbers” button.

This will assign numbers 001, 002, 003… to the teams with the “Registered” status. If the teams change after this (for
example because someone unregisters), you can assign the numbers again. The system will by default try to fill in any
gaps in the numbering sequence.

There is also an option to force reassignment for all teams, which will reset the numbering altogether. This can be
useful in some situations, but beware that this will entirely change the team numbers, which can introduce difficulties
if you already have any materials printed out.

## Exporting Teams

There is also the option to export all teams to CSV/JSON/YAML format. You can filter which teams you want to export.
This filter is the same as the one on the team list page.

## Editing Teams

The team editing interface is pretty straightforward. Herein, we point out some important notes about team editing:

### Operators and Editing

An operator has limited ability to edit teams. Operator does not have access to view or edit the following fields:
* School
* Venue
* Contact's name, email, and phone number
* Team number
* Disqualified flag

### Changing Team Numbers

You can change team number manually. This can be used to use backup problem tear-off for a team by changing their number
to 999 (or whatever is used on the backup tear-off). Keep in mind that team numbers must be unique, and the system will
enforce such constraint (this can be an issue when you want to swap a team number between two teams).

Also note that when changing the team's venue, the system will keep the team's number. If that number is already
assigned to another team in the destination venue, the system will disallow such edit.

### Changing Team Status

The system allows you to change team status in some instances, like moving the team from the waiting list to the
competition. The system allows you to do so even if it is against the competition rules.
