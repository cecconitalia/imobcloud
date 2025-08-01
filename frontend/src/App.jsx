// frontend/src/App.jsx

import React, { useState, useEffect, Suspense, lazy } from 'react';

// Use lazy loading para importar os componentes.
// Isso ajuda a isolar erros de importação e melhora o desempenho.
const SuperuserDashboard = lazy(() => import('./SuperuserDashboard.jsx'));
const LoginForm = lazy(() => import('./LoginForm.jsx'));

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Verifica se o token de acesso já existe no localStorage
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsLoggedIn(true);
    }
    setLoading(false);
  }, []);

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
  };
  
  const handleLogout = () => {
    setIsLoggedIn(false);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        Carregando...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
      <Suspense fallback={<div>Carregando...</div>}>
        {isLoggedIn ? (
          <SuperuserDashboard onLogout={handleLogout} />
        ) : (
          <LoginForm onLoginSuccess={handleLoginSuccess} />
        )}
      </Suspense>
    </div>
  );
}

export default App;
