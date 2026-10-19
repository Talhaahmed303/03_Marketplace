import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from decimal import Decimal
from apps.users.models import CustomUser
from apps.listings.models import Category, Listing
from apps.offers.models import Offer, OfferHistory
from apps.reviews.models import Review

def seed():
    print("Seeding Marketplace database (marketplace_db)...")

    # 1. Users
    admin_user, _ = CustomUser.objects.get_or_create(
        username='market_admin',
        defaults={
            'email': 'admin@marketplace.falconxoft.internal',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
            'bio': 'Marketplace Operations Administrator'
        }
    )
    admin_user.set_password('Password@123')
    admin_user.save()

    sarah, _ = CustomUser.objects.get_or_create(
        username='sarah_seller',
        defaults={
            'email': 'sarah@creatorgear.io',
            'role': 'seller',
            'location': 'Austin, TX',
            'bio': 'Audio engineer and vintage boutique gear collector.'
        }
    )
    sarah.set_password('Password@123')
    sarah.save()

    david, _ = CustomUser.objects.get_or_create(
        username='david_buyer',
        defaults={
            'email': 'david@soundlab.dev',
            'role': 'buyer',
            'location': 'Brooklyn, NY',
            'bio': 'Indie music producer and modular synthesis composer.'
        }
    )
    david.set_password('Password@123')
    david.save()

    emma, _ = CustomUser.objects.get_or_create(
        username='emma_buyer',
        defaults={
            'email': 'emma@filmmaker.co',
            'role': 'buyer',
            'location': 'Los Angeles, CA',
            'bio': 'Commercial DP & documentary camera operator.'
        }
    )
    emma.set_password('Password@123')
    emma.save()

    # 2. Categories
    cat_audio, _ = Category.objects.get_or_create(
        slug='pro-audio-studio',
        defaults={'name': 'Pro Audio & Studio', 'description': 'Microphones, studio monitors, preamps, and racks.'}
    )
    cat_cinema, _ = Category.objects.get_or_create(
        slug='cinema-cameras',
        defaults={'name': 'Cinema & Cameras', 'description': 'Full-frame bodies, cine lenses, and production monitors.'}
    )
    cat_synths, _ = Category.objects.get_or_create(
        slug='synthesizers-keys',
        defaults={'name': 'Synthesizers & Keys', 'description': 'Analog poly synths, Eurorack modules, and workstations.'}
    )
    cat_compute, _ = Category.objects.get_or_create(
        slug='creative-computing',
        defaults={'name': 'Creative Computing', 'description': 'High-spec workstation laptops, eGPUs, and color-accurate displays.'}
    )

    # 3. Listings
    l1, _ = Listing.objects.get_or_create(
        slug='sony-fx3-cinema-camera-body',
        defaults={
            'seller': sarah,
            'category': cat_cinema,
            'title': 'Sony FX3 Full-Frame Cinema Line Camera',
            'description': 'Pristine condition Sony FX3 body with XLR top handle unit. Shutter count under 1,500. Kept in pelican case.',
            'price': Decimal('3899.00'),
            'condition': 'like_new',
            'status': 'active',
            'location': 'Austin, TX',
            'image_url': 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=800&q=80'
        }
    )

    l2, _ = Listing.objects.get_or_create(
        slug='moog-subsequent-37-analog-synth',
        defaults={
            'seller': sarah,
            'category': cat_synths,
            'title': 'Moog Subsequent 37 Paraphonic Analog Synthesizer',
            'description': 'Authentic Moog analog warmth. Studio-kept, smoke-free environment. Includes original dust cover and power cable.',
            'price': Decimal('1750.00'),
            'condition': 'like_new',
            'status': 'active',
            'location': 'Austin, TX',
            'image_url': 'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?auto=format&fit=crop&w=800&q=80'
        }
    )

    l3, _ = Listing.objects.get_or_create(
        slug='neumann-u87-ai-condenser-mic',
        defaults={
            'seller': sarah,
            'category': cat_audio,
            'title': 'Neumann U87 Ai Large-Diaphragm Condenser Microphone',
            'description': 'The definitive broadcast and vocal reference mic. Includes EA87 shockmount and wooden presentation box.',
            'price': Decimal('3200.00'),
            'condition': 'mint',
            'status': 'reserved',
            'location': 'Austin, TX',
            'image_url': 'https://images.unsplash.com/photo-1590602847861-f357a9332bbc?auto=format&fit=crop&w=800&q=80'
        }
    )

    l4, _ = Listing.objects.get_or_create(
        slug='genelec-8341a-sam-studio-monitors',
        defaults={
            'seller': sarah,
            'category': cat_audio,
            'title': 'Genelec 8341A SAM Coaxial Studio Monitors (Stereo Pair)',
            'description': 'Flagship point-source active acoustic monitors with GLM calibration kit. Uncompromising stereo imaging.',
            'price': Decimal('4900.00'),
            'condition': 'like_new',
            'status': 'sold',
            'location': 'Austin, TX',
            'image_url': 'https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=800&q=80'
        }
    )

    l5, _ = Listing.objects.get_or_create(
        slug='apple-macbook-pro-16-m3-max',
        defaults={
            'seller': sarah,
            'category': cat_compute,
            'title': 'Apple MacBook Pro 16" (M3 Max 16-Core, 64GB RAM, 2TB SSD)',
            'description': 'Space Black mobile rendering powerhouse. 100% battery health, AppleCare+ active through 2027.',
            'price': Decimal('3400.00'),
            'condition': 'mint',
            'status': 'active',
            'location': 'Austin, TX',
            'image_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80'
        }
    )

    # 4. Interactive Negotiations & Offers
    # Negotiation A: Multi-step counter-offer negotiation on Moog Subsequent 37
    off_a, created_a = Offer.objects.get_or_create(
        listing=l2,
        buyer=david,
        defaults={
            'seller': sarah,
            'initial_amount': Decimal('1500.00'),
            'current_amount': Decimal('1600.00'),
            'status': 'countered_by_buyer',
            'last_actor': david
        }
    )
    if created_a:
        OfferHistory.objects.create(offer=off_a, actor=david, action='initial_offer', amount=Decimal('1500.00'), message='Hi Sarah, offering $1,500. Can pick up locally.')
        OfferHistory.objects.create(offer=off_a, actor=sarah, action='counter_offer', amount=Decimal('1650.00'), message='Thanks David. Lowest I can do is $1,650 including the dust cover.')
        OfferHistory.objects.create(offer=off_a, actor=david, action='counter_offer', amount=Decimal('1600.00'), message='Meet in the middle at $1,600 cash and we have a deal?')

    # Negotiation B: Accepted offer on Neumann U87
    off_b, created_b = Offer.objects.get_or_create(
        listing=l3,
        buyer=emma,
        defaults={
            'seller': sarah,
            'initial_amount': Decimal('3000.00'),
            'current_amount': Decimal('3000.00'),
            'status': 'accepted',
            'last_actor': sarah
        }
    )
    if created_b:
        OfferHistory.objects.create(offer=off_b, actor=emma, action='initial_offer', amount=Decimal('3000.00'), message='Would you take $3,000 for immediate invoice settlement?')
        OfferHistory.objects.create(offer=off_b, actor=sarah, action='accepted', amount=Decimal('3000.00'), message='Offer accepted! Reserving microphone for pickup.')

    # Negotiation C: Completed transaction on Genelec Monitors
    off_c, created_c = Offer.objects.get_or_create(
        listing=l4,
        buyer=david,
        defaults={
            'seller': sarah,
            'initial_amount': Decimal('4500.00'),
            'current_amount': Decimal('4650.00'),
            'status': 'completed',
            'last_actor': sarah
        }
    )
    if created_c:
        OfferHistory.objects.create(offer=off_c, actor=david, action='initial_offer', amount=Decimal('4500.00'), message='Offering $4,500 for the Genelec pair.')
        OfferHistory.objects.create(offer=off_c, actor=sarah, action='counter_offer', amount=Decimal('4650.00'), message='Countering with $4,650.')
        OfferHistory.objects.create(offer=off_c, actor=david, action='accepted', amount=Decimal('4650.00'), message='Accepted at $4,650.')
        OfferHistory.objects.create(offer=off_c, actor=sarah, action='completed', amount=Decimal('4650.00'), message='Payment received, monitors delivered.')

        # Verified Review
        Review.objects.create(
            listing=l4,
            offer=off_c,
            reviewer=david,
            reviewee=sarah,
            rating=5,
            comment='Pristine condition, fast local delivery, and transparent communication throughout the counter-offer negotiation. A+ verified seller!'
        )

    print("Marketplace database seeded successfully!")

if __name__ == '__main__':
    seed()
