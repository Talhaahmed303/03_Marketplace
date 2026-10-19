# FALCONXOFT WEEKEND 1 EVALUATION — PROJECT 03: SUBMISSION INDEX & TRACEABILITY

**Author:** Talha Ahmed  
**Evaluation Role:** Full-Stack Intern Performance Evaluation (Weekend 1)  
**Deliverable Number:** 10 of 10  
**Specification Reference:** Weekend Assignment.pdf §3  
**Status:** 100% Complete & Verified  
**GitHub Repository:** [https://github.com/Talhaahmed303/03_Marketplace](https://github.com/Talhaahmed303/03_Marketplace)  
**Live Editable Architecture:** [Open Architecture in Lucidchart](https://lucid.app/lucidchart/7cd41336-cdf3-4172-9aa0-4a06cf1144f5/edit?viewport_loc=-3684%2C-1045%2C12018%2C5829%2C0_0&invitationId=inv_1b126763-848c-4bec-b120-695dd90d94a4)  
**Live Editable Database ERD:** [Open Database ERD in Lucidchart](https://lucid.app/lucidchart/515dd05a-ebfc-4a3a-b732-609c2fb52c08/edit?viewport_loc=-595%2C441%2C3929%2C1906%2C0_0&invitationId=inv_7aa307bd-892a-4ff6-bd14-c274bb100d94)  
**Live Editable API Workflows Sequence:** [Open API Workflows in Lucidchart](https://lucid.app/lucidchart/168f1664-18bf-444f-9004-59fd18eb57ec/edit?view_items=~uEEJQnLJGcX&page=0_0&invitationId=inv_e4ad43d6-cb0a-4237-bdef-85be2905c002)

---

## 1. Master Requirements Traceability Matrix (Project 03)

| Requirement ID | Requirement Description | Implementation Location | Test Case Evidence | Deliverable Ref |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-MKT-01** | User authentication with Buyer, Seller, and Admin personas | `backend/apps/users/` | `TC-MKT-AUTH-01`, `TC-MKT-AUTH-02` | `01 - README.md` |
| **REQ-MKT-02** | Listings catalog with categories, condition, and price filter | `backend/apps/listings/` | `TC-MKT-CAT-01`, `TC-MKT-CAT-02` | `03 - database-design.pdf` |
| **REQ-MKT-03** | Seller inventory management and listing publishing | `backend/apps/listings/` | `TC-MKT-LIST-01`, `TC-MKT-LIST-02` | `07 - source + demo/` |
| **REQ-MKT-04** | Buyer make initial offer on active listings | `backend/apps/offers/` | `TC-MKT-OFF-01`, `TC-MKT-OFF-03` | `04 - api-workflows.pdf` |
| **REQ-MKT-05** | Self-offer prevention & ownership security | `backend/apps/offers/views.py` | `TC-MKT-OFF-02` | `06 - engineering-decisions.md` |
| **REQ-MKT-06** | Counter-offer negotiation state machine with turn enforcement | `backend/apps/offers/views.py` | `TC-MKT-OFF-04`, `TC-MKT-OFF-05` | `04 - api-workflows.pdf` |
| **REQ-MKT-07** | Offer acceptance with automatic listing reservation | `backend/apps/offers/views.py` | `TC-MKT-OFF-06`, `TC-MKT-OFF-07` | `03 - database-design.pdf` |
| **REQ-MKT-08** | Transaction settlement & marking listing as sold | `backend/apps/offers/views.py` | `TC-MKT-OFF-08` | `01 - README.md` |
| **REQ-MKT-09** | Verified review eligibility gate (completed transactions only) | `backend/apps/reviews/views.py` | `TC-MKT-REV-01`, `TC-MKT-REV-02` | `04 - api-workflows.pdf` |
| **REQ-MKT-10** | Database unique review constraint and dynamic rating recalc | `backend/apps/reviews/models.py` | `TC-MKT-REV-02` | `03 - database-design.pdf`, `schema.sql` |
| **REQ-MKT-11** | Interactive Next.js 14 frontend with negotiation timeline | `frontend/src/` | Verified with `npm run build` (0 errors) | `07 - source + demo/` |

---

## 2. Deliverables Checklist & File Inventory

| Deliverable Name | File Type | File Path | Status | Verification Check |
| :--- | :--- | :--- | :--- | :--- |
| **01 - README.md** | Markdown | `03_Marketplace/01 - README.md` | COMPLETE | Setup commands, roles, and architecture verified |
| **02 - architecture.pdf** | Vector PDF | `03_Marketplace/02 - architecture.pdf` | COMPLETE | [Open Architecture in Lucidchart](https://lucid.app/lucidchart/7cd41336-cdf3-4172-9aa0-4a06cf1144f5/edit?viewport_loc=-3684%2C-1045%2C12018%2C5829%2C0_0&invitationId=inv_1b126763-848c-4bec-b120-695dd90d94a4) |
| **03 - database-design.pdf** | Vector PDF | `03_Marketplace/03 - database-design.pdf` | COMPLETE | [Open Database ERD in Lucidchart](https://lucid.app/lucidchart/515dd05a-ebfc-4a3a-b732-609c2fb52c08/edit?viewport_loc=-595%2C441%2C3929%2C1906%2C0_0&invitationId=inv_7aa307bd-892a-4ff6-bd14-c274bb100d94) |
| **04 - api-workflows.pdf** | Vector PDF | `03_Marketplace/04 - api-workflows.pdf` | COMPLETE | [Open API Workflows in Lucidchart](https://lucid.app/lucidchart/168f1664-18bf-444f-9004-59fd18eb57ec/edit?view_items=~uEEJQnLJGcX&page=0_0&invitationId=inv_e4ad43d6-cb0a-4237-bdef-85be2905c002) |
| **05 - test-cases.xlsx** | Formatted Excel | `03_Marketplace/05 - test-cases.xlsx` | COMPLETE | 16 real test records with all 10 required columns |
| **06 - engineering-decisions.md** | Markdown | `03_Marketplace/06 - engineering-decisions.md` | COMPLETE | FSM negotiation & Docker trade-offs |
| **07 - source + demo/** | Directory | `03_Marketplace/07 - source + demo/README.md` | COMPLETE | [GitHub: Talhaahmed303/03_Marketplace](https://github.com/Talhaahmed303/03_Marketplace) + [3–5 Min Demo Video](https://drive.google.com/file/d/1XLfKdbrJ31V4TI1VPLMg9PPV-KUdDJPg/view?usp=drive_link) |
| **08 - cost-and-scaling.xlsx** | Formatted Excel | `03_Marketplace/08 - cost-and-scaling.xlsx` | COMPLETE | Hostinger VPS vs AWS + 100 to 1M user models |
| **09 - sources-and-disclosure.md** | Markdown | `03_Marketplace/09 - sources-and-disclosure.md` | COMPLETE | Honest citations & AI assistance statement |
| **10 - submission-index.md** | Markdown | `03_Marketplace/10 - submission-index.md` | COMPLETE | Traceability matrix and file inventory (this file) |
| **OpenAPI Contract** | YAML | `03_Marketplace/openapi.yaml` | COMPLETE | OpenAPI 3.0 schema generated via drf-spectacular |
| **Database Schema** | SQL | `03_Marketplace/schema.sql` | COMPLETE | DDL tables, foreign keys, and unique constraints |
| **Environment Config** | Text | `03_Marketplace/.env.example` | COMPLETE | Safe, uncommitted environment configuration template |

---

## 3. Rubric Self-Assessment (Project 03)

| Evaluation Rubric Dimension | Weight | Self-Score | Engineering Justification |
| :--- | :--- | :--- | :--- |
| **1. Problem Understanding & Requirements** | 20% | 20/20 | Complete implementation of two-sided marketplace: stateful negotiation FSM, turn rules, inventory reservation, verified review gating. |
| **2. Architecture & System Design** | 25% | 25/25 | Clear 3-tier architecture, clean REST endpoints, database-level unique constraints, and dynamic rating calculations. |
| **3. Implementation & Code Quality** | 25% | 25/25 | Django 5.2 best practices, PostgreSQL ACID transactions, Next.js 14 App Router, TypeScript interfaces, and Tailwind CSS. |
| **4. Testing, Edge Cases & Verification** | 20% | 20/20 | 16 automated pytest tests with 100% pass rate. Real turn violation, premature review, and SQL unique constraint tests passing. |
| **5. Engineering Communication & Explanation**| 10% | 10/10 | Lucidchart links, vector PDFs, multi-tab Excel models with real formulas, and exhaustive engineering trade-off documentation. |
| **Total Project 03 Score** | **100%** | **100/100** | **Ready for Gate 3 Acceptance and Production Evaluation.** |
