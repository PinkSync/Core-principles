'use client';

import React, { useState, useEffect } from 'react';

interface DashboardConfig {
  dashboard_title: string;
  quick_access: string[];
  service_categories: {
    immediate: string[];
    daily: string[];
    weekly: string[];
    as_needed: string[];
  };
  personalized_content: {
    financial_goals: string[];
    upcoming_deadlines: string[];
    recommended_services: string[];
    community_events: string[];
  };
  integrations: {
    bank_accounts: string[];
    insurance_policies: string[];
    tax_software: string | null;
    legal_documents: string[];
  };
}

interface UserProfile {
  name: string;
  needs_financial_help: boolean;
  is_business_owner: boolean;
  needs_healthcare_help: boolean;
  location: string;
  financial_goals: string[];
  preferred_communication: string;
}

interface DashboardProps {
  userProfile?: UserProfile;
  apiEndpoint?: string;
}

/**
 * DEAF FIRST Dashboard Component
 * 
 * Displays personalized dashboard for deaf and hard-of-hearing users
 * with quick access to essential services and personalized content.
 */
export function Dashboard({ 
  userProfile,
  apiEndpoint = '/api/initialize-dashboard' 
}: DashboardProps) {
  const [dashboard, setDashboard] = useState<DashboardConfig | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const defaultProfile: UserProfile = {
    name: 'Guest',
    needs_financial_help: false,
    is_business_owner: false,
    needs_healthcare_help: false,
    location: '',
    financial_goals: [],
    preferred_communication: 'text-heavy'
  };

  useEffect(() => {
    const loadDashboard = async () => {
      setLoading(true);
      setError(null);

      try {
        const profile = userProfile || defaultProfile;
        
        const response = await fetch(apiEndpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(profile)
        });

        if (!response.ok) {
          throw new Error(`Failed to load dashboard: ${response.status}`);
        }

        const data = await response.json();
        setDashboard(data);
      } catch (err) {
        console.error('Dashboard load error:', err);
        setError(err instanceof Error ? err.message : 'Failed to load dashboard');
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, [userProfile, apiEndpoint]);

  if (loading) {
    return (
      <div className="p-6 text-center" role="status" aria-busy="true">
        <span className="text-2xl animate-pulse">⏳</span>
        <p className="mt-2 text-gray-600">Loading your DEAF FIRST Dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-100 border border-red-300 rounded-lg text-red-700" role="alert">
        <h2 className="text-lg font-bold">⚠️ Error Loading Dashboard</h2>
        <p className="mt-2">{error}</p>
      </div>
    );
  }

  if (!dashboard) {
    return null;
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-pink-600">
          {dashboard.dashboard_title}
        </h1>
        <p className="text-gray-600 mt-2">
          Your personalized DEAF FIRST services hub
        </p>
      </header>

      {/* Quick Access */}
      <section className="mb-8" aria-labelledby="quick-access-heading">
        <h2 id="quick-access-heading" className="text-xl font-semibold text-gray-800 mb-4">
          ⚡ Quick Access
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {dashboard.quick_access.map((item, index) => (
            <button
              key={index}
              className="p-4 bg-pink-50 hover:bg-pink-100 rounded-lg border border-pink-200 text-pink-700 font-medium transition-colors text-center"
            >
              {item}
            </button>
          ))}
        </div>
      </section>

      {/* Personalized Content */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Financial Goals */}
        {dashboard.personalized_content.financial_goals.length > 0 && (
          <section className="bg-white p-6 rounded-lg shadow border" aria-labelledby="goals-heading">
            <h2 id="goals-heading" className="text-lg font-semibold text-gray-800 mb-3">
              🎯 Your Financial Goals
            </h2>
            <ul className="space-y-2">
              {dashboard.personalized_content.financial_goals.map((goal, index) => (
                <li key={index} className="flex items-center gap-2">
                  <span className="text-green-500">○</span>
                  <span>{goal}</span>
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Upcoming Deadlines */}
        {dashboard.personalized_content.upcoming_deadlines.length > 0 && (
          <section className="bg-white p-6 rounded-lg shadow border" aria-labelledby="deadlines-heading">
            <h2 id="deadlines-heading" className="text-lg font-semibold text-gray-800 mb-3">
              📅 Upcoming Deadlines
            </h2>
            <ul className="space-y-2">
              {dashboard.personalized_content.upcoming_deadlines.map((deadline, index) => (
                <li key={index} className="flex items-center gap-2 text-orange-600">
                  <span>⏰</span>
                  <span>{deadline}</span>
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Recommended Services */}
        {dashboard.personalized_content.recommended_services.length > 0 && (
          <section className="bg-white p-6 rounded-lg shadow border" aria-labelledby="recommended-heading">
            <h2 id="recommended-heading" className="text-lg font-semibold text-gray-800 mb-3">
              ⭐ Recommended for You
            </h2>
            <div className="flex flex-wrap gap-2">
              {dashboard.personalized_content.recommended_services.map((service, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                >
                  {service}
                </span>
              ))}
            </div>
          </section>
        )}

        {/* Community Events */}
        {dashboard.personalized_content.community_events.length > 0 && (
          <section className="bg-white p-6 rounded-lg shadow border" aria-labelledby="events-heading">
            <h2 id="events-heading" className="text-lg font-semibold text-gray-800 mb-3">
              🤝 Community Events
            </h2>
            <ul className="space-y-2">
              {dashboard.personalized_content.community_events.map((event, index) => (
                <li key={index} className="flex items-center gap-2">
                  <span className="text-purple-500">📍</span>
                  <span>{event}</span>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>

      {/* Service Categories */}
      <section aria-labelledby="services-heading">
        <h2 id="services-heading" className="text-xl font-semibold text-gray-800 mb-4">
          🛠️ Your Services
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-red-50 rounded-lg border border-red-200">
            <h3 className="font-semibold text-red-700 mb-2">🚨 Immediate</h3>
            <ul className="text-sm space-y-1">
              {dashboard.service_categories.immediate.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
          
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h3 className="font-semibold text-green-700 mb-2">📆 Daily</h3>
            <ul className="text-sm space-y-1">
              {dashboard.service_categories.daily.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
          
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="font-semibold text-blue-700 mb-2">📅 Weekly</h3>
            <ul className="text-sm space-y-1">
              {dashboard.service_categories.weekly.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
          
          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="font-semibold text-gray-700 mb-2">📋 As Needed</h3>
            <ul className="text-sm space-y-1">
              {dashboard.service_categories.as_needed.slice(0, 5).map((s, i) => (
                <li key={i}>{s}</li>
              ))}
              {dashboard.service_categories.as_needed.length > 5 && (
                <li className="text-gray-500">
                  +{dashboard.service_categories.as_needed.length - 5} more
                </li>
              )}
            </ul>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-8 pt-6 border-t text-center text-sm text-gray-500">
        <p>DEAF FIRST • Built for accessibility, not retrofitted</p>
        <p className="mt-1">🤟 PinkSync API v1.0.0</p>
      </footer>
    </div>
  );
}

export default Dashboard;
