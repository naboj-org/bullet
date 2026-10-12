# Waiting list

A confirmed team goes on the waiting list if the venue is full, its school has reached the category limit, or it confirms after registration closes. Waiting teams do not have a place in the competition yet.

Open "Venues", select a venue and open "Waiting list". The page shows the remaining capacity, waiting teams and their school counts. Venue administrators can manage their own venues; country and branch administrators can manage venues within their scope.

## How the order works

The waiting list is not ordered only by registration time. The system first sorts teams by their corrected school count, then by confirmation time.

The school count includes competing teams and earlier-confirmed waiting teams from the same school in the same category, across all venues. Category-specific wildcards reduce the count used for ordering. The page shows this as "Teams from school" and, where applicable, the wildcard adjustment.

This means a school's first team can appear ahead of another school's additional team, even if the additional team confirmed earlier. The date displayed in the table is the form submission date; confirmation time is what breaks ties in the ordering.

## Moving eligible teams automatically

1. Check the venue's capacity and the category's current school limit.
2. Open the venue's "Waiting list" tab.
3. If places are available, click "Move automatically".
4. Confirm the action, then review the list.

The system fills available places in waiting-list order, subject to the current school limit. It stops when the remaining places are filled or the next team's corrected school count exceeds the limit. Each promoted team receives an email.

The automatic move uses the second-round limit once that round begins. After registration ends, the system treats the school limit as unlimited for this action. Venue capacity still applies. Check local rules before promoting teams after the deadline.

## Moving teams between registration rounds

At the transition to the second registration round, a branch administrator should use the global "Move waiting lists" action in the sidebar. This runs the automatic move for every venue in the competition, so organisers do not have to process each waiting list separately.

1. Check the configured second-round start time and school limits.
2. Once the second round has started, open "Move waiting lists".
3. Confirm with "Move automatically".
4. Allow the background job to finish, then review the venue waiting lists.

Run the action after the second-round start time, not before: it uses the rules in effect when it runs. Opening the second round alone does not promote existing waiting teams.

The global move respects each venue's capacity and the current school limits. Promoted teams receive an email; teams that still do not qualify remain on the waiting list.

## Moving one team manually

The "Move" action beside a team promotes it and sends an email to its contact. This manual action bypasses the capacity and school-limit checks.

Use it only for an agreed exception. Check that the venue can accommodate the team and that you have approval to override the rules. Operators cannot promote waiting teams.

## When a place becomes free

If a competing team unregisters through its private link while registration is open, the system can promote the first waiting team if it meets the school-limit check.

Do not assume that every cancellation or capacity change will fill the vacancy automatically. Review the waiting list after an administrator deletes a team, after increasing capacity, and when the second registration round starts. Run "Move automatically" if eligible teams are still waiting.

## If a team does not move

Check:

- The venue still has free places.
- The team has confirmed its registration. Unconfirmed teams are not on this list.
- Its corrected school count fits the current limit.
- You are viewing the right competition and venue.

Promotion and confirmation are separate from [check-in](/admin/documentation/check-in/). Once a team has a place, assign it a number before generating its [tearoffs](/admin/documentation/tearoffs/).
