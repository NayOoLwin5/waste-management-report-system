import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, AlertTriangle, MapPin, Calendar } from 'lucide-react';
import { analyticsAPI } from '../api/analytics';

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

export default function Dashboard() {
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['summary'],
    queryFn: () => analyticsAPI.getSummary(),
  });

  const { data: timeSeries, isLoading: timeSeriesLoading } = useQuery({
    queryKey: ['timeSeries'],
    queryFn: () => analyticsAPI.getTimeSeries(30),
  });

  const { data: anomalies } = useQuery({
    queryKey: ['anomalies'],
    queryFn: () => analyticsAPI.getAnomalies(),
  });

  const { data: keywords } = useQuery({
    queryKey: ['keywords'],
    queryFn: () => analyticsAPI.getKeywords(15),
  });

  const { data: adminSummary } = useQuery({
    queryKey: ['adminSummary'],
    queryFn: () => analyticsAPI.getAdminSummary(7),
  });

  // Transform waste type distribution for pie chart
  const wasteTypeData = summary?.waste_type_distribution
    ? Object.entries(summary.waste_type_distribution).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  if (summaryLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        {/* <div className="text-sm text-gray-500">
          <Calendar className="inline h-4 w-4 mr-1" />
          Real-time Analytics
        </div> */}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Incidents</p>
              <p className="text-3xl font-bold text-gray-900">{summary?.total_incidents || 0}</p>
            </div>
            <div className="bg-green-100 rounded-full p-3">
              <AlertTriangle className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Last 7 Days</p>
              <p className="text-3xl font-bold text-gray-900">{summary?.recent_incidents_7d || 0}</p>
            </div>
            <div className="bg-blue-100 rounded-full p-3">
              <TrendingUp className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Waste Types</p>
              <p className="text-3xl font-bold text-gray-900">{wasteTypeData.length}</p>
            </div>
            <div className="bg-purple-100 rounded-full p-3">
              <BarChart className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Anomalies</p>
              <p className="text-3xl font-bold text-red-600">{anomalies?.length || 0}</p>
            </div>
            <div className="bg-red-100 rounded-full p-3">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
          </div>
        </div>
      </div>

      {/* AI-Generated Insights */}
      {adminSummary && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg shadow-lg p-6 border border-blue-200">
          <div className="flex items-center gap-2 mb-4">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-full p-2">
              <TrendingUp className="h-5 w-5 text-white" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">AI Summary Insights</h2>
            {/* <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded-full">
              OFFLINE AI
            </span> */}
          </div>

          {/* Executive Summary */}
          <div className="bg-white rounded-lg p-4 mb-4 border border-gray-200">
            <h3 className="text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">
              Executive Summary
            </h3>
            <p className="text-gray-800 leading-relaxed">{adminSummary.executive_summary}</p>
          </div>

          {/* Insights Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {adminSummary.insights.map((insight, index) => {
              const severityColors = {
                error: 'border-red-300 bg-red-50',
                warning: 'border-yellow-300 bg-yellow-50',
                success: 'border-green-300 bg-green-50',
                info: 'border-blue-300 bg-blue-50',
              };

              const iconColors = {
                error: 'text-red-600',
                warning: 'text-yellow-600',
                success: 'text-green-600',
                info: 'text-blue-600',
              };

              return (
                <div
                  key={index}
                  className={`p-4 rounded-lg border-2 ${
                    severityColors[insight.severity as keyof typeof severityColors] || severityColors.info
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <AlertTriangle
                      className={`h-4 w-4 flex-shrink-0 mt-0.5 ${
                        iconColors[insight.severity as keyof typeof iconColors] || iconColors.info
                      }`}
                    />
                    <p className="text-sm text-gray-800">{insight.text}</p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Trends Summary */}
          {(adminSummary.trends.rising_trends.length > 0 || adminSummary.trends.falling_trends.length > 0) && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Rising Trends */}
              {adminSummary.trends.rising_trends.length > 0 && (
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <h4 className="text-sm font-semibold text-red-700 mb-2 flex items-center gap-1">
                    <span>📈</span> Rising Trends
                  </h4>
                  <div className="space-y-2">
                    {adminSummary.trends.rising_trends.slice(0, 3).map((trend, idx) => (
                      <div key={idx} className="flex items-center justify-between text-sm">
                        <span className="text-gray-700 capitalize">{trend.waste_type}</span>
                        <span className="font-semibold text-red-600">+{trend.change_percentage}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Falling Trends */}
              {adminSummary.trends.falling_trends.length > 0 && (
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <h4 className="text-sm font-semibold text-green-700 mb-2 flex items-center gap-1">
                    <span>📉</span> Declining Trends
                  </h4>
                  <div className="space-y-2">
                    {adminSummary.trends.falling_trends.slice(0, 3).map((trend, idx) => (
                      <div key={idx} className="flex items-center justify-between text-sm">
                        <span className="text-gray-700 capitalize">{trend.waste_type}</span>
                        <span className="font-semibold text-green-600">{trend.change_percentage}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="mt-4 text-xs text-gray-500 text-right">
            Generated at {new Date(adminSummary.generated_at).toLocaleString()} • Period: {adminSummary.period_days} days
          </div>
        </div>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Time Series Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Incidents Over Time (30 Days)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timeSeries || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="count" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Waste Type Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Waste Type Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={wasteTypeData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {wasteTypeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Locations and Keywords */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Locations */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <MapPin className="mr-2 h-5 w-5" />
            Top Locations
          </h2>
          <div className="space-y-3">
            {summary?.top_locations?.slice(0, 5).map((loc, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm text-gray-700">{loc.location}</span>
                <span className="text-sm font-medium text-gray-900">{loc.count} incidents</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Keywords */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Common Keywords</h2>
          <div className="flex flex-wrap gap-2">
            {keywords?.keywords?.slice(0, 15).map((kw: { keyword: string; count: number }, index: number) => (
              <span
                key={index}
                className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium"
              >
                {kw.keyword} ({kw.count})
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Anomalies */}
      {anomalies && anomalies.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <AlertTriangle className="mr-2 h-5 w-5 text-red-600" />
            Detected Anomalies
          </h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Location
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Incident Count
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Severity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Threshold
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {anomalies.map((anomaly, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {anomaly.location}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {anomaly.count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          anomaly.severity === 'high'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {anomaly.severity.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {anomaly.threshold.toFixed(1)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
