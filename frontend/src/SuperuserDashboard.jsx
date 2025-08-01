import React, { useState, useEffect } from 'react';
import axios from 'axios';
// Importação CORRETA dos ícones diretamente da biblioteca 'lucide-react'
import { User, Lock, ArrowRight } from 'lucide-react';

// Use a variável de ambiente definida no docker-compose.yml para a URL base da API.
// Isso garante que a URL esteja correta tanto para o ambiente de desenvolvimento local
// quanto para o contêiner do Docker.
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function SuperuserDashboard() {
  // Estado para armazenar as credenciais de login
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  // Estado para armazenar o token de autenticação
  const [authToken, setAuthToken] = useState(null);
  // Estado para exibir mensagens de status, como sucesso ou erro
  const [message, setMessage] = useState('');
  // Estado para controlar o estado de carregamento durante a requisição de login
  const [isLoading, setIsLoading] = useState(false);

  // Efeito para carregar o token de acesso do armazenamento local (localStorage)
  // ao carregar o componente, mantendo o usuário logado entre recarregamentos.
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setAuthToken(token);
    }
  }, []);

  /**
   * Função para lidar com a mudança nos campos de entrada do formulário.
   * Atualiza o estado das credenciais com o novo valor.
   * @param {object} e O evento de mudança do input.
   */
  const handleChange = (e) => {
    setCredentials({ ...credentials, [e.target.name]: e.target.value });
  };

  /**
   * Função assíncrona para lidar com o envio do formulário de login.
   * Envia uma requisição POST para o endpoint de autenticação do backend.
   * @param {object} e O evento de envio do formulário.
   */
  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true); // Ativa o estado de carregamento
    setMessage(''); // Limpa mensagens anteriores

    try {
      // Faz a requisição de login para o endpoint público de obtenção de token.
      // O `API_BASE_URL` agora é a URL acessível pelo navegador.
      const response = await axios.post(`${API_BASE_URL}/api/auth/token/`, credentials);
      const { access, refresh } = response.data;
      
      // Armazena os tokens no estado e no localStorage
      setAuthToken(access);
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      
      setMessage('Login realizado com sucesso!');
      console.log('Login bem-sucedido. Token de acesso:', access);
    } catch (error) {
      console.error('Erro no login:', error);
      if (error.response) {
        // Se a resposta da API tiver um status de erro
        if (error.response.status === 401) {
          setMessage('Credenciais inválidas. Por favor, tente novamente.');
        } else {
          setMessage(`Erro de autenticação: ${error.response.status}. Verifique as credenciais.`);
        }
      } else if (error.request) {
        // A requisição foi feita, mas não houve resposta
        setMessage('Erro de conexão com o servidor. O backend pode não estar respondendo.');
      } else {
        // Outros erros
        setMessage('Ocorreu um erro inesperado. Verifique o console para mais detalhes.');
      }
    } finally {
      setIsLoading(false); // Desativa o estado de carregamento
    }
  };

  /**
   * Função para realizar o logout do usuário.
   * Remove os tokens do estado e do localStorage.
   */
  const handleLogout = () => {
    setAuthToken(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setMessage('Sessão encerrada com sucesso.');
  };

  // Se o usuário estiver autenticado, renderiza o painel de superusuário
  if (authToken) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
        <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md text-center">
          <h2 className="text-2xl font-bold text-gray-900">
            Bem-vindo, Superusuário!
          </h2>
          <p className="text-gray-600">
            Você está logado com sucesso.
          </p>
          <button
            onClick={handleLogout}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            Sair
          </button>
        </div>
      </div>
    );
  }

  // Se o usuário não estiver autenticado, renderiza o formulário de login
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center text-gray-900">
          Login do Superusuário
        </h2>
        {message && (
          <div className={`p-3 rounded-md text-center font-medium ${message.includes('sucesso') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
            {message}
          </div>
        )}
        <form className="space-y-6" onSubmit={handleLogin}>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              <span className="flex items-center">
                {/* Uso CORRETO do componente de ícone */}
                <User className="mr-2" size={16} /> Usuário
              </span>
            </label>
            <input
              type="text"
              name="username"
              value={credentials.username}
              onChange={handleChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              <span className="flex items-center">
                {/* Uso CORRETO do componente de ícone */}
                <Lock className="mr-2" size={16} /> Senha
              </span>
            </label>
            <input
              type="password"
              name="password"
              value={credentials.password}
              onChange={handleChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              required
            />
          </div>
          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {isLoading ? 'Entrando...' : (
                <span className="flex items-center">
                  Entrar {/* Uso CORRETO do componente de ícone */}
                  <ArrowRight className="ml-2" size={16} />
                </span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default SuperuserDashboard;
