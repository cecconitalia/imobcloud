<template>
  <div class="page-container">
    
    <div v-if="!isLoading" class="dashboard-grid">
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-users"></i></div>
        <div class="stat-info">
            <h3>Total de Utilizadores</h3>
            <p>{{ stats.total }}</p>
        </div>
      </div>
      <div class="stat-card stat-admin">
        <div class="stat-icon"><i class="fas fa-user-shield"></i></div>
        <div class="stat-info">
            <h3>Administradores</h3>
            <p>{{ stats.admins }}</p>
        </div>
      </div>
      <div class="stat-card stat-corretor">
        <div class="stat-icon"><i class="fas fa-user-tie"></i></div>
        <div class="stat-info">
            <h3>Corretores</h3>
            <p>{{ stats.corretores }}</p>
        </div>
      </div>
    </div>

    <div class="search-and-filter-bar">
      <input 
        type="text" 
        v-model="searchTerm" 
        placeholder="Buscar por nome, email ou CRECI..." 
        class="search-input"
      />
      
      <div class="filter-group">
        <label for="cargo">Cargo:</label>
        <select id="cargo" v-model="filterCargo">
          <option value="">Todos</option>
          <option value="ADMIN">Administrador</option>
          <option value="CORRETOR">Corretor</option>
        </select>
      </div>

      <router-link :to="{ name: 'corretor-novo' }" class="btn-add">
        <i class="fas fa-plus"></i> <span class="mobile-hide">Novo Utilizador</span>
      </router-link>
    </div>

    <div v-if="isLoading" class="loading-message card">
      <div class="spinner"></div>
      A carregar utilizadores...
    </div>
    <div v-else-if="error" class="error-message card">{{ error }}</div>
    
    <div v-else-if="filteredUsers.length === 0" class="empty-state card">
      <div class="empty-icon"><i class="fas fa-users-slash"></i></div>
      <p>Nenhum utilizador encontrado com os filtros selecionados.</p>
    </div>

    <div v-else class="users-grid">
      <div 
        v-for="user in filteredUsers" 
        :key="user.id" 
        class="user-card"
      >
        <div class="card-top-bar">
           <div class="badges-left">
               <span class="user-id">#{{ user.id }}</span>
               <span class="username-badge">@{{ user.username }}</span>
           </div>
           <div class="badges-right">
               <span :class="['role-pill', getRoleClass(user.perfil?.cargo)]">
                  <i :class="getRoleIcon(user.perfil?.cargo)"></i>
                  {{ formatRole(user.perfil?.cargo) }}
               </span>
           </div>
        </div>
        
        <div class="card-body">
          <div class="user-main-info">
             <div class="user-avatar" :class="getRoleClass(user.perfil?.cargo)">
                <i :class="getRoleIcon(user.perfil?.cargo)"></i>
             </div>
             <div class="user-names">
                 <h4 class="user-fullname">{{ user.first_name }} {{ user.last_name }}</h4>
                 <p class="user-creci" v-if="user.perfil?.creci">
                    CRECI: {{ user.perfil.creci }}
                 </p>
                 <p class="user-creci text-muted" v-else>Sem CRECI</p>
             </div>
          </div>

          <div class="contacts-grid">
             <div class="contact-row">
                <i class="fas fa-envelope text-muted"></i>
                <span class="contact-value" :title="user.email">{{ user.email }}</span>
             </div>
             <div class="contact-row">
                <i class="fas fa-phone-alt text-muted"></i>
                <span class="contact-value">{{ user.perfil?.telefone || '—' }}</span>
             </div>
             <div class="contact-row" v-if="user.perfil?.endereco_cidade">
                <i class="fas fa-map-marker-alt text-muted"></i>
                <span class="contact-value">
                    {{ user.perfil.endereco_cidade }} - {{ user.perfil.endereco_estado }}
                </span>
             </div>
          </div>
        </div>
        
        <div class="card-actions">
          <div class="actions-full">
              <router-link :to="`/corretores/editar/${user.id}`" class="btn-action" title="Editar">
                <i class="fas fa-pen"></i> Editar Dados
              </router-link>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';

