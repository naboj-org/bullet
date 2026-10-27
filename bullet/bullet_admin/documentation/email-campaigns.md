# Email campaigns

Use email campaigns to send instructions or reminders to team contacts. By default, each matching team receives a separate message at its contact email address. If one contact registered several teams, they may receive several emails. Check "Send only to unique email addresses" to send one message per contact address instead.

Open "Email campaigns" in the sidebar and create a new campaign. Check that you have selected the correct competition first.

## Who can send campaigns

Branch administrators can create campaigns for the whole competition. Country administrators must limit campaigns to their countries or venues within those countries. Venue administrators must select their venues and cannot edit country-targeted campaigns.

Only branch administrators can leave both the country and venue filters blank. Other filters, such as language or status, do not replace this scope requirement.

## Choosing recipients

The selection form has filters for country, language, venue, status and number of contestants. A blank filter adds no restriction. Within a filter, teams can match any selected value; between filters, they must match all the restrictions.

For example, selecting a venue, "Registered" status and English includes only registered teams at that venue whose chosen problem language is English. To include teams that have already checked in, select "Checked in" too.

Enter contestant counts as a comma-separated list, such as `0, 1, 2`, to reach teams with any of those counts.

Save the campaign, then open "List teams" on its detail page. Review the recipients, select "Exclude?" for any teams you do not want to contact, and save the exclusions.

With "Send only to unique email addresses" checked, addresses are deduplicated after applying all filters and team exclusions. Differences in letter case are ignored when deduplicating addresses. The recipient count shows unique addresses rather than teams. Excluding a team does not exclude its address if another selected team uses it.

Recipient selection is live, not a saved snapshot. Teams can enter or leave the selection as they register, check in or change details. Review the list again just before sending.

## Writing the message

Enter a subject and write the message template. The body supports Markdown and Django template syntax. Available variables include:

- `{{ team.display_name }}` for the full team name.
- `{{ team.school }}` for the school.
- `{{ team.contestants_names }}` for contestant names.
- `{{ edit_link }}` for the team's private edit link.
- `{{ team.code }}` for the team shortcode.
- `{{ team.id }}` for the database ID.
- `{{ team.online_password }}` for an online team's password.

When "Send only to unique email addresses" is checked, neither `team` nor `edit_link` is available. Write a generic message without team-specific details or private links.

For example, when sending one email per team:

    Hello {{ team.display_name }},

    Please arrive at the venue by 08:30. Bring your school ID.

    Check your contestant details before the competition:
    [Edit team details]({{ edit_link }})

Replace the arrival time and instructions with those agreed for your venue. Write separate campaigns if you need different language versions.

Treat private edit links and online passwords as confidential. Do not copy them into public pages or shared recipient lists.

## Testing and sending

1. Save with "Save without sending".
2. Review the recipient count and "List teams".
3. Click "Send testing email".
4. Check the message in the inbox of your organiser account.
5. Review the selection once more, then click "Send campaign".

The test sends the email to your organiser account, not to a team. In per-team mode it uses the first matching team's details. In unique-address mode it omits `team` and `edit_link`, just like the actual campaign. Testing and sending are unavailable when the campaign has no matching recipients.

Sending queues the emails in the background. The success message and last-sent time record the send action; they do not confirm that every message has arrived.

You cannot recall sent emails. Sending the campaign again queues another message for every currently selected team (or unique address when that option is checked), including recipients contacted by the previous send. Do not click again just because delivery is taking time.

Replies go to each team's venue contact address, with the country's default address used when the venue has no email configured.

## Common problems

### No recipients

Check for conflicting filters, excluded teams and the selected competition. A "Registered" filter excludes waiting, unconfirmed and checked-in teams. Remove only the restrictions you actually want to change.

### You cannot edit or send

Check the campaign's country and venue scope. A campaign may be visible to you without being editable if it also targets countries or venues outside your permissions. Ask the appropriate country or branch administrator to handle it.

### The test or campaign does not arrive

Check spam and the destination address. Tests go to your organiser account; campaigns go to team contact addresses. If messages still do not arrive, contact IT support with the campaign details so they can check the background queue and delivery errors.
