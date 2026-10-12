# Permissions

You can edit account permissions on the ["Users" page](/admin/users/) in the administration interface.
Permissions apply to the selected branch and competition. Check which competition is selected before editing a user's
competition permissions.

There are two types of permissions:

- Branch permissions apply to the whole branch (Math, Physics...) and persist between competition editions.
- Competition permissions apply to one competition (Math 2025, Physics 2026...) and do not automatically carry over
  to another edition.

## Branch permissions

The "Is branch administrator" option gives a user access to all administration features in the current branch,
across competition editions. Branch administrators can manage competition and category settings, create and finalize
competitions, edit website content, manage photos, and manage users.

Branch administrators do not need country or venue assignments. If you save a user with this option enabled, the form
saves their branch permissions but does not save changes to their competition permissions.

## Competition permissions

Choose either venue or country access:

- "Venue administrator in" lets you select one or more venues. The user can manage teams and venue operations at those
  venues, including team data, email campaigns, document generation, problem scanning, and review.
- "Country administrator in" lets you select one or more countries. The user has venue administrator access to every
  venue in those countries, including new venues. They can also create venues, manage schools in their countries,
  manage wildcards, and upload competition files.

A user cannot have both venue and country assignments in the same competition role.

### Content and photo management

Country administrators and branch administrators can manage pages, page blocks, content blocks, and menu items.
They can edit content throughout the branch, not just content for their assigned countries.

Venue, country, and branch administrators can manage albums and photos. Album access is not limited to their assigned
venues or countries. Country and venue administrators need their role in the selected competition to access content or
photo management. Branch administrators have access across competition editions.

### Operator access

Select "Limit to operator access" to give a user access to competition-day tasks at their assigned venues without full
venue administrator access. Select the venues where they will work. You cannot combine this option with country assignments.

Operators can:

- View teams and use the restricted team editing form, including team check-in.
- Generate documents for individual teams.
- Scan problems, undo scans, and review teams and problems when the scanning and review state allows it.
- Use results announcement tools for venues or countries they have access to, once the applicable review requirements
  are met.

Operators cannot manage user permissions, email campaigns, albums or website content, or create venues. They also cannot
use team actions reserved for administrators, such as deleting teams or moving them from the waiting list into the competition.

## Managing users and delegating permissions

Branch, country, and venue administrators can create users and edit users whose permissions are within their own scope.

- Branch administrators can edit any user in the current branch and grant or remove branch administrator access.
  Only branch administrators see the branch permission checkbox.
- Country administrators can grant country access within their assigned countries, or venue administrator and operator
  access to venues in those countries. They can edit another country administrator only if they have access to all of
  that user's countries. To edit a venue administrator or operator, all of that user's venues must be in their countries.
- Venue administrators can grant venue administrator or operator access at their assigned venues. They can edit
  another venue administrator or operator only if they have access to all of that user's venues.

Country and venue administrators cannot edit branch administrators. Administrators can also edit users who have no
branch administrator access and no country or venue assignments in the selected competition.

## Competition state restrictions

Some actions also require an unlocked competition. Once results are public, administrators cannot delete teams, move
teams into the competition, resend confirmation emails, change venue start times, or upload tearoffs.
These restrictions apply to branch administrators too.

Scanning and review have their own checks. For example, problem scanning requires the competition to have started,
and a team or venue already marked as reviewed prevents further scans and some review actions.
Operators and administrators must both meet these requirements.
