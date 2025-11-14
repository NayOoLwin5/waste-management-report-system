const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Incidents
  incidents: `${API_BASE_URL}/api/incidents`,
  incidentById: (id: string) => `${API_BASE_URL}/api/incidents/${id}`,
  
  // Analytics
  analyticsBase: `${API_BASE_URL}/api/analytics`,
  analyticsSummary: `${API_BASE_URL}/api/analytics/summary`,
  analyticsTimeSeries: `${API_BASE_URL}/api/analytics/time-series`,
  analyticsWasteTypeTrends: `${API_BASE_URL}/api/analytics/waste-type-trends`,
  analyticsHeatmap: `${API_BASE_URL}/api/analytics/heatmap`,
  analyticsAnomalies: `${API_BASE_URL}/api/analytics/anomalies`,
  analyticsKeywords: `${API_BASE_URL}/api/analytics/keywords`,
  analyticsTrends: `${API_BASE_URL}/api/analytics/trends`,
  analyticsAdminSummary: `${API_BASE_URL}/api/analytics/admin-summary`,
  
  // AI
  aiClassify: `${API_BASE_URL}/api/ai/classify`,
  aiExtractKeywords: `${API_BASE_URL}/api/ai/extract-keywords`,
  aiSimilarIncidents: `${API_BASE_URL}/api/ai/similar-incidents`,
};

export default API_BASE_URL;
