# Mine detection implementation plan

**Goal:** Replace the services Use Cases map with the two supplied template1 detection scenes, using the existing MetriX rover in a mine.

**Architecture:** A scoped sticky section drives an isolated local scene iframe. The scene combines a generated photographic mine plate with the project's original Three.js rover geometry, animated detection overlays, scanner beams, and a thermal view. Keep the surrounding site's animation runtime intact.

**Tech stack:** Existing local Three.js, HTML/CSS, browser animation frames, Python page update script.

## Constraints

- Preserve the reference's scroll-driven progression, moving detection boxes, animated scanning, thermal reveal, and rover movement.
- Keep all unrelated sections and navigation animation intact.
- Use the actual existing six-wheel articulated model; no aircraft.
- Support desktop, mobile, reduced motion, keyboard mode selection, and non-WebGL fallback.
- Identify sensor readouts as a concept demonstration.

## Tasks

- [x] Inspect template1 scene copy, local runtime and rover geometry.
- [x] Generate a mine background using the built-in imagegen tool; save to `site/_assets/metrix/mine/tunnel.webp`.
- [x] Extract original rover geometry to `site/_assets/metrix/mine/rover-model.js`, merging static meshes for rendering efficiency.
- [x] Build `mine/index.html`, `mine.css`, `mine.js` with real-time and thermal modes and scroll transitions.
- [x] Replace only `.section_projects` in both services pages; initialize through `product.js` for existing page navigation transitions.
- [x] Check served resources, desktop/mobile screenshots, scroll mode transitions, keyboard controls and browser errors.

## Background provenance

Built-in imagegen, not CLI. Prompt: Photorealistic spacious underground hard-rock mine tunnel background plate; fractured slate and mineral veins, clear grey gravel foreground for compositing the project's rover, cool work lighting, subtle amber distant lamps and dust, no robot/aircraft/people/text/overlays. Full prompt is retained in the conversation. Original generated image retained; project assets are in `site/_assets/metrix/mine/`.

## Verification

Desktop 1440?900 and mobile 390?844: live WebGL model, both modes, forward/reverse scene buttons, no horizontal overflow, no page errors. Wheel input forwards to the original Lenis container (300px verified); pause and reduced-motion controls checked. See `verification/mine-report.json` and `verification/mine-*-*.png`. The surrounding animation bundle and original rover viewer were not modified.

Mobile touch input was verified with a 200px swipe through the actual scene iframe.

## Image generation prompt

Tool: built-in imagegen. Saved assets: `site/_assets/metrix/mine/tunnel.png` (source) and `site/_assets/metrix/mine/tunnel.webp` (web version).

Generate a single photorealistic cinematic underground hard-rock mine tunnel environment BACKGROUND PLATE for a premium robotics website, landscape 1536x1024 or widescreen. NO robots, NO vehicles, NO aircraft, NO people, NO text, NO overlays. Camera about 1.8 metres above the ground, slightly tilted down, looking diagonally along a spacious 6 metre wide excavated rough rock tunnel, vanishing point around 58% across and 38% down the image. The central foreground from x 25%-65% and y 55%-85% must be a clear flat compacted grey gravel floor on which we will later composite a small real 3D rover. Very detailed fractured slate and mineral rock walls, subtle rusty copper veins, scattered angular stones concentrated along the sides. On the right middle ground a localized rough orange mineral patch and a few fallen rocks; a cable and sparse utilitarian mining lamps running into the distance on the left. Strong cool white directional work light from upper left illuminating the central floor and rocks; a few very restrained warm amber practical lights far inside the tunnel. Gentle dusty haze in depth. Dark steel grey/blue palette with credible visible midtone detail; premium dramatic editorial lighting but NOT pitch black. Top left darker wall space for a white title, lower corners dark for white captions. Real geology, real mine, no science fiction, no glowing crystals, no wide exterior vista. Full bleed, sharp geological textures and natural photographic depth.

## Follow-up: motion and section consistency

Requested: make rover travel visibly and restore a moving scanner presentation; remove duplicate Materials from services only; renumber to S.01 AI Solutions, S.02 Use Cases, S.03 Pilot Process, S.04 Next Page; use original outlined-number/filled-name badges. Preserve home Materials and unrelated animation.

Implementation: retain independently merged wheel and mast groups; animate local wheel spin, rover travel, mast sweep and synchronized contact shadow; move thermal viewport and beam endpoints together; preserve pause and reduced motion. Check desktop/mobile, actual motion over time, reduced motion, scrolling, numbering, and home Materials presence.

User refinement: keep thermal viewport and target fixed; animate only the opening/reveal of the viewport and widening of the light cone on entry. Keep the requested rover movement.