// Interfaces
interface UserProfile {
    cargo: string;
    creci?: string;
    telefone?: string;
    endereco_cidade?: string;
    endereco_estado?: string;
}
interface User {
    id: number;
    username: string;
    first_name: string;
    last_name?: string;
    email: string;
    perfil?: UserProfile;
}

const users = ref<User[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');
const filterCargo = ref('');

// Estatísticas computadas localmente (já que a API retorna a lista toda)
const stats = computed(() => {
    const total = users.value.length;
    const admins = users.value.filter(u => u.perfil?.cargo === 'ADMIN').length;
    const corretores = users.value.filter(u => u.perfil?.cargo === 'CORRETOR').length;
    return { total, admins, corretores };
});

// Filtragem
const filteredUsers = computed(() => {
  let filteredList = users.value;

  if (filterCargo.value) {
    filteredList = filteredList.filter(user => user.perfil?.cargo === filterCargo.value);
  }

  if (searchTerm.value) {
    const searchLower = searchTerm.value.toLowerCase();
    filteredList = filteredList.filter(user =>
      user.first_name.toLowerCase().includes(searchLower) ||
      (user.last_name || '').toLowerCase().includes(searchLower) ||
      user.email.toLowerCase().includes(searchLower) ||
      (user.perfil?.creci || '').toLowerCase().includes(searchLower)
    );
  }

  return filteredList;
});

async function fetchUsers() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/v1/core/usuarios/');
    users.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar utilizadores:", err);
    error.value = 'Não foi possível carregar a lista de utilizadores.';
  } finally {
    isLoading.value = false;
  }
}

// Helpers Visuais
function getRoleClass(cargo?: string) {
    return cargo === 'ADMIN' ? 'role-admin' : 'role-corretor';
}

function getRoleIcon(cargo?: string) {
    return cargo === 'ADMIN' ? 'fas fa-user-shield' : 'fas fa-user-tie';
}

function formatRole(cargo?: string) {
    if (cargo === 'ADMIN') return 'Administrador';
    if (cargo === 'CORRETOR') return 'Corretor';
    return cargo || 'Indefinido';
}

onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
/* ================================================== */
/* 1. Layout Geral */
/* ================================================== */
.page-container { padding: 0; }

