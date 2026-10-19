# FALCONXOFT WEEKEND 1 — TWO-SIDED MARKETPLACE MVP (GEAREXCHANGE)
## Complete Browser Testing & Viva Defense Guide (Roman Urdu & English)

**Author:** Talha Ahmed  
**Project:** 03_Marketplace (Two-Sided Audio & Cinema Gear Marketplace — GearExchange)  
**Frontend URL:** `http://localhost:3003`  
**Backend API URL:** `http://127.0.0.1:8003/api/`  
**Database:** PostgreSQL 18 (`marketplace_db`)  
**Live Diagram Definitions:** [`LUCIDCHART_DIAGRAMS_CODE.md`](LUCIDCHART_DIAGRAMS_CODE.md)

---

## 1. Task Background — Aapko Task Kya Mila Tha? (Requirements Overview)

FalconXoft Weekend 1 evaluation ka teesra aur final project tha ek **Two-Sided Peer-to-Peer Marketplace MVP** banana.

Standard retail stores (jaise Project 02) mein static pricing hoti hai — buyer cart mein item dalta hai aur fixed price pay kar deta hai. Lekin **Two-Sided Marketplaces** (jaise Reverb, eBay, Upwork, OLX) mein buyer aur seller aapas mein negotiate karte hain, counter-proposals bhejte hain, aur trust verify karte hain:
- **Negotiation Race Conditions:** Agar buyer aur seller simultaneously counter karein ya koi user apne hi counter-offer ko accept karne ki koshish kare, to system corrupt ho jata hai.
- **Inventory Theft / Double Dealing:** Agar seller ek buyer ka offer accept kar le, lekin listing public rahe aur koi doosra user usay buy kar le (Listing state reservation failure).
- **Self-Bidding & Fraud:** Seller fake account ya apni hi listing par offers submit karke artificial hype create kare (Self-offer fraud).
- **Review Spam & Extortion:** Koi bhi random user bina deal complete kiye fake 1-star ya 5-star review daal de (Fake review vulnerability).

HR assessment specification (§2.3) ke mutabiq humne ek **zero-defect, state-machine driven Two-Sided Marketplace (GearExchange)** banaya hai jisme:
1. **Interactive Counter-Offer Negotiation Engine:** Complete finite state machine (`pending` ➔ `countered_by_seller` ⟷ `countered_by_buyer` ➔ `accepted` ➔ `declined` ➔ `completed`).
2. **Strict Turn Enforcement:** Awaiting counter-party move rule — koi user apne hi offer ke baad dubara counter nahi bhej sakta.
3. **Self-Offer Prevention:** Sellers structurally apni listing par offer submit nahi kar sakte (`HTTP 400 Bad Request`).
4. **Atomic Inventory Reservation:** Offer accept hote hi listing status automatically `reserved` ho jata hai; deal complete hote hi `sold` ho jata hai.
5. **Gated Verified Reviews:** Review creation sirf unhi users ke liye unlock hoti hai jinki deal status `completed` ho chuki ho.
6. **Database Integrity Defense:** PostgreSQL par hard `UNIQUE (offer_id, reviewer_id)` constraint aur `CHECK (rating BETWEEN 1 AND 5)`.
7. **Dynamic Reputation Scorecard:** Review aate hi seller ka average rating (`rating_avg`) aur total review count automatically recalculate ho jata hai.
8. **Multi-User Persona Demo Switcher:** 1-Click navbar switcher between `sarah_seller`, `david_buyer`, `emma_buyer`, and `market_admin`.

---

## 2. Humne Kya Aur Kaise Banaya? (Architecture & Technical Decisions)

### Tech Stack:
- **Backend:** Python 3.11 + **Django 5.2** + **Django REST Framework (DRF)**.
  - State Machine & Services: `apps.offers.views` (atomic transaction transitions).
  - Review Gating & Rating Aggregator: `apps.reviews.models` (auto `save()` recalculation).
  - JWT Authentication: `djangorestframework-simplejwt` with custom role claims.
  - API Documentation: `drf-spectacular` (OpenAPI 3.0 schema and Swagger/Redoc endpoints).
