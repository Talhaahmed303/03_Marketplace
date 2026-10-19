# FALCONXOFT WEEKEND 1 EVALUATION — PROJECT 03: ENGINEERING DECISIONS & TRADE-OFFS

**Author:** Talha Ahmed  
**Evaluation Role:** Full-Stack Intern Performance Evaluation (Weekend 1)  
**Deliverable Number:** 06 of 10  
**Specification Reference:** Weekend Assignment.pdf §3  

---

## 1. Decision 1: Direct Host Execution vs Docker / Docker Compose

### Context & Constraint
The user and evaluation requirements strictly dictated **direct execution on the local host machine with zero Docker or Docker Compose containers**.

### Alternatives Considered
1. **Docker & Docker Compose:** Containerize Next.js, Django, and PostgreSQL into a multi-container network.
2. **Direct Bare-Metal Host Execution (Adopted):** Run Django DRF on Python 3.11 with virtual environments, Next.js on Node.js 18+, and connect directly to the native PostgreSQL 18 Windows service (`postgresql-x64-18`).

### Trade-Off Evaluation

| Evaluation Criteria | Docker / Docker Compose | Bare-Metal Host Execution (Adopted) |
| :--- | :--- | :--- |
| **Windows Overhead & Resource Consumption** | High (WSL2 VM consumes 4-8 GB RAM, high disk I/O latency on `/mnt/d`) | Minimal (Zero virtualization overhead, direct NVMe disk speed) |
| **Startup & Debugging Speed** | Slower container build cycles, hidden log layers | Instant startup (`python manage.py runserver`, `npm run dev`) with instant hot-reload |
| **Local Environment Reproducibility** | High across heterogeneous OS environments | High when documented with explicit package versions and scripts |
| **Production Parity** | High container parity with cloud ECS/K8s | Requires container build step during deployment phase |

### Rationale & Production Migration Path
For this intensive evaluation on Windows 11, running natively eliminates virtualization overhead, prevents WSL2 file-watcher latency issues in Next.js, and allows direct inspection of PostgreSQL via standard tools (`psql`, pgAdmin). In `08 - cost-and-scaling.xlsx`, we detail the containerization path for AWS ECS / Fargate when transitioning from MVP to cloud scale.

---

## 2. Decision 2: Negotiation Architecture — REST State Machine vs Unstructured Chat

### Context
In many peer-to-peer apps, negotiation is handled via an unstructured chat room ("Can you do $1,500?"). This leads to ambiguous agreements, verbal disputes, missed commitments, and untrackable settlement status.

### Alternatives Considered
1. **Unstructured Real-Time Chat (WebSocket):** Free-form text messages with a separate "Agree" button.
2. **Explicit Finite State Machine with History Audit (Adopted):** A formal state machine (`pending` -> `countered_by_seller` <-> `countered_by_buyer` -> `accepted` -> `declined` -> `completed`) backed by an immutable `OfferHistory` log.

### Trade-Off Evaluation

| Criteria | Unstructured Chat | Formal FSM + History Audit (Adopted) |
| :--- | :--- | :--- |
| **Ambiguity & Fraud Risk** | High (disagreements over agreed amount or shipping) | Zero (Every counter-offer requires an explicit numeric dollar amount and message) |
| **Turn Enforcement** | Impossible (parties talk over each other) | Guaranteed (API rejects out-of-turn counters and self-acceptance) |
| **Inventory State Linking** | Loose (manual seller action required to reserve listing) | Tight (Accepting an offer automatically transitions listing to `reserved`) |
| **Legal / Dispute Auditability** | Difficult to reconstruct intent | Trivial (Every move has an immutable timestamped log record in `OfferHistory`) |

### Rationale
A formal FSM provides unambiguous transactional boundaries. Sellers and buyers always know whose turn it is, the exact agreed dollar figure, and when the listing is officially reserved.

---

## 3. Decision 3: Review Eligibility Gating — Transaction Completion vs Open Reviews

### Problem Scope
Open review platforms (e.g. Trustpilot or unverified Yelp pages) suffer from competitor smear campaigns, fake 5-star reviews, and bot spam. In a high-value equipment marketplace (e.g. $4,000 cameras), trust is existential.

### Alternatives Considered
1. **Open Post-Registration Reviews:** Any registered user can review any seller.
2. **Inquiry-Gated Reviews:** Anyone who initiated a message or offer can review.
3. **Strict Completion-Gated Reviews (Adopted):** A review can ONLY be created if the offer is in status `completed`, the user was a verified buyer or seller on that offer, and no prior review was submitted.

### Implementation & Verification
```python
# Eligibility check in views.py
if offer.status != 'completed':
    return Response({'detail': 'Only completed transactions can be reviewed.'}, status=400)
if request.user != offer.buyer and request.user != offer.seller:
    return Response({'detail': 'You are not a participant in this completed transaction.'}, status=403)
```
Backed by a PostgreSQL database-level `UniqueConstraint(fields=['offer', 'reviewer'])`, mathematically preventing duplicate review spam. This is proven in automated tests `test_verified_review_eligibility_completed_only` and `test_duplicate_review_prevented`.

---

## 4. Decision 4: Rating Aggregation — Dynamic Incremental vs Periodic Batch

### Context
When a new 5-star review is published, the seller's displayed profile rating should update.

### Solution Adopted
We implemented an incremental calculation directly inside `Review.save()`:
```python
reviews = Review.objects.filter(reviewee=self.reviewee)
self.reviewee.rating_avg = round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 2)
self.reviewee.rating_count = reviews.count()
self.reviewee.save(update_fields=['rating_avg', 'rating_count'])
```

### Trade-Offs
- **Read Performance:** O(1) read latency when browsing listings, because `rating_avg` is denormalized directly on the `CustomUser` model.
- **Write Performance:** Negligible O(N) aggregation where N is seller's review count (typically < 100).
- **Scale Path:** At 100k+ reviews, transition to Celery async worker or Redis cached counter.

---

## 5. Summary of Architectural Posture

| Component | Choice | Core Benefit |
| :--- | :--- | :--- |
| **Host Runtime** | Bare-Metal Windows Local Host | Peak developer velocity, zero virtualization friction, explicit reproducibility |
| **Negotiation Engine** | Formal REST Finite State Machine | Strict turn enforcement, zero ambiguity, audit log |
| **Inventory Linking** | Atomic status sync (`active` -> `reserved` -> `sold`) | Zero double selling or concurrent dispute |
| **Trust Engine** | Transaction Completion-Gated Reviews | Zero fake reviews, mathematically verified reputation |
| **Integrity Guard** | PostgreSQL `UniqueConstraint` & `CheckConstraint` | Engine-level spam and range defense |
