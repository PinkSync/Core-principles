'use client';

import React, { useState, useEffect } from 'react';

interface SubscriptionInfo {
  subscription_id: string;
  customer_id: string;
  plan_id: string;
  status: string;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  verifications_used: number;
  verifications_remaining: number;
}

interface UsageReport {
  subscription_id: string;
  period_start: string;
  period_end: string;
  verifications_included: number;
  verifications_used: number;
  overage_count: number;
  overage_cost: number;
  breakdown_by_use_case: Record<string, number>;
}

interface SubscriptionManagementProps {
  subscriptionId: string;
  apiEndpoint?: string;
  portalEndpoint?: string;
  onManageSubscription?: (portalUrl: string) => void;
}

/**
 * Subscription Management Component
 * 
 * Displays subscription status, usage statistics, and
 * provides access to manage subscription via Stripe portal.
 */
export function SubscriptionManagement({
  subscriptionId,
  apiEndpoint = '/api/subscription',
  portalEndpoint = '/api/subscription/portal',
  onManageSubscription
}: SubscriptionManagementProps) {
  const [subscription, setSubscription] = useState<SubscriptionInfo | null>(null);
  const [usage, setUsage] = useState<UsageReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [portalLoading, setPortalLoading] = useState(false);

  useEffect(() => {
    const loadSubscriptionData = async () => {
      try {
        // Load subscription info
        const subResponse = await fetch(`${apiEndpoint}/${subscriptionId}`);
        if (!subResponse.ok) {
          throw new Error('Failed to load subscription');
        }
        const subData = await subResponse.json();
        setSubscription(subData);

        // Load usage report
        const usageResponse = await fetch(`${apiEndpoint}/${subscriptionId}/usage`);
        if (usageResponse.ok) {
          const usageData = await usageResponse.json();
          setUsage(usageData);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    loadSubscriptionData();
  }, [subscriptionId, apiEndpoint]);

  const handleManageSubscription = async () => {
    if (!subscription) return;
    
    setPortalLoading(true);
    try {
      const response = await fetch(portalEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
          customer_id: subscription.customer_id,
          return_url: window.location.href
        })
      });

      if (!response.ok) {
        throw new Error('Failed to open portal');
      }

      const portal = await response.json();
      
      if (onManageSubscription) {
        onManageSubscription(portal.url);
      } else {
        window.location.href = portal.url;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to open portal');
    } finally {
      setPortalLoading(false);
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'past_due':
        return 'bg-yellow-100 text-yellow-800';
      case 'canceled':
        return 'bg-red-100 text-red-800';
      case 'trialing':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string): string => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  const getUsagePercentage = (): number => {
    if (!usage) return 0;
    return Math.min(100, Math.round((usage.verifications_used / usage.verifications_included) * 100));
  };

  const getUsageColor = (): string => {
    const percentage = getUsagePercentage();
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (loading) {
    return (
      <div className="p-8 text-center" role="status" aria-busy="true">
        <span className="text-3xl animate-pulse">⏳</span>
        <p className="mt-4 text-gray-600">Loading subscription...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-100 border border-red-300 rounded-lg text-red-700" role="alert">
        <h2 className="text-lg font-bold">⚠️ Error</h2>
        <p className="mt-2">{error}</p>
      </div>
    );
  }

  if (!subscription) {
    return (
      <div className="p-6 bg-gray-100 rounded-lg text-center">
        <p className="text-gray-600">No subscription found</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Subscription Management
          </h1>
          <p className="text-gray-600 mt-1">
            Manage your ASL Biometric verification subscription
          </p>
        </div>
        <button
          onClick={handleManageSubscription}
          disabled={portalLoading}
          className="px-4 py-2 bg-pink-500 hover:bg-pink-600 text-white font-medium rounded-lg transition-colors disabled:opacity-50"
        >
          {portalLoading ? 'Opening...' : 'Manage Subscription'}
        </button>
      </div>

      {/* Status Card */}
      <div className="bg-white rounded-xl shadow-md p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Subscription Status</h2>
          <span className={`px-3 py-1 rounded-full text-sm font-medium capitalize ${getStatusColor(subscription.status)}`}>
            {subscription.status.replace('_', ' ')}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-gray-500">Plan</p>
            <p className="text-lg font-medium text-gray-900 capitalize">{subscription.plan_id}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Current Period</p>
            <p className="text-lg font-medium text-gray-900">
              {formatDate(subscription.current_period_start)} - {formatDate(subscription.current_period_end)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Renewal</p>
            <p className="text-lg font-medium text-gray-900">
              {subscription.cancel_at_period_end 
                ? 'Cancels at period end' 
                : `Renews ${formatDate(subscription.current_period_end)}`
              }
            </p>
          </div>
        </div>

        {subscription.cancel_at_period_end && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-yellow-800 text-sm">
              ⚠️ Your subscription will end on {formatDate(subscription.current_period_end)}.
              You can reactivate it from the subscription management portal.
            </p>
          </div>
        )}
      </div>

      {/* Usage Card */}
      <div className="bg-white rounded-xl shadow-md p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Usage This Period</h2>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Verifications Used</span>
            <span>{subscription.verifications_used} / {usage?.verifications_included ?? '∞'}</span>
          </div>
          <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className={`h-full ${getUsageColor()} transition-all`}
              style={{ width: `${getUsagePercentage()}%` }}
            />
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-3xl font-bold text-gray-900">
              {subscription.verifications_used}
            </p>
            <p className="text-sm text-gray-500">Used</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-3xl font-bold text-gray-900">
              {subscription.verifications_remaining}
            </p>
            <p className="text-sm text-gray-500">Remaining</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-3xl font-bold text-gray-900">
              {usage?.overage_count ?? 0}
            </p>
            <p className="text-sm text-gray-500">Overage</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-3xl font-bold text-gray-900">
              ${usage?.overage_cost?.toFixed(2) ?? '0.00'}
            </p>
            <p className="text-sm text-gray-500">Overage Cost</p>
          </div>
        </div>

        {/* Usage Breakdown */}
        {usage && Object.keys(usage.breakdown_by_use_case).length > 0 && (
          <div className="mt-6">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Usage by Category</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {Object.entries(usage.breakdown_by_use_case).map(([useCase, count]) => (
                <div 
                  key={useCase} 
                  className="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
                >
                  <span className="text-gray-700 capitalize">{useCase.replace('_', ' ')}</span>
                  <span className="font-semibold text-gray-900">{count}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
            <span className="text-2xl mb-2 block">📊</span>
            <span className="font-medium text-gray-900">View Full Report</span>
            <p className="text-sm text-gray-500 mt-1">Detailed usage analytics</p>
          </button>
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
            <span className="text-2xl mb-2 block">💳</span>
            <span className="font-medium text-gray-900">Update Payment</span>
            <p className="text-sm text-gray-500 mt-1">Change payment method</p>
          </button>
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
            <span className="text-2xl mb-2 block">📧</span>
            <span className="font-medium text-gray-900">Billing History</span>
            <p className="text-sm text-gray-500 mt-1">View past invoices</p>
          </button>
        </div>
      </div>

      {/* Help Section */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg text-center">
        <p className="text-blue-800">
          Need help? Contact our support team at{' '}
          <a href="mailto:support@pinksync.com" className="underline">
            support@pinksync.com
          </a>
        </p>
      </div>
    </div>
  );
}

export default SubscriptionManagement;
