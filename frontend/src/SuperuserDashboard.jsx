// frontend/src/components/SuperuserDashboard.jsx

import React, { useState, useEffect } from 'react';
import axios from 'axios';

function SuperuserDashboard() {
    const [tenants, setTenants] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const apiUrl = 'http://127.0.0.1:8000/api/tenants/';

        // IMPORTANTE: Adicionamos 'withCredentials: true'
        // para enviar o cookie de sessão do admin para o backend.
        axios.get(apiUrl, { withCredentials: true })
            .then(response => {
                setTenants(response.data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Erro ao buscar tenants:", err);
                setError('Você precisa estar logado como administrador para ver esta página.');
                setLoading(false);
            });
    }, []);

    if (loading) {
        return <div className="text-center p-10">Carregando dados do painel...</div>;
    }

    if (error) {
        return <div className="text-center p-10 text-red-500">{error}</div>;
    }

    return (
        <div className="p-8">
            <h1 className="text-4xl font-bold mb-6">Painel do Superusuário</h1>
            <div className="bg-gray-700 p-6 rounded-lg shadow-xl">
                <h2 className="text-2xl font-semibold text-cyan-400 mb-4">Clientes (Tenants) Registrados</h2>
                <ul>
                    {tenants.map(tenant => (
                        <li key={tenant.id} className="border-b border-gray-600 py-3">
                            <p className="text-xl font-bold">{tenant.name}</p>
                            <p className="text-sm text-gray-400">Schema: <span className="font-mono">{tenant.schema_name}</span></p>
                            <div className="mt-2">
                                {tenant.domains.map(domain => (
                                    <span key={domain.id} className="inline-block bg-gray-600 text-yellow-300 text-xs font-mono mr-2 px-2.5 py-0.5 rounded-full">
                                        {domain.domain}
                                    </span>
                                ))}
                            </div>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}

export default SuperuserDashboard;