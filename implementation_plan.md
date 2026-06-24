# Build Production-Style AeroOps AI Dashboard

## Goal
Create a modern, aviation‑themed web dashboard for the AeroOps AI FastAPI service. The dashboard will allow a dispatcher to input flight details, NOTAM text, weather text, and operational notes, then invoke the existing `/aeroops/run` endpoint and display the analysis results. It must also support the human‑review workflow via `/aeroops/resume`.

## User Review Required
> [!IMPORTANT]
> The visual design (color palette, fonts, logo) is not yet specified. Please confirm if the default dark‑blue/gray theme is acceptable or provide branding preferences.

> [!WARNING]
> The dashboard will expose the `/aeroops/run` and `/aeroops/resume` endpoints to the browser. Ensure the FastAPI server is configured to run in a trusted environment (no public internet exposure) or enable appropriate CORS/security settings.

## Open Questions
- Preferred primary color and accent colors for the aviation theme?
- Should the dashboard include a logo image? If so, provide the image file or URL.
- Do you want the results panel to auto‑scroll on long briefings?
- Any additional fields beyond the listed inputs (e.g., aircraft type, crew notes)?

## Proposed Changes
---
### Backend (FastAPI) Adjustments
- **[MODIFY]** [`app.py`](file:///C:/Users/m000m/Downloads/my-first-project/app.py)
  - Mount `StaticFiles` at `/static` and configure `Jinja2Templates`.
  - Add a new GET route `/` that renders `templates/index.html`.
  - Ensure CORS middleware allows same‑origin requests (optional).

---
### Frontend Assets
- **[NEW]** [`templates/index.html`](file:///C:/Users/m000m/Downloads/my-first-project/templates/index.html)
  - HTML skeleton with a responsive layout.
  - Form fields: Flight Number, Origin, Destination, Scheduled Time, NOTAM Text, Weather Text, Operational Notes.
  - "Run Analysis" button triggers JavaScript.
  - Result sections for Risk Score, Risk Level, Recommended Action, NOTAM Summary, Weather Summary, Final Briefing.
  - Conditional Human Review panel with Approve / Reject buttons.
  - Loading spinner and status messages.

- **[NEW]** [`static/style.css`](file:///C:/Users/m000m/Downloads/my-first-project/static/style.css)
  - Aviation‑themed dark background, teal/amber accents.
  - Use Google Font **Inter** for modern typography.
  - Responsive grid layout, glass‑morphism cards, subtle hover animations.

- **[NEW]** [`static/main.js`](file:///C:/Users/m000m/Downloads/my-first-project/static/main.js)
  - JavaScript module handling form submission via `fetch` POST to `/aeroops/run`.
  - Parses JSON response and populates the result fields.
  - Shows a spinner while awaiting response.
  - If `needs_human_review` is true, displays the review panel.
  - Review panel buttons POST to `/aeroops/resume` with `{action: "APPROVE"}` or `{action: "REJECT"}` and updates UI accordingly.
  - Basic error handling and user feedback.

---
### Asset Management
- Add placeholder image `static/logo.png` (optional) for branding.

---
### Verification Plan
### Automated Tests
- Run existing pytest suite to ensure no regression.
- Add a new integration test (`tests/test_dashboard_integration.py`) that starts the FastAPI app with `TestClient`, posts a mock payload to `/aeroops/run`, and verifies the JSON response structure is correctly served to the frontend (status 200, JSON keys present).

### Manual Verification
- Start the server (`uv run python -m uvicorn app:app --reload`).
- Open `http://localhost:8000/` in a browser.
- Fill in sample data (use DEMO_MODE=true for deterministic mock responses).
- Click **Run Analysis** and confirm:
  - Loading spinner appears then disappears.
  - All result fields populate.
  - If `needs_human_review` is true, the review panel shows and buttons work.
- Verify that the approve/reject actions call `/aeroops/resume` and UI updates accordingly.
- Capture screenshots for the Kaggle Capstone README.

---
### Timeline
- Backend modifications: 15 min.
- Frontend assets creation: 30 min.
- Integration test addition: 10 min.
- Manual validation & screenshot capture: 15 min.

Total estimated effort: ~1 hour.

Please review the plan, answer the open questions, and approve to proceed.
