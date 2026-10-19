-- =============================================================================
-- FALCONXOFT INTERN EVALUATION — PROJECT 03: TWO-SIDED MARKETPLACE
-- PostgreSQL 18 Relational DDL for Lucidchart SQL ERD Import
-- Candidate: Talha Ahmed | Date: October 2026
-- =============================================================================

CREATE TABLE users_customuser (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(254) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'buyer',
    bio TEXT NOT NULL DEFAULT '',
    location VARCHAR(150) NOT NULL DEFAULT '',
    rating_avg NUMERIC(3, 2) NOT NULL DEFAULT 5.00,
    rating_count INTEGER NOT NULL DEFAULT 0,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE listings_category (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(120) NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    icon VARCHAR(50) NOT NULL DEFAULT 'tag'
);

CREATE TABLE listings_listing (
    id BIGSERIAL PRIMARY KEY,
    seller_id BIGINT NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    category_id BIGINT NOT NULL REFERENCES listings_category(id) ON DELETE RESTRICT,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(280) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price > 0),
    condition VARCHAR(30) NOT NULL DEFAULT 'like_new',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    image_url VARCHAR(500) NOT NULL DEFAULT '',
    location VARCHAR(150) NOT NULL DEFAULT 'US',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE offers_offer (
    id BIGSERIAL PRIMARY KEY,
    listing_id BIGINT NOT NULL REFERENCES listings_listing(id) ON DELETE CASCADE,
    buyer_id BIGINT NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    seller_id BIGINT NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    initial_amount NUMERIC(10, 2) NOT NULL CHECK (initial_amount > 0),
    current_amount NUMERIC(10, 2) NOT NULL CHECK (current_amount > 0),
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    last_actor_id BIGINT REFERENCES users_customuser(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE offers_offerhistory (
    id BIGSERIAL PRIMARY KEY,
    offer_id BIGINT NOT NULL REFERENCES offers_offer(id) ON DELETE CASCADE,
    actor_id BIGINT NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    action VARCHAR(25) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    message TEXT NOT NULL DEFAULT '',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reviews_review (
    id BIGSERIAL PRIMARY KEY,
    listing_id BIGINT NOT NULL REFERENCES listings_listing(id) ON DELETE CASCADE,
    offer_id BIGINT NOT NULL REFERENCES offers_offer(id) ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    reviewee_id BIGINT NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    rating SMALLINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_offer_reviewer UNIQUE (offer_id, reviewer_id)
);

CREATE INDEX idx_listings_status_created ON listings_listing(status, created_at DESC);
CREATE INDEX idx_listings_category_status ON listings_listing(category_id, status);
CREATE INDEX idx_offers_buyer_status ON offers_offer(buyer_id, status);
CREATE INDEX idx_offers_seller_status ON offers_offer(seller_id, status);
CREATE INDEX idx_offers_listing_status ON offers_offer(listing_id, status);
