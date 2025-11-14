import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Trash2, BarChart3, AlertTriangle, Sparkles } from 'lucide-react';
import IncidentList from './pages/IncidentList';
import IncidentForm from './pages/IncidentForm';
import Dashboard from './pages/Dashboard';
import SemanticSearch from './pages/SemanticSearch';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <Link to="/" className="flex-shrink-0 flex items-center cursor-pointer hover:opacity-80 transition-opacity">
                  <Trash2 className="h-8 w-8 text-green-600" />
                  <span className="ml-2 text-xl font-bold text-gray-900">GEPP</span>
                </Link>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  <Link
                    to="/"
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900"
                  >
                    <BarChart3 className="mr-2 h-4 w-4" />
                    Dashboard
                  </Link>
                  <Link
                    to="/incidents"
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900"
                  >
                    <AlertTriangle className="mr-2 h-4 w-4" />
                    Incidents
                  </Link>
                  <Link
                    to="/search"
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900"
                  >
                    <Sparkles className="mr-2 h-4 w-4" />
                    AI Search
                  </Link>
                  <Link
                    to="/report"
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900"
                  >
                    Report Incident
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/incidents" element={<IncidentList />} />
            <Route path="/search" element={<SemanticSearch />} />
            <Route path="/report" element={<IncidentForm />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t mt-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <p className="text-center text-sm text-gray-500">
              GEPP - Waste Incident Reporting Platform.
            </p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
