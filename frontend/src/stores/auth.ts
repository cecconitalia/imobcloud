// frontend/src/stores/auth.ts

import { defineStore } from 'pinia';
import apiClient from '@/services/api';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('authToken') || null,
        // Tenta fazer o parse do JSON, se falhar ou for null, inicia como null
        user: JSON.parse(localStorage.getItem('userData') || 'null'),
        userCargo: localStorage.getItem('userCargo') || null,
    }),

    getters: {
        isAuthenticated: (state) => !!state.token,
        
        isAdmin: (state) => state.userCargo === 'ADMIN' || state.userCargo === 'SUPERADMIN' || state.user?.is_superuser,
        
        isSuperUser: (state) => state.user?.is_superuser === true,

        // --- LÓGICA DO BANNER FINANCEIRO ---
        // Retorna true se o status for 'PENDENTE' (Vencido, mas na tolerância)
        isFinancialPending: (state) => {
            // Superusuários nunca veem avisos de pagamento
            if (state.user?.is_superuser) return false;

            // Verifica o status dentro dos detalhes da imobiliária (vindos do serializer atualizado)
            // Usa optional chaining (?.) para evitar erro se imobiliaria_detalhes for undefined
            const status = state.user?.imobiliaria_detalhes?.status_financeiro;
            return status === 'PENDENTE';
        },

        // Recupera e formata a data de vencimento para exibir no banner
        vencimentoAtual: (state) => {
            const data = state.user?.imobiliaria_detalhes?.data_vencimento_atual;
            if (!data) return '';
            
            // Formata YYYY-MM-DD para DD/MM/YYYY
            try {
                const [ano, mes, dia] = data.split('-');
                return `${dia}/${mes}/${ano}`;
            } catch (e) {
                return data;
            }
        }
    },

    actions: {
        async login(credentials: any) {
            try {
                // CORREÇÃO: Removido '/api' do início. 
                // O axios já tem baseURL 'http://localhost:8000/api'
                // Resultado final será: http://localhost:8000/api/v1/token/
                const response = await apiClient.post('/v1/token/', credentials);
                const { access, refresh } = response.data;

                this.token = access;
                localStorage.setItem('authToken', access);
                localStorage.setItem('refreshToken', refresh);

                // Configura o header padrão para as próximas requisições
                apiClient.defaults.headers.common['Authorization'] = `Bearer ${access}`;

                // Busca dados do usuário (incluindo status financeiro atualizado)
                await this.fetchUser();
                
                return true; 
            } catch (error) {
                console.error('Erro no login:', error);
                throw error;
            }
        },

        async fetchUser() {
            try {
                // CORREÇÃO: Removido '/api' do início
                const response = await apiClient.get('/v1/core/usuarios/me/');
                this.user = response.data;
                
                // Define cargo
                let cargo = 'CORRETOR';
                if (this.user.is_superuser) cargo = 'SUPERADMIN';
                else if (this.user.is_admin) cargo = 'ADMIN';
                
                this.userCargo = cargo;

                // Salva no LocalStorage
                localStorage.setItem('userData', JSON.stringify(this.user));
                localStorage.setItem('userCargo', cargo);
            } catch (error) {
                console.error('Erro ao buscar usuário:', error);
                // Erros de autenticação (401/403) são tratados pelo interceptor do api.ts
            }
        },

        logout() {
            this.token = null;
            this.user = null;
            this.userCargo = null;
            
            localStorage.removeItem('authToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('userData');
            localStorage.removeItem('userCargo');
            
            delete apiClient.defaults.headers.common['Authorization'];
        },

        initialize() {
            const token = localStorage.getItem('authToken');
            if (token) {
                this.token = token;
                apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
                // Atualiza dados do usuário ao recarregar a página 
                // Isso garante que se o status financeiro mudou, o banner atualiza
                this.fetchUser();
            }
        }
    },
});