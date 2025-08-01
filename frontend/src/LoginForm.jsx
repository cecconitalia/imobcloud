import React, { useState } from 'react';
import axios from 'axios';
import { User, Lock, ArrowRight } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function LoginForm({ onLoginSuccess }) {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    setCredentials({ ...credentials, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/token/`, credentials);
      const { access, refresh } = response.data;
      
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      
      setMessage('Login realizado com sucesso!');
      console.log('Login bem-sucedido. Token de acesso:', access);
      
      if (onLoginSuccess) {
        onLoginSuccess(access);
      }

    } catch (error) {
      console.error('Erro no login:', error);
      if (error.response) {
        if (error.response.status === 401) {
          setMessage('Credenciais inválidas. Por favor, tente novamente.');
        } else {
          setMessage(`Erro de autenticação: ${error.response.status}. Verifique as credenciais.`);
        }
      } else if (error.request) {
        setMessage('Erro de conexão com o servidor. O backend pode não estar respondendo.');
      } else {
        setMessage('Ocorreu um erro inesperado. Verifique o console para mais detalhes.');
        }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4 font-sans">
      <div className="w-full max-w-sm p-8 bg-white rounded-2xl shadow-xl space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-gray-900">
            Acessar sua conta
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Bem-vindo de volta! Por favor, insira os seus dados.
          </p>
        </div>

        {message && (
          <div className={`p-4 rounded-xl text-center font-medium transition-opacity duration-300 ${message.includes('sucesso') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
            {message}
          </div>
        )}

        <form className="space-y-6" onSubmit={handleSubmit}>
          <div className="relative">
            <User className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              name="username"
              value={credentials.username}
              onChange={handleChange}
              className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 ease-in-out"
              placeholder="Nome de Usuário"
              required
            />
          </div>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="password"
              name="password"
              value={credentials.password}
              onChange={handleChange}
              className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 ease-in-out"
              placeholder="Palavra-passe"
              required
            />
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="remember_me"
                name="remember_me"
                type="checkbox"
                className="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              />
              <label htmlFor="remember_me" className="ml-2 block text-sm text-gray-900">
                Lembrar-me
              </label>
            </div>
            <a href="#" className="text-sm font-medium text-indigo-600 hover:text-indigo-500 transition duration-150 ease-in-out">
              Esqueceu a palavra-passe?
            </a>
          </div>
          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center px-4 py-3 border border-transparent rounded-xl shadow-sm text-base font-bold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition duration-150 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'A entrar...' : (
                <>
                  Entrar
                  <ArrowRight size={20} className="ml-2" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default LoginForm;
