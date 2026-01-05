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

    setUser(user: any, cargo: string | null, imobiliaria: string | null) {
      // --- LÓGICA DE CORREÇÃO AUTOMÁTICA DE CARGO ---
      let finalCargo = cargo;

      if (!finalCargo && user) {
          if (user.is_superuser) {
              finalCargo = 'SUPERADMIN';
          } 
          // CORREÇÃO: Aceita 'is_staff' (padrão Django) ou 'is_admin'
          else if (user.is_admin || user.is_staff) {
              finalCargo = 'ADMIN';
          } 
          else if (user.is_corretor) {
              finalCargo = 'CORRETOR';
          } else {
              finalCargo = 'USUARIO';
          }
          console.log("AuthStore: Cargo detectado automaticamente:", finalCargo);
      }
      // ------------------------------------------------

      this.user = user;
      this.userCargo = finalCargo;
      this.imobiliariaName = imobiliaria;
      
      localStorage.setItem('userData', JSON.stringify(user));
      
      if (finalCargo) {
          localStorage.setItem('userCargo', finalCargo);
      }
      
      if (imobiliaria) {
          localStorage.setItem('imobiliariaName', imobiliaria);
      }
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
        
        // Garante que o cargo seja lido do localStorage na inicialização
        const cargo = localStorage.getItem('userCargo');
        if (cargo) {
            this.userCargo = cargo;
        }
    }
  },
});