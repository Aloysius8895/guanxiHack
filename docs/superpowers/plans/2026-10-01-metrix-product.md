# MetriX AI Product Content Implementation Plan

**Goal:** Adapt the existing site to MetriX AI without changing its web design.

**Architecture:** Apply source-controlled content mappings to existing HTML text and image slots. Preserve original classes, animation hooks and stylesheets. Store pre-edit HTML in verification/product-before for reproducibility and rollback.

**Tech Stack:** Existing HTML/CSS/JavaScript, Python/BeautifulSoup content migration, existing Three.js rover demo.

## Global Constraints

- Preserve existing web design, cave animation, layout and interactions.
- Use only supported facts from the supplied product introduction.
- Keep existing English typography and use the document's English product terminology.
- Preserve unrelated user changes and original rover source.
- No publication or external form submissions.

### Task 1: Content and asset adaptation

- [x] Snapshot current HTML; retain the original embedded image from the supplied DOCX.
- [x] Create `tools/adapt_product.py` with explicit copy mappings and page-specific content replacement; run `python tools/adapt_product.py`.
- [x] Replace equipment imagery and old partner logos within existing slots. Preserve selectors and stylesheet contents.
- [x] Adapt all linked pages, metadata and contact destinations; retain existing routes and page transitions.

### Task 2: Rover integration

- [x] Copy the existing model to `site/rover/index.html`, use local Three.js modules, and replace prototype-editor copy with product descriptions.
- [x] Link the existing technology-page CTA to the standalone demo; retain its existing controls.
- [x] Provide the original supplied product introduction through the contact page; contact form produces a local enquiry brief because no recipient was supplied.

### Task 3: Verification

- [x] Check that stylesheet hashes, page classes and animation hooks match the snapshot except documented content-specific replacements.
- [x] Check all local resources, internal links, metadata and stale company claims.
- [x] Run HTTP and JavaScript syntax checks; test interaction and appearance if browser becomes available.
- [x] Record results in `verification/product-report.json` and provide local preview URL.