/* ================================================== */
/* 2. Dashboard Stats */
/* ================================================== */
.dashboard-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem; margin-bottom: 2rem;
}
.stat-card {
  background-color: #fff; border: none; border-radius: 12px; padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04); display: flex; align-items: center; gap: 1rem;
  transition: transform 0.2s ease;
}
.stat-card:hover { transform: translateY(-3px); }
.stat-icon {
    width: 50px; height: 50px; border-radius: 12px; background-color: #e7f1ff; color: #0d6efd;
    display: flex; align-items: center; justify-content: center; font-size: 1.5rem;
}
.stat-admin .stat-icon { background-color: #f3e8ff; color: #9333ea; } /* Roxo */
.stat-corretor .stat-icon { background-color: #dcfce7; color: #166534; } /* Verde */

.stat-info h3 { font-size: 0.8rem; color: #6c757d; font-weight: 600; margin: 0; text-transform: uppercase; }
.stat-info p { font-size: 1.5rem; font-weight: 700; color: #212529; margin: 0; }

/* ================================================== */
/* 3. Filtros */
/* ================================================== */
.search-and-filter-bar {
  display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem;
  align-items: center; background-color: transparent; padding: 0; box-shadow: none;
}
.search-input {
  padding: 10px; border: 1px solid #ccc; border-radius: 5px; width: 100%; max-width: 350px; box-sizing: border-box; font-family: system-ui, sans-serif;
}
.filter-group { display: flex; align-items: center; gap: 0.5rem; }
.filter-group label { font-weight: 500; color: #555; white-space: nowrap; }
.filter-group select {
  padding: 8px 12px; border: 1px solid #ccc; border-radius: 5px; font-size: 0.95rem;
  background-color: #f8f9fa; min-width: 120px; font-family: system-ui, sans-serif;
}
.btn-add {
  background-color: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 5px;
  cursor: pointer; font-weight: bold; transition: background-color 0.3s ease; font-size: 0.95rem;
  display: flex; align-items: center; gap: 0.5rem; margin-left: auto; width: auto; text-decoration: none;
  font-family: system-ui, sans-serif;
}
.btn-add:hover { background-color: #0056b3; }
.mobile-hide { display: inline; }
@media (max-width: 768px) {
  .search-and-filter-bar { flex-direction: column; align-items: stretch; }
  .search-input { max-width: 100%; }
  .filter-group { flex-direction: column; align-items: stretch; }
  .btn-add { margin-left: 0; justify-content: center; }
}

/* ================================================== */
/* 4. Grid de Utilizadores */
/* ================================================== */
.users-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem; padding-bottom: 2rem;
}

.user-card {
  background-color: #fff; border-radius: 12px; border: 1px solid rgba(0,0,0,0.06);
  box-shadow: 0 4px 12px rgba(0,0,0,0.03); display: flex; flex-direction: column;
  transition: all 0.3s ease; position: relative; overflow: hidden;
}
.user-card:hover { transform: translateY(-5px); box-shadow: 0 12px 24px rgba(0,0,0,0.08); }

/* Header */
.card-top-bar {
    padding: 0.85rem 1.25rem; display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid #f0f2f5; background: #fff;
}
.badges-left, .badges-right { display: flex; align-items: center; gap: 8px; }

.user-id {
    font-size: 0.75rem; font-weight: 800; color: #6b7280;
    background: #f3f4f6; padding: 3px 8px; border-radius: 6px;
}
.username-badge {
    font-size: 0.8rem; color: #6b7280; font-weight: 600;
}

/* Badges de Cargo */
.role-pill {
    padding: 0.35em 0.85em; border-radius: 50px; font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; display: flex; align-items: center; gap: 5px;
}
.role-admin { background-color: #f3e8ff; color: #9333ea; } /* Roxo */
.role-corretor { background-color: #e0f2fe; color: #0284c7; } /* Azul */


/* Body */
.card-body { padding: 0; flex-grow: 1; display: flex; flex-direction: column; }

/* User Main Info */
.user-main-info {
    padding: 1.5rem 1.25rem; display: flex; align-items: center; gap: 1rem;
    border-bottom: 1px solid #f0f2f5;
}
.user-avatar {
    width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; flex-shrink: 0;
}
.user-names { overflow: hidden; }
.user-fullname {
    font-size: 1rem; font-weight: 700; color: #111827; margin: 0 0 0.2rem 0;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.user-creci { font-size: 0.8rem; color: #6b7280; margin: 0; font-weight: 500; }

/* Contact Info Grid */
.contacts-grid {
    padding: 1rem 1.25rem; display: flex; flex-direction: column; gap: 0.8rem; background-color: #f8fafc;
    flex-grow: 1;
}
.contact-row {
    display: flex; align-items: center; gap: 10px; font-size: 0.9rem; color: #374151;
}
.contact-value { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* Actions */
.card-actions {
    padding: 0.85rem 1.25rem; background-color: #fff; border-top: 1px solid #f0f2f5;
}
.actions-full { display: flex; width: 100%; }

.btn-action {
    width: 100%; text-align: center; background-color: #f3f4f6; color: #4b5563;
    padding: 8px; border-radius: 6px; font-weight: 600; font-size: 0.9rem;
    text-decoration: none; transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px;
}
.btn-action:hover { background-color: #e5e7eb; color: #111827; }

/* Utils */
.text-muted { color: #9ca3af; }
.loading-message, .error-message, .empty-state { text-align: center; padding: 4rem 2rem; color: #6c757d; }
.empty-icon { font-size: 3rem; color: #dee2e6; margin-bottom: 1rem; }
.spinner {
  border: 3px solid #e9ecef; border-top: 3px solid #0d6efd; border-radius: 50%;
  width: 40px; height: 40px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>