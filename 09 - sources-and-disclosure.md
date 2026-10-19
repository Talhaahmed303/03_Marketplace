# FALCONXOFT WEEKEND 1 EVALUATION — PROJECT 03: SOURCES & ASSISTANCE DISCLOSURE

**Author:** Talha Ahmed  
**Evaluation Role:** Full-Stack Intern Performance Evaluation (Weekend 1)  
**Deliverable Number:** 09 of 10  
**Specification Reference:** Weekend Assignment.pdf §3  

---

## 1. Professional Integrity Statement

In adherence to FalconXoft's engineering integrity guidelines, this document discloses all third-party libraries, architectural patterns, reference documentation, and AI assistance utilized during the development and verification of Project 03: Two-Sided Marketplace (GearExchange).

Every line of application code, database schema, migration, automated test, and deployment specification was reviewed, executed, and verified by the author on local bare-metal infrastructure.

---

## 2. Third-Party Libraries & Framework Dependencies

| Library / Tool | Version | License | Justification & Purpose |
| :--- | :--- | :--- | :--- |
| **Django** | 5.2.x | BSD-3-Clause | Robust Python web framework with ORM and transactional state handling |
| **Django REST Framework** | 3.16.x | BSD-2-Clause | Standardized RESTful serializers, APIViews, and permissions |
| **djangorestframework-simplejwt** | 5.5.x | MIT | Cryptographically signed HMAC-SHA256 JWT token authentication |
| **drf-spectacular** | 0.29.x | BSD-3-Clause | OpenAPI 3.0 schema generation from Django serializers and views |
| **psycopg2-binary** | 2.9.10 | LGPL / BSD | High-performance C-adapter for native PostgreSQL communication |
| **pytest & pytest-django** | 8.4.x / 4.11.x | MIT / BSD | Automated test runner with isolated transaction fixture support |
| **ReportLab** | 4.4.x | BSD | Programmatic PDF generation engine for architectural diagrams |
| **XlsxWriter** | 3.2.x | BSD-2-Clause | Excel workbook compilation engine with native formatting & formulas |
| **Next.js** | 14.2.35 | MIT | React framework for server/client components and fast page compilation |
| **React & React-DOM** | 18.3.1 | MIT | Declarative component UI library |
| **Tailwind CSS** | 3.4.17 | MIT | Utility-first CSS framework for responsive layout and styling |

---

## 3. Reference Documentation & Technical Standards

1. **PostgreSQL 18 Documentation:**
   - *Table Constraints & Unique Constraints:* `https://www.postgresql.org/docs/current/ddl-constraints.html`
   - *Check Constraints & Rating Validation:* `https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-CHECK-CONSTRAINTS`
2. **Reverb.com Negotiation API & Experience Design:**
   - *Offers & Counter-Offer Workflow Inspiration:* `https://reverb.com/page/making-an-offer`
3. **Django Model Constraints & Aggregations:**
   - *Django UniqueConstraint API:* `https://docs.djangoproject.com/en/5.2/ref/models/constraints/#uniqueconstraint`
   - *QuerySet Aggregation:* `https://docs.djangoproject.com/en/5.2/topics/db/aggregation/`
4. **AWS Pricing Calculator & Documentation:**
   - *ECS Fargate Pricing:* `https://aws.amazon.com/fargate/pricing/`
   - *RDS PostgreSQL Pricing:* `https://aws.amazon.com/rds/postgresql/pricing/`
5. **Hostinger VPS Pricing Reference:**
   - *Hostinger KVM Hosting Specifications:* `https://www.hostinger.com/vps-hosting` (Retrieved 2026-10-17)

---

## 4. AI Assistance Disclosure

In alignment with evaluation guidelines, AI assistance (Antigravity IDE / Claude 3.5 / Gemini) was utilized as an intelligent pair programmer for:
- Scaffolding initial repetitive boilerplate code for Django serializers and Next.js layout files.
- Drafting initial mathematical pricing models in Python XlsxWriter scripts.
- Accelerating vector coordinate placement for ReportLab drawing flowables.
- Formulating edge-case negotiation test cases (`test_counter_offer_turn_enforcement`, `test_cannot_accept_own_counter_offer`).

**Engineering Ownership:**
All architectural decisions, database normalization (3NF), state machine turn enforcement, and test assertions were authored, debugged, and verified by Talha Ahmed.
