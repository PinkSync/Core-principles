'use client';

import React, { useState, useEffect } from 'react';

interface PricingPlan {
  id: string;
  name: string;
  tier: string;
  price_monthly: number;
  price_yearly: number;
  features: string[];
  verifications_included: number;
  overage_cost: number;
  use_cases: string[];
}

interface PricingPageProps {
  apiEndpoint?: string;
  onSelectPlan?: (planId: string, billingPeriod: string) => void;
}

/**
 * Pricing Page Component for ASL Biometric Subscription
 * 
 * Displays subscription tiers with features and pricing
 * for the DEAF FIRST ASL Biometric verification system.
 */
export function PricingPage({ 
  apiEndpoint = '/api/subscription/plans',
  onSelectPlan
}: PricingPageProps) {
  const [plans, setPlans] = useState<PricingPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');

  useEffect(() => {
    const loadPlans = async () => {
      try {
        const response = await fetch(apiEndpoint);
        if (!response.ok) {
          throw new Error('Failed to load pricing plans');
        }
        const data = await response.json();
        setPlans(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load plans');
      } finally {
        setLoading(false);
      }
    };

    loadPlans();
  }, [apiEndpoint]);

  const getPrice = (plan: PricingPlan): number => {
    return billingPeriod === 'yearly' ? plan.price_yearly : plan.price_monthly;
  };

  const getMonthlyEquivalent = (plan: PricingPlan): number => {
    if (billingPeriod === 'yearly') {
      return Math.round(plan.price_yearly / 12);
    }
    return plan.price_monthly;
  };

  const getSavingsPercent = (plan: PricingPlan): number => {
    const yearlyMonthly = plan.price_yearly / 12;
    const savings = ((plan.price_monthly - yearlyMonthly) / plan.price_monthly) * 100;
    return Math.round(savings);
  };

  const handleSelectPlan = (planId: string) => {
    if (onSelectPlan) {
      onSelectPlan(planId, billingPeriod);
    }
  };

  const getTierColor = (tier: string): string => {
    switch (tier) {
      case 'starter':
        return 'border-blue-500';
      case 'professional':
        return 'border-pink-500';
      case 'enterprise':
        return 'border-purple-500';
      default:
        return 'border-gray-300';
    }
  };

  const getTierBg = (tier: string): string => {
    switch (tier) {
      case 'starter':
        return 'bg-blue-50';
      case 'professional':
        return 'bg-pink-50';
      case 'enterprise':
        return 'bg-purple-50';
      default:
        return 'bg-gray-50';
    }
  };

  const getTierButtonColor = (tier: string): string => {
    switch (tier) {
      case 'starter':
        return 'bg-blue-500 hover:bg-blue-600';
      case 'professional':
        return 'bg-pink-500 hover:bg-pink-600';
      case 'enterprise':
        return 'bg-purple-500 hover:bg-purple-600';
      default:
        return 'bg-gray-500 hover:bg-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="p-8 text-center" role="status" aria-busy="true">
        <span className="text-3xl animate-pulse">⏳</span>
        <p className="mt-4 text-gray-600">Loading pricing plans...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-100 border border-red-300 rounded-lg text-red-700" role="alert">
        <h2 className="text-lg font-bold">⚠️ Error Loading Plans</h2>
        <p className="mt-2">{error}</p>
      </div>
    );
  }

  return (
    <div className="py-12 px-4 max-w-7xl mx-auto">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          🎯 ASL Biometric Verification Pricing
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Secure, accessible identity verification for the Deaf community.
          Choose the plan that fits your organization's needs.
        </p>
      </div>

      {/* Billing Toggle */}
      <div className="flex justify-center mb-10">
        <div className="bg-gray-100 p-1 rounded-lg inline-flex">
          <button
            onClick={() => setBillingPeriod('monthly')}
            className={`px-6 py-2 rounded-md font-medium transition-colors ${
              billingPeriod === 'monthly'
                ? 'bg-white text-gray-900 shadow'
                : 'text-gray-600 hover:text-gray-900'
            }`}
            aria-pressed={billingPeriod === 'monthly'}
          >
            Monthly
          </button>
          <button
            onClick={() => setBillingPeriod('yearly')}
            className={`px-6 py-2 rounded-md font-medium transition-colors ${
              billingPeriod === 'yearly'
                ? 'bg-white text-gray-900 shadow'
                : 'text-gray-600 hover:text-gray-900'
            }`}
            aria-pressed={billingPeriod === 'yearly'}
          >
            Yearly
            <span className="ml-2 text-green-600 text-sm font-normal">
              Save up to 20%
            </span>
          </button>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className={`rounded-2xl border-2 ${getTierColor(plan.tier)} ${getTierBg(plan.tier)} p-8 relative flex flex-col`}
          >
            {/* Popular Badge */}
            {plan.tier === 'professional' && (
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <span className="bg-pink-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                  Most Popular
                </span>
              </div>
            )}

            {/* Plan Header */}
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">{plan.name}</h2>
              <div className="mt-4">
                <span className="text-4xl font-bold text-gray-900">
                  ${getMonthlyEquivalent(plan)}
                </span>
                <span className="text-gray-600">/month</span>
              </div>
              {billingPeriod === 'yearly' && (
                <p className="mt-2 text-green-600 text-sm">
                  Save {getSavingsPercent(plan)}% with yearly billing
                </p>
              )}
              <p className="mt-2 text-gray-500 text-sm">
                Billed {billingPeriod === 'yearly' ? `$${getPrice(plan)} annually` : 'monthly'}
              </p>
            </div>

            {/* Verifications */}
            <div className="bg-white rounded-lg p-4 mb-6 text-center">
              <p className="text-3xl font-bold text-gray-900">
                {plan.verifications_included === 10000 
                  ? 'Unlimited' 
                  : plan.verifications_included.toLocaleString()}
              </p>
              <p className="text-gray-600">verifications/month</p>
              <p className="text-sm text-gray-500 mt-1">
                ${plan.overage_cost} per additional verification
              </p>
            </div>

            {/* Features */}
            <ul className="space-y-3 flex-grow mb-6">
              {plan.features.map((feature, index) => (
                <li key={index} className="flex items-start gap-3">
                  <span className="text-green-500 mt-0.5">✓</span>
                  <span className="text-gray-700">{feature}</span>
                </li>
              ))}
            </ul>

            {/* Use Cases */}
            <div className="mb-6">
              <p className="text-sm font-medium text-gray-700 mb-2">Supported use cases:</p>
              <div className="flex flex-wrap gap-2">
                {plan.use_cases.map((useCase, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-white rounded text-xs text-gray-600 capitalize"
                  >
                    {useCase.replace('_', ' ')}
                  </span>
                ))}
              </div>
            </div>

            {/* CTA Button */}
            <button
              onClick={() => handleSelectPlan(plan.id)}
              className={`w-full py-3 px-6 rounded-lg font-semibold text-white transition-colors ${getTierButtonColor(plan.tier)}`}
            >
              {plan.tier === 'enterprise' ? 'Contact Sales' : 'Get Started'}
            </button>
          </div>
        ))}
      </div>

      {/* Bottom Info */}
      <div className="mt-12 text-center">
        <div className="bg-gray-50 rounded-lg p-6 max-w-2xl mx-auto">
          <h3 className="font-semibold text-gray-900 mb-2">
            🤟 Built for the Deaf Community
          </h3>
          <p className="text-gray-600">
            All plans include HIPAA, FERPA, and ADA compliance. 
            Our ASL biometric verification ensures accessible identity 
            verification across healthcare, legal, education, and government sectors.
          </p>
        </div>
      </div>

      {/* FAQ Link */}
      <div className="mt-8 text-center">
        <p className="text-gray-600">
          Questions? Check our{' '}
          <a href="#faq" className="text-pink-600 hover:text-pink-700 underline">
            FAQ
          </a>{' '}
          or{' '}
          <a href="#contact" className="text-pink-600 hover:text-pink-700 underline">
            contact us
          </a>
        </p>
      </div>
    </div>
  );
}

export default PricingPage;