- **Frontend:** **Next.js 14** (App Router, React 18, TypeScript) + **Tailwind CSS**.
  - Glassmorphic dark UI, 280ms debounced search, category filter pills, price range slider.
  - Interactive Negotiation Timeline Workspace (real-time badge status, offer history, counter-offer modal).
  - Verified Review & Rating Submission Modal (interactive 1–5 star selector).
  - Built-in **1-Click Demo Persona Switcher** in the top navigation bar.
- **Database:** **PostgreSQL 18** (`marketplace_db`) ACID relational engine.
- **Testing:** `pytest` + `pytest-django` ke **16 automated test cases** (100% pass rate in ~59s).

---

## 3. Demo Accounts & Pre-Seeded States

Frontend navbar ke top-right par **"Demo Switcher"** buttons diye gaye hain. Har account ka real marketplace persona pre-configured hai:

| Role / Avatar | Username | Password | Pre-Seeded State & Persona Story |
| :--- | :--- | :--- | :--- |
| 🎙️ **Sarah (Pro Seller)** | `sarah_seller` | `Password@123` | **Audio Engineer & Cinema Gear Owner (Austin, TX):** High-end synthesizers (Moog), Sony FX3 cameras, aur Neumann microphones listed hain. Has active offers to review and counter. |
| 🎹 **David (Active Buyer)** | `david_buyer` | `Password@123` | **Indie Music Producer:** Active negotiation chal rahi hai Sarah ke Moog Subsequent 37 synthesizer par (Initial offer: $1,850 on $2,200 asking price). |
| 🎬 **Emma (Accepted Deal)** | `emma_buyer` | `Password@123` | **Commercial Filmmaker:** Has an accepted negotiation on Neumann U87 microphone ($2,900) ready for final settlement & review. |
| 👑 **Market Admin** | `market_admin` | `Password@123` | **Platform Administrator:** Global oversight of all listings, active negotiations, disputes, and system categories. |

---

## 4. Browser Testing Walkthrough — Step-by-Step Test Kaise Karein?

Dono servers already aapke system par chal rahe hain:
- **Backend API:** `http://127.0.0.1:8003/api/`
- **Frontend App:** `http://localhost:3003`

Apne browser mein **`http://localhost:3003`** open karein aur yeh steps follow karein:

---

### Step 1: Browse Gear Catalog & Test 280ms Debounced Search
1. Browser mein `http://localhost:3003` kholein.
2. Catalog mein 6 seeded pro gear items nazar aayenge (Moog Subsequent 37, Sony FX3, Neumann U87, Apollo x8, Genelec 8341A, RED Komodo).
3. **Category Filter Test:** Category pills par click karein:
   - `Synthesizers`, `Cinema Cameras`, `Microphones`, `Studio Monitors`.
   - Cards dynamically filter honge bina page reload ke!
4. **Debounced Search Test:** Search bar mein `Moog` ya `Sony` type karein:
   - 280ms ke debounce delay ke baad catalog live filter ho jayega.
   - Price range inputs (`Min $` / `Max $`) enter karke `Apply` click karein.

---

### Step 2: Test "Make an Offer" & Self-Offer Prevention (Fraud Guard)
1. Navbar se switch karein **"🎙️ Sarah (Seller)"** par.
2. Sarah ke apne listing (e.g. *Moog Subsequent 37*) par dekhein:
   - Action button par likha aayega: **`Your Listing (active)`**.
   - Sarah apni hi listing par offer submit **NAHI** kar sakti!
3. Ab navbar se switch karein **"🎹 David (Buyer)"** par.
4. Moog Subsequent 37 card par ab green button activate ho jayega: **`[ Make an Offer (Negotiate Price) ]`**.
5. Button par click karein:
   - Make Offer Modal open hoga showing: Asking Price: `$2,200.00`.
   - Offer Amount enter karein (e.g. `$1,950`) aur proposal message likhein: *"Can pick up locally in Austin today"*.
   - Click karein **`[ Submit Proposal ]`**.
6. **Result:**
   - Toast notification: `Offer submitted successfully! Awaiting seller review.`
   - Screen automatically switch hogi **"Counter-Offer Negotiations"** tab par!

---

### Step 3: Test Interactive Negotiation & Turn Enforcement (Viva Key Point!)
1. "Negotiations" tab mein David ka naya offer card nazar aayega:
   - Status Badge: **`PENDING SELLER REVIEW`** (Amber badge).
   - Timeline audit trail: `david_buyer initial_offer $1,950`.
   - Action buttons par status show hoga: **`Awaiting Counter-Party (You cannot counter your own move)`**.
   - David back-to-back doosra counter nahi bhej sakta!
