// frontend/src/stores/auth.ts

import { defineStore } from 'pinia';
import api from '@/services/api'; 

interface UserState {
  token: string | null;
  user: any | null;
  userCargo: string | null;
  imobiliariaName: string | null;
}

export const useAuthStore = defineStore('auth', {
  state: (): UserState => ({
    token: localStorage.getItem('authToken') || null,
    user: JSON.parse(localStorage.getItem('userData') || 'null'),
    userCargo: localStorage.getItem('userCargo') || null,
    imobiliariaName: localStorage.getItem('imobiliariaName') || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.userCargo === 'ADMIN' || state.userCargo === 'SUPERADMIN',
    userName: (state) => state.user?.first_name || state.user?.username || 'Usuário',
  },

  actions: {
    setToken(token: string) {
      this.token = token;
      localStorage.setItem('authToken', token);
      // Configura o header padrão do Axios para futuras requisições
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    },

    setUser(user: any, cargo: string, imobiliaria: string) {
      this.user = user;
      this.userCargo = cargo;
      this.imobiliariaName = imobiliaria;
      
      localStorage.setItem('userData', JSON.stringify(user));
      localStorage.setItem('userCargo', cargo);
      localStorage.setItem('imobiliariaName', imobiliaria);
    },

    logout() {
      // 1. Limpa o estado da store
      this.token = null;
      this.user = null;
      this.userCargo = null;
      this.imobiliariaName = null;

      // 2. Limpa o LocalStorage
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
      localStorage.removeItem('userCargo');
      localStorage.removeItem('imobiliariaName');
      localStorage.removeItem('refreshToken');
      
      // 3. Remove o header do axios para evitar uso acidental do token antigo
      delete api.defaults.headers.common['Authorization'];
    },

    // Ação opcional para inicializar o store ao carregar a página
    initialize() {
        const token = localStorage.getItem('authToken');
        if (token) {
            this.setToken(token);
        }
    }
  },
});