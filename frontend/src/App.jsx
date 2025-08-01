// frontend/src/App.jsx

import React from 'react';
import SuperuserDashboard from './components/SuperuserDashboard';

function App() {
  return (
    <div className="min-h-screen bg-gray-800 text-white">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Renderiza o painel do superusuário */}
        <SuperuserDashboard />
      </div>
    </div>
  );
}

export default App;