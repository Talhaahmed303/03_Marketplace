import pytest
from decimal import Decimal
from django.db import IntegrityError
from rest_framework.test import APIClient
from apps.users.models import CustomUser
from apps.listings.models import Category, Listing
from apps.offers.models import Offer, OfferHistory
from apps.reviews.models import Review

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_data(db):
    # Users
    admin = CustomUser.objects.create_superuser(
        username='admin_test', email='admin@test.com', password='Password@123', role='admin'
    )
    seller = CustomUser.objects.create_user(
        username='seller_test', email='seller@test.com', password='Password@123', role='seller', location='Austin, TX'
    )
    buyer1 = CustomUser.objects.create_user(
        username='buyer1_test', email='buyer1@test.com', password='Password@123', role='buyer', location='Brooklyn, NY'
    )
    buyer2 = CustomUser.objects.create_user(
        username='buyer2_test', email='buyer2@test.com', password='Password@123', role='buyer', location='Seattle, WA'
    )

    # Categories
    cat_audio = Category.objects.create(name='Pro Audio', slug='pro-audio', description='Studio gear')
    cat_cameras = Category.objects.create(name='Cinema Cameras', slug='cinema-cameras', description='Video cameras')

    # Listings
    listing1 = Listing.objects.create(
        seller=seller, category=cat_audio, title='Analog Compressor 1176',
        slug='analog-compressor-1176', description='Studio rack compressor',
        price=Decimal('1800.00'), condition='mint', status='active'
    )
    listing2 = Listing.objects.create(
        seller=seller, category=cat_cameras, title='Cinema Body 4K',
        slug='cinema-body-4k', description='4K Production body',
        price=Decimal('2500.00'), condition='like_new', status='active'
    )

    return {
        'admin': admin,
        'seller': seller,
        'buyer1': buyer1,
        'buyer2': buyer2,
        'cat_audio': cat_audio,
        'cat_cameras': cat_cameras,
        'listing1': listing1,
        'listing2': listing2,
    }

# 1. Authentication
@pytest.mark.django_db
def test_user_registration_and_jwt_login(api_client):
    # Registration
    reg_res = api_client.post('/api/auth/register/', {
        'username': 'new_member',
        'email': 'new_member@test.com',
        'password': 'Password@123',
        'role': 'buyer',
        'location': 'Denver, CO'
    })
    assert reg_res.status_code == 201
    assert reg_res.data['username'] == 'new_member'
    assert reg_res.data['role'] == 'buyer'

    # Login
    login_res = api_client.post('/api/auth/login/', {
        'username': 'new_member',
        'password': 'Password@123'
    })
    assert login_res.status_code == 200
    assert 'access' in login_res.data
    assert login_res.data['user']['role'] == 'buyer'

# 2. Public Catalog & Filtering
@pytest.mark.django_db
def test_listings_public_catalog_and_category_filter(api_client, test_data):
    # Unauthenticated catalog view
    res = api_client.get('/api/listings/')
    assert res.status_code == 200
    assert len(res.data) >= 2

    # Filter by category
    res_cat = api_client.get('/api/listings/?category=pro-audio')
    assert res_cat.status_code == 200
    assert len(res_cat.data) == 1
    assert res_cat.data[0]['slug'] == 'analog-compressor-1176'

# 3. Search & Price Filtering
@pytest.mark.django_db
def test_listings_keyword_search_and_price_filter(api_client, test_data):
    # Keyword search
    res_search = api_client.get('/api/listings/?search=compressor')
    assert res_search.status_code == 200
    assert len(res_search.data) == 1

    # Price filter
    res_price = api_client.get('/api/listings/?min_price=2000')
    assert res_price.status_code == 200
    assert len(res_price.data) == 1
    assert res_price.data[0]['slug'] == 'cinema-body-4k'

# 4. Listing Creation
@pytest.mark.django_db
def test_seller_create_listing_success(api_client, test_data):
    api_client.force_authenticate(user=test_data['seller'])
    res = api_client.post('/api/listings/', {
        'title': 'Stereo Ribbon Microphone',
        'description': 'Figure-8 ribbon microphone in wooden box',
        'price': '850.00',
        'condition': 'mint',
        'category_id': test_data['cat_audio'].id,
        'location': 'Austin, TX'
    })
    assert res.status_code == 201
    assert res.data['title'] == 'Stereo Ribbon Microphone'
    assert Decimal(res.data['price']) == Decimal('850.00')
    assert res.data['seller']['username'] == 'seller_test'

