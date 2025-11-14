import axios from 'axios';
import { API_ENDPOINTS } from '../config/api';

export interface SummaryStats {
  total_incidents: number;
  recent_incidents_7d: number;
  waste_type_distribution: Record<string, number>;
  top_locations: Array<{ location: string; count: number }>;
  period: {
    start_date?: string;
    end_date?: string;
  };
}

export interface TimeSeriesData {
  period: string;
  count: number;
}

export interface Anomaly {
  location: string;
  count: number;
  mean: number;
  threshold: number;
  severity: string;
}

export interface TrendData {
  waste_type: string;
  current_count: number;
  previous_count: number;
  change_percentage: number;
  change_absolute: number;
  trend: string;
  severity?: string;
}

export interface AdminInsight {
  type: string;
  severity: string;
  text: string;
  data: any;
}

export interface AdminSummary {
  generated_at: string;
  period_days: number;
  executive_summary: string;
  insights: AdminInsight[];
  statistics: SummaryStats;
  trends: {
    rising_trends: TrendData[];
    falling_trends: TrendData[];
    stable_trends: TrendData[];
    new_waste_types: any[];
    spikes: any[];
    summary: {
      total_waste_types: number;
      trending_up: number;
      trending_down: number;
      stable: number;
    };
  };
  anomalies: Anomaly[];
}

export const analyticsAPI = {
  getSummary: async (): Promise<SummaryStats> => {
    const response = await axios.get<SummaryStats>(API_ENDPOINTS.analyticsSummary);
    return response.data;
  },

  getTimeSeries: async (days: number = 30): Promise<TimeSeriesData[]> => {
    const response = await axios.get<{ data: TimeSeriesData[] }>(
      API_ENDPOINTS.analyticsTimeSeries,
      { params: { days } }
    );
    return response.data.data;
  },

  getWasteTypeTrends: async (days: number = 30) => {
    const response = await axios.get(API_ENDPOINTS.analyticsWasteTypeTrends, {
      params: { days },
    });
    return response.data;
  },

  getAnomalies: async (): Promise<Anomaly[]> => {
    const response = await axios.get<{ anomalies: Anomaly[] }>(
      API_ENDPOINTS.analyticsAnomalies
    );
    return response.data.anomalies;
  },

  getKeywords: async (limit: number = 20) => {
    const response = await axios.get(API_ENDPOINTS.analyticsKeywords, {
      params: { limit },
    });
    return response.data;
  },

  getTrends: async (days: number = 30) => {
    const response = await axios.get(API_ENDPOINTS.analyticsTrends, {
      params: { days },
    });
    return response.data;
  },

  getAdminSummary: async (days: number = 7): Promise<AdminSummary> => {
    const response = await axios.get<AdminSummary>(
      API_ENDPOINTS.analyticsAdminSummary,
      { params: { days } }
    );
    return response.data;
  },
};
