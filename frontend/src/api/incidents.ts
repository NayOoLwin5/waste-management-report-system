import axios from 'axios';
import { API_ENDPOINTS } from '../config/api';

export interface Incident {
  id: string;
  description: string;
  timestamp: string;
  location: string;
  latitude?: number;
  longitude?: number;
  waste_type?: string;
  waste_type_confidence?: number;
  keywords?: string[];
  similar_incident_ids?: string[];
  created_at: string;
  updated_at: string;
}

export interface IncidentCreate {
  description: string;
  timestamp: string;
  location: string;
  latitude?: number;
  longitude?: number;
}

export interface IncidentListResponse {
  items: Incident[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export const incidentAPI = {
  // Create a new incident
  create: async (data: IncidentCreate): Promise<Incident> => {
    const response = await axios.post<Incident>(API_ENDPOINTS.incidents, data);
    return response.data;
  },

  // Get all incidents with pagination
  list: async (params?: {
    page?: number;
    page_size?: number;
    waste_type?: string;
    location?: string;
  }): Promise<IncidentListResponse> => {
    const response = await axios.get<IncidentListResponse>(API_ENDPOINTS.incidents, { params });
    return response.data;
  },

  // Get single incident
  get: async (id: string): Promise<Incident> => {
    const response = await axios.get<Incident>(API_ENDPOINTS.incidentById(id));
    return response.data;
  },

  // Delete incident
  delete: async (id: string): Promise<void> => {
    await axios.delete(API_ENDPOINTS.incidentById(id));
  },
};