# 5. Permission Security
@pytest.mark.django_db
def test_non_seller_cannot_edit_other_seller_listing(api_client, test_data):
    api_client.force_authenticate(user=test_data['buyer1'])
    listing_id = test_data['listing1'].id
    res = api_client.patch(f'/api/listings/{listing_id}/', {'price': '999.00'})
    assert res.status_code == 403

# 6. Offer Creation Success
@pytest.mark.django_db
def test_buyer_make_offer_success(api_client, test_data):
    api_client.force_authenticate(user=test_data['buyer1'])
    res = api_client.post('/api/offers/', {
        'listing_id': test_data['listing1'].id,
        'amount': '1600.00',
        'message': 'Can pick up tomorrow cash.'
    })
    assert res.status_code == 201
    assert res.data['status'] == 'pending'
    assert Decimal(res.data['current_amount']) == Decimal('1600.00')
    assert res.data['buyer']['username'] == 'buyer1_test'
    assert len(res.data['history']) == 1
    assert res.data['history'][0]['action'] == 'initial_offer'

# 7. Seller Cannot Offer On Own Listing
@pytest.mark.django_db
def test_seller_cannot_make_offer_on_own_listing(api_client, test_data):
    api_client.force_authenticate(user=test_data['seller'])
    res = api_client.post('/api/offers/', {
        'listing_id': test_data['listing1'].id,
        'amount': '1500.00'
    })
    assert res.status_code == 400
    assert 'own listing' in res.data['detail'].lower()

# 8. Offer On Non-Active Listing Rejected
@pytest.mark.django_db
def test_offer_on_non_active_listing_rejected(api_client, test_data):
    test_data['listing1'].status = 'sold'
    test_data['listing1'].save()

    api_client.force_authenticate(user=test_data['buyer1'])
    res = api_client.post('/api/offers/', {
        'listing_id': test_data['listing1'].id,
        'amount': '1500.00'
    })
    assert res.status_code == 400
    assert 'sold' in res.data['detail'].lower()

# 9. Counter-Offer Turn Enforcement
@pytest.mark.django_db
def test_counter_offer_turn_enforcement(api_client, test_data):
    # Buyer makes initial offer
    offer = Offer.objects.create(
        listing=test_data['listing1'],
        buyer=test_data['buyer1'],
        seller=test_data['seller'],
        initial_amount=Decimal('1500.00'),
        current_amount=Decimal('1500.00'),
        status='pending',
        last_actor=test_data['buyer1']
    )

    # Seller counters
    api_client.force_authenticate(user=test_data['seller'])
    counter_res = api_client.post(f'/api/offers/{offer.id}/counter/', {
        'amount': '1700.00',
        'message': 'Best I can do is $1,700.'
    })
    assert counter_res.status_code == 200
    assert counter_res.data['status'] == 'countered_by_seller'
    assert Decimal(counter_res.data['current_amount']) == Decimal('1700.00')

    # Seller attempts to counter AGAIN before buyer answers (Invalid turn)
    double_counter = api_client.post(f'/api/offers/{offer.id}/counter/', {'amount': '1650.00'})
    assert double_counter.status_code == 400
    assert 'awaiting response' in double_counter.data['detail'].lower()

# 10. Buyer Counter Back Success
@pytest.mark.django_db
def test_buyer_counter_back_success(api_client, test_data):
    offer = Offer.objects.create(
        listing=test_data['listing1'],
        buyer=test_data['buyer1'],
        seller=test_data['seller'],
        initial_amount=Decimal('1500.00'),
        current_amount=Decimal('1700.00'),
        status='countered_by_seller',
        last_actor=test_data['seller']
    )

    api_client.force_authenticate(user=test_data['buyer1'])
    res = api_client.post(f'/api/offers/{offer.id}/counter/', {
        'amount': '1625.00',
        'message': 'Meet in the middle at $1,625?'
    })
    assert res.status_code == 200
    assert res.data['status'] == 'countered_by_buyer'
    assert Decimal(res.data['current_amount']) == Decimal('1625.00')

# 11. Cannot Accept Own Move
@pytest.mark.django_db
def test_cannot_accept_own_counter_offer(api_client, test_data):
    offer = Offer.objects.create(
        listing=test_data['listing1'],
        buyer=test_data['buyer1'],
        seller=test_data['seller'],
        initial_amount=Decimal('1500.00'),
        current_amount=Decimal('1625.00'),
        status='countered_by_buyer',
        last_actor=test_data['buyer1']
    )

    # Buyer cannot accept their own move
    api_client.force_authenticate(user=test_data['buyer1'])
    res = api_client.post(f'/api/offers/{offer.id}/accept/')
    assert res.status_code == 400
    assert 'cannot accept your own' in res.data['detail'].lower()

