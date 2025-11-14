import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Send, AlertCircle, AlertTriangle, X } from 'lucide-react';
import { format } from 'date-fns';
import { incidentAPI, type IncidentCreate, type Incident } from '../api/incidents';

export default function IncidentForm() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState<IncidentCreate>({
    description: '',
    timestamp: new Date().toISOString().slice(0, 16),
    location: '',
    latitude: undefined,
    longitude: undefined,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [similarIncidents, setSimilarIncidents] = useState<Incident[]>([]);
  const [showDuplicateModal, setShowDuplicateModal] = useState(false);
  const [isCheckingDuplicates, setIsCheckingDuplicates] = useState(false);

  const createMutation = useMutation({
    mutationFn: incidentAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      queryClient.invalidateQueries({ queryKey: ['summary'] });
      alert('Incident reported successfully! AI analysis completed.');
      navigate('/incidents');
    },
    onError: (error: any) => {
      alert(`Failed to report incident: ${error.message}`);
    },
  });

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (formData.description.length < 10) {
      newErrors.description = 'Description must be at least 10 characters';
    }

    if (!formData.location || formData.location.length < 3) {
      newErrors.location = 'Location must be at least 3 characters';
    }

    if (formData.latitude && (formData.latitude < -90 || formData.latitude > 90)) {
      newErrors.latitude = 'Latitude must be between -90 and 90';
    }

    if (formData.longitude && (formData.longitude < -180 || formData.longitude > 180)) {
      newErrors.longitude = 'Longitude must be between -180 and 180';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const checkForDuplicates = async (): Promise<Incident[]> => {
    try {
      const searchQuery = `${formData.description} ${formData.location}`;
      const response = await fetch(
        `http://localhost:8000/api/incidents/search/semantic?query=${encodeURIComponent(searchQuery)}&threshold=0.4&limit=5`
      );
      
      if (!response.ok) {
        return [];
      }
      
      const similar = await response.json();
      return similar;
    } catch (error) {
      console.error('Error checking for duplicates:', error);
      return [];
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validate()) {
      return;
    }

    // Check for similar incidents before submitting
    setIsCheckingDuplicates(true);
    const similar = await checkForDuplicates();
    setIsCheckingDuplicates(false);

    if (similar.length > 0) {
      // Show duplicate warning modal
      setSimilarIncidents(similar);
      setShowDuplicateModal(true);
    } else {
      // No duplicates, submit directly
      submitIncident();
    }
  };

  const submitIncident = () => {
    createMutation.mutate({
      ...formData,
      timestamp: new Date(formData.timestamp).toISOString(),
    });
  };

  const handleConfirmSubmit = () => {
    setShowDuplicateModal(false);
    submitIncident();
  };

  const handleCancelSubmit = () => {
    setShowDuplicateModal(false);
    setSimilarIncidents([]);
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
    <div className="max-w-3xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Report Waste Incident</h1>
          <p className="mt-2 text-gray-600">
            Fill in the details below. Our AI will automatically classify the waste type and detect similar incidents.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Description *
            </label>
            <textarea
              id="description"
              rows={4}
              className={`w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent ${
                errors.description ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Describe the waste incident in detail..."
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              required
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-600 flex items-center">
                <AlertCircle className="h-4 w-4 mr-1" />
                {errors.description}
              </p>
            )}
          </div>

          {/* Location */}
          <div>
            <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
              Location *
            </label>
            <input
              id="location"
              type="text"
              className={`w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent ${
                errors.location ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="e.g., 123 Main Street, City Center, Downtown Park"
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              required
            />
            {errors.location && (
              <p className="mt-1 text-sm text-red-600 flex items-center">
                <AlertCircle className="h-4 w-4 mr-1" />
                {errors.location}
              </p>
            )}
          </div>

          {/* Date and Time */}
          <div>
            <label htmlFor="timestamp" className="block text-sm font-medium text-gray-700 mb-2">
              Date and Time *
            </label>
            <input
              id="timestamp"
              type="datetime-local"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent"
              value={formData.timestamp}
              onChange={(e) => setFormData({ ...formData, timestamp: e.target.value })}
              required
            />
          </div>

          {/* Coordinates (Optional) */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="latitude" className="block text-sm font-medium text-gray-700 mb-2">
                Latitude (Optional)
              </label>
              <input
                id="latitude"
                type="number"
                step="any"
                className={`w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent ${
                  errors.latitude ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="e.g., 40.7128"
                value={formData.latitude || ''}
                onChange={(e) =>
                  setFormData({ ...formData, latitude: e.target.value ? parseFloat(e.target.value) : undefined })
                }
              />
              {errors.latitude && (
                <p className="mt-1 text-sm text-red-600">{errors.latitude}</p>
              )}
            </div>

            <div>
              <label htmlFor="longitude" className="block text-sm font-medium text-gray-700 mb-2">
                Longitude (Optional)
              </label>
              <input
                id="longitude"
                type="number"
                step="any"
                className={`w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent ${
                  errors.longitude ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="e.g., -74.0060"
                value={formData.longitude || ''}
                onChange={(e) =>
                  setFormData({ ...formData, longitude: e.target.value ? parseFloat(e.target.value) : undefined })
                }
              />
              {errors.longitude && (
                <p className="mt-1 text-sm text-red-600">{errors.longitude}</p>
              )}
            </div>
          </div>

          {/* AI Info Box */}
          {/* <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-green-800">AI-Powered Analysis</h3>
                <div className="mt-2 text-sm text-green-700">
                  <ul className="list-disc list-inside space-y-1">
                    <li>Automatic waste type classification</li>
                    <li>Keyword extraction from description</li>
                    <li>Similar incident detection</li>
                    <li>Real-time analytics update</li>
                  </ul>
                </div>
              </div>
            </div>
          </div> */}

          {/* Submit Button */}
          <div className="flex items-center justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate('/incidents')}
              className="px-6 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending || isCheckingDuplicates}
              className="flex items-center px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="mr-2 h-4 w-4" />
              {isCheckingDuplicates 
                ? 'Checking for duplicates...' 
                : createMutation.isPending 
                ? 'Submitting...' 
                : 'Submit Report'}
            </button>
          </div>
        </form>
      </div>

      {/* Duplicate Detection Modal */}
      {showDuplicateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="bg-yellow-50 border-b border-yellow-200 p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="h-8 w-8 text-yellow-600" />
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">
                      Similar Incidents Detected
                    </h2>
                    <p className="mt-1 text-sm text-gray-600">
                      We found {similarIncidents.length} similar incident{similarIncidents.length !== 1 ? 's' : ''} already reported. 
                      Please review to avoid duplicates.
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleCancelSubmit}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
            </div>

            {/* Your Report */}
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Your Report:</h3>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-gray-900 mb-2">{formData.description}</p>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <span>📍 {formData.location}</span>
                  <span>🕒 {format(new Date(formData.timestamp), 'MMM dd, yyyy HH:mm')}</span>
                </div>
              </div>
            </div>

            {/* Similar Incidents */}
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Similar Incidents Found:
              </h3>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {similarIncidents.map((incident) => (
                  <div
                    key={incident.id}
                    className="bg-gray-50 border border-gray-200 rounded-lg p-4"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <p className="text-gray-900 mb-2">{incident.description}</p>
                        
                        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                          <span className="flex items-center gap-1">
                            📍 {incident.location}
                          </span>
                          <span>
                            🕒 {format(new Date(incident.timestamp), 'MMM dd, yyyy HH:mm')}
                          </span>
                        </div>

                        {incident.keywords && incident.keywords.length > 0 && (
                          <div className="mt-3 flex flex-wrap gap-2">
                            {incident.keywords.slice(0, 5).map((keyword, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-1 bg-white text-gray-700 text-xs rounded border border-gray-300"
                              >
                                {keyword}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      {incident.waste_type && (
                        <div className="flex-shrink-0">
                          <span
                            className={`px-3 py-1 text-xs font-semibold rounded-full ${getWasteTypeColor(
                              incident.waste_type
                            )}`}
                          >
                            {incident.waste_type}
                            {incident.waste_type_confidence && (
                              <span className="ml-1">
                                ({Math.round(incident.waste_type_confidence * 100)}%)
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

            {/* Modal Actions */}
            <div className="bg-gray-50 border-t border-gray-200 p-6">
              <div className="flex items-center justify-between gap-4">
                <p className="text-sm text-gray-600">
                  Are you sure this is a new incident and not a duplicate?
                </p>
                <div className="flex items-center gap-3">
                  <button
                    onClick={handleCancelSubmit}
                    className="px-6 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100"
                  >
                    Don't Submit
                  </button>
                  <button
                    onClick={handleConfirmSubmit}
                    className="px-6 py-2 bg-green-600 text-white rounded-md text-sm font-medium hover:bg-green-700"
                  >
                    Submit Anyway
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