2. Ab navbar se switch karein **"🎙️ Sarah (Seller)"** par!
3. Sarah ke dashboard par yahi negotiation card show hoga:
   - Sarah ke paas 3 action buttons activate honge:
     - **`[ Accept Offer ($1,950) ]`**
     - **`[ Counter-Offer ]`**
     - **`[ Decline ]`**
4. Sarah **`[ Counter-Offer ]`** par click karegi:
   - Counter modal open hoga.
   - Amount enter karein: `$2,050` with message: *"Includes custom hardcase and extra patch cables"*.
   - Click karein **`[ Dispatch Counter-Offer ]`**.
5. **Result:**
   - Status instantly update hoga: **`COUNTERED BY SELLER`**.
   - Offer history mein record persist ho jayega.
   - Sarah ke buttons disable ho jayenge: `Awaiting response from counter-party`.

---

### Step 4: Test Offer Acceptance & Atomic Listing Reservation
1. Switch back to **"🎹 David (Buyer)"**.
2. David ko Sarah ka counter `$2,050` timeline mein nazar aayega.
3. David green button click karta hai: **`[ Accept Counter-Offer ($2,050) ]`**.
4. **Result:**
   - Offer status instantly transition hota hai: **`ACCEPTED (PROPOSAL SEALED)`** (Green pill).
   - "Browse Marketplace" tab par ja kar Moog Subsequent 37 listing check karein:
     - Listing ka status `active` se change hokar **`RESERVED`** ho chuka hai!
     - Koi doosra buyer is par naya offer nahi bana sakta!
   - Timeline mein audit record generate hota hai: `david_buyer accepted $2,050`.

---

### Step 5: Final Settlement & Verified Review Eligibility Gate
1. Negotiations tab mein accepted deal ke card par button show hoga:
   - **`[ 📦 Finalize & Complete Transaction ]`**.
2. Click karein finalize button:
   - Listing status permanent **`SOLD`** ho jata hai!
   - Offer status **`COMPLETED & SETTLED`** ho jata hai.
   - Review button unlock ho jata hai: **`[ ⭐ Leave Verified Review ]`**!
3. Review button par click karein:
   - Interactive Star Selector open hoga (1 to 5 stars).
   - Select karein 5 Stars ★★★★★.
   - Comment likhein: *"Incredible synthesizer! Sarah was super professional and gear arrived in mint condition."*
   - Click karein **`[ Submit Verified Review ]`**.
4. **Result:**
   - Review automatically publish ho jayega "Verified Reviews" tab mein.
   - Sarah ki profile rating automatically update ho jayegi!
5. **Test Double Review Prevention:**
   - Dubara usi offer par review submit karne ki koshish karein.
   - Database hard constraint `UNIQUE(offer_id, reviewer_id)` trigger hoga aur error aayega: `You have already reviewed this transaction.`

---

## 5. Viva Questions & Model Answers (Oral Defense)

Reviewer ya examiner ke samne confidently yeh points present karein:

### Q1: Two-Sided Marketplace mein state machine implement karne ki kya zaroorat thi? Simple CRUD kyu nahi use kiya?
> **Answer:** "Two-Sided commerce mein standard CRUD logic race conditions aur fraud create karti hai. Humne `apps.offers` mein ek formal Finite State Machine (FSM) implement kiya hai: `pending` ➔ `countered_by_seller` ⟷ `countered_by_buyer` ➔ `accepted` ➔ `declined` ➔ `completed`. Isse teen critical business rules enforce hoti hain:
> 1. **Turn Enforcement:** Naive CRUD mein buyer back-to-back 5 counter bhej kar price drive down kar sakta tha. FSM mein `offer.last_actor != request.user` rule enforced hai, ensuring strict turn-based proposal exchange.
> 2. **Terminal State Lock:** Jab offer `accepted` ya `declined` ho jaye, to purane counter-offers illegal ho jate hain (`HTTP 400 Bad Request`).
> 3. **Audit Immutability:** Har proposal ka snapshot `OfferHistory` table mein timestamp aur actor ke sath permanent store hota hai dispute resolution ke liye."

---

