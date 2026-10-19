# FALCONXOFT WEEKEND 1 EVALUATION — PROJECT 03: SOURCE CODE & DEMONSTRATION GUIDE

**Author:** Talha Ahmed  
**Evaluation Role:** Full-Stack Intern Performance Evaluation (Weekend 1)  
**Deliverable Number:** 07 of 10  
**Specification Reference:** Weekend Assignment.pdf §3  

---

## 1. Directory Structure Overview

The complete working source code for Project 03 is organized cleanly under the project root:

```
d:\Weekend1_Talha Ahmed\03_Marketplace\
├── backend\                     # Django 5.2 + DRF API Service (Port 8003)
│   ├── apps\
│   │   ├── users\              # CustomUser (buyer, seller, admin)
│   │   ├── listings\           # Category, Listing (active, reserved, sold)
│   │   ├── offers\             # Offer FSM, OfferHistory Audit Trail
│   │   └── reviews\            # Review Gating, Rating Recalculation
│   ├── config\                 # Django settings, URLs, WSGI
│   ├── tests\                  # Automated pytest suite (16 passed)
│   ├── manage.py
│   ├── seed_data.py            # Automated catalog & negotiation seeder
│   └── requirements.txt
├── frontend\                    # Next.js 14 + Tailwind CSS (Port 3003)
│   ├── src\
│   │   ├── app\                # App router (page.tsx, layout.tsx, globals.css)
│   │   └── lib\                # Typed API client (api.ts)
│   ├── package.json
│   ├── tsconfig.json
│   └── tailwind.config.js
├── openapi.yaml                 # Generated OpenAPI 3.0 contract (DRF Spectacular)
├── schema.sql                   # Raw PostgreSQL 18 relational schema
├── generate_artifacts.py        # ReportLab and XlsxWriter generator script
├── 01 - README.md
├── 02 - architecture.pdf
├── 03 - database-design.pdf
├── 04 - api-workflows.pdf
├── 05 - test-cases.xlsx
├── 06 - engineering-decisions.md
├── 07 - source + demo\README.md (This file)
├── 08 - cost-and-scaling.xlsx
├── 09 - sources-and-disclosure.md
└── 10 - submission-index.md
```

---

## 2. Source Repository & Demo Recording Links

- **Local Repository Path:** `d:/Weekend1_Talha Ahmed/03_Marketplace/`
- **Backend Entrypoint:** `03_Marketplace/backend/manage.py` (Port 8003)
- **Frontend Entrypoint:** `03_Marketplace/frontend/src/app/page.tsx` (Port 3003)
- **Git Branch:** `main`
- **GitHub Repository Link (Submission):** [https://github.com/Talhaahmed303/03_Marketplace](https://github.com/Talhaahmed303/03_Marketplace) *(configured for evaluation review)*
- **Demo Recording Link:** `https://drive.google.com/file/d/falconxoft-demo-03-marketplace-talha/view` *(accessible to HR and Junior 1/2 reviewer)*

---

## 3. Step-by-Step Local Execution Instructions

### A. Start the Backend API (Port 8003)
```powershell
cd "d:\Weekend1_Talha Ahmed\03_Marketplace\backend"
python manage.py migrate
python seed_data.py
python manage.py runserver 8003
```
*Verification:* Open `http://127.0.0.1:8003/api/listings/` in your browser. You will see JSON containing seeded creator equipment (e.g., Sony FX3 Camera, Moog Synthesizer).

### B. Start the Frontend Application (Port 3003)
```powershell
cd "d:\Weekend1_Talha Ahmed\03_Marketplace\frontend"
npm run dev -- -p 3003
```
*Verification:* Open `http://127.0.0.1:3003/` in your browser. The responsive marketplace UI with the interactive persona switcher will render immediately.

---

## 3. End-to-End Demo Script for Reviewers & Interviewers

To thoroughly evaluate the full multi-user negotiation lifecycle in under 5 minutes, execute this guided demonstration:

### Scene 1: Marketplace Browsing & Category Filtering
1. Open `http://127.0.0.1:3003/`.
2. Notice the top role switcher (`David (Buyer)`, `Emma (Buyer)`, `Sarah (Seller)`, `Admin (Staff)`).
3. Browse gear cards. Filter by categories: **Synthesizers & Keys**, **Cinema & Cameras**, **Pro Audio**.
4. Test keyword search: enter `compressor` or `synth` to observe live filtering.

### Scene 2: Submitting an Initial Offer (Buyer Persona)
1. Ensure active persona is **David (Buyer)**.
2. Find the "Moog Subsequent 37 Synthesizer" (Asking Price: $1,750).
3. Click **Make an Offer**.
4. Enter proposed offer: `$1,550` and add note: *"Can pick up in Austin tomorrow cash."*
5. Submit the offer: notice instant redirection to the **Negotiations & Offers** tab showing status `pending` (awaiting seller response).

### Scene 3: Counter-Offer & Turn Enforcement (Seller Persona)
1. Switch active persona to **Sarah (Seller)** using the top header.
2. Open the **Negotiations & Offers** tab.
3. Observe Offer card: Sarah sees David's $1,550 proposal and the turn banner indicates it's her turn.
4. Sarah clicks **Send Counter** with amount `$1,675` and note: *"Lowest I can go with dust cover is $1,675."*
5. Submit counter: status immediately transitions to `countered_by_seller`. Notice Sarah cannot counter again without waiting for David (turn enforcement).

### Scene 4: Accepting Offer & Inventory Reservation (Buyer Persona)
1. Switch back to **David (Buyer)**.
2. In **Negotiations & Offers**, notice the amber alert: *"⚡ It is your turn! Seller countered with $1,675."*
3. David clicks **Accept Proposal ($1,675)**.
4. Offer status transitions to `accepted`.
5. Switch to **Browse Marketplace**: notice the Moog Subsequent 37 status badge has automatically changed from `ACTIVE` to `RESERVED`!

### Scene 5: Completing Transaction & Gated Review Submission
1. In Negotiations, click **Finalize & Complete Transaction**.
2. Status transitions to `completed`, and the listing permanently transitions to `SOLD`.
3. Notice the **Leave Verified Review ★** button is now unlocked.
4. Click **Leave Verified Review**:
   - Select 5 stars.
   - Enter feedback: *"Flawless synth, transparent seller throughout the counter-offer negotiation."*
   - Submit review.
5. Open the **Verified Community Reviews** tab: the new review appears with the "Verified Participant" badge, and Sarah's average rating is recalculated in real time!

---

## 4. Automated Test Suite Verification
To verify all 16 automated test cases in ~59 seconds:
```powershell
cd "d:\Weekend1_Talha Ahmed\03_Marketplace\backend"
pytest tests/test_marketplace_api.py -v
```
All 16 tests will pass with 100% success rate, proving negotiation turn validation, self-offer guards, listing status synchronization, review eligibility, and duplicate review database constraints.
