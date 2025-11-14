import { useState } from 'react';
import { Search, Sparkles, AlertCircle } from 'lucide-react';
import { format } from 'date-fns';

interface SearchResult {
  id: string;
  description: string;
  location: string;
  timestamp: string;
  waste_type?: string;
  waste_type_confidence?: number;
  keywords?: string[];
}

export default function SemanticSearch() {
  const [query, setQuery] = useState('');
  const [threshold, setThreshold] = useState(0.30);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setIsSearching(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8000/api/incidents/search/semantic?query=${encodeURIComponent(query)}&threshold=${threshold}&limit=10`
      );

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setResults(data);
      
      if (data.length === 0) {
        setError('No similar incidents found. Try adjusting the similarity threshold or using different keywords.');
      }
    } catch (err) {
      setError('Failed to perform search. Please try again.');
      console.error(err);
    } finally {
      setIsSearching(false);
    }
  };

  const getWasteTypeColor = (wasteType: string | undefined) => {
    if (!wasteType) return 'bg-gray-100 text-gray-800';
    
    const colors: Record<string, string> = {
      plastic: 'bg-blue-100 text-blue-800',
      organic: 'bg-green-100 text-green-800',
      paper: 'bg-yellow-100 text-yellow-800',
      glass: 'bg-purple-100 text-purple-800',
      metal: 'bg-gray-100 text-gray-800',
      electronic: 'bg-red-100 text-red-800',
      hazardous: 'bg-red-200 text-red-900',
      textile: 'bg-pink-100 text-pink-800',
      construction: 'bg-orange-100 text-orange-800',
      mixed: 'bg-indigo-100 text-indigo-800',
    };
    
    return colors[wasteType] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="h-8 w-8 text-green-600" />
          <h1 className="text-3xl font-bold text-gray-900">Semantic Search</h1>
        </div>
        <p className="text-gray-600">
          Use AI-powered semantic search to find similar incidents based on meaning, not just keywords.
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Query
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., 'plastic waste near parks' or 'hazardous chemical spills'"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent text-lg"
              />
            </div>
            <p className="mt-1 text-sm text-gray-500">
              Describe what you're looking for in natural language
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Similarity Threshold: {(threshold * 100).toFixed(0)}%
            </label>
            <input
              type="range"
              min="0.3"
              max="0.95"
              step="0.05"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-green-600"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>More results (30%)</span>
              <span>More precise (95%)</span>
            </div>
          </div>

          <button
            type="submit"
            disabled={isSearching}
            className="w-full bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors flex items-center justify-center gap-2"
          >
            {isSearching ? (
              <>
                <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                Searching...
              </>
            ) : (
              <>
                <Search className="h-5 w-5" />
                Search with AI
              </>
            )}
          </button>
        </form>

        {/* Example Queries */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-sm font-medium text-gray-700 mb-2">Example queries:</p>
          <div className="flex flex-wrap gap-2">
            {[
              'plastic waste near parks',
              'hazardous chemical spills',
              'electronic waste disposal',
              'organic food waste',
              'construction debris downtown'
            ].map((example) => (
              <button
                key={example}
                onClick={() => setQuery(example)}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full transition-colors"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-yellow-800">{error}</p>
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Found {results.length} similar incident{results.length !== 1 ? 's' : ''}
          </h2>

          <div className="space-y-3">
            {results.map((result) => (
              <div
                key={result.id}
                className="bg-white rounded-lg shadow p-5 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <p className="text-gray-900 mb-2">{result.description}</p>
                    
                    <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                      <span className="flex items-center gap-1">
                        📍 {result.location}
                      </span>
                      <span>
                        🕒 {format(new Date(result.timestamp), 'MMM dd, yyyy HH:mm')}
                      </span>
                    </div>

                    {result.keywords && result.keywords.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {result.keywords.slice(0, 5).map((keyword, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                          >
                            {keyword}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {result.waste_type && (
                    <div className="flex-shrink-0">
                      <span
                        className={`px-3 py-1 text-xs font-semibold rounded-full ${getWasteTypeColor(
                          result.waste_type
                        )}`}
                      >
                        {result.waste_type}
                        {result.waste_type_confidence && (
                          <span className="ml-1">
                            ({Math.round(result.waste_type_confidence * 100)}%)
                          </span>
                        )}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* How it Works */}
      {/* <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3 flex items-center gap-2">
          <Sparkles className="h-5 w-5" />
          How Semantic Search Works
        </h3>
        <div className="space-y-2 text-sm text-blue-800">
          <p>
            <strong>🧠 AI-Powered:</strong> Uses sentence-transformers (all-MiniLM-L6-v2) to understand meaning, not just match keywords
          </p>
          <p>
            <strong>📊 Vector Similarity:</strong> Converts text to 384-dimensional vectors and finds similar incidents using cosine similarity
          </p>
          <p>
            <strong>🔒 Completely Offline:</strong> All AI processing happens locally - no external APIs used
          </p>
          <p>
            <strong>⚡ Fast:</strong> Results in ~50-100ms even with thousands of incidents
          </p>
        </div>
      </div> */}
    </div>
  );
}