# 12. Accept Offer Reserves Listing
@pytest.mark.django_db
def test_accept_offer_reserves_listing(api_client, test_data):
    offer = Offer.objects.create(
        listing=test_data['listing1'],
        buyer=test_data['buyer1'],
        seller=test_data['seller'],
        initial_amount=Decimal('1500.00'),
        current_amount=Decimal('1625.00'),
        status='countered_by_buyer',
        last_actor=test_data['buyer1']
    )

    # Seller accepts buyer's counter
    api_client.force_authenticate(user=test_data['seller'])
    res = api_client.post(f'/api/offers/{offer.id}/accept/')
    assert res.status_code == 200
    assert res.data['status'] == 'accepted'

    test_data['listing1'].refresh_from_db()
    assert test_data['listing1'].status == 'reserved'

# 13. Complete Offer Marks Listing Sold
@pytest.mark.django_db
def test_complete_offer_marks_listing_sold(api_client, test_data):
    offer = Offer.objects.create(
        listing=test_data['listing1'],
        buyer=test_data['buyer1'],
        seller=test_data['seller'],
        initial_amount=Decimal('1625.00'),
        current_amount=Decimal('1625.00'),
        status='accepted',
        last_actor=test_data['seller']
    )
    test_data['listing1'].status = 'reserved'
    test_data['listing1'].save()

    api_client.force_authenticate(user=test_data['seller'])
    res = api_client.post(f'/api/offers/{offer.id}/complete/')
    assert res.status_code == 200
    assert res.data['status'] == 'completed'

    test_data['listing1'].refresh_from_db()
    assert test_data['listing1'].status == 'sold'

# 14. Review Eligibility: Only Completed Transactions
@pytest.mark.django_db
def test_verified_review_eligibility_completed_only(api_client, test_data):
    offer = Offer.objects.create(
        listing=test_data['listing1'],
        buyer=test_data['buyer1'],
        seller=test_data['seller'],
        initial_amount=Decimal('1600.00'),
        current_amount=Decimal('1600.00'),
        status='accepted', # NOT completed yet
        last_actor=test_data['seller']
    )

    api_client.force_authenticate(user=test_data['buyer1'])
    res = api_client.post('/api/reviews/', {
        'offer_id': offer.id,
        'rating': 5,
        'comment': 'Premature review attempt'
    })
    assert res.status_code == 400
    assert 'completed transactions' in res.data['detail'].lower()

# 15. Review Security: Unauthorized Third Party Rejected
@pytest.mark.django_db
def test_verified_review_unauthorized_third_party_rejected(api_client, test_data):
    offer = Offer.objects.create(
        listing=test_data['listing1'],
        buyer=test_data['buyer1'],
        seller=test_data['seller'],
        initial_amount=Decimal('1600.00'),
        current_amount=Decimal('1600.00'),
        status='completed',
        last_actor=test_data['seller']
    )

    # Buyer 2 was not a party
    api_client.force_authenticate(user=test_data['buyer2'])
    res = api_client.post('/api/reviews/', {
        'offer_id': offer.id,
        'rating': 1,
        'comment': 'Snooper review'
    })
    assert res.status_code == 403

# 16. Duplicate Review Prevention
@pytest.mark.django_db
def test_duplicate_review_prevented(api_client, test_data):
    offer = Offer.objects.create(
        listing=test_data['listing1'],
        buyer=test_data['buyer1'],
        seller=test_data['seller'],
        initial_amount=Decimal('1600.00'),
        current_amount=Decimal('1600.00'),
        status='completed',
        last_actor=test_data['seller']
    )

    # First review succeeds
    api_client.force_authenticate(user=test_data['buyer1'])
    res1 = api_client.post('/api/reviews/', {
        'offer_id': offer.id,
        'rating': 5,
        'comment': 'Superb gear and prompt pickup.'
    })
    assert res1.status_code == 201

    # Second review rejected
    res2 = api_client.post('/api/reviews/', {
        'offer_id': offer.id,
        'rating': 4,
        'comment': 'Duplicate review attempt.'
    })
    assert res2.status_code == 400
    assert 'already submitted a review' in res2.data['detail'].lower()
