# Pages and page blocks

Use pages to write the homepage, rules and other information for participants.
Open **Pages** under Content in the sidebar to manage them. You need to be a
country administrator or higher.

Pages belong to the current branch (e.g., Náboj Physics). All competition
editions in that branch share the same pages, so switching editions does not
create a new set. Saving a page changes the public website immediately. You do
not need to publish it separately.

## Creating a page

1. Open **Pages** and click **New page**.
2. Fill out the page details:

   - **Title:** The page title. For a simple text page, this is also the heading shown
     above its content.
   - **URL:** The short identifier after the country and language in the website
     address. For example, `rules` gives `/sk/en/rules/`. Enter only the identifier,
     not the full address. Use letters, numbers, hyphens or underscores, without
     spaces or slashes.
   - **Language:** The language of this version of the page.
   - **Countries:** The countries where this version should be available. Select
     at least one. The chosen language must be enabled for every selected country.
   - **Content:** The page text, using Markdown, unless you plan to use page blocks.

3. Click **Save**.
4. Use the view icon in the page list to open the public page. This opens it for
   the first country listed. Check other country versions separately if needed.

The same URL can have separate pages for different languages or countries.
Two pages in the same branch cannot use the same URL and language if they
share any selected countries.

A page shared by several countries has the same content in all of them. To use
country-specific text, create separate pages with the same URL and language but
different country selections, with no country selected on both pages. Create
a separate page for each translation too.

Creating a page does not add it to the navigation menu. Add a
[menu item](/admin/documentation/menu-items/) separately if visitors should be
able to find it there.

### The homepage

The page with URL identifier `_homepage_` is the homepage at
`/<country>/<language>/`. Edit that page to change the homepage for its selected
countries and language. Opening `/<country>/<language>/_homepage_/` redirects to
that homepage.

Do not use identifiers that belong to built-in screens, such as `register`,
`teams`, `live` or `archive`. A page with one of these identifiers will not
replace the built-in screen.

## Writing a simple text page

For rules or other text-heavy pages, use the **Content** field without adding
page blocks. Common Markdown syntax includes:

```markdown
## A section heading

**Bold text** and _italic text_.

- First item
- Second item

[Link text](https://example.org/)

![Image description](/uploads/files/physics/information/photo.jpg)
```

For files and images, copy the public address from the
[file browser](/admin/documentation/file-browser/). Replace the example image
address above with your file's address.

## Building a page with blocks

Page blocks divide a page into sections with different layouts. They are useful
for homepages, sponsor lists and illustrated information pages.

1. Open the page using its edit icon.
2. Click **Page blocks**, then **New block**.
3. Select **Visibility**, set **Order**, and choose a **Block type**.
4. Save. This opens the block's content form.
5. Fill out the content and save again.

On the block list:

- **Edit content** changes text, images and the other fields for that block type.
- **Settings** changes visibility and order. You cannot change the block type
  here. Create a new block if you need a different layout.
- **Delete** removes the block after confirmation.

Blocks appear in ascending **Order**. Use different numbers, such as 10,
20 and 30, to leave room for another block later.

When at least one block is visible in the current competition phase, the page
shows those blocks instead of the page's **Content** field and title heading.
Add a **Main header** block if you want a large heading at the top.
If no blocks match the phase, the page shows its title and **Content** instead.
This also applies when the editor warns that Content is ignored because the
page has blocks.

### Available block types

- **Main header:** A large heading with introductory text, an optional image and
  an optional button. Set both **Button label** and **Button link URL** when using
  the button.
- **Markdown text:** A section with an optional title and introductory text,
  followed by Markdown **Content**.
- **Text with image on side:** Text alongside an image. Choose whether the image
  appears on the left or right on large screens. An optional button can link to
  another page.
- **Grid with icons:** A collection of titles and descriptions with icons.
  Use an icon identifier such as `mdi:account-group`. The **Icon** field has a
  link to the icon catalogue. Set each item's **Order** to arrange the grid.
- **Grid with images:** Images with titles and descriptions in a grid that
  adapts to the screen size. Items appear in their form order.
- **Logo cloud:** Linked logos, for example for sponsors. Each item has a **Name**,
  **Image** and **Link URL**. Choose the alignment and logo size for the section.
  Larger size values make logos taller. Set each item's **Order** to arrange
  the logos.
- **Competition timeline:** Automatically displays the current public
  competition's registration start, optional second-round start, registration
  end and competition day. Update these dates in competition settings, not in
  the block. The competition selected in the admin switcher does not determine
  which edition the public timeline uses.

Most section types have **Background** (white or the branch colour) and
**Spacing** (normal or half) settings. The title and introductory text fields
are separate from Markdown Content and do not format Markdown.

For blocks with multiple items, fill in the available item rows and use each
item's **Delete** checkbox to remove it when saving. There are four extra empty
rows each time you open the form, so save and reopen it to add more items.

Use **Select file** for image fields. Upload images through the
[file browser](/admin/documentation/file-browser/) first.
The website uses button and logo links exactly as you enter them. It does not
add a country/language prefix. Use a full `https://...` address or a website
path such as `/sk/en/register/`.

### Showing different content during the competition cycle

Under **Visibility**, select every phase where you want the block to appear.
The block list shows a check or cross for each phase.

- **Before web start:** Before the edition's Web start date.
- **Before registration:** From Web start until registration opens.
- **Registration:** From registration start until registration end, including
  both registration rounds if a second round is configured.
- **After registration:** After registration closes and before the competition.
- **Competition:** From competition start until its duration has elapsed.
- **After competition:** After the competition ends, before results are published.
- **Locked:** After the competition ends and results have been published/locked.

The public website uses the branch's most recent competition whose **Web start**
has passed. Selecting another edition in the admin does not change this. A
future edition will only appear after its Web start.
Previewing another phase does not switch editions or change the timeline dates.

For example, show a registration invitation before and during registration, then
show a different block with competition-day instructions after registration.

When logged in, a block-based public page has a **View page during:** selector at
its bottom right. Use it to preview other phases. Choose **(real)** to return to
the actual phase. This only changes your preview, not what other visitors see.

## Copying content from another page

1. Create or open the destination page.
2. Click **Copy from...**.
3. Select the source page and submit the form.
4. Edit the copied text and blocks as needed, for example to translate them.

**Copying replaces the current page's Content and deletes its existing blocks.**
It copies all blocks from the source page, with their content, order and
visibility settings. The current page keeps its title, URL, language and countries.
Do not select the current page as the source.

You can edit either page without changing the other. Both pages still use the
same uploaded images, though. Replacing one of those files changes the image
on both pages.

## Deleting a page

Use the delete icon in **Pages** and confirm the deletion. This also deletes all
of the page's blocks, but does not delete uploaded files or menu items. Remove or
update any menu items and other links that pointed to the deleted page.
