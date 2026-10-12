# Registration

## How registration works

Registration opens and closes at the dates set on the competition. A team chooses a category, venue and school, then fills in contact details and contestant names. The available problem languages depend on the venue.

Submitting the form creates an unconfirmed team and sends a confirmation email to its contact address. The team must open the link in that email to confirm its registration. Submitting the form alone does not reserve a place.

When the contact opens the link, the system checks the venue capacity and the current per-school limit for the category. It counts teams from the same school across all venues in that category, not just the selected venue. Wildcards can allow extra teams.

If both checks pass while registration is still open, the team becomes registered. Otherwise, it goes on the [waiting list](/admin/documentation/waiting-list/). A team that confirms after registration closes also goes on the waiting list.

The second registration round uses the category's second-round school limit. It does not increase venue capacity or, by itself, move existing waiting teams into the competition.

## Before registration opens

Branch administrators set the registration dates and category rules. Country and venue administrators should check the settings for their venues:

- Capacity matches the number of teams the venue can accommodate.
- Accepted languages include the languages you can provide on paper.
- The venue's contact email is correct. Replies to team emails go there, or to the country's default address if the venue email is blank.

See [competition setup](/admin/documentation/competition-init/) and [venue setup](/admin/documentation/venues/) for the settings.

## Helping a team

Open "Teams" and filter by venue or status. Search for the school or contact details rather than contestant names, which the search does not support. Open the team's edit page to check its contact email, contestants and status.

A confirmed team can normally use its private email link to change details until the competition starts or the team checks in. Some registration flows restrict this further. For example, the Spanish flow does not allow teams to edit their own details.

Treat the private link as a password: anyone with it can access the team's page.

### The confirmation email did not arrive

1. Find the team and check that it is still unconfirmed.
2. Check the contact email for spelling mistakes and correct it if needed.
3. Ask the contact to check their spam folder.
4. On the edit page, click "Re-send confirmation email".

Emails are sent through a background queue, so they may not arrive immediately. If resending does not help, contact IT support with the team ID shown with a `#` prefix. Do not ask the team to register repeatedly, as this can create duplicate entries.

### The team is on the waiting list despite free places

Check the number of competing teams from its school in the same category, including teams at other venues. The school limit can block registration even when the selected venue has free places. Late confirmation is another reason.

Use the [waiting-list page](/admin/documentation/waiting-list/) to review eligibility and move teams.

### A school or language is missing

For a missing school, ask the person responsible for the school database to check the school's record. Avoid choosing an unrelated school just to finish registration: this affects school limits and results.

For a missing language, ask a venue administrator to check the venue's accepted languages. Add it only if the organisers can provide the required problem statements.

## Creating a team as an administrator

Administrators can create a team from the "Teams" page. The "Send confirmation e-mail" option controls whether the contact must confirm by email. If you leave it unchecked, the system confirms the team immediately. Administrative creation does not run the public registration capacity and school-limit checks, so check those rules yourself before adding a team.

Use this for registrations you have agreed with the team, and check the resulting status before promising a place. See [managing teams](/admin/documentation/teams/) for editing, [exporting teams](/admin/documentation/team-export/) for downloads, and [tearoffs](/admin/documentation/tearoffs/#assigning-team-numbers) for number assignment.
