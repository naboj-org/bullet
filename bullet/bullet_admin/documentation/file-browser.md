# File browser

The file browser stores images, logos, PDFs and other files used on the public
website. Open **File browser** under Content in the sidebar. You need to be
a country administrator or higher.

All countries, languages and competition editions in the current branch share
these files. Every uploaded file has a public address, so do not upload
confidential material, such as participant personal data or unreleased
competition problems.

## Browsing and organising files

Click a folder name to open it. Use the breadcrumbs above the file list to return
to a parent folder or the root. The list shows folders first, then files,
with each group sorted by name. You can see each file's size. Click a file to
open its public address in a new tab.

To create a folder:

1. Open the folder where you want to create it.
2. Click **New folder**.
3. Enter **Name** and save. Use letters, numbers, hyphens or underscores, without
   spaces. **Parent path** shows where the folder will go. You cannot edit it.

Use descriptive folders and filenames, for example `sponsors/partner-logo.png`
or `2026/instructions.pdf`. Avoid changing an existing file's location once it
is linked from the website.

## Uploading a file

1. Open the folder where the file should go.
2. Click **Upload file**.
3. Choose the **File** from your computer.
4. Optionally fill in **Name** to choose a different filename. Include the file
   extension, such as `.png` or `.pdf`. Leave it blank to keep the uploaded file's
   name.
5. Save to upload the file to the displayed **Parent path**.

**Uploading to an existing filename in the same folder replaces that file
without a separate overwrite confirmation.** All pages and links using that
address will use the new file. A browser may still show its cached copy for
a while. Use a new filename if you want to keep both versions.

## Using files on the website

### Images in page blocks

Upload the image first, then open the relevant
[page block](/admin/documentation/pages/):

1. Click **Select file** beside the image field.
2. Browse folders in the picker.
3. Click the image to select it.
4. Save the block's content form to keep the selection.

The field shows the path within the branch's files, such as
`sponsors/partner-logo.png`. The website adds the branch's upload location
automatically. Click **Cancel** to close the picker and keep your previous
selection. You can only select existing files here. To upload a new one, open
File browser from the sidebar.

### Links and Markdown images

Click the file in the File browser and copy its public address from the opened
tab. Use that address in Markdown:

```markdown
[Download the instructions](https://math.naboj.org/path/to/instructions.pdf)

![Venue entrance](https://math.naboj.org/path/to/entrance.jpg)
```

Replace the example addresses with your files' public addresses. Do not use
the short path shown in the image picker, such as `sponsors/partner-logo.png`,
on its own in Markdown or a menu link.

To link a file from the navigation, create a
[menu item](/admin/documentation/menu-items/) with **Is external** checked and
paste the public address into **URL**.

## Deleting files and folders

Click the delete icon beside a file or folder, check the **Path** on the deletion
form, then submit it to delete the item.

**Deleting a folder also deletes all files and subfolders inside it.** There is
no recycle bin or restore action in the File browser. Make a local copy first if
you may need the files again.

Deleting a file does not remove it from pages, page blocks or menu items that
use it. Those images and download links will stop working. Before deleting a
file, check where you use it and change the image selections or links.

There is no rename or move action. To change a file's name or location, upload
it under the new name or in the new folder. Update any image selections and
links that use it, then delete the old copy.
