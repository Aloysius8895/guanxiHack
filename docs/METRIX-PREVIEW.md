# MetriX AI product website

Run from the project directory:

```powershell
python serve.py --port 8002
```

Open http://127.0.0.1:8002/ for the English product website. The existing cave animation, typography, navigation and page transitions are retained.

- `/our-services`: MineFit AI, QualityGuard AI, CircularMine AI and proposed pilot applications.
- `/technology`: rover concept, embedded interactive model and components.
- `/rover/`: standalone English model with orbit, drive, sample and exploded-view controls.
- `/about-us`: mission, project status and planned 2027–2029 roadmap.
- `/contact`: local pilot-brief download; no email is sent and no backend submission is configured.

The website describes prototype and proof-of-concept capabilities. Proposed subscriptions, private deployment and integration are not presented as existing commercial delivery. The Chinese source introduction remains available as a download.

The model is derived from `MetriX-Rover-Six-Legs.html`, with English controls, local Three.js dependencies, a light shell and a raised sensor mast informed by the supplied photos. The original source model is preserved. Website photography uses the rover image extracted from the product introduction.

Content migration can be reproduced with `python tools/adapt_product.py`; the rover with `python tools/build_rover.py`. Original page snapshots are in `verification/product-before/`. Run `python tools/audit_product.py` for page/resource checks and `python tools/verify_product.py` for desktop/mobile interactions. Reports and screenshots are saved under `verification/`.
