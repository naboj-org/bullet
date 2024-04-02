# Permissions

Every account with access to the administration system can have different access permissions. These can be edited in
the [“Users” page](/admin/users/) of the administration interface.

There are two types of permissions:

* **Branch permissions:** These are bound to the whole branch (Math, Physics…) and are persisted between competition
  years.
* **Competition permissions:** These are bound to a given competition (Math 2023, Physics 2024…) and do not persist
  between competition years.

## Branch Permissions

* **“Allow access to content management”:** This allows the user to access all admin pages in the “Content” section.
  This includes access to edit page content, menu items, and others.
* **“Photo management”:** This allows the user to upload and manage photos in the album section of the website.
* **“Is branch administrator”:** This allows the user to access and manage everything in the current branch (excluding
  the 2 prior options, which must be granted separately).

## Competition Permissions

There are two main types of competition permissions: Venue administrator and Country administrator. These are granted
using the “Venue administrator in” and “Country administrator in” options and are mutually exclusive.

A venue administrator can manage everything (teams, email campaigns, problem scanning…) in his/her venue(s).

A country administrator has all the permissions that a venue administrator with all venues of a given country/countries
would have. Moreover, he/she can also create new venues and manage schools in their country.

There are two additional options that can be selected when granting competition permissions:

* **“Can delegate permissions”:** This allows the user to grant the same (or lower) permissions to another user. This is
  useful to allow country administrators to create and manage accounts for their venue administrators. It is also useful
  to allow venue administrators to create more accounts for their helpers and operators.
* **“Limit to operator access”:** This limits the user access to operator actions. The operator is designed to only
  allow access to the most important functions, while limiting access to potentially sensitive data and destructive
  features. The operator can do team check-in, problem scanning and review.
