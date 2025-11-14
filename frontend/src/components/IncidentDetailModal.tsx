import { format } from 'date-fns';
import { MapPin, Calendar, Tag, Hash } from 'lucide-react';
import Modal from './Modal';
import type { Incident } from '../api/incidents';

interface IncidentDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  incident: Incident | null;
}

export default function IncidentDetailModal({
  isOpen,
  onClose,
  incident,
}: IncidentDetailModalProps) {
  if (!incident) return null;

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
    <Modal isOpen={isOpen} onClose={onClose} title="Incident Details" size="lg">
      <div className="space-y-6">
        {/* Timestamp */}
        <div className="flex items-start gap-3">
          <Calendar className="h-5 w-5 text-gray-400 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-gray-500">Reported At</p>
            <p className="text-base text-gray-900">
              {format(new Date(incident.timestamp), 'MMMM dd, yyyy HH:mm:ss')}
            </p>
          </div>
        </div>

        {/* Location */}
        <div className="flex items-start gap-3">
          <MapPin className="h-5 w-5 text-gray-400 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-gray-500">Location</p>
            <p className="text-base text-gray-900">{incident.location}</p>
            {incident.latitude && incident.longitude && (
              <p className="text-sm text-gray-500 mt-1">
                Coordinates: {incident.latitude.toFixed(6)}, {incident.longitude.toFixed(6)}
              </p>
            )}
          </div>
        </div>

        {/* Description */}
        <div>
          <p className="text-sm font-medium text-gray-500 mb-2">Description</p>
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <p className="text-gray-900 leading-relaxed">{incident.description}</p>
          </div>
        </div>

        {/* Waste Type Classification */}
        <div className="flex items-start gap-3">
          <Tag className="h-5 w-5 text-gray-400 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-500 mb-2">Waste Type (AI Classification)</p>
            <div className="flex items-center gap-2">
              <span
                className={`px-3 py-1.5 text-sm font-semibold rounded-full ${getWasteTypeColor(
                  incident.waste_type
                )}`}
              >
                {incident.waste_type || 'Not classified'}
              </span>
              {incident.waste_type_confidence && (
                <span className="text-sm text-gray-600">
                  Confidence: {Math.round(incident.waste_type_confidence * 100)}%
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Keywords */}
        {incident.keywords && incident.keywords.length > 0 && (
          <div className="flex items-start gap-3">
            <Hash className="h-5 w-5 text-gray-400 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-500 mb-2">Extracted Keywords</p>
              <div className="flex flex-wrap gap-2">
                {incident.keywords.map((keyword, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Metadata */}
        <div className="pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            Incident ID: <span className="font-mono">{incident.id}</span>
          </p>
          {incident.created_at && (
            <p className="text-xs text-gray-500 mt-1">
              Created: {format(new Date(incident.created_at), 'MMM dd, yyyy HH:mm:ss')}
            </p>
          )}
        </div>

        {/* Close Button */}
        <div className="flex justify-end pt-4">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            Close
          </button>
        </div>
      </div>
    </Modal>
  );
}
