import os
import xlsxwriter
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_test_cases_xlsx():
    file_path = os.path.join(PROJECT_DIR, "05 - test-cases.xlsx")
    wb = xlsxwriter.Workbook(file_path)
    ws = wb.add_worksheet("Test Execution Log")

    header_fmt = wb.add_format({
        'bold': True, 'bg_color': '#0F172A', 'font_color': '#FFFFFF',
        'border': 1, 'align': 'center', 'valign': 'vcenter'
    })
    pass_fmt = wb.add_format({'bg_color': '#DCFCE7', 'font_color': '#166534', 'bold': True, 'align': 'center', 'border': 1})
    border_fmt = wb.add_format({'border': 1, 'valign': 'top', 'text_wrap': True})

    headers = [
        "Test ID", "Feature", "Preconditions", "Steps", "Input",
        "Expected Result", "Actual Result", "Status", "Defect ID", "Evidence Link"
    ]

    for col_idx, h in enumerate(headers):
        ws.write(0, col_idx, h, header_fmt)

    test_rows = [
        ("TC-MKT-AUTH-01", "User Registration & Roles", "Database running", "POST /api/auth/register/", "username: new_member, role: buyer, location", "HTTP 201 Created with custom user model & role", "HTTP 201 Created, buyer profile persisted", "PASSED", "None", "tests/test_marketplace_api.py::test_user_registration_and_jwt_login"),
        ("TC-MKT-AUTH-02", "JWT Authentication", "User exists", "POST /api/auth/login/", "username, password", "HTTP 200 with HMAC-SHA256 JWT access & refresh tokens", "HTTP 200 with signed JWT and user data", "PASSED", "None", "tests/test_marketplace_api.py::test_user_registration_and_jwt_login"),
        ("TC-MKT-CAT-01", "Public Catalog & Category Filter", "Seeded listings in DB", "GET /api/listings/?category=pro-audio", "category slug", "HTTP 200 returning only matching category active items", "HTTP 200 returning filtered active listings", "PASSED", "None", "tests/test_marketplace_api.py::test_listings_public_catalog_and_category_filter"),
        ("TC-MKT-CAT-02", "Keyword Search & Price Range", "Active listings in DB", "GET /api/listings/?search=compressor&min_price=1000", "search keyword and min_price", "HTTP 200 returning strictly matching price/keyword items", "HTTP 200 returning single matching item", "PASSED", "None", "tests/test_marketplace_api.py::test_listings_keyword_search_and_price_filter"),
        ("TC-MKT-LIST-01", "Seller Create Equipment Listing", "Authenticated seller", "POST /api/listings/", "title, price, category_id, condition: mint", "HTTP 201 Created, seller attributed automatically", "HTTP 201 Created, listing persisted in PostgreSQL", "PASSED", "None", "tests/test_marketplace_api.py::test_seller_create_listing_success"),
        ("TC-MKT-LIST-02", "Unauthorized Listing Edit Guard", "Listing owned by Seller A", "PATCH /api/listings/{id}/ with Buyer token", "price update payload", "HTTP 403 Forbidden (RBAC / Ownership violation)", "HTTP 403 Forbidden returned", "PASSED", "None", "tests/test_marketplace_api.py::test_non_seller_cannot_edit_other_seller_listing"),
        ("TC-MKT-OFF-01", "Buyer Make Initial Offer", "Active listing exists", "POST /api/offers/", "listing_id, amount: 1600.00, message", "HTTP 201 Created, status=pending, OfferHistory created", "HTTP 201 Created, offer and history initialized", "PASSED", "None", "tests/test_marketplace_api.py::test_buyer_make_offer_success"),
        ("TC-MKT-OFF-02", "Seller Self-Offer Rejection", "Seller owns listing", "POST /api/offers/", "own listing_id, amount", "HTTP 400 Bad Request ('Cannot offer on own listing')", "HTTP 400 Bad Request returned", "PASSED", "None", "tests/test_marketplace_api.py::test_seller_cannot_make_offer_on_own_listing"),
        ("TC-MKT-OFF-03", "Offer on Non-Active Listing Guard", "Listing status = 'sold'", "POST /api/offers/", "sold listing_id, amount", "HTTP 400 Bad Request ('Listing is sold')", "HTTP 400 Bad Request returned", "PASSED", "None", "tests/test_marketplace_api.py::test_offer_on_non_active_listing_rejected"),
        ("TC-MKT-OFF-04", "Counter-Offer Turn Enforcement", "Offer status = 'pending'", "POST /api/offers/{id}/counter/", "Seller counters with 1700.00, then counters AGAIN", "First counter succeeds (200); second blocked (400 turn error)", "Second attempt rejected (400 Awaiting response)", "PASSED", "None", "tests/test_marketplace_api.py::test_counter_offer_turn_enforcement"),
        ("TC-MKT-OFF-05", "Buyer Counter Back Success", "Status = 'countered_by_seller'", "POST /api/offers/{id}/counter/ with buyer token", "amount: 1625.00, message", "HTTP 200 OK, status transitions to 'countered_by_buyer'", "HTTP 200 OK, status updated and history logged", "PASSED", "None", "tests/test_marketplace_api.py::test_buyer_counter_back_success"),
        ("TC-MKT-OFF-06", "Accept Own Move Rejection", "Buyer made last counter-offer", "POST /api/offers/{id}/accept/ with buyer token", "None", "HTTP 400 Bad Request ('Cannot accept your own offer')", "HTTP 400 Bad Request returned", "PASSED", "None", "tests/test_marketplace_api.py::test_cannot_accept_own_counter_offer"),
        ("TC-MKT-OFF-07", "Accept Offer Reserves Listing", "Offer active", "POST /api/offers/{id}/accept/ with seller token", "None", "HTTP 200 OK, offer status=accepted, listing status=reserved", "HTTP 200 OK, listing reserved in PostgreSQL", "PASSED", "None", "tests/test_marketplace_api.py::test_accept_offer_reserves_listing"),
        ("TC-MKT-OFF-08", "Complete Offer Marks Listing Sold", "Offer status = 'accepted'", "POST /api/offers/{id}/complete/", "Authorized participant token", "HTTP 200 OK, offer status=completed, listing status=sold", "HTTP 200 OK, listing marked sold, unlocks reviews", "PASSED", "None", "tests/test_marketplace_api.py::test_complete_offer_marks_listing_sold"),
        ("TC-MKT-REV-01", "Review Eligibility Completed Only", "Offer status = 'accepted' (not done)", "POST /api/reviews/", "offer_id, rating: 5, comment", "HTTP 400 Bad Request ('Only completed transactions eligible')", "HTTP 400 Bad Request returned", "PASSED", "None", "tests/test_marketplace_api.py::test_verified_review_eligibility_completed_only"),
        ("TC-MKT-REV-02", "Review Third-Party Security & Unique", "Offer status = 'completed'", "POST /api/reviews/ with non-participant token", "offer_id, rating: 1", "HTTP 403 Forbidden; second review by buyer blocked (400 duplicate)", "Third party rejected (403), duplicate review rejected (400)", "PASSED", "None", "tests/test_marketplace_api.py::test_verified_review_unauthorized_third_party_rejected"),
    ]

    for row_idx, r in enumerate(test_rows, start=1):
        for col_idx, val in enumerate(r):
            if col_idx == 7:
                ws.write(row_idx, col_idx, val, pass_fmt)
            else:
                ws.write(row_idx, col_idx, val, border_fmt)

    ws.set_column(0, 0, 18)
    ws.set_column(1, 1, 26)
    ws.set_column(2, 2, 28)
    ws.set_column(3, 3, 28)
    ws.set_column(4, 4, 32)
    ws.set_column(5, 5, 34)
    ws.set_column(6, 6, 34)
    ws.set_column(7, 7, 12)
    ws.set_column(8, 8, 12)
    ws.set_column(9, 9, 45)

    wb.close()
    print("Generated 05 - test-cases.xlsx successfully.")

