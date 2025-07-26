// Caminho: imobcloud/frontend/app/admin/imobiliarias/page.js (ATUALIZADO)

"use client";

import { useState, useEffect } from 'react';

export default function GerenciarImobiliariasPage() {
  const [imobiliarias, setImobiliarias] = useState([]);
  const [nome, setNome] = useState('');
  const [slug, setSlug] = useState('');
  const [mensagem, setMensagem] = useState('');

  // --- ALTERAÇÃO AQUI ---
  // A função agora obtém o token do localStorage antes de fazer a chamada.
  const fetchImobiliarias = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setMensagem('Acesso negado. Por favor, faça login.');
        return;
      }

      const res = await fetch('http://localhost:8000/imobiliarias/', {
        headers: {
          // Envia o token no cabeçalho de autorização
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        throw new Error('Falha ao buscar imobiliárias. Verifique se está autenticado.');
      }
      const data = await res.json();
      setImobiliarias(data);
    } catch (error) {
      console.error(error);
      setMensagem(error.message);
    }
  };

  useEffect(() => {
    fetchImobiliarias();
  }, []);

  // --- ALTERAÇÃO AQUI ---
  // A função de criar também precisa de enviar o token.
  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensagem('A criar imobiliária...');
    
    const token = localStorage.getItem('access_token');
    if (!token) {
      setMensagem('Acesso negado. Por favor, faça login.');
      return;
    }

    try {
      const res = await fetch('http://localhost:8000/imobiliarias/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Envia o token no cabeçalho de autorização
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ nome, slug }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Falha ao criar imobiliária');
      }

      setMensagem('Imobiliária criada com sucesso!');
      setNome('');
      setSlug('');
      fetchImobiliarias();
    } catch (error) {
      console.error(error);
      setMensagem(error.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Gerir Imobiliárias</h1>

        <div className="bg-white p-6 rounded-lg shadow-md mb-8">
          <h2 className="text-2xl font-semibold mb-4">Criar Nova Imobiliária</h2>
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor="nome" className="block text-gray-700 font-medium mb-2">Nome da Imobiliária</label>
              <input
                type="text" id="nome" value={nome} onChange={(e) => setNome(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div className="mb-4">
              <label htmlFor="slug" className="block text-gray-700 font-medium mb-2">Slug (identificador na URL, ex: minha-imob)</label>
              <input
                type="text" id="slug" value={slug} onChange={(e) => setSlug(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Criar
            </button>
          </form>
          {mensagem && <p className="mt-4 text-center text-gray-600">{mensagem}</p>}
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Imobiliárias Cadastradas</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-4">ID</th>
                  <th className="text-left py-2 px-4">Nome</th>
                  <th className="text-left py-2 px-4">Slug</th>
                </tr>
              </thead>
              <tbody>
                {imobiliarias.map((imob) => (
                  <tr key={imob.id} className="border-b hover:bg-gray-50">
                    <td className="py-2 px-4">{imob.id}</td>
                    <td className="py-2 px-4">{imob.nome}</td>
                    <td className="py-2 px-4">{imob.slug}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {imobiliarias.length === 0 && <p className="text-center py-4">Nenhuma imobiliária encontrada.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
