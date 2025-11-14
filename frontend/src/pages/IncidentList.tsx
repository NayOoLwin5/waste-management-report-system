import { useState, useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import { Trash2, Eye, Filter } from 'lucide-react';
import { incidentAPI, type Incident } from '../api/incidents';
import ConfirmDialog from '../components/ConfirmDialog';
import IncidentDetailModal from '../components/IncidentDetailModal';

export default function IncidentList() {
  const [page, setPage] = useState(1);
  
  // Input values (updated immediately on typing)
  const [locationInput, setLocationInput] = useState<string>('');
  const [wasteTypeInput, setWasteTypeInput] = useState<string>('');
  
  // Debounced filter values (used for API calls)
  const [location, setLocation] = useState<string>('');
  const [wasteType, setWasteType] = useState<string>('');
  
  // Modal states
  const [deleteConfirm, setDeleteConfirm] = useState<{
    isOpen: boolean;
    incident: Incident | null;
  }>({ isOpen: false, incident: null });
  
  const [detailModal, setDetailModal] = useState<{
    isOpen: boolean;
    incident: Incident | null;
  }>({ isOpen: false, incident: null });
  
  // Refs to preserve input focus
  const locationInputRef = useRef<HTMLInputElement>(null);
  const wasteTypeInputRef = useRef<HTMLInputElement>(null);

  // Debounce filter updates (500ms delay)
  useEffect(() => {
    const timer = setTimeout(() => {
      setLocation(locationInput);
      setWasteType(wasteTypeInput);
      setPage(1);
    }, 500);

    return () => clearTimeout(timer);
  }, [locationInput, wasteTypeInput]);

  const { data, isLoading, isFetching, refetch } = useQuery({
    queryKey: ['incidents', page, wasteType, location],
    queryFn: () =>
      incidentAPI.list({
        page,
        page_size: 20,
        waste_type: wasteType || undefined,
        location: location || undefined,
      }),
    placeholderData: (previousData) => previousData, // Keep previous data while fetching new data
  });

  const handleDelete = async (id: string) => {
    try {
      await incidentAPI.delete(id);
      refetch();
      setDeleteConfirm({ isOpen: false, incident: null });
    } catch (error) {
      console.error('Failed to delete incident:', error);
      alert('Failed to delete incident');
    }
  };

  const openDeleteConfirm = (incident: Incident) => {
    setDeleteConfirm({ isOpen: true, incident });
  };

  const openDetailModal = (incident: Incident) => {
    setDetailModal({ isOpen: true, incident });
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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Loading incidents...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Incidents</h1>
        <span className="text-sm text-gray-500">{data?.total || 0} total incidents</span>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center gap-4">
          <Filter className="h-5 w-5 text-gray-400" />
          <input
            ref={locationInputRef}
            type="text"
            placeholder="Filter by location..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent"
            value={locationInput}
            onChange={(e) => setLocationInput(e.target.value)}
          />
          <input
            ref={wasteTypeInputRef}
            type="text"
            placeholder="Filter by waste type..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent"
            value={wasteTypeInput}
            onChange={(e) => setWasteTypeInput(e.target.value)}
          />
        </div>
        {(locationInput !== location || wasteTypeInput !== wasteType) && (
          <div className="mt-2 text-xs text-gray-500 text-center">
            Filtering will apply after you stop typing...
          </div>
        )}
      </div>

      {/* Incidents Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden relative">
        {/* Loading overlay - only shows when fetching new data */}
        {isFetching && (
          <div className="absolute inset-0 bg-white/80 backdrop-blur-sm z-10 flex items-center justify-center">
            <div className="flex items-center gap-2">
              <div className="animate-spin h-6 w-6 border-3 border-green-500 border-t-transparent rounded-full"></div>
              <span className="text-gray-600 font-medium">Loading...</span>
            </div>
          </div>
        )}
        
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date/Time
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Description
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Location
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Waste Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Keywords
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data?.items.map((incident: Incident) => (
              <tr key={incident.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {format(new Date(incident.timestamp), 'MMM dd, yyyy HH:mm')}
                </td>
                <td className="px-6 py-4 text-sm text-gray-900 max-w-md truncate">
                  {incident.description}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {incident.location}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`px-2 py-1 text-xs font-semibold rounded-full ${getWasteTypeColor(
                      incident.waste_type
                    )}`}
                  >
                    {incident.waste_type || 'N/A'}
                    {incident.waste_type_confidence && (
                      <span className="ml-1 text-xs">
                        ({Math.round(incident.waste_type_confidence * 100)}%)
                      </span>
                    )}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {incident.keywords?.slice(0, 3).join(', ') || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                  <button
                    onClick={() => openDetailModal(incident)}
                    className="text-green-600 hover:text-green-900"
                    title="View details"
                  >
                    <Eye className="h-4 w-4 inline" />
                  </button>
                  <button
                    onClick={() => openDeleteConfirm(incident)}
                    className="text-red-600 hover:text-red-900"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4 inline" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between bg-white px-4 py-3 rounded-lg shadow">
        <div className="text-sm text-gray-700">
          Showing page {data?.page} of {data?.total_pages}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={page === data?.total_pages}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <ConfirmDialog
        isOpen={deleteConfirm.isOpen}
        onClose={() => setDeleteConfirm({ isOpen: false, incident: null })}
        onConfirm={() => deleteConfirm.incident && handleDelete(deleteConfirm.incident.id)}
        title="Delete Incident"
        message={`Are you sure you want to delete this incident? This action cannot be undone.${
          deleteConfirm.incident ? `\n\nLocation: ${deleteConfirm.incident.location}` : ''
        }`}
        confirmText="Delete"
        cancelText="Cancel"
        type="danger"
      />

      {/* Incident Detail Modal */}
      <IncidentDetailModal
        isOpen={detailModal.isOpen}
        onClose={() => setDetailModal({ isOpen: false, incident: null })}
        incident={detailModal.incident}
      />
    </div>
  );
}