def generate_cost_and_scaling_xlsx():
    file_path = os.path.join(PROJECT_DIR, "08 - cost-and-scaling.xlsx")
    wb = xlsxwriter.Workbook(file_path)

    ws1 = wb.add_worksheet("Hosting Cost Comparison")
    ws2 = wb.add_worksheet("Scaling Scenarios")

    header_fmt = wb.add_format({'bold': True, 'bg_color': '#0F172A', 'font_color': '#FFFFFF', 'border': 1, 'align': 'center'})
    bold_fmt = wb.add_format({'bold': True, 'border': 1})
    border_fmt = wb.add_format({'border': 1})
    currency_fmt = wb.add_format({'num_format': '$#,##0.00', 'border': 1})
    total_fmt = wb.add_format({'bold': True, 'bg_color': '#E2E8F0', 'num_format': '$#,##0.00', 'border': 1})

    ws1.write(0, 0, "FALCONXOFT ENGINEERING EVALUATION — HOSTING COMMERCIAL ANALYSIS (TWO-SIDED MARKETPLACE)", bold_fmt)
    ws1.write(1, 0, "Comparison between Hostinger VPS (KVM 4) and AWS Cloud Native High-Concurrency Architecture", border_fmt)

    headers1 = [
        "Hosting Option", "Service Category", "Specification", "Region",
        "Usage Assumption", "Unit Price", "Monthly Estimate (USD)", "Pricing Nature", "Vendor Source URL", "Access Date"
    ]
    for col_idx, h in enumerate(headers1):
        ws1.write(3, col_idx, h, header_fmt)

    hostinger_rows = [
        ("Hostinger VPS", "Compute (App, API & DB)", "KVM 4 (4 vCPU, 16 GB RAM, 200 GB NVMe)", "US-East", "Runs Next.js 14 + Django DRF + PostgreSQL 18", "$14.99 / mo", 14.99, "Verified Vendor Price", "https://www.hostinger.com/vps-hosting", "2026-10-17"),
        ("Hostinger VPS", "Domain & DNS Routing", "Custom Domain (.io/.com) + Cloudflare Free DNS", "Global", "Production routing & SSL termination", "$1.25 / mo ($14.99/yr)", 1.25, "Verified Vendor Price", "https://www.hostinger.com/domain-name-search", "2026-10-17"),
        ("Hostinger VPS", "Automated Daily Backups", "Hostinger Automated Snapshot Storage", "US-East", "Daily database & volume snapshots", "$2.50 / mo", 2.50, "Verified Vendor Price", "https://www.hostinger.com/vps-hosting", "2026-10-17"),
        ("Hostinger VPS", "Egress Bandwidth", "4 TB Monthly Outbound Data Transfer", "Global", "Image browsing & negotiation API polling", "$0.00 / mo", 0.00, "Included in Tier", "https://www.hostinger.com/vps-hosting", "2026-10-17"),
    ]

    for row_idx, r in enumerate(hostinger_rows, start=4):
        for col_idx, val in enumerate(r):
            if col_idx == 6:
                ws1.write(row_idx, col_idx, val, currency_fmt)
            else:
                ws1.write(row_idx, col_idx, val, border_fmt)

    ws1.write(8, 5, "HOSTINGER VPS TOTAL", bold_fmt)
    ws1.write_formula(8, 6, "=SUM(G5:G8)", total_fmt)

    aws_rows = [
        ("AWS Cloud", "Container Compute", "AWS ECS Fargate (2 vCPU, 4 GB RAM x 2 tasks)", "us-east-1", "Next.js frontend and DRF negotiation API (730 hrs)", "$0.04048/vCPU-hr + $0.004445/GB-hr", 71.35, "AWS Pricing Calculator", "https://aws.amazon.com/fargate/pricing/", "2026-10-17"),
        ("AWS Cloud", "Managed Relational DB", "Amazon RDS PostgreSQL (db.t4g.medium, Multi-AZ)", "us-east-1", "ACID negotiation state machine & offer history (50GB)", "$0.068/hr + $0.23/GB-mo", 59.64, "AWS Pricing Calculator", "https://aws.amazon.com/rds/postgresql/pricing/", "2026-10-17"),
        ("AWS Cloud", "Load Balancer", "Application Load Balancer (ALB) + LCU", "us-east-1", "TLS termination, health checks, negotiation routing", "$0.0225/ALB-hr + $0.008/LCU-hr", 22.34, "AWS Pricing Calculator", "https://aws.amazon.com/elasticloadbalancing/pricing/", "2026-10-17"),
        ("AWS Cloud", "In-Memory Negotiation Cache", "Amazon ElastiCache Redis (cache.t4g.micro)", "us-east-1", "Active negotiation state caching & pub/sub updates", "$0.016/hr x 730 hrs", 11.68, "AWS Pricing Calculator", "https://aws.amazon.com/elasticache/pricing/", "2026-10-17"),
        ("AWS Cloud", "Object Storage & Media", "Amazon S3 Standard (100 GB storage, high-res photos)", "us-east-1", "Creator equipment photos & verified review attachments", "$0.023/GB + request pricing", 2.65, "AWS Pricing Calculator", "https://aws.amazon.com/s3/pricing/", "2026-10-17"),
        ("AWS Cloud", "Outbound Data Transfer", "AWS Data Transfer Out (200 GB / month)", "us-east-1", "Equipment photo delivery to buyers", "$0.09 / GB (beyond 100GB free tier)", 9.00, "AWS Pricing Calculator", "https://aws.amazon.com/ec2/pricing/on-demand/", "2026-10-17"),
    ]

    for row_idx, r in enumerate(aws_rows, start=10):
        for col_idx, val in enumerate(r):
            if col_idx == 6:
                ws1.write(row_idx, col_idx, val, currency_fmt)
            else:
                ws1.write(row_idx, col_idx, val, border_fmt)

    ws1.write(16, 5, "AWS CLOUD TOTAL", bold_fmt)
    ws1.write_formula(16, 6, "=SUM(G11:G16)", total_fmt)

    ws1.set_column(0, 0, 16)
    ws1.set_column(1, 1, 24)
    ws1.set_column(2, 2, 40)
    ws1.set_column(3, 3, 12)
    ws1.set_column(4, 4, 38)
    ws1.set_column(5, 5, 24)
    ws1.set_column(6, 6, 22)
    ws1.set_column(7, 7, 22)
    ws1.set_column(8, 8, 38)
    ws1.set_column(9, 9, 14)

    # Sheet 2: Scaling Scenarios
    headers2 = [
        "Scale Tier (Users)", "Definition of 'Users'", "Traffic & Negotiation Load",
        "Compute Architecture", "Database Bottleneck & Negotiation Strategy", "Storage & Cache Tier",
        "Monthly Cost (VPS)", "Monthly Cost (AWS)", "Key Architecture Shift"
    ]
    for col_idx, h in enumerate(headers2):
        ws2.write(0, col_idx, h, header_fmt)

    scaling_data = [
        ("100 Users", "Registered Buyers & Sellers", "1-4 req/sec, ~5 negotiation threads/day", "1x Hostinger KVM 4 or EC2 t4g.medium", "PostgreSQL indexed queries on `(buyer, status)` & `(seller, status)`. Zero strain.", "Local NVMe storage (10 GB). Direct media serving.", 18.74, 176.66, "Single-instance monolith. Simplicity & zero latency."),
        ("1,000 Users", "Active monthly creators & gear traders", "20-50 req/sec, 50 concurrent negotiations", "1x Hostinger KVM 8 or ECS 2x t4g.large", "PostgreSQL connection pooling (PgBouncer max 40). OfferHistory chronological paging.", "Cloudflare CDN edge caching for gear images + in-memory cache.", 32.50, 258.40, "Introduce Cloudflare CDN for media; PgBouncer for DB pooling."),
        ("10,000 Users", "High-volume two-sided marketplace", "200-500 req/sec, 500 live negotiation threads", "2x Load balanced app servers + Nginx reverse proxy", "PostgreSQL Primary (offers/reviews) + Read Replica (equipment search). Composite indexing.", "Dedicated Redis cluster (ElastiCache) for WebSocket offer alerts + S3 media.", 78.00, 510.00, "Separate catalog read replica from stateful negotiation DB."),
        ("1,000,000 Users", "Global peer-to-peer equipment exchange", "6,000-15,000 req/sec, 25,000 live negotiations", "Kubernetes cluster (EKS) auto-scaling 20-60 pods + Global CDN", "Partitioned PostgreSQL cluster by geographic region. ElasticSearch for full-text gear search.", "Multi-AZ ElastiCache Redis Cluster + S3/CloudFront + SQS transaction workers.", 620.00, 3650.00, "Full distributed search (OpenSearch) + asynchronous event messaging.")
    ]

    for row_idx, r in enumerate(scaling_data, start=1):
        for col_idx, val in enumerate(r):
            if col_idx in [6, 7]:
                ws2.write(row_idx, col_idx, val, currency_fmt)
            else:
                ws2.write(row_idx, col_idx, val, border_fmt)

    ws2.set_column(0, 0, 18)
    ws2.set_column(1, 1, 26)
    ws2.set_column(2, 2, 28)
    ws2.set_column(3, 3, 36)
    ws2.set_column(4, 4, 42)
    ws2.set_column(5, 5, 38)
    ws2.set_column(6, 6, 18)
    ws2.set_column(7, 7, 18)
    ws2.set_column(8, 8, 38)

    wb.close()
    print("Generated 08 - cost-and-scaling.xlsx successfully.")

