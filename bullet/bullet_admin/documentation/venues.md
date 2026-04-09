# Creating new venue

1. Navigate to "Venues" in the sidebar.
2. Click on "New venue" button.
3. Fill out venue details:

- **Barcode prefix:** This will be used in the problem barcodes. Only uppercase
  letters. Use 5 letters: 2 for country, 2 for city, 1 for category.
  For example: category junior in Bratislava, Slovakia would be "SKBAS".
  Náboj Junior does not have the last letter as it has just one category.
- **Place:** The name of the venue (e.g., "Bratislava"). Should not contain the
  category name.
- **Category:** Select the competition category this venue belongs to (Junior, Senior).
- **Email:** Contact email for this venue. Responses to automatic emails from this
  venue will be sent there. If left blank, the country's default email will be used.
- **Address:** Physical address of the venue.
- **Country:** The country where the venue is located.
- **Capacity:** The maximum number of teams that can register for this venue.
  Teams registering beyond this limit will be placed on the waiting list.
- **Accepted languages:** Select the languages that teams can choose when registering
  at this venue.
- **Local start:** *Optional.* The local start time for this venue in YYYY-MM-DD
  HH:MM:SS format.
  If left blank, the global competition start time will be used. Time is in UTC.
- **Online venue:** Check if this is an online venue (no physical location).
- **Isolated results:** If checked, teams from this venue won't be shown in country-wide
  and international results. Useful for practice venues or test runs.
- **Registration flow:** The registration flow type to use for this venue.
  Only change this if you know what you're doing.

## Barcode prefix rules

The system enforces several validation rules for the barcode prefix:

- Must contain only uppercase letters
- Must be unique within the competition
- Must start with the country code (e.g., "SK" for Slovakia, "CZ" for Czech Republic)
- For normal categories: must be exactly 5 characters and end with the category
  identifier (e.g., "S" for Senior)
- For Náboj Junior: must be exactly 4 characters (no category identifier)
