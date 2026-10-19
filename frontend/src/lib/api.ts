const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8003/api';

export interface User {
  id: number;
  username: string;
  email: string;
  role: 'buyer' | 'seller' | 'admin';
  bio?: string;
  location?: string;
  rating_avg: string | number;
  rating_count: number;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  icon?: string;
}

export interface Listing {
  id: number;
  title: string;
  slug: string;
  description: string;
  price: string;
  condition: 'brand_new' | 'mint' | 'like_new' | 'good' | 'fair';
  status: 'active' | 'reserved' | 'sold';
  image_url: string;
  location: string;
  seller: User;
  category: Category;
  category_slug: string;
  category_name: string;
  created_at: string;
  updated_at: string;
}

export interface OfferHistoryItem {
  id: number;
  actor: number;
  actor_username: string;
  actor_role: string;
  action: 'initial_offer' | 'counter_offer' | 'accepted' | 'declined' | 'completed';
  amount: string;
  message: string;
  timestamp: string;
}

export interface Offer {
  id: number;
  listing: {
    id: number;
    title: string;
    slug: string;
    price: string;
    status: string;
    image_url: string;
  };
  buyer: User;
  seller: User;
  initial_amount: string;
  current_amount: string;
  status: 'pending' | 'countered_by_seller' | 'countered_by_buyer' | 'accepted' | 'declined' | 'completed';
  last_actor: number | null;
  last_actor_username: string;
  history: OfferHistoryItem[];
  created_at: string;
  updated_at: string;
}

export interface Review {
  id: number;
  listing: number;
  listing_title: string;
  offer: number;
  reviewer: User;
  reviewee: User;
  rating: number;
  comment: string;
  created_at: string;
}

export const api = {
  async login(username: string, password = 'Password@123') {
    const res = await fetch(`${API_BASE}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) throw new Error('Authentication failed');
    return res.json();
  },

  async getCategories(): Promise<Category[]> {
    const res = await fetch(`${API_BASE}/listings/categories/`);
    if (!res.ok) return [];
    const data = await res.json();
    return Array.isArray(data) ? data : data.results || [];
  },

  async getListings(params?: { category?: string; search?: string; min_price?: string; max_price?: string; my?: boolean }, token?: string): Promise<Listing[]> {
    const query = new URLSearchParams();
    if (params?.category) query.append('category', params.category);
    if (params?.search) query.append('search', params.search);
    if (params?.min_price) query.append('min_price', params.min_price);
    if (params?.max_price) query.append('max_price', params.max_price);
    if (params?.my && token) query.append('my', 'true');

    const headers: Record<string, string> = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/listings/?${query.toString()}`, { headers });
    if (!res.ok) return [];
    const data = await res.json();
    return Array.isArray(data) ? data : data.results || [];
  },

  async createListing(token: string, data: { title: string; description: string; price: string; condition: string; category_id: number; image_url?: string; location?: string }) {
    const res = await fetch(`${API_BASE}/listings/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || JSON.stringify(err));
    }
    return res.json();
  },

  async getOffers(token: string, asRole?: 'buyer' | 'seller'): Promise<Offer[]> {
    const query = asRole ? `?as=${asRole}` : '';
    const res = await fetch(`${API_BASE}/offers/${query}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return Array.isArray(data) ? data : data.results || [];
  },

  async createOffer(token: string, listingId: number, amount: string | number, message: string) {
    const res = await fetch(`${API_BASE}/offers/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ listing_id: listingId, amount, message }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to submit offer');
    }
    return res.json();
  },

  async counterOffer(token: string, offerId: number, amount: string | number, message: string) {
    const res = await fetch(`${API_BASE}/offers/${offerId}/counter/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ amount, message }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Counter-offer rejected');
    }
    return res.json();
  },

  async acceptOffer(token: string, offerId: number) {
    const res = await fetch(`${API_BASE}/offers/${offerId}/accept/`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to accept offer');
    }
    return res.json();
  },

  async declineOffer(token: string, offerId: number) {
    const res = await fetch(`${API_BASE}/offers/${offerId}/decline/`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to decline offer');
    }
    return res.json();
  },

  async completeOffer(token: string, offerId: number) {
    const res = await fetch(`${API_BASE}/offers/${offerId}/complete/`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to complete transaction');
    }
    return res.json();
  },

  async getReviews(params?: { user_id?: number; listing_id?: number }): Promise<Review[]> {
    const query = new URLSearchParams();
    if (params?.user_id) query.append('user_id', params.user_id.toString());
    if (params?.listing_id) query.append('listing_id', params.listing_id.toString());
    const res = await fetch(`${API_BASE}/reviews/?${query.toString()}`);
    if (!res.ok) return [];
    const data = await res.json();
    return Array.isArray(data) ? data : data.results || [];
  },

  async createReview(token: string, offerId: number, rating: number, comment: string) {
    const res = await fetch(`${API_BASE}/reviews/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ offer_id: offerId, rating, comment }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to post review');
    }
    return res.json();
  },
};
