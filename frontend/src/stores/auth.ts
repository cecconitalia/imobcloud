// frontend/src/stores/auth.ts

import { defineStore } from 'pinia';
import apiClient from '@/services/api';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('authToken') || null,
        user: JSON.parse(localStorage.getItem('userData') || 'null'),
        userCargo: localStorage.getItem('userCargo') || null,
    }),

    getters: {
        isAuthenticated: (state) => !!state.token,
        
        isAdmin: (state) => state.userCargo === 'ADMIN' || state.userCargo === 'SUPERADMIN' || state.user?.is_superuser,
        
        isSuperUser: (state) => state.user?.is_superuser === true,

        isFinancialPending: (state) => {
            if (state.user?.is_superuser) return false;
            const status = state.user?.imobiliaria_detalhes?.status_financeiro;
            return status === 'PENDENTE';
        },

        vencimentoAtual: (state) => {
            const data = state.user?.imobiliaria_detalhes?.data_vencimento_atual;
            if (!data) return '';
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
                // AJUSTE: Adicionado '/v1/' (já que a base agora é só /api)
                // Resultado: http://localhost:8001/api/v1/token/
                const response = await apiClient.post('/v1/token/', credentials);
                const { access, refresh } = response.data;

                this.token = access;
                localStorage.setItem('authToken', access);
                localStorage.setItem('refreshToken', refresh);

                apiClient.defaults.headers.common['Authorization'] = `Bearer ${access}`;

                await this.fetchUser();
                
                return true; 
            } catch (error) {
                console.error('Erro no login:', error);
                throw error;
            }
        },

        async fetchUser() {
            try {
                // AJUSTE: Adicionado '/v1/' para alinhar com a nova base
                // Resultado: http://localhost:8001/api/v1/core/usuarios/me/
                const response = await apiClient.get('/v1/core/usuarios/me/');
                this.user = response.data;
                
                let cargo = 'CORRETOR';
                if (this.user.is_superuser) cargo = 'SUPERADMIN';
                else if (this.user.is_admin) cargo = 'ADMIN';
                
                this.userCargo = cargo;

                localStorage.setItem('userData', JSON.stringify(this.user));
                localStorage.setItem('userCargo', cargo);
            } catch (error) {
                console.error('Erro ao buscar usuário:', error);
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
                this.fetchUser();
            }
        }
    },
});