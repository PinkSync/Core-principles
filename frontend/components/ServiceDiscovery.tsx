'use client';

import React, { useState } from 'react';

interface ServiceDiscoveryResult {
  matched_services: string[];
  alternative_services?: string[];
  community_recommendations?: string[];
  message?: string;
  suggestions?: string[];
}

interface ServiceDiscoveryProps {
  apiEndpoint?: string;
}

/**
 * Service Discovery Component
 * 
 * Helps deaf users find relevant services based on their needs.
 * Uses natural language queries to match with available services.
 */
export function ServiceDiscovery({ 
  apiEndpoint = '/api/discover' 
}: ServiceDiscoveryProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<ServiceDiscoveryResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Common queries for quick access
  const quickQueries = [
    'tax help',
    'insurance question',
    'buying house',
    'emergency',
    'start business',
    'doctor appointment'
  ];

  const handleSearch = async (searchQuery?: string) => {
    const q = searchQuery || query;
    if (!q.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch(`${apiEndpoint}?query=${encodeURIComponent(q)}`);

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      console.error('Service discovery error:', err);
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickQuery = (q: string) => {
    setQuery(q);
    handleSearch(q);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-pink-600 mb-2">
          🔍 Service Discovery
        </h2>
        <p className="text-gray-600">
          Find the right DEAF FIRST services for your needs
        </p>
      </div>

      {/* Search Input */}
      <div className="flex gap-2 mb-6">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="What do you need help with?"
          className="flex-1 p-3 border rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
          disabled={loading}
          aria-label="Search for services"
        />
        <button
          onClick={() => handleSearch()}
          className="px-6 py-3 bg-pink-500 hover:bg-pink-600 text-white font-semibold rounded-lg transition-colors disabled:opacity-50"
          disabled={loading}
        >
          {loading ? '...' : 'Search'}
        </button>
      </div>

      {/* Quick Queries */}
      <div className="mb-6">
        <p className="text-sm text-gray-500 mb-2">Quick searches:</p>
        <div className="flex flex-wrap gap-2">
          {quickQueries.map((q, index) => (
            <button
              key={index}
              onClick={() => handleQuickQuery(q)}
              className="px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full text-sm transition-colors"
              disabled={loading}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-100 border border-red-300 rounded-lg text-red-700 mb-6" role="alert">
          ⚠️ {error}
        </div>
      )}

      {/* Results */}
      {results && (
        <div className="space-y-6">
          {/* Matched Services */}
          {results.matched_services && results.matched_services.length > 0 && (
            <section className="bg-green-50 p-6 rounded-lg border border-green-200">
              <h3 className="font-semibold text-green-800 mb-3">
                ✅ Matched Services
              </h3>
              <div className="flex flex-wrap gap-2">
                {results.matched_services.map((service, index) => (
                  <button
                    key={index}
                    className="px-4 py-2 bg-green-100 hover:bg-green-200 text-green-800 rounded-lg transition-colors"
                  >
                    {service}
                  </button>
                ))}
              </div>
            </section>
          )}

          {/* Alternative Services */}
          {results.alternative_services && results.alternative_services.length > 0 && (
            <section className="bg-blue-50 p-6 rounded-lg border border-blue-200">
              <h3 className="font-semibold text-blue-800 mb-3">
                💡 Related Services
              </h3>
              <div className="flex flex-wrap gap-2">
                {results.alternative_services.map((service, index) => (
                  <button
                    key={index}
                    className="px-4 py-2 bg-blue-100 hover:bg-blue-200 text-blue-800 rounded-lg transition-colors"
                  >
                    {service}
                  </button>
                ))}
              </div>
            </section>
          )}

          {/* No Results Message */}
          {results.message && (
            <section className="bg-yellow-50 p-6 rounded-lg border border-yellow-200">
              <h3 className="font-semibold text-yellow-800 mb-3">
                ℹ️ {results.message}
              </h3>
              {results.suggestions && results.suggestions.length > 0 && (
                <div>
                  <p className="text-sm text-yellow-700 mb-2">Try one of these:</p>
                  <div className="flex flex-wrap gap-2">
                    {results.suggestions.slice(0, 8).map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => handleQuickQuery(suggestion)}
                        className="px-3 py-1 bg-yellow-100 hover:bg-yellow-200 text-yellow-800 rounded-full text-sm transition-colors"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </section>
          )}

          {/* Community Recommendations */}
          {results.community_recommendations && results.community_recommendations.length > 0 && (
            <section className="bg-purple-50 p-6 rounded-lg border border-purple-200">
              <h3 className="font-semibold text-purple-800 mb-3">
                🤝 Community Recommendations
              </h3>
              <ul className="space-y-2">
                {results.community_recommendations.map((rec, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <span className="text-purple-500">★</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      )}

      {/* Help Text */}
      <div className="mt-8 p-4 bg-gray-50 rounded-lg text-sm text-gray-600">
        <strong>🤟 Need help?</strong>
        <p className="mt-1">
          Type what you need in plain language. Our DEAF FIRST services are designed
          to understand your needs and connect you with the right support.
        </p>
      </div>
    </div>
  );
}

export default ServiceDiscovery;
