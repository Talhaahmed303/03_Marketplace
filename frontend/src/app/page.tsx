'use client';

import React, { useState, useEffect } from 'react';
import { api, User, Category, Listing, Offer, Review } from '@/lib/api';

const USERS = [
  { username: 'david_buyer', label: 'David (Buyer)', role: 'buyer', color: 'bg-emerald-600' },
  { username: 'emma_buyer', label: 'Emma (Buyer)', role: 'buyer', color: 'bg-cyan-600' },
  { username: 'sarah_seller', label: 'Sarah (Seller)', role: 'seller', color: 'bg-indigo-600' },
  { username: 'market_admin', label: 'Admin (Staff)', role: 'admin', color: 'bg-rose-600' },
];

export default function MarketplacePage() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [token, setToken] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'browse' | 'negotiations' | 'seller_studio' | 'reviews'>('browse');

  // Catalog State
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [debouncedSearch, setDebouncedSearch] = useState<string>('');
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [minPrice, setMinPrice] = useState<string>('');
  const [maxPrice, setMaxPrice] = useState<string>('');
  const [listings, setListings] = useState<Listing[]>([]);
  const [myListings, setMyListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Negotiation & Offers State
  const [offers, setOffers] = useState<Offer[]>([]);
  const [selectedListingForOffer, setSelectedListingForOffer] = useState<Listing | null>(null);
  const [offerAmount, setOfferAmount] = useState<string>('');
  const [offerMessage, setOfferMessage] = useState<string>('');
  const [counterAmount, setCounterAmount] = useState<string>('');
  const [counterMessage, setCounterMessage] = useState<string>('');
  const [activeNegotiationOffer, setActiveNegotiationOffer] = useState<Offer | null>(null);

  // Reviews State
  const [reviews, setReviews] = useState<Review[]>([]);
  const [reviewOffer, setReviewOffer] = useState<Offer | null>(null);
  const [reviewRating, setReviewRating] = useState<number>(5);
  const [reviewComment, setReviewComment] = useState<string>('');

  // Listing Creation Modal
  const [showCreateListing, setShowCreateListing] = useState<boolean>(false);
  const [newTitle, setNewTitle] = useState<string>('');
  const [newDesc, setNewDesc] = useState<string>('');
  const [newPrice, setNewPrice] = useState<string>('');
  const [newCondition, setNewCondition] = useState<string>('like_new');
  const [newCategoryId, setNewCategoryId] = useState<number>(1);
  const [newImageUrl, setNewImageUrl] = useState<string>('');

  // Banner message
  const [statusMessage, setStatusMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  // Initialize with default user (David)
  useEffect(() => {
    switchUser('david_buyer');
  }, []);

  const switchUser = async (username: string) => {
    try {
      setLoading(true);
      const res = await api.login(username);
      setToken(res.access);
      setCurrentUser(res.user);
      await loadInitialData(res.access);
      setStatusMessage({ text: `Switched active persona to ${username} (${res.user.role})`, type: 'success' });
      setTimeout(() => setStatusMessage(null), 3500);
    } catch (err: any) {
      console.error(err);
      setStatusMessage({ text: 'Failed to switch user account.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // Debounce search input by 280ms to avoid UI flickering and rapid API calls
  useEffect(() => {
    if (searchQuery !== debouncedSearch) {
      setIsSearching(true);
    }
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 280);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Refresh listings when category or debouncedSearch changes
  useEffect(() => {
    if (categories.length > 0) {
      refreshListings();
    }
  }, [selectedCategory, debouncedSearch]);

  const loadInitialData = async (authToken: string) => {
    const [cats, items, offList, revs] = await Promise.all([
      api.getCategories(),
      api.getListings({ category: selectedCategory, search: debouncedSearch, min_price: minPrice, max_price: maxPrice }),
      api.getOffers(authToken),
      api.getReviews(),
    ]);
    setCategories(cats);
    setListings(items);
    setOffers(offList);
    setReviews(revs);
    if (cats.length > 0) setNewCategoryId(cats[0].id);
  };

  const refreshListings = async () => {
    try {
      const items = await api.getListings({
        category: selectedCategory,
        search: debouncedSearch,
        min_price: minPrice,
        max_price: maxPrice,
      });
      setListings(items);
    } catch (err: any) {
      console.error(err);
    } finally {
      setIsSearching(false);
    }
  };

  const refreshOffers = async () => {
    if (!token) return;
    const offList = await api.getOffers(token);
    setOffers(offList);
    if (activeNegotiationOffer) {
      const updated = offList.find((o) => o.id === activeNegotiationOffer.id);
      if (updated) setActiveNegotiationOffer(updated);
    }
  };

  const refreshReviews = async () => {
    const revs = await api.getReviews();
    setReviews(revs);
  };

  // Submit initial offer
  const handleMakeOffer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedListingForOffer || !token) return;
    try {
      await api.createOffer(token, selectedListingForOffer.id, offerAmount, offerMessage);
      setStatusMessage({ text: `Offer of $${offerAmount} submitted to ${selectedListingForOffer.seller.username}!`, type: 'success' });
      setSelectedListingForOffer(null);
      setOfferAmount('');
      setOfferMessage('');
      await refreshOffers();
      setActiveTab('negotiations');
    } catch (err: any) {
      setStatusMessage({ text: err.message, type: 'error' });
    }
  };

  // Submit counter-offer
  const handleCounterOffer = async (offerId: number) => {
    if (!token || !counterAmount) return;
    try {
      await api.counterOffer(token, offerId, counterAmount, counterMessage);
      setStatusMessage({ text: `Counter-offer of $${counterAmount} submitted successfully!`, type: 'success' });
      setCounterAmount('');
      setCounterMessage('');
      await refreshOffers();
    } catch (err: any) {
      setStatusMessage({ text: err.message, type: 'error' });
    }
  };

  // Accept offer
  const handleAcceptOffer = async (offerId: number) => {
    if (!token) return;
    try {
      await api.acceptOffer(token, offerId);
      setStatusMessage({ text: 'Offer accepted! The listing has been reserved for settlement.', type: 'success' });
      await refreshOffers();
      await refreshListings();
    } catch (err: any) {
      setStatusMessage({ text: err.message, type: 'error' });
    }
  };

  // Decline offer
  const handleDeclineOffer = async (offerId: number) => {
    if (!token) return;
    try {
      await api.declineOffer(token, offerId);
      setStatusMessage({ text: 'Negotiation declined.', type: 'success' });
      await refreshOffers();
    } catch (err: any) {
      setStatusMessage({ text: err.message, type: 'error' });
    }
  };

  // Complete transaction
  const handleCompleteOffer = async (offerId: number) => {
    if (!token) return;
    try {
      await api.completeOffer(token, offerId);
      setStatusMessage({ text: 'Transaction finalized & completed! Both parties may now leave a verified review.', type: 'success' });
      await refreshOffers();
      await refreshListings();
    } catch (err: any) {
      setStatusMessage({ text: err.message, type: 'error' });
    }
  };

  // Submit verified review
  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewOffer || !token) return;
    try {
      await api.createReview(token, reviewOffer.id, reviewRating, reviewComment);
      setStatusMessage({ text: 'Verified review submitted successfully!', type: 'success' });
      setReviewOffer(null);
      setReviewComment('');
      await refreshReviews();
      setActiveTab('reviews');
    } catch (err: any) {
      setStatusMessage({ text: err.message, type: 'error' });
    }
  };

  // Create listing
  const handleCreateListing = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    try {
      await api.createListing(token, {
        title: newTitle,
        description: newDesc,
        price: newPrice,
        condition: newCondition,
        category_id: newCategoryId,
        image_url: newImageUrl || 'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?auto=format&fit=crop&w=800&q=80',
        location: currentUser?.location || 'Austin, TX',
      });
      setStatusMessage({ text: `Listing '${newTitle}' published successfully!`, type: 'success' });
      setShowCreateListing(false);
      setNewTitle('');
      setNewDesc('');
      setNewPrice('');
      await refreshListings();
    } catch (err: any) {
      setStatusMessage({ text: err.message, type: 'error' });
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Header & Role Switcher */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center font-black text-xl text-slate-950 shadow-lg shadow-emerald-500/20">
              GX
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg text-white tracking-tight">GearExchange</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
                  Marketplace MVP
                </span>
              </div>
              <p className="text-xs text-slate-400">Two-Sided Audio & Cinema Gear Marketplace</p>
            </div>
          </div>

          {/* Persona Switcher */}
          <div className="flex items-center gap-2 bg-slate-800/80 p-1.5 rounded-xl border border-slate-700/60 text-xs">
            <span className="text-slate-400 px-2 font-medium">Active Persona:</span>
            {USERS.map((u) => {
              const active = currentUser?.username === u.username;
              return (
                <button
                  key={u.username}
                  onClick={() => switchUser(u.username)}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-all ${active ? `${u.color} text-white shadow-md font-semibold` : 'text-slate-300 hover:bg-slate-700/50'
                    }`}
                >
                  {u.label}
                </button>
              );
            })}
          </div>

          {/* User Info Capsule */}
          <div className="flex items-center gap-3 bg-slate-800/50 border border-slate-700 px-3 py-1.5 rounded-xl">
            <div className="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-300 flex items-center justify-center font-bold text-sm">
              {currentUser?.username?.[0]?.toUpperCase()}
            </div>
            <div className="text-left text-xs">
              <div className="font-semibold text-white flex items-center gap-1.5">
                {currentUser?.username}
                <span className="text-amber-400 font-bold">★ {currentUser?.rating_avg || '5.0'}</span>
              </div>
              <div className="text-slate-400 capitalize">{currentUser?.role} • {currentUser?.location || 'Remote'}</div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="max-w-7xl mx-auto px-4 flex gap-1 border-t border-slate-800/60 pt-2">
          <button
            onClick={() => setActiveTab('browse')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'browse'
                ? 'border-emerald-500 text-emerald-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
          >
            Browse Marketplace
          </button>
          <button
            onClick={() => setActiveTab('negotiations')}
            className={`px-4 py-2 text-sm font-medium border-b-2 flex items-center gap-2 transition-colors ${activeTab === 'negotiations'
                ? 'border-emerald-500 text-emerald-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
          >
            Negotiations & Offers
            {offers.filter((o) => ['pending', 'countered_by_seller', 'countered_by_buyer'].includes(o.status)).length > 0 && (
              <span className="w-5 h-5 rounded-full bg-emerald-500 text-slate-950 text-xs font-bold flex items-center justify-center">
                {offers.filter((o) => ['pending', 'countered_by_seller', 'countered_by_buyer'].includes(o.status)).length}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('seller_studio')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'seller_studio'
                ? 'border-emerald-500 text-emerald-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
          >
            Seller Studio {currentUser?.role === 'seller' ? '(Manage Listings)' : ''}
          </button>
          <button
            onClick={() => setActiveTab('reviews')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'reviews'
                ? 'border-emerald-500 text-emerald-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
          >
            Verified Community Reviews ({reviews.length})
          </button>
        </div>
      </header>

      {/* Status Banner */}
      {statusMessage && (
        <div
          className={`px-4 py-2.5 text-center text-sm font-medium transition-all ${statusMessage.type === 'success'
              ? 'bg-emerald-900/70 text-emerald-200 border-b border-emerald-500/30'
              : 'bg-rose-900/70 text-rose-200 border-b border-rose-500/30'
            }`}
        >
          {statusMessage.text}
        </div>
      )}

      {/* Main Workspace Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
        {/* ========================================================================= */}
        {/* TAB 1: BROWSE MARKETPLACE */}
        {/* ========================================================================= */}
        {activeTab === 'browse' && (
          <div>
            {/* Search & Filter Bar */}
            <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl mb-6 shadow-xl flex flex-wrap gap-4 items-center justify-between">
              <div className="flex-1 min-w-[260px] relative">
                <input
                  type="text"
                  placeholder="Search synthesizer, camera, microphone..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && refreshListings()}
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl pl-9 pr-8 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                />
                <span className="absolute left-3 top-2.5 text-slate-400 text-xs">🔍</span>
                {isSearching ? (
                  <span className="absolute right-3 top-2.5 inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-emerald-500"></span>
                ) : searchQuery ? (
                  <button
                    type="button"
                    onClick={() => setSearchQuery('')}
                    className="absolute right-3 top-2 text-slate-400 hover:text-slate-200 text-xs"
                  >
                    ✕
                  </button>
                ) : null}
              </div>

              {/* Price range */}
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  placeholder="Min $"
                  value={minPrice}
                  onChange={(e) => setMinPrice(e.target.value)}
                  className="w-24 bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                />
                <span className="text-slate-500">-</span>
                <input
                  type="number"
                  placeholder="Max $"
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(e.target.value)}
                  className="w-24 bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                />
                <button
                  onClick={refreshListings}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-sm font-medium border border-slate-700"
                >
                  Apply
                </button>
              </div>
            </div>

            {/* Category Pills */}
            <div className="flex flex-wrap gap-2 mb-6">
              <button
                onClick={() => {
                  setSelectedCategory('');
                  setTimeout(refreshListings, 50);
                }}
                className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${selectedCategory === ''
                    ? 'bg-emerald-500 text-slate-950 font-bold shadow-md shadow-emerald-500/20'
                    : 'bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-800'
                  }`}
              >
                All Categories
              </button>
              {categories.map((c) => (
                <button
                  key={c.id}
                  onClick={() => {
                    setSelectedCategory(c.slug);
                    setTimeout(refreshListings, 50);
                  }}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${selectedCategory === c.slug
                      ? 'bg-emerald-500 text-slate-950 font-bold shadow-md shadow-emerald-500/20'
                      : 'bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-800'
                    }`}
                >
                  {c.name}
                </button>
              ))}
            </div>

            {/* Listing Cards Grid */}
            {listings.length === 0 ? (
              <div className="text-center py-20 bg-slate-900/60 rounded-2xl border border-slate-800 p-8">
                <span className="text-4xl mb-3 block">🔍</span>
                <h3 className="text-base font-bold text-white">No gear listings found</h3>
                <p className="text-slate-400 text-xs mt-1">Try clearing your filters or search keywords.</p>
              </div>
            ) : (
              <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 transition-opacity duration-200 ${isSearching ? 'opacity-60' : 'opacity-100'}`}>
                {listings.map((l) => {
                  const isMyListing = currentUser?.id === l.seller.id;
                  return (
                    <div
                      key={l.id}
                      className="bg-slate-900/70 border border-slate-800 hover:border-slate-700 rounded-2xl overflow-hidden shadow-lg transition-all flex flex-col group"
                    >
                      {/* Image & Status Badge */}
                      <div className="relative h-48 bg-slate-950 overflow-hidden">
                        <img
                          src={l.image_url || 'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?auto=format&fit=crop&w=800&q=80'}
                          alt={l.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                        <div className="absolute top-3 left-3 flex gap-2">
                          <span className="px-2.5 py-1 rounded-md bg-slate-950/80 backdrop-blur text-xs font-semibold uppercase tracking-wider text-emerald-400 border border-emerald-500/30">
                            {l.category_name}
                          </span>
                          <span className="px-2.5 py-1 rounded-md bg-slate-950/80 backdrop-blur text-xs font-medium capitalize text-slate-300 border border-slate-700">
                            {l.condition.replace('_', ' ')}
                          </span>
                        </div>
                        <div className="absolute top-3 right-3">
                          <span
                            className={`px-2.5 py-1 rounded-md text-xs font-bold uppercase ${l.status === 'active'
                                ? 'bg-emerald-500/90 text-slate-950'
                                : l.status === 'reserved'
                                  ? 'bg-amber-500/90 text-slate-950'
                                  : 'bg-rose-500/90 text-white'
                              }`}
                          >
                            {l.status}
                          </span>
                        </div>
                      </div>

                      {/* Content */}
                      <div className="p-5 flex-1 flex flex-col justify-between">
                        <div>
                          <div className="flex justify-between items-start gap-2 mb-2">
                            <h3 className="font-bold text-base text-white group-hover:text-emerald-400 transition-colors line-clamp-1">
                              {l.title}
                            </h3>
                          </div>
                          <p className="text-xs text-slate-400 line-clamp-2 mb-4">{l.description}</p>
                        </div>

                        <div className="border-t border-slate-800/80 pt-4">
                          <div className="flex justify-between items-center mb-4">
                            <div>
                              <span className="text-xs text-slate-500 block">Asking Price</span>
                              <span className="text-xl font-extrabold text-white">${parseFloat(l.price).toLocaleString()}</span>
                            </div>
                            <div className="text-right">
                              <span className="text-xs text-slate-400 font-medium block">{l.seller.username}</span>
                              <span className="text-xs text-amber-400 font-semibold">★ {l.seller.rating_avg || '5.0'}</span>
                            </div>
                          </div>

                          {/* Action buttons */}
                          {isMyListing ? (
                            <div className="w-full py-2 px-3 rounded-xl bg-slate-800/60 border border-slate-700/60 text-center text-xs font-medium text-slate-400">
                              Your Listing ({l.status})
                            </div>
                          ) : l.status !== 'active' ? (
                            <div className="w-full py-2 px-3 rounded-xl bg-slate-800/40 border border-slate-800 text-center text-xs font-medium text-slate-500 capitalize">
                              Listing {l.status}
                            </div>
                          ) : (
                            <button
                              onClick={() => {
                                setSelectedListingForOffer(l);
                                setOfferAmount(Math.round(parseFloat(l.price) * 0.9).toString());
                              }}
                              className="w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold transition-all shadow-md shadow-emerald-600/20 flex items-center justify-center gap-2"
                            >
                              <span>Make an Offer</span>
                              <span className="text-xs opacity-80">(Negotiate Price)</span>
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 2: NEGOTIATIONS & OFFERS */}
        {/* ========================================================================= */}
        {activeTab === 'negotiations' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold text-white">Counter-Offer Negotiations</h2>
                <p className="text-xs text-slate-400">Review active offer history, counter amounts, or accept final proposals</p>
              </div>
              <button
                onClick={refreshOffers}
                className="px-3 py-1.5 rounded-lg bg-slate-800 text-xs font-medium hover:bg-slate-700 border border-slate-700"
              >
                Refresh Offers
              </button>
            </div>

            {offers.length === 0 ? (
              <div className="p-12 text-center bg-slate-900/50 border border-slate-800 rounded-2xl">
                <p className="text-slate-400 text-sm">No negotiation threads found for this user.</p>
                <p className="text-slate-500 text-xs mt-1">Browse equipment and make an offer to initiate a deal!</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {offers.map((off) => {
                  const isBuyer = currentUser?.id === off.buyer.id;
                  const isSeller = currentUser?.id === off.seller.id;
                  const isMyTurn = off.last_actor !== currentUser?.id;
                  const isTerminal = ['accepted', 'declined', 'completed'].includes(off.status);

                  return (
                    <div
                      key={off.id}
                      className={`bg-slate-900 border rounded-2xl p-5 shadow-xl transition-all ${off.status === 'accepted'
                          ? 'border-emerald-500/40 bg-emerald-950/10'
                          : off.status === 'completed'
                            ? 'border-indigo-500/40 bg-indigo-950/10'
                            : off.status === 'declined'
                              ? 'border-rose-500/30 bg-rose-950/10'
                              : isMyTurn
                                ? 'border-amber-500/50 shadow-amber-500/5'
                                : 'border-slate-800'
                        }`}
                    >
                      {/* Negotiation Header */}
                      <div className="flex justify-between items-start gap-3 pb-3 border-b border-slate-800">
                        <div>
                          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                            Offer #{off.id} • {off.listing.title}
                          </span>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-2xl font-extrabold text-white">
                              ${parseFloat(off.current_amount).toLocaleString()}
                            </span>
                            <span className="text-xs text-slate-400">
                              (Original Asking: ${parseFloat(off.listing.price).toLocaleString()})
                            </span>
                          </div>
                        </div>

                        {/* Status Badge */}
                        <div className="text-right">
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${off.status === 'accepted'
                                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                : off.status === 'completed'
                                  ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                                  : off.status === 'declined'
                                    ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                                    : isMyTurn
                                      ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30 animate-pulse'
                                      : 'bg-slate-800 text-slate-400 border border-slate-700'
                              }`}
                          >
                            {off.status.replace(/_/g, ' ')}
                          </span>
                          <span className="block text-[11px] text-slate-500 mt-1">
                            {isBuyer ? `Seller: ${off.seller.username}` : `Buyer: ${off.buyer.username}`}
                          </span>
                        </div>
                      </div>

                      {/* Turn / Guidance Banner */}
                      <div className="my-3 py-2 px-3 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs">
                        {off.status === 'accepted' ? (
                          <div className="text-emerald-400 font-semibold flex items-center justify-between">
                            <span>✓ Offer accepted! Reserving listing for pickup & payment.</span>
                            <button
                              onClick={() => handleCompleteOffer(off.id)}
                              className="px-3 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs"
                            >
                              Finalize & Complete Transaction
                            </button>
                          </div>
                        ) : off.status === 'completed' ? (
                          <div className="text-indigo-400 font-semibold flex items-center justify-between">
                            <span>✓ Transaction finalized & settled!</span>
                            <button
                              onClick={() => setReviewOffer(off)}
                              className="px-3 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs"
                            >
                              Leave Verified Review ★
                            </button>
                          </div>
                        ) : off.status === 'declined' ? (
                          <span className="text-rose-400">Negotiation concluded with no agreement.</span>
                        ) : isMyTurn ? (
                          <span className="text-amber-400 font-semibold">
                            ⚡ It is your turn! The counter-party made a move. Accept, counter, or decline below.
                          </span>
                        ) : (
                          <span className="text-slate-400">
                            ⏳ Waiting for {isBuyer ? off.seller.username : off.buyer.username} to respond to your proposal.
                          </span>
                        )}
                      </div>

                      {/* Chronological History Log */}
                      <div className="space-y-2 max-h-44 overflow-y-auto my-3 pr-1">
                        <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
                          Negotiation Timeline
                        </span>
                        {off.history.map((h) => {
                          const isSelf = h.actor === currentUser?.id;
                          return (
                            <div
                              key={h.id}
                              className={`p-2.5 rounded-xl text-xs flex flex-col gap-0.5 border ${isSelf
                                  ? 'bg-emerald-950/20 border-emerald-500/20 ml-4'
                                  : 'bg-slate-800/50 border-slate-700/60 mr-4'
                                }`}
                            >
                              <div className="flex justify-between font-semibold">
                                <span className={isSelf ? 'text-emerald-400' : 'text-slate-300'}>
                                  {h.actor_username} ({h.actor_role}) — {h.action.replace('_', ' ')}
                                </span>
                                <span className="font-bold text-white">${parseFloat(h.amount).toLocaleString()}</span>
                              </div>
                              {h.message && <p className="text-slate-400 italic mt-0.5 font-normal">"{h.message}"</p>}
                            </div>
                          );
                        })}
                      </div>

                      {/* Interactive Action Controls (If active and my turn) */}
                      {!isTerminal && isMyTurn && (
                        <div className="pt-3 border-t border-slate-800 space-y-3">
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleAcceptOffer(off.id)}
                              className="flex-1 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md shadow-emerald-600/20"
                            >
                              Accept Proposal (${parseFloat(off.current_amount).toLocaleString()})
                            </button>
                            <button
                              onClick={() => handleDeclineOffer(off.id)}
                              className="px-4 py-2 rounded-xl bg-rose-950 hover:bg-rose-900 text-rose-300 border border-rose-800 text-xs font-semibold"
                            >
                              Decline
                            </button>
                          </div>

                          {/* Counter-offer submission */}
                          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex flex-col gap-2">
                            <span className="text-xs font-semibold text-slate-400">Or Counter with a New Offer:</span>
                            <div className="flex gap-2">
                              <input
                                type="number"
                                placeholder="Counter Amount $"
                                value={counterAmount}
                                onChange={(e) => setCounterAmount(e.target.value)}
                                className="w-36 bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500"
                              />
                              <input
                                type="text"
                                placeholder="Note (e.g. Can do $1,625 with shipping included)"
                                value={counterMessage}
                                onChange={(e) => setCounterMessage(e.target.value)}
                                className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500"
                              />
                              <button
                                onClick={() => handleCounterOffer(off.id)}
                                disabled={!counterAmount}
                                className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold text-xs"
                              >
                                Send Counter
                              </button>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 3: SELLER STUDIO */}
        {/* ========================================================================= */}
        {activeTab === 'seller_studio' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center bg-slate-900 border border-slate-800 p-5 rounded-2xl">
              <div>
                <h2 className="text-xl font-bold text-white">Seller Studio & Inventory Management</h2>
                <p className="text-xs text-slate-400">Post audio/cinema equipment, set asking prices, and manage active listings</p>
              </div>
              <button
                onClick={() => setShowCreateListing(true)}
                className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm shadow-md shadow-emerald-600/20"
              >
                + Post New Equipment Listing
              </button>
            </div>

            {/* Seller's Listings Table */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
              <div className="px-6 py-4 border-b border-slate-800 font-bold text-sm text-white">
                Equipment Listed by {currentUser?.username}
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="bg-slate-950 text-slate-400 text-xs uppercase">
                    <tr>
                      <th className="px-6 py-3">Item</th>
                      <th className="px-6 py-3">Category</th>
                      <th className="px-6 py-3">Condition</th>
                      <th className="px-6 py-3">Asking Price</th>
                      <th className="px-6 py-3">Status</th>
                      <th className="px-6 py-3">Negotiation Offers</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {listings
                      .filter((l) => l.seller.id === currentUser?.id)
                      .map((l) => {
                        const relatedOffers = offers.filter((o) => o.listing.id === l.id);
                        return (
                          <tr key={l.id} className="hover:bg-slate-800/40">
                            <td className="px-6 py-4 font-semibold text-white flex items-center gap-3">
                              <img src={l.image_url} alt="" className="w-10 h-10 rounded-lg object-cover bg-slate-950" />
                              <span>{l.title}</span>
                            </td>
                            <td className="px-6 py-4 text-slate-400">{l.category_name}</td>
                            <td className="px-6 py-4 capitalize text-slate-300">{l.condition.replace('_', ' ')}</td>
                            <td className="px-6 py-4 font-bold text-white">${parseFloat(l.price).toLocaleString()}</td>
                            <td className="px-6 py-4">
                              <span
                                className={`px-2.5 py-1 rounded-md text-xs font-bold uppercase ${l.status === 'active'
                                    ? 'bg-emerald-500/20 text-emerald-400'
                                    : l.status === 'reserved'
                                      ? 'bg-amber-500/20 text-amber-400'
                                      : 'bg-rose-500/20 text-rose-400'
                                  }`}
                              >
                                {l.status}
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              <span className="font-semibold text-emerald-400">{relatedOffers.length} offers</span>
                            </td>
                          </tr>
                        );
                      })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 4: VERIFIED COMMUNITY REVIEWS */}
        {/* ========================================================================= */}
        {activeTab === 'reviews' && (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold text-white">Verified Peer Reviews</h2>
                <p className="text-xs text-slate-400">
                  Reviews are strictly gated: users can only leave ratings for settled, completed transactions.
                </p>
              </div>
              <div className="text-right">
                <span className="text-xs text-emerald-400 font-semibold block">100% Transaction Gated</span>
                <span className="text-xs text-slate-400">Zero Unverified Feedback</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {reviews.map((r) => (
                <div key={r.id} className="bg-slate-900 border border-slate-800 p-5 rounded-2xl shadow-xl flex flex-col justify-between">
                  <div>
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-white text-sm">{r.reviewer.username}</span>
                          <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20">
                            Verified Participant
                          </span>
                        </div>
                        <span className="text-xs text-slate-400">Reviewed Seller: {r.reviewee.username}</span>
                      </div>
                      <div className="flex items-center text-amber-400 text-base font-bold">
                        {'★'.repeat(r.rating)}
                        {'☆'.repeat(5 - r.rating)}
                      </div>
                    </div>
                    <p className="text-sm text-slate-300 italic mb-4">"{r.comment}"</p>
                  </div>
                  <div className="border-t border-slate-800 pt-3 text-xs text-slate-500 flex justify-between">
                    <span>Transaction: {r.listing_title}</span>
                    <span>{new Date(r.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* ========================================================================= */}
      {/* MODAL: MAKE AN OFFER */}
      {/* ========================================================================= */}
      {selectedListingForOffer && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-lg w-full shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1">Make an Offer</h3>
            <p className="text-xs text-slate-400 mb-4">
              Negotiate price on <span className="text-emerald-400 font-semibold">{selectedListingForOffer.title}</span> (Asking: ${parseFloat(selectedListingForOffer.price).toLocaleString()})
            </p>

            <form onSubmit={handleMakeOffer} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Your Proposed Offer ($)</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={offerAmount}
                  onChange={(e) => setOfferAmount(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-base font-bold text-white focus:outline-none focus:border-emerald-500"
                />
                {offerAmount && (
                  <span className="text-xs text-slate-400 block mt-1">
                    {Math.round((parseFloat(offerAmount) / parseFloat(selectedListingForOffer.price)) * 100)}% of asking price
                  </span>
                )}
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Message to Seller (Optional)</label>
                <textarea
                  rows={3}
                  placeholder="e.g. Can pick up locally tomorrow in Austin, cash or invoice."
                  value={offerMessage}
                  onChange={(e) => setOfferMessage(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-xs text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setSelectedListingForOffer(null)}
                  className="flex-1 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-xs font-bold text-white shadow-lg shadow-emerald-600/25"
                >
                  Submit Offer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL: VERIFIED REVIEW */}
      {/* ========================================================================= */}
      {reviewOffer && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-lg w-full shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1">Leave Verified Transaction Review</h3>
            <p className="text-xs text-slate-400 mb-4">
              Rating transaction on <span className="text-indigo-400 font-semibold">{reviewOffer.listing.title}</span>
            </p>

            <form onSubmit={handleSubmitReview} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-2">Rating (1 to 5 Stars)</label>
                <div className="flex gap-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      type="button"
                      key={star}
                      onClick={() => setReviewRating(star)}
                      className={`text-2xl transition-transform ${star <= reviewRating ? 'text-amber-400 scale-110' : 'text-slate-600'
                        }`}
                    >
                      ★
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Review Feedback</label>
                <textarea
                  rows={4}
                  required
                  placeholder="Describe equipment condition, seller communication, and negotiation transparency..."
                  value={reviewComment}
                  onChange={(e) => setReviewComment(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setReviewOffer(null)}
                  className="flex-1 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-bold text-white shadow-lg shadow-indigo-600/25"
                >
                  Submit Review
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL: POST NEW EQUIPMENT LISTING */}
      {/* ========================================================================= */}
      {showCreateListing && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-lg w-full shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1">Post New Equipment Listing</h3>
            <p className="text-xs text-slate-400 mb-4">Add your audio, camera, or computing gear to the marketplace</p>

            <form onSubmit={handleCreateListing} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Item Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Neumann TLM 103 Condenser Microphone"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Category</label>
                  <select
                    value={newCategoryId}
                    onChange={(e) => setNewCategoryId(parseInt(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                  >
                    {categories.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Condition</label>
                  <select
                    value={newCondition}
                    onChange={(e) => setNewCondition(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="brand_new">Brand New</option>
                    <option value="mint">Mint</option>
                    <option value="like_new">Like New</option>
                    <option value="good">Good</option>
                    <option value="fair">Fair</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Asking Price ($)</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  placeholder="1200.00"
                  value={newPrice}
                  onChange={(e) => setNewPrice(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Description</label>
                <textarea
                  rows={3}
                  required
                  placeholder="Details on usage hours, accessories, case, and cosmetic condition..."
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-xs text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Image URL (Optional)</label>
                <input
                  type="text"
                  placeholder="https://images.unsplash.com/..."
                  value={newImageUrl}
                  onChange={(e) => setNewImageUrl(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateListing(false)}
                  className="flex-1 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-xs font-bold text-white shadow-lg shadow-emerald-600/25"
                >
                  Publish Listing
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Clean Minimalist Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-900/80 backdrop-blur py-6 mt-16 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 rounded-lg bg-emerald-500 text-slate-950 font-black text-xs flex items-center justify-center">
              GX
            </div>
            <span className="font-bold text-white text-sm tracking-tight">GearExchange</span>
            <span className="text-slate-600">•</span>
            <span className="text-slate-400">Two-Sided Peer-to-Peer Marketplace</span>
          </div>

          <div className="flex items-center space-x-1.5 text-slate-300">
            <span>Crafted & Engineered by</span>
            <span className="font-bold text-white px-2.5 py-0.5 bg-slate-800 rounded-md border border-slate-700">
              Talha Ahmed
            </span>
          </div>

          <div className="flex items-center space-x-4 text-[11px] text-slate-500">
            <span className="flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              <span>PostgreSQL 18</span>
            </span>
            <span className="flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-sky-500"></span>
              <span>Django DRF</span>
            </span>
            <span className="flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
              <span>Next.js 14</span>
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
