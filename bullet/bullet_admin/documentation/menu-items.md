# Menu items

Menu items are the links in the public website's menu, on both desktop and
mobile. Open **Menu items** under Content in the sidebar to manage them. You
need to be a country administrator or higher.

All competition editions in the current branch share the same menu items.
Saving an item changes the public menu immediately.

## Adding a link

1. Open **Menu items** and click **New menu item**.
2. Fill out the details:

   - **Title:** The label visitors see, for example "Rules".
   - **URL:** The link destination. Its format depends on **Is external**, as
     explained below.
   - **Order:** Position in the menu. Lower numbers appear first. Use different
     numbers, such as 10, 20 and 30, to leave room for later additions.
   - **Is external:** Whether to use the URL exactly as entered instead of adding
     the current country and language prefix.
   - **Is visible:** Whether to show this item in the public menu.
   - **Language:** The language of the menu label and the website version where it
     should appear.
   - **Countries:** The countries where the item should appear. Select at least one.
     The language must be enabled for every selected country.

3. Click **Save**.
4. Open the public website for the country and language you selected. Check
   that the link appears and opens the right destination.

A menu item appears only when its language and one of its countries match the
visitor's website version and **Is visible** is checked. Create separate menu
items for translated labels or different country-specific destinations.

## Internal links

Leave **Is external** unchecked for a page or built-in screen within the same
country/language version of the website.

Enter the destination without a leading slash or country/language prefix:

- `rules/` for a [page](/admin/documentation/pages/) with URL identifier `rules`.
- `register/` for registration.
- `teams/` for the team list.
- `archive/` for the competition archive.

For example, an English item shown in Slovakia with URL `rules/` links to
`/sk/en/rules/`. The country prefix follows the visitor's selected country, so
you can use one item for several countries if the destination exists in all
of them.

Create the destination page separately. Adding a menu item does not create
a page, and creating a page does not add it to the menu. Check that both exist
and that their country/language settings match.

## External or direct links

Check **Is external** to use the URL unchanged. Usually this is a complete
address, such as `https://example.org/`.

You can also use this option for a direct link to an uploaded file or a specific
country/language path. For example, paste a PDF's public address from the
[file browser](/admin/documentation/file-browser/). **Is external** only controls
how the website builds the URL. It does not make the link open in a new tab.

## Editing, hiding and deleting

Use the edit icon to change an item's label, destination, order or availability.
Uncheck **Is visible** and save to hide a link without deleting it. You need
to show or hide menu items yourself. Unlike page blocks, they cannot change
visibility automatically with the competition phase.

Use the delete icon in the list or **Delete menu item** on its edit screen to
remove the link. Deleting or hiding a menu item does not delete or restrict access
to its destination. Visitors can still open the page directly or through other
links. If you change a page's URL or delete a page, update its menu items too.
The system does not update them automatically.
