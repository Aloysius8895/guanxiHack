# Rover images and title layout

**Goal:** Use the 14 supplied original images in their corresponding rover cards and prevent the homepage heading from overlapping its subtitle.

**Design:** Preserve the existing cards and interactions. Map the six component cutouts and eight scenario images by their labels. Keep cutouts fully visible. Let the homepage title determine its container height, removing the obsolete overlapping mask layers in this title only.

**Architecture:** A small BeautifulSoup helper updates current pages and is called by the existing page generator. Scoped CSS handles image sizing and title flow.

**Tech stack:** Static HTML, CSS, Python, BeautifulSoup.

- [x] Save the original attached images with descriptive filenames.
- [x] Update cards in both technology routes, including expanded views.
- [x] Add scoped layout rules and integrate them into the rebuild script.
- [x] Verify image loading, expanded cards, and title/subtitle separation at desktop and mobile widths; save screenshots.
