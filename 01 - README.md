# FALCONXOFT WEEKEND 1 EVALUATION — PROJECT 03: TWO-SIDED MARKETPLACE

**Author:** Talha Ahmed  
**Evaluation Role:** Full-Stack Intern Performance Evaluation (Weekend 1)  
**Deliverable Number:** 01 of 10  
**Specification Reference:** Weekend Assignment.pdf §2.3 & §3  
**Implementation Status:** 100% Implemented, Seeded, Tested, and Verified  
**Active Backend Port:** `http://127.0.0.1:8003`  
**Active Frontend Port:** `http://127.0.0.1:3003`  
**GitHub Repository:** [https://github.com/Talhaahmed303/03_Marketplace](https://github.com/Talhaahmed303/03_Marketplace)  
**Live Editable Architecture:** [Open Architecture in Lucidchart](https://lucid.app/lucidchart/7cd41336-cdf3-4172-9aa0-4a06cf1144f5/edit?viewport_loc=-3684%2C-1045%2C12018%2C5829%2C0_0&invitationId=inv_1b126763-848c-4bec-b120-695dd90d94a4)  
**Live Editable Database ERD:** [Open Database ERD in Lucidchart](https://lucid.app/lucidchart/515dd05a-ebfc-4a3a-b732-609c2fb52c08/edit?viewport_loc=-595%2C441%2C3929%2C1906%2C0_0&invitationId=inv_7aa307bd-892a-4ff6-bd14-c274bb100d94)  
**Live Editable API Workflows Sequence:** [Open API Workflows in Lucidchart](https://lucid.app/lucidchart/168f1664-18bf-444f-9004-59fd18eb57ec/edit?view_items=~uEEJQnLJGcX&page=0_0&invitationId=inv_e4ad43d6-cb0a-4237-bdef-85be2905c002)

---

## 1. Executive Summary & Problem Scope

Two-sided peer-to-peer marketplaces (such as Reverb, Upwork, and Chrono24) require far more sophisticated domain logic than traditional static retail stores. Negotiation is stateful, pricing is dynamic, inventory must be reserved upon agreement, and marketplace trust relies strictly on the mathematical validity of buyer/seller reputation.

Project 03 delivers a **production-grade Two-Sided Marketplace (GearExchange)** for professional audio and cinema equipment. Architected with Django 5.2, Django REST Framework, PostgreSQL 18, and Next.js 14 (TypeScript + Tailwind CSS), this application features:
1. **Interactive Counter-Offer Negotiation State Machine:** A finite state machine (`pending` -> `countered_by_seller` <-> `countered_by_buyer` -> `accepted` -> `declined` -> `completed`) with strict turn enforcement, preventing out-of-turn bidding or double counters.
2. **Self-Offer Prevention & Ownership Guards:** Sellers are structurally blocked from making offers on their own listings; unauthorized parties are barred from meddling with active deals.
3. **Atomic Listing Reservation & Settlement:** Accepting an offer automatically transitions listing inventory status to `reserved`; completing the transaction marks it permanently as `sold`.
4. **Verified Review & Rating Eligibility Gate:** Zero fake reviews. Users can strictly only submit a review if they were a legitimate participant in a completed and settled transaction.
5. **Database-Level Fraud Prevention:** Hard PostgreSQL `UniqueConstraint(fields=['offer', 'reviewer'])` preventing duplicate reviews, and `CheckConstraint(rating >= 1 AND rating <= 5)`.

---

## 2. Technology Stack & Local Host Environment

| Layer | Technology | Version | Purpose / Port |
| :--- | :--- | :--- | :--- |
| **Frontend** | Next.js / React / TypeScript | 14.2.35 / 18.3.1 / 5.x | Responsive Marketplace UI (`http://127.0.0.1:3003`) |
| **Styling** | Tailwind CSS | 3.4.17 | Glassmorphic cards, negotiation timelines, star selectors |
| **Backend API** | Django / DRF | 5.2.x / 3.16.x | Negotiation state machine, audit logs (`http://127.0.0.1:8003`) |
| **Database** | PostgreSQL | 18 (x64 Windows) | ACID relational engine (`marketplace_db`, port 5432) |
| **Authentication** | Django SimpleJWT | 5.5.x | Cryptographic HMAC-SHA256 Bearer tokens |
| **API Contract** | drf-spectacular | 0.29.x | OpenAPI 3.0 contract and Swagger/Redoc interactive docs |
| **Testing** | pytest + pytest-django | 8.4.x / 4.11.x | Automated API test suite (16 passing tests) |
| **Architecture** | ReportLab & XlsxWriter | 4.4.x / 3.2.x | Generated Vector PDFs and multi-tab financial models |

---

## 3. Marketplace Architecture & Data Flow

```
[ Next.js 14 Marketplace UI (Port 3003) ]
         │ (REST / JSON + JWT Bearer)
         ▼
[ Django DRF API Layer (Port 8003) ]
   ├── Authentication & Role Switcher (Buyer vs Seller vs Admin)
   ├── Listing ViewSet (Categories, Search, Price Range)
   ├── Negotiation Engine (apps.offers)
   │     ├── Turn Enforcement Middleware
   │     ├── State Machine (Pending -> Countered -> Accepted -> Completed)
   │     └── Immutable OfferHistory Audit Trail
   └── Verified Review System (apps.reviews)
         │ (Eligibility Gate: Status == 'completed' & Participant Check)
         ▼
[ PostgreSQL 18 Engine (marketplace_db) ]
   ├── UniqueConstraint(offer, reviewer)
   ├── CheckConstraint(rating BETWEEN 1 AND 5)
   └── Composite Indexes on (buyer, status) & (seller, status)
```

---

## 4. Visual Architecture & Database ERD Diagrams

All diagrams required by the FalconXoft evaluation specification have been exported and provided in multiple formats for maximum defensibility. Clicking any preview diagram below will open the **live, editable Lucidchart workspace**:

### 4.1 System Architecture Diagram
[![System Architecture Diagram](02%20-%20architecture.png)](https://lucid.app/lucidchart/7cd41336-cdf3-4172-9aa0-4a06cf1144f5/edit?viewport_loc=-3684%2C-1045%2C12018%2C5829%2C0_0&invitationId=inv_1b126763-848c-4bec-b120-695dd90d94a4)
- **Vector PDF Deliverable:** [`02 - architecture.pdf`](02%20-%20architecture.pdf)
- **High-Res PNG Deliverable:** [`02 - architecture.png`](02%20-%20architecture.png)
- **Live Editable Lucidchart URL:** [Open Architecture in Lucidchart](https://lucid.app/lucidchart/7cd41336-cdf3-4172-9aa0-4a06cf1144f5/edit?viewport_loc=-3684%2C-1045%2C12018%2C5829%2C0_0&invitationId=inv_1b126763-848c-4bec-b120-695dd90d94a4)

---

### 4.2 Database ERD & Relational Schema
[![Database ERD Diagram](03%20-%20database-design.png)](https://lucid.app/lucidchart/515dd05a-ebfc-4a3a-b732-609c2fb52c08/edit?viewport_loc=-595%2C441%2C3929%2C1906%2C0_0&invitationId=inv_7aa307bd-892a-4ff6-bd14-c274bb100d94)
- **Vector PDF Deliverable:** [`03 - database-design.pdf`](03%20-%20database-design.pdf)
- **High-Res PNG Deliverable:** [`03 - database-design.png`](03%20-%20database-design.png)
- **Live Editable Lucidchart ERD URL:** [Open Database ERD in Lucidchart](https://lucid.app/lucidchart/515dd05a-ebfc-4a3a-b732-609c2fb52c08/edit?viewport_loc=-595%2C441%2C3929%2C1906%2C0_0&invitationId=inv_7aa307bd-892a-4ff6-bd14-c274bb100d94)
- **PostgreSQL 1-Click DDL:** [`schema.sql`](schema.sql)

---

### 4.3 API Workflows & Sequence Workflows
[![API Sequence Workflows](04%20-%20api-workflows.png)](https://lucid.app/lucidchart/168f1664-18bf-444f-9004-59fd18eb57ec/edit?view_items=~uEEJQnLJGcX&page=0_0&invitationId=inv_e4ad43d6-cb0a-4237-bdef-85be2905c002)
- **Vector PDF Deliverable:** [`04 - api-workflows.pdf`](04%20-%20api-workflows.pdf)
- **High-Res PNG Deliverable:** [`04 - api-workflows.png`](04%20-%20api-workflows.png)
- **Live Editable Lucidchart Sequence URL:** [Open API Workflows in Lucidchart](https://lucid.app/lucidchart/168f1664-18bf-444f-9004-59fd18eb57ec/edit?view_items=~uEEJQnLJGcX&page=0_0&invitationId=inv_e4ad43d6-cb0a-4237-bdef-85be2905c002)
- **Complete OpenAPI 3.0 Contract:** [`openapi.yaml`](openapi.yaml)

---

## 5. Quick Start & Execution Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 18 running locally on port 5432 with database `marketplace_db` created

### Step 1: Backend Setup & Seeding
```powershell
# Navigate to backend directory
cd "d:\Weekend1_Talha Ahmed\03_Marketplace\backend"

# Run database migrations
python manage.py migrate

# Seed catalog, test customers, and admin users
python seed_data.py

# Launch backend API server
python manage.py runserver 8003
```
Backend will be live at `http://127.0.0.1:8003/api/`.  
OpenAPI Documentation: `http://127.0.0.1:8003/api/docs/`  
Raw OpenAPI YAML: `http://127.0.0.1:8003/api/schema/`

### Step 2: Frontend Setup & Launch
```powershell
# Navigate to frontend directory
cd "d:\Weekend1_Talha Ahmed\03_Marketplace\frontend"

# Launch Next.js dev server
npm run dev -- -p 3003
```
Frontend will be live at `http://127.0.0.1:3003/`.

---

## 6. Seed Credentials & User Personas

| Username | Password | Role | Persona Description |
| :--- | :--- | :--- | :--- |
| `sarah_seller` | `Password@123` | `seller` | Audio engineer in Austin, TX with high-end synthesizers and cinema cameras listed |
| `david_buyer` | `Password@123` | `buyer` | Indie music producer actively negotiating on the Moog Subsequent 37 |
| `emma_buyer` | `Password@123` | `buyer` | Commercial filmmaker with an accepted offer on the Neumann U87 microphone |
| `market_admin` | `Password@123` | `admin` | Operations administrator with moderation and dispute resolution privileges |

---

## 7. Automated Test Suite Verification

Run the comprehensive pytest suite verifying negotiation state transitions, turn enforcement, self-offer guards, listing status propagation, review eligibility gating, and database uniqueness constraints:

```powershell
cd "d:\Weekend1_Talha Ahmed\03_Marketplace\backend"
pytest tests/test_marketplace_api.py -v
```

**Results:**
- Total Tests: **16**
- Passed: **16 (100%)**
- Execution Duration: ~59 seconds
- Key Verified Tests:
  - `test_counter_offer_turn_enforcement`: Confirms out-of-turn counters are strictly blocked.
  - `test_accept_offer_reserves_listing`: Proves listing is atomically reserved upon offer acceptance.
  - `test_verified_review_eligibility_completed_only`: Validates uncompleted transactions cannot be reviewed.
  - `test_duplicate_review_prevented`: Proves PostgreSQL unique constraint blocks duplicate review spam.

---

## 8. Deliverables Index

Per Weekend Assignment §3, all 10 standard deliverables are provided:
1. `01 - README.md` — Project overview and setup instructions (this file)
2. `02 - architecture.pdf` — High-resolution landscape vector architecture diagram with editable Lucidchart link
3. `03 - database-design.pdf` — Relational ERD diagram, primary/foreign keys, check constraints, and 3NF analysis
4. `04 - api-workflows.pdf` — Sequence diagrams of counter-offer negotiation and review gating flows
5. `05 - test-cases.xlsx` — 16 detailed test execution records with 10 required columns
6. `06 - engineering-decisions.md` — In-depth architectural trade-off analysis (including Docker exclusion rationale)
7. `07 - source + demo/` — Complete runnable source code and verified demo script
8. `08 - cost-and-scaling.xlsx` — Hostinger VPS vs AWS comparison and 100 to 1M user scaling roadmap
9. `09 - sources-and-disclosure.md` — Complete honesty and AI assistance disclosures
10. `10 - submission-index.md` — Traceability index linking requirements to code and artifacts
11. `LUCIDCHART_DIAGRAMS_CODE.md` — Raw Mermaid and SQL definitions for 1-click Lucidchart import
12. [`MARKETPLACE_TESTING_AND_VIVA_GUIDE.md`](MARKETPLACE_TESTING_AND_VIVA_GUIDE.md) — Complete oral interview defense, persona walkthrough, and browser testing guide
