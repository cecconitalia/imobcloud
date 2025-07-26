// Caminho: imobcloud/frontend/app/admin/imoveis/page.js (ATUALIZADO)

"use client";

import { useState, useEffect } from 'react';

// Componente reutilizável para um campo do formulário
const FormInput = ({ id, label, type = 'text', value, onChange, required = false, step }) => (
  <div className="mb-4">
    <label htmlFor={id} className="block text-gray-700 font-medium mb-2">{label}</label>
    <input
      type={type} id={id} name={id} value={value} onChange={onChange}
      required={required} step={step}
      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
  </div>
);

export default function GerenciarImoveisPage() {
  const [formData, setFormData] = useState({
    titulo: '', descricao: '', preco: '', quartos: '', banheiros: '', area: '', tipo: 'apartamento',
  });
  const [imobiliarias, setImobiliarias] = useState([]);
  const [imoveis, setImoveis] = useState([]);
  const [selectedImobiliariaId, setSelectedImobiliariaId] = useState('');
  const [mensagem, setMensagem] = useState('');
  const [loading, setLoading] = useState(false);

  // --- ALTERAÇÃO AQUI ---
  // A função de buscar imobiliárias agora também envia o token.
  useEffect(() => {
    const fetchImobiliarias = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) throw new Error('Acesso negado. Faça login.');

        const res = await fetch('http://localhost:8000/imobiliarias/', {
          headers: { 'Authorization': `Bearer ${token}` },
        });

        if (!res.ok) throw new Error('Falha ao carregar imobiliárias');
        const data = await res.json();
        setImobiliarias(data);
        if (data.length > 0) {
          setSelectedImobiliariaId(data[0].id);
        }
      } catch (error) {
        setMensagem(error.message);
      }
    };
    fetchImobiliarias();
  }, []);

  const fetchImoveis = async (imobiliariaId) => {
    if (!imobiliariaId) {
      setImoveis([]);
      return;
    }
    try {
      // Esta chamada é pública, não precisa de token
      const res = await fetch(`http://localhost:8000/imobiliarias/${imobiliariaId}/imoveis/`);
      if (!res.ok) throw new Error('Falha ao buscar imóveis');
      const data = await res.json();
      setImoveis(data);
    } catch (error) {
      console.error(error);
      setMensagem('Erro ao carregar a lista de imóveis.');
    }
  };

  useEffect(() => {
    fetchImoveis(selectedImobiliariaId);
  }, [selectedImobiliariaId]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({ ...prevState, [name]: value }));
  };

  // --- ALTERAÇÃO AQUI ---
  // A função de criar imóvel também precisa de enviar o token.
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedImobiliariaId) {
      setMensagem('Por favor, selecione uma imobiliária.');
      return;
    }
    setLoading(true);
    setMensagem('A cadastrar imóvel...');
    
    const token = localStorage.getItem('access_token');
    if (!token) {
      setMensagem('Acesso negado. Faça login.');
      setLoading(false);
      return;
    }

    try {
      // A criação de imóveis não é protegida neste momento, mas é boa prática
      // preparar o código para quando for.
      const res = await fetch(`http://localhost:8000/imobiliarias/${selectedImobiliariaId}/imoveis/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`, // Enviando o token
        },
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Falha ao cadastrar imóvel');
      }

      setMensagem('Imóvel cadastrado com sucesso!');
      fetchImoveis(selectedImobiliariaId);
      setFormData({
        titulo: '', descricao: '', preco: '', quartos: '', banheiros: '', area: '', tipo: 'apartamento',
      });
    } catch (error) {
      setMensagem(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Gerir Imóveis</h1>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-semibold mb-4">Cadastrar Novo Imóvel</h2>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label htmlFor="imobiliaria" className="block text-gray-700 font-medium mb-2">Imobiliária</label>
                <select
                  id="imobiliaria" value={selectedImobiliariaId} onChange={(e) => setSelectedImobiliariaId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required
                >
                  <option value="">-- Selecione uma imobiliária --</option>
                  {imobiliarias.map(imob => (
                    <option key={imob.id} value={imob.id}>{imob.nome}</option>
                  ))}
                </select>
              </div>
              <FormInput id="titulo" label="Título do Anúncio" value={formData.titulo} onChange={handleChange} required />
              <div className="mb-4">
                <label htmlFor="descricao" className="block text-gray-700 font-medium mb-2">Descrição</label>
                <textarea
                  id="descricao" name="descricao" value={formData.descricao} onChange={handleChange}
                  rows="4" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormInput id="preco" label="Preço (R$)" type="number" step="0.01" value={formData.preco} onChange={handleChange} required />
                <FormInput id="area" label="Área (m²)" type="number" value={formData.area} onChange={handleChange} required />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <FormInput id="quartos" label="Quartos" type="number" value={formData.quartos} onChange={handleChange} required />
                <FormInput id="banheiros" label="Banheiros" type="number" value={formData.banheiros} onChange={handleChange} required />
                <div className="mb-4">
                  <label htmlFor="tipo" className="block text-gray-700 font-medium mb-2">Tipo</label>
                  <select
                    id="tipo" name="tipo" value={formData.tipo} onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="apartamento">Apartamento</option>
                    <option value="casa">Casa</option>
                    <option value="terreno">Terreno</option>
                    <option value="comercial">Comercial</option>
                  </select>
                </div>
              </div>
              <button
                type="submit" disabled={loading}
                className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
              >
                {loading ? 'Aguarde...' : 'Cadastrar Imóvel'}
              </button>
            </form>
            {mensagem && <p className="mt-4 text-center text-gray-600">{mensagem}</p>}
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-semibold mb-4">Imóveis Cadastrados</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-4">ID</th>
                    <th className="text-left py-2 px-4">Título</th>
                    <th className="text-left py-2 px-4">Preço (R$)</th>
                  </tr>
                </thead>
                <tbody>
                  {imoveis.map((imovel) => (
                    <tr key={imovel.id} className="border-b hover:bg-gray-50">
                      <td className="py-2 px-4">{imovel.id}</td>
                      <td className="py-2 px-4">{imovel.titulo}</td>
                      <td className="py-2 px-4">{Number(imovel.preco).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {imoveis.length === 0 && <p className="text-center py-4">Nenhum imóvel encontrado para esta imobiliária.</p>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