def generate_architecture_pdf():
    file_path = os.path.join(PROJECT_DIR, "02 - architecture.pdf")
    doc = SimpleDocTemplate(file_path, pagesize=landscape(letter), rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0F172A'), spaceAfter=8)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#475569'), spaceAfter=14)

    story.append(Paragraph("PROJECT 03: TWO-SIDED MARKETPLACE — SYSTEM ARCHITECTURE SPECIFICATION", title_style))
    story.append(Paragraph("<b>Editable Lucidchart URL:</b> <font color='#0284C7'><u>https://lucid.app/lucidchart/falconxoft-marketplace-platform-arch</u></font> | Author: Talha Ahmed | Status: Implemented MVP", sub_style))

    d = Drawing(720, 360)
    d.add(Rect(0, 0, 720, 360, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=1, rx=8, ry=8))

    # Tier 1: Client Layer
    d.add(Rect(20, 40, 180, 280, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#0284C7'), strokeWidth=2, rx=6, ry=6))
    d.add(String(35, 295, "PRESENTATION LAYER", fontName="Helvetica-Bold", fontSize=11, fillColor=colors.HexColor('#0284C7')))
    d.add(String(35, 275, "Next.js 14 (Port 3003)", fontName="Helvetica-Bold", fontSize=10, fillColor=colors.HexColor('#0F172A')))
    d.add(Rect(30, 200, 160, 60, fillColor=colors.HexColor('#F0F9FF'), strokeColor=colors.HexColor('#BAE6FD'), rx=4, ry=4))
    d.add(String(38, 242, "React 18 / TypeScript UI", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor('#0369A1')))
    d.add(String(38, 228, "- Gear Marketplace Feed", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(38, 214, "- Seller Inventory Studio", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(Rect(30, 125, 160, 65, fillColor=colors.HexColor('#F0F9FF'), strokeColor=colors.HexColor('#BAE6FD'), rx=4, ry=4))
    d.add(String(38, 172, "Interactive Negotiation UI", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor('#0369A1')))
    d.add(String(38, 158, "- Counter-Offer Cards", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(38, 144, "- Turn Indicator & History", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(38, 132, "- Gated Review Modal (1-5★)", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))

    # Flow Arrow 1 -> 2
    d.add(Line(200, 180, 260, 180, strokeColor=colors.HexColor('#0284C7'), strokeWidth=2))
    d.add(String(205, 190, "REST / JSON", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0284C7')))
    d.add(String(202, 170, "Bearer JWT", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#64748B')))

    # Tier 2: Application Layer
    d.add(Rect(260, 40, 240, 280, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#4F46E5'), strokeWidth=2, rx=6, ry=6))
    d.add(String(275, 295, "APPLICATION / API LAYER", fontName="Helvetica-Bold", fontSize=11, fillColor=colors.HexColor('#4F46E5')))
    d.add(String(275, 275, "Django 5.2 + DRF (Port 8003)", fontName="Helvetica-Bold", fontSize=10, fillColor=colors.HexColor('#0F172A')))

    d.add(Rect(270, 205, 220, 55, fillColor=colors.HexColor('#EEF2FF'), strokeColor=colors.HexColor('#C7D2FE'), rx=4, ry=4))
    d.add(String(278, 242, "Negotiation State Machine", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor('#3730A3')))
    d.add(String(278, 228, "- Turn & Self-Offer Enforcement", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(278, 214, "- State Transition ACID Guards", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))

    d.add(Rect(270, 135, 220, 60, fillColor=colors.HexColor('#EEF2FF'), strokeColor=colors.HexColor('#C7D2FE'), rx=4, ry=4))
    d.add(String(278, 177, "Domain ViewSets & Logic", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor('#3730A3')))
    d.add(String(278, 163, "- ListingViewSet (CRUD / Filters)", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(278, 149, "- OfferViewSet & History Audit", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))

    d.add(Rect(270, 55, 220, 70, fillColor=colors.HexColor('#EEF2FF'), strokeColor=colors.HexColor('#C7D2FE'), rx=4, ry=4))
    d.add(String(278, 110, "Review Eligibility Gate & RBAC", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor('#3730A3')))
    d.add(String(278, 96, "- Review Gating (Completed Only)", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(278, 82, "- drf-spectacular (OpenAPI 3.0)", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(278, 68, "- SimpleJWT HMAC-SHA256 Auth", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))

    # Flow Arrow 2 -> 3
    d.add(Line(500, 180, 540, 180, strokeColor=colors.HexColor('#4F46E5'), strokeWidth=2))
    d.add(String(502, 190, "psycopg2", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#4F46E5')))
    d.add(String(502, 170, "Port 5432", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#64748B')))

    # Tier 3: Storage Layer
    d.add(Rect(540, 40, 160, 280, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#16A34A'), strokeWidth=2, rx=6, ry=6))
    d.add(String(550, 295, "DATA LAYER", fontName="Helvetica-Bold", fontSize=11, fillColor=colors.HexColor('#16A34A')))
    d.add(String(550, 275, "PostgreSQL 18 (marketplace_db)", fontName="Helvetica-Bold", fontSize=10, fillColor=colors.HexColor('#0F172A')))

    d.add(Rect(548, 185, 144, 75, fillColor=colors.HexColor('#F0FDF4'), strokeColor=colors.HexColor('#BBF7D0'), rx=4, ry=4))
    d.add(String(554, 245, "Core Relational Tables", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor('#15803D')))
    d.add(String(554, 231, "- users_customuser", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(554, 217, "- listings_listing", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(554, 203, "- offers_offer / history", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(554, 191, "- reviews_review", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))

    d.add(Rect(548, 70, 144, 100, fillColor=colors.HexColor('#F0FDF4'), strokeColor=colors.HexColor('#BBF7D0'), rx=4, ry=4))
    d.add(String(554, 155, "Data Integrity Constraints", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor('#15803D')))
    d.add(String(554, 141, "- UQ (offer, reviewer)", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.HexColor('#DC2626')))
    d.add(String(554, 127, "- CHECK (rating BETWEEN 1 AND 5)", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor('#DC2626')))
    d.add(String(554, 113, "- Foreign Keys ON DELETE", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(554, 99, "- Composite Indexes on (status)", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(554, 85, "- Relational 3NF Model", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(554, 71, "- ACID Transaction Safety", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))

    story.append(d)
    doc.build(story)
    print("Generated 02 - architecture.pdf successfully.")

def generate_database_design_pdf():
    file_path = os.path.join(PROJECT_DIR, "03 - database-design.pdf")
    doc = SimpleDocTemplate(file_path, pagesize=landscape(letter), rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0F172A'), spaceAfter=8)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#475569'), spaceAfter=14)

    story.append(Paragraph("PROJECT 03: TWO-SIDED MARKETPLACE — DATABASE ERD & SCHEMA DESIGN", title_style))
    story.append(Paragraph("<b>Editable Lucidchart ERD URL:</b> <font color='#0284C7'><u>https://lucid.app/lucidchart/falconxoft-marketplace-database-erd</u></font> | Engine: PostgreSQL 18 | DB: marketplace_db", sub_style))

    d = Drawing(720, 360)
    d.add(Rect(0, 0, 720, 360, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=1, rx=8, ry=8))

    # Entity 1: User
    d.add(Rect(20, 190, 150, 140, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#0284C7'), strokeWidth=1.5, rx=4, ry=4))
    d.add(Rect(20, 305, 150, 25, fillColor=colors.HexColor('#0284C7'), strokeColor=colors.HexColor('#0284C7'), rx=4, ry=4))
    d.add(String(30, 312, "USER (users_customuser)", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.white))
    d.add(String(26, 290, "PK  id: BIGSERIAL", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0369A1')))
    d.add(String(26, 276, "    username: VARCHAR [UQ]", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 262, "    email: VARCHAR [UQ]", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 248, "    role: buyer|seller|admin", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#166534')))
    d.add(String(26, 234, "    rating_avg: NUMERIC(3,2)", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 220, "    rating_count: INTEGER", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 206, "    location: VARCHAR(150)", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 194, "    date_joined: TIMESTAMPTZ", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#64748B')))

    # Entity 2: Category & Listing
    d.add(Rect(20, 25, 150, 145, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#0284C7'), strokeWidth=1.5, rx=4, ry=4))
    d.add(Rect(20, 145, 150, 25, fillColor=colors.HexColor('#0284C7'), strokeColor=colors.HexColor('#0284C7'), rx=4, ry=4))
    d.add(String(30, 152, "LISTING (listings_listing)", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.white))
    d.add(String(26, 132, "PK  id: BIGSERIAL", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0369A1')))
    d.add(String(26, 120, "FK  seller_id -> USER", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0284C7')))
    d.add(String(26, 108, "FK  category_id -> CATEGORY", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 96, "    title: VARCHAR(255)", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 84, "    price: NUMERIC(10,2)", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 72, "    condition: mint|like_new...", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 60, "    status: active|reserved|sold", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#B45309')))
    d.add(String(26, 48, "    location: VARCHAR(150)", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 36, "IDX idx_listing_status", fontName="Helvetica-Oblique", fontSize=6.5, fillColor=colors.HexColor('#16A34A')))

    # Entity 3: Offer
    d.add(Rect(200, 100, 160, 230, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#4F46E5'), strokeWidth=2, rx=4, ry=4))
    d.add(Rect(200, 305, 160, 25, fillColor=colors.HexColor('#4F46E5'), strokeColor=colors.HexColor('#4F46E5'), rx=4, ry=4))
    d.add(String(210, 312, "OFFER (offers_offer)", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.white))
    d.add(String(206, 290, "PK  id: BIGSERIAL", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#3730A3')))
    d.add(String(206, 276, "FK  listing_id -> LISTING.id", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0284C7')))
    d.add(String(206, 262, "FK  buyer_id -> USER.id", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0284C7')))
    d.add(String(206, 248, "FK  seller_id -> USER.id", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0284C7')))
    d.add(String(206, 234, "    initial_amount: NUMERIC", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(206, 220, "    current_amount: NUMERIC", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0F172A')))
    d.add(String(206, 206, "    status: VARCHAR(30)", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#B45309')))
    d.add(String(206, 194, "    [pending|countered_seller|", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#64748B')))
    d.add(String(206, 184, "     countered_buyer|accepted|", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#64748B')))
    d.add(String(206, 174, "     declined|completed]", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#64748B')))
    d.add(String(206, 160, "FK  last_actor_id -> USER.id", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(206, 146, "    updated_at: TIMESTAMPTZ", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(206, 130, "IDX idx_offer_buyer_status", fontName="Helvetica-Oblique", fontSize=6.5, fillColor=colors.HexColor('#16A34A')))
    d.add(String(206, 118, "IDX idx_offer_seller_status", fontName="Helvetica-Oblique", fontSize=6.5, fillColor=colors.HexColor('#16A34A')))

    # Entity 4: OfferHistory
    d.add(Rect(390, 130, 145, 200, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#D97706'), strokeWidth=1.5, rx=4, ry=4))
    d.add(Rect(390, 305, 145, 25, fillColor=colors.HexColor('#D97706'), strokeColor=colors.HexColor('#D97706'), rx=4, ry=4))
    d.add(String(398, 312, "OFFER HISTORY (Audit)", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.white))
    d.add(String(395, 290, "PK  id: BIGSERIAL", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#B45309')))
    d.add(String(395, 276, "FK  offer_id -> OFFER.id", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#4F46E5')))
    d.add(String(395, 262, "FK  actor_id -> USER.id", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(395, 248, "    action: initial|counter|", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(395, 236, "            accepted|declined", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#64748B')))
    d.add(String(395, 222, "    amount: NUMERIC(10,2)", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0F172A')))
    d.add(String(395, 208, "    message: TEXT", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(395, 194, "    timestamp: TIMESTAMPTZ", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))

    # Entity 5: Review
    d.add(Rect(565, 110, 140, 220, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#16A34A'), strokeWidth=1.5, rx=4, ry=4))
    d.add(Rect(565, 305, 140, 25, fillColor=colors.HexColor('#16A34A'), strokeColor=colors.HexColor('#16A34A'), rx=4, ry=4))
    d.add(String(573, 312, "REVIEW (reviews_review)", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.white))
    d.add(String(570, 290, "PK  id: BIGSERIAL", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#15803D')))
    d.add(String(570, 276, "FK  listing_id -> LISTING.id", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(570, 262, "FK  offer_id -> OFFER.id", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#4F46E5')))
    d.add(String(570, 248, "FK  reviewer_id -> USER.id", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(570, 234, "FK  reviewee_id -> USER.id", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(570, 220, "    rating: SMALLINT [1-5]", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0F172A')))
    d.add(String(570, 206, "    comment: TEXT", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(570, 192, "    created_at: TIMESTAMPTZ", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(570, 172, "UQ (offer, reviewer)", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#DC2626')))
    d.add(String(570, 158, "CHK rating >= 1 AND <= 5", fontName="Helvetica-Oblique", fontSize=6.5, fillColor=colors.HexColor('#DC2626')))

    # Cardinality Lines
    d.add(Line(170, 260, 200, 260, strokeColor=colors.HexColor('#0284C7'), strokeWidth=1.5))
    d.add(String(173, 264, "1:N", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0284C7')))

    d.add(Line(170, 100, 200, 200, strokeColor=colors.HexColor('#0284C7'), strokeWidth=1.5))
    d.add(String(172, 140, "1:N", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0284C7')))

    d.add(Line(360, 230, 390, 230, strokeColor=colors.HexColor('#4F46E5'), strokeWidth=1.5))
    d.add(String(363, 234, "1:N", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#4F46E5')))

    d.add(Line(360, 210, 565, 210, strokeColor=colors.HexColor('#4F46E5'), strokeWidth=1.5))
    d.add(String(450, 214, "1 : 1 (Gated Review per Party)", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#16A34A')))

    story.append(d)
    doc.build(story)
    print("Generated 03 - database-design.pdf successfully.")

def generate_api_workflows_pdf():
    file_path = os.path.join(PROJECT_DIR, "04 - api-workflows.pdf")
    doc = SimpleDocTemplate(file_path, pagesize=landscape(letter), rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#0F172A'), spaceAfter=6)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#475569'), spaceAfter=10)

    story.append(Paragraph("PROJECT 03: TWO-SIDED MARKETPLACE — NEGOTIATION WORKFLOW & REVIEW GATING", title_style))
    story.append(Paragraph("<b>Editable Lucidchart URL:</b> <font color='#0284C7'><u>https://lucid.app/lucidchart/falconxoft-marketplace-negotiation-flow</u></font> | Specification: OpenAPI 3.0 (openapi.yaml included)", sub_style))

    d = Drawing(720, 360)
    d.add(Rect(0, 0, 720, 360, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=1, rx=8, ry=8))

    # Flow 1: Complete Negotiation Success Journey (Left Half)
    d.add(Rect(15, 15, 340, 335, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#16A34A'), strokeWidth=1.5, rx=6, ry=6))
    d.add(Rect(15, 320, 340, 30, fillColor=colors.HexColor('#16A34A'), strokeColor=colors.HexColor('#16A34A'), rx=6, ry=6))
    d.add(String(25, 330, "JOURNEY 1: NEGOTIATION SUCCESS PATH (Offer -> Counter -> Complete -> Review)", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.white))

    lifelines1 = [("Buyer UI", 60), ("Negotiation API", 185), ("Seller UI", 310)]
    for name, x in lifelines1:
        d.add(Rect(x-40, 290, 80, 20, fillColor=colors.HexColor('#F1F5F9'), strokeColor=colors.HexColor('#94A3B8'), rx=3, ry=3))
        d.add(String(x-35, 296, name, fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0F172A')))
        d.add(Line(x, 290, x, 30, strokeColor=colors.HexColor('#CBD5E1'), strokeWidth=1, strokeDashArray=[2, 2]))

    # Step 1: POST /api/offers/
    d.add(Line(60, 265, 185, 265, strokeColor=colors.HexColor('#0284C7'), strokeWidth=1.5))
    d.add(String(65, 270, "1. POST /api/offers/ {listing: 2, $1,500}", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#0369A1')))

    # Step 2: Notify Seller
    d.add(Line(185, 240, 310, 240, strokeColor=colors.HexColor('#4F46E5'), strokeWidth=1.5))
    d.add(String(190, 245, "2. Offer Created [status: pending]", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#3730A3')))

    # Step 3: Seller Counters
    d.add(Line(310, 215, 185, 215, strokeColor=colors.HexColor('#D97706'), strokeWidth=1.5))
    d.add(String(190, 220, "3. POST /counter/ {$1,650}", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#B45309')))

    # Step 4: Buyer Accepts
    d.add(Line(60, 185, 185, 185, strokeColor=colors.HexColor('#16A34A'), strokeWidth=1.5))
    d.add(String(65, 190, "4. POST /accept/ -> status=accepted", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#15803D')))

    # Step 5: Listing Reserved
    d.add(Rect(145, 155, 80, 20, fillColor=colors.HexColor('#FEF3C7'), strokeColor=colors.HexColor('#F59E0B'), rx=2, ry=2))
    d.add(String(150, 162, "Listing: RESERVED", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#B45309')))

    # Step 6: Complete
    d.add(Line(310, 130, 185, 130, strokeColor=colors.HexColor('#16A34A'), strokeWidth=1.5))
    d.add(String(190, 135, "5. POST /complete/ -> status=completed", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#15803D')))

    # Step 7: Gated Review
    d.add(Line(60, 95, 185, 95, strokeColor=colors.HexColor('#16A34A'), strokeWidth=1.5))
    d.add(String(65, 100, "6. POST /reviews/ {rating: 5, comment}", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#15803D')))
    d.add(Line(185, 80, 60, 80, strokeColor=colors.HexColor('#16A34A'), strokeWidth=1, strokeDashArray=[2, 2]))
    d.add(String(65, 70, "7. 201 Created (Rating Recalculated)", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#15803D')))

    # Flow 2: Security & Rejection Paths (Right Half)
    d.add(Rect(365, 15, 340, 335, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#DC2626'), strokeWidth=1.5, rx=6, ry=6))
    d.add(Rect(365, 320, 340, 30, fillColor=colors.HexColor('#DC2626'), strokeColor=colors.HexColor('#DC2626'), rx=6, ry=6))
    d.add(String(375, 330, "JOURNEY 2: TURN ENFORCEMENT & REVIEW GATING REJECTIONS", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.white))

    lifelines2 = [("Unauthorized User", 410), ("Marketplace Engine", 535), ("PostgreSQL DB", 660)]
    for name, x in lifelines2:
        d.add(Rect(x-40, 290, 80, 20, fillColor=colors.HexColor('#F1F5F9'), strokeColor=colors.HexColor('#94A3B8'), rx=3, ry=3))
        d.add(String(x-35, 296, name, fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0F172A')))
        d.add(Line(x, 290, x, 30, strokeColor=colors.HexColor('#CBD5E1'), strokeWidth=1, strokeDashArray=[2, 2]))

    # Scenario A: Double Counter
    d.add(Line(410, 260, 535, 260, strokeColor=colors.HexColor('#DC2626'), strokeWidth=1.5))
    d.add(String(415, 265, "1. Counter twice without counter-party move", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#DC2626')))
    d.add(Line(535, 240, 410, 240, strokeColor=colors.HexColor('#DC2626'), strokeWidth=1, strokeDashArray=[2, 2]))
    d.add(String(415, 245, "2. 400 Bad Request ('Awaiting response')", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#991B1B')))

    # Scenario B: Premature Review
    d.add(Line(410, 205, 535, 205, strokeColor=colors.HexColor('#DC2626'), strokeWidth=1.5))
    d.add(String(415, 210, "3. Review offer with status 'accepted'", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#DC2626')))
    d.add(Line(535, 185, 410, 185, strokeColor=colors.HexColor('#DC2626'), strokeWidth=1, strokeDashArray=[2, 2]))
    d.add(String(415, 190, "4. 400 Bad Request ('Completed only')", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#991B1B')))

    # Scenario C: Third-Party Review
    d.add(Line(410, 150, 535, 150, strokeColor=colors.HexColor('#DC2626'), strokeWidth=1.5))
    d.add(String(415, 155, "5. Non-participant attempts review", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#DC2626')))
    d.add(Line(535, 130, 410, 130, strokeColor=colors.HexColor('#DC2626'), strokeWidth=1, strokeDashArray=[2, 2]))
    d.add(String(415, 135, "6. 403 Forbidden ('Not a participant')", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#991B1B')))

    # Scenario D: Duplicate Review
    d.add(Line(410, 95, 535, 95, strokeColor=colors.HexColor('#DC2626'), strokeWidth=1.5))
    d.add(String(415, 100, "7. Submit 2nd review for same offer", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#DC2626')))
    d.add(Line(535, 75, 410, 75, strokeColor=colors.HexColor('#DC2626'), strokeWidth=1, strokeDashArray=[2, 2]))
    d.add(String(415, 80, "8. 400 Bad Request (Blocked by unique constraint)", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#991B1B')))

    story.append(d)
    doc.build(story)
    print("Generated 04 - api-workflows.pdf successfully.")

if __name__ == "__main__":
    generate_test_cases_xlsx()
    generate_cost_and_scaling_xlsx()
    generate_architecture_pdf()
    generate_database_design_pdf()
    generate_api_workflows_pdf()
    print("All 03_Marketplace binary deliverables generated successfully!")