### Q2: Listing inventory reservation kaise ensure hoti hai jab deal seal ho?
> **Answer:** "Jab buyer ya seller `POST /api/offers/{id}/accept/` execute karta hai, to hum execution ko PostgreSQL `transaction.atomic()` context mein wrap karte hain. Offer ka status `accepted` hote hi sath hi linked `Listing.status` ko atomically `'reserved'` set kiya jata hai. Isse marketplace catalog par listing reserved mark ho jati hai aur peer buyers us par naya offer submit nahi kar sakte, eliminating the classic double-dealing problem."

---

### Q3: Fake reviews aur rating manipulation ko engine level par kaise roka?
> **Answer:** "Humne defense-in-depth approach use ki hai:
> 1. **Eligibility Gate:** Unauthenticated ya random users review create nahi kar sakte. API strictly verify karti hai ke `offer.status == 'completed'` ho aur `request.user` us negotiation ka legitimate `buyer` ya `seller` ho.
> 2. **Database Hard Uniqueness:** PostgreSQL level par `UniqueConstraint(fields=['offer', 'reviewer'])` laga hua hai, making duplicate review spam mathematically impossible.
> 3. **Rating Range Constraint:** Table par `CheckConstraint(rating >= 1 AND rating <= 5)` hai taake out-of-range values inject na ho sakein.
> 4. **Dynamic Score Recalculation:** Har naye verified review par ORM hook seller ka `rating_avg = round(total / count, 2)` automatically calculate karke profile update karta hai."

---

### Q4: Self-bidding fraud kaise prevent hota hai?
> **Answer:** "`OfferListCreateView.post()` method mein listing retrieve karte hi hum ownership check execute karte hain: `if listing.seller == request.user: return Response(HTTP 400 Bad Request)`. Frontend UI par bhi seller ko 'Your Listing' disabled badge dikhaya jata hai aur backend API level par self-offers strictly rejected hain."

---

### Q5: Docker kyu nahi use kiya is evaluation mein?
> **Answer:** "Weekend Assignment instructions mein directly zero-Docker bare-metal evaluation explicitly mention ki gayi thi taake local host reproducibility aur direct framework understanding assess ho sake. Humne Python 3.11, Django 5.2, Next.js 14, aur PostgreSQL 18 ko native host level par configure kiya hai jo 100% reproducible hai aur zero container overhead consume karta hai. Production Docker architecture aur AWS ECS scaling trade-offs humne Deliverable 06 (`engineering-decisions.md`) mein thoroughly document kiye hain."

---

## 6. Automated Pytest Execution Proof (16 of 16 Tests)

Agar reviewer automated tests ka proof maange, to aap terminal mein yeh command chala kar live dikha sakte hain:

```powershell
cd "d:\Weekend1_Talha Ahmed\03_Marketplace\backend"
pytest tests/test_marketplace_api.py -v
```

**Passing Test Cases Summary:**
- `TC-MKT-AUTH-01`: Buyer / Seller registration & JWT issuance.
- `TC-MKT-CAT-01`: Listing creation & category classification.
- `TC-MKT-OFF-01`: Buyer initial offer creation (`status = pending`).
- `TC-MKT-OFF-02`: Self-offer on own listing blocked (`HTTP 400`).
- `TC-MKT-OFF-03`: Counter-offer turn enforcement (back-to-back counter blocked).
- `TC-MKT-OFF-04`: Seller counter-offer success (`status = countered_by_seller`).
- `TC-MKT-OFF-05`: Offer acceptance reserves listing (`listing.status = reserved`).
- `TC-MKT-OFF-06`: Transaction completion marks listing sold (`listing.status = sold`).
- `TC-MKT-REV-01`: Verified review creation on completed transaction.
- `TC-MKT-REV-02`: Premature review rejected on pending offer.
- `TC-MKT-REV-03`: Non-participant review rejected (`HTTP 403`).
- `TC-MKT-REV-04`: Duplicate review on same offer blocked (`UniqueConstraint`).
- `TC-MKT-REV-05`: Out-of-bounds rating blocked (`rating > 5`).
- `TC-MKT-REV-06`: Seller dynamic average rating update.
- `TC-MKT-SEC-01`: Private negotiation isolation between peer users.
- `TC-MKT-ADM-01`: Market admin dispute & global listing moderation.
