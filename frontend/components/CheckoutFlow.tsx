'use client';

import React, { useState } from 'react';

interface CheckoutFlowProps {
  planId: string;
  planName: string;
  billingPeriod: 'monthly' | 'yearly';
  price: number;
  apiEndpoint?: string;
  successUrl?: string;
  cancelUrl?: string;
  onSuccess?: (sessionId: string, url: string) => void;
  onError?: (error: string) => void;
}

/**
 * Checkout Flow Component for ASL Biometric Subscription
 * 
 * Handles the Stripe checkout process for subscription plans.
 */
export function CheckoutFlow({
  planId,
  planName,
  billingPeriod,
  price,
  apiEndpoint = '/api/subscription/checkout',
  successUrl = '/subscription/success',
  cancelUrl = '/subscription/cancel',
  onSuccess,
  onError
}: CheckoutFlowProps) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !email.includes('@')) {
      setError('Please enter a valid email address');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          plan_id: planId,
          billing_period: billingPeriod,
          customer_email: email,
          success_url: `${window.location.origin}${successUrl}?session_id={CHECKOUT_SESSION_ID}`,
          cancel_url: `${window.location.origin}${cancelUrl}`
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Checkout failed');
      }

      const session = await response.json();
      
      if (onSuccess) {
        onSuccess(session.session_id, session.url);
      }

      // Redirect to Stripe checkout
      if (session.url) {
        window.location.href = session.url;
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Checkout failed';
      setError(errorMessage);
      if (onError) {
        onError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-xl shadow-lg">
      {/* Header */}
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          Complete Your Subscription
        </h2>
        <p className="text-gray-600 mt-2">
          Subscribe to {planName} plan
        </p>
      </div>

      {/* Order Summary */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-gray-900 mb-3">Order Summary</h3>
        <div className="flex justify-between items-center">
          <div>
            <p className="font-medium text-gray-900">{planName} Plan</p>
            <p className="text-sm text-gray-500 capitalize">{billingPeriod} billing</p>
          </div>
          <div className="text-right">
            <p className="text-xl font-bold text-gray-900">${price}</p>
            <p className="text-sm text-gray-500">
              /{billingPeriod === 'yearly' ? 'year' : 'month'}
            </p>
          </div>
        </div>
      </div>

      {/* Checkout Form */}
      <form onSubmit={handleCheckout} className="space-y-4">
        <div>
          <label 
            htmlFor="email" 
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Email Address
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@organization.com"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
            disabled={loading}
            required
            aria-describedby="email-help"
          />
          <p id="email-help" className="text-sm text-gray-500 mt-1">
            We'll send your receipt to this email
          </p>
        </div>

        {error && (
          <div className="p-3 bg-red-100 border border-red-300 rounded-lg text-red-700 text-sm" role="alert">
            ⚠️ {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 px-6 bg-pink-500 hover:bg-pink-600 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="animate-spin">⏳</span>
              Processing...
            </span>
          ) : (
            `Subscribe - $${price}/${billingPeriod === 'yearly' ? 'year' : 'month'}`
          )}
        </button>
      </form>

      {/* Security Info */}
      <div className="mt-6 text-center">
        <p className="text-sm text-gray-500 flex items-center justify-center gap-2">
          <span>🔒</span>
          Secured by Stripe. Your payment info is never stored on our servers.
        </p>
      </div>

      {/* Features Reminder */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="font-medium text-blue-900 mb-2">What you'll get:</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>✓ ASL biometric identity verification</li>
          <li>✓ HIPAA & ADA compliant</li>
          <li>✓ API access for integration</li>
          <li>✓ Cancel anytime</li>
        </ul>
      </div>
    </div>
  );
}

export default CheckoutFlow;
