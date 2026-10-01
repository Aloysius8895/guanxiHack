# Layout, route search and navigation implementation plan

**Goal:** Apply the approved compact spacing and independent route-search scene, remove duplicated home components, reveal descriptions on every Technology card, and restore Back/Forward scroll positions.

**Architecture:** Keep the existing page transitions and Lenis scroller. Use scoped CSS, a self-contained canvas scene, and history-entry scroll records restored after page initialization.

**Tech stack:** Existing HTML/CSS, native JavaScript canvas, Python/BeautifulSoup, Playwright.

- [ ] Reduce section gaps and CTA spacing in sections.css; verify desktop/mobile computed distances.
- [ ] Remove only the home component grid; retain Smart Rover heading and Technology entry.
- [ ] Convert all 14 Technology cards to accessible hover/focus reveal cards; expose descriptions on touch screens.
- [ ] Add route-search canvas between the mine and pilot process in both services pages: terrain grid, candidate network, weighted shortest path, orange result, traveling rover, pause and reduced motion.
- [ ] Preserve unique history entry keys and save the real Lenis wrapper offset; restore after existing transition completion. Check back, forward, repeated visits and home return.
- [ ] Verify screenshots, missing resources, JavaScript errors, mobile overflow and motion states; record results in verification.
