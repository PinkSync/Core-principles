'use client';

import React, { useState } from 'react';

interface ValidationResult {
  url: string;
  deaf_score: number;
  asl_compatible: boolean;
  audio_issues_found: boolean;
}

interface AITriggerPanelProps {
  apiEndpoint?: string;
}

/**
 * AI Trigger Panel for PinkSync Validator
 * 
 * Allows users or AI agents to trigger batch deaf-first accessibility
 * validations from the dashboard UI with real-time results.
 */
export function AITriggerPanel({ 
  apiEndpoint = '/api/py/ai-validate' 
}: AITriggerPanelProps) {
  const [urls, setUrls] = useState('');
  const [results, setResults] = useState<ValidationResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleValidate = async () => {
    setLoading(true);
    setResults([]);
    setError(null);

    try {
      const urlArray = urls
        .split(',')
        .map((u) => u.trim())
        .filter(Boolean);

      if (urlArray.length === 0) {
        setError('Please enter at least one URL');
        setLoading(false);
        return;
      }

      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Magician-Role': 'accessibility-auditor'
        },
        body: JSON.stringify({ task: 'validate_batch', urls: urlArray })
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const data = await response.json();
      setResults(data.results || []);
    } catch (err) {
      console.error('Validation error:', err);
      setError(err instanceof Error ? err.message : 'Validation failed');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBadge = (score: number): string => {
    if (score >= 90) return 'bg-green-100';
    if (score >= 70) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="p-6 rounded-xl shadow-lg bg-white border border-gray-200 max-w-3xl mx-auto mt-10">
      <h2 className="text-2xl font-bold mb-4 text-pink-600">
        🎯 AI Trigger Validator
      </h2>
      
      <p className="text-gray-600 mb-4">
        Enter URLs separated by commas to validate their deaf-first accessibility.
      </p>

      <textarea
        value={urls}
        onChange={(e) => setUrls(e.target.value)}
        placeholder="https://example.com, https://another-site.com"
        className="w-full h-24 p-3 border rounded-md mb-4 focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
        disabled={loading}
        aria-label="URLs to validate"
      />

      <button
        onClick={handleValidate}
        className="bg-pink-500 hover:bg-pink-600 text-white font-semibold py-2 px-6 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        disabled={loading}
        aria-busy={loading}
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <span className="animate-spin">⏳</span>
            Validating...
          </span>
        ) : (
          'Run AI Batch Validation'
        )}
      </button>

      {error && (
        <div className="mt-4 p-4 bg-red-100 border border-red-300 rounded-md text-red-700" role="alert">
          ⚠️ {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            🧾 Validation Results
          </h3>
          
          <ul className="space-y-3" role="list" aria-label="Validation results">
            {results.map((res, index) => (
              <li 
                key={index} 
                className={`p-4 rounded-md ${getScoreBadge(res.deaf_score)}`}
              >
                <div className="font-semibold text-gray-800 break-all">
                  {res.url}
                </div>
                
                <div className="mt-2 grid grid-cols-1 sm:grid-cols-3 gap-2 text-sm">
                  <div>
                    🧠 Deaf Score:{' '}
                    <span className={`font-bold ${getScoreColor(res.deaf_score)}`}>
                      {res.deaf_score}
                    </span>
                  </div>
                  
                  <div>
                    🤟 ASL Compatible:{' '}
                    <span className={res.asl_compatible ? 'text-green-600' : 'text-red-600'}>
                      {res.asl_compatible ? '✅ Yes' : '❌ No'}
                    </span>
                  </div>
                  
                  <div>
                    🔇 Audio Issues:{' '}
                    <span className={res.audio_issues_found ? 'text-yellow-600' : 'text-green-600'}>
                      {res.audio_issues_found ? '⚠️ Found' : '✅ Clean'}
                    </span>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-6 p-4 bg-gray-50 rounded-md text-sm text-gray-600">
        <strong>💡 Tip:</strong> This validator checks for deaf-first accessibility compliance including:
        <ul className="list-disc list-inside mt-2 space-y-1">
          <li>Text-based primary interfaces</li>
          <li>Visual indicators and feedback</li>
          <li>No audio requirements</li>
          <li>ASL compatibility</li>
          <li>Cultural competency markers</li>
        </ul>
      </div>
    </div>
  );
}

export default AITriggerPanel;
