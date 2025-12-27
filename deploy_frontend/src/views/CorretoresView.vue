<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Configurações</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Utilizadores</span>
           </nav>
           
           <h1>Gerenciar Utilizadores</h1>
        </div>
        
        <div class="actions-area">
            <button class="btn-icon-thin" @click="fetchCorretores" title="Atualizar Dados">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            </button>
            
            <router-link :to="{ name: 'corretor-novo' }" class="btn-primary-thin">
              <i class="fas fa-plus"></i> Novo Utilizador
            </router-link>
        </div>
      </div>
    </header>

    <div class="kpi-grid">
      <div class="kpi-card blue" :class="{ active: filterCargo === '' }" @click="filterCargo = ''">
        <div class="kpi-content">
          <span class="kpi-value">{{ stats.total }}</span>
          <span class="kpi-label">Total Utilizadores</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-users"></i></div>
      </div>

      <div class="kpi-card purple" :class="{ active: filterCargo === 'ADMIN' }" @click="filterCargo = 'ADMIN'">
        <div class="kpi-content">
          <span class="kpi-value">{{ stats.admins }}</span>
          <span class="kpi-label">Administradores</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-user-shield"></i></div>
      </div>

      <div class="kpi-card green" :class="{ active: filterCargo === 'CORRETOR' }" @click="filterCargo = 'CORRETOR'">
        <div class="kpi-content">
          <span class="kpi-value">{{ stats.corretores }}</span>
          <span class="kpi-label">Corretores / Agentes</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-briefcase"></i></div>
      </div>

      <div class="kpi-card orange">
        <div class="kpi-content">
          <span class="kpi-value">{{ stats.ativos }}</span>
          <span class="kpi-label">Utilizadores Ativos</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-user-check"></i></div>
      </div>
    </div>

    <div class="toolbar-grid">
        <div class="filter-cell search-cell">
          <label>Buscar</label>
          <div class="input-with-icon">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="searchTerm" 
              placeholder="Nome, e-mail ou telemóvel..." 
              class="form-control"
            >
          </div>
        </div>

        <div class="filter-cell">
          <label>Cargo / Função</label>
          <select v-model="filterCargo" class="form-control">
            <option value="">Todos os Cargos</option>
            <option value="ADMIN">Administrador</option>
            <option value="CORRETOR">Corretor</option>
            <option value="VISTORIADOR">Vistoriador</option>
          </select>
        </div>

        <div class="filter-cell clear-cell">
            <label>&nbsp;</label>
            <button @click="resetFilters" class="btn-clear" title="Limpar Filtros">
                <i class="fas fa-eraser"></i>
            </button>
        </div>
    </div>

    <main class="report-main-wrapper">
      
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>A carregar utilizadores...</p>
      </div>

      <div v-else-if="filteredCorretores.length === 0" class="empty-state">
        <i class="fas fa-user-slash empty-icon"></i>
        <p>Nenhum utilizador encontrado com estes filtros.</p>
      </div>

      <div v-else class="report-scroll-viewport">
        <table class="report-table">
          <thead>
            <tr>
              <th width="30%">Utilizador</th>
              <th width="20%">E-mail / Contacto</th>
              <th width="15%">Cargo</th>
              <th width="15%">CRECI / Registo</th>
              <th width="10%" class="text-center">Status</th>
              <th width="10%" class="text-right">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="corretor in filteredCorretores" :key="corretor.id">
              <td>
                <div class="user-info-cell">
                   <div class="user-avatar" v-if="!corretor.foto">
                      {{ corretor.first_name.charAt(0) }}{{ corretor.last_name.charAt(0) }}
                   </div>
                   <img v-else :src="corretor.foto" class="user-avatar-img" />
                   <div class="user-name-group">
                      <span class="user-full-name">{{ corretor.first_name }} {{ corretor.last_name }}</span>
                      <span class="user-username">@{{ corretor.username }}</span>
                   </div>
                </div>
              </td>
              
              <td>
                  <div class="contact-group">
                      <span class="contact-email"><i class="far fa-envelope"></i> {{ corretor.email }}</span>
                      <span class="contact-phone" v-if="corretor.telefone"><i class="fas fa-phone"></i> {{ corretor.telefone }}</span>
                  </div>
              </td>

              <td>
                <span class="badge-cargo" :class="corretor.cargo">
                    {{ corretor.cargo }}
                </span>
              </td>

              <td class="text-muted">
                  {{ corretor.creci || '---' }}
              </td>

              <td class="text-center">
                <span :class="['status-pill', corretor.is_active ? 'status-green' : 'status-red']">
                  {{ corretor.is_active ? 'Ativo' : 'Inativo' }}
                </span>
              </td>

              <td class="text-right">
                <div class="actions-flex">
                    <router-link :to="{ name: 'corretor-editar', params: { id: corretor.id } }" class="btn-action primary" title="Editar">
                        <i class="fas fa-pen"></i>
                    </router-link>
                    <button @click="deleteCorretor(corretor.id)" class="btn-action danger" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
import { useToast } from 'vue-toast-notification';

interface Corretor {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  cargo: string;
  telefone?: string;
  creci?: string;
  is_active: boolean;
  foto?: string;
}

const corretores = ref<Corretor[]>([]);
const isLoading = ref(true);
const searchTerm = ref('');
const filterCargo = ref('');
const toast = useToast();

const fetchCorretores = async () => {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/core/usuarios/');
    corretores.value = response.data;
  } catch (error) {
    console.error('Erro ao buscar utilizadores:', error);
    toast.error('Erro ao carregar lista de utilizadores.');
  } finally {
    isLoading.value = false;
  }
};

const deleteCorretor = async (id: number) => {
  if (!confirm('Tem a certeza de que deseja eliminar este utilizador?')) return;
  try {
    await apiClient.delete(`/v1/core/usuarios/${id}/`);
    toast.success('Utilizador eliminado com sucesso.');
    fetchCorretores();
  } catch (error) {
    toast.error('Não foi possível eliminar o utilizador.');
  }
};

const resetFilters = () => {
    searchTerm.value = '';
    filterCargo.value = '';
};

const stats = computed(() => {
    return {
        total: corretores.value.length,
        admins: corretores.value.filter(c => c.cargo === 'ADMIN').length,
        corretores: corretores.value.filter(c => c.cargo === 'CORRETOR').length,
        ativos: corretores.value.filter(c => c.is_active).length
    };
});

const filteredCorretores = computed(() => {
  return corretores.value.filter(c => {
    const nameMatch = (c.first_name + ' ' + c.last_name).toLowerCase().includes(searchTerm.value.toLowerCase()) ||
                     c.email.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
                     c.username.toLowerCase().includes(searchTerm.value.toLowerCase());
    const cargoMatch = filterCargo.value === '' || c.cargo === filterCargo.value;
    return nameMatch && cargoMatch;
  });
});

onMounted(fetchCorretores);
</script>

<style scoped>
/* CONFIGURAÇÃO GERAL (Page Scroll) */
.page-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #fcfcfc;
  font-family: 'Inter', sans-serif;
  padding: 1.5rem 2.5rem;
  box-sizing: border-box;
}

/* HEADER */
.page-header { margin-bottom: 2rem; flex-shrink: 0; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }
.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.actions-area { display: flex; gap: 0.75rem; }

/* Botões Estilo Thin */
.btn-primary-thin {
  background: #2563eb; color: white; border: none; padding: 0.5rem 1.2rem;
  border-radius: 6px; font-weight: 400; font-size: 0.85rem; cursor: pointer; text-decoration: none;
  display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s;
}
.btn-primary-thin:hover { background: #1d4ed8; }

.btn-icon-thin {
  background: white; border: 1px solid #e2e8f0; color: #64748b; width: 34px; height: 34px;
  border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center;
}

/* KPI GRID */
.kpi-grid { 
    display: grid; grid-template-columns: repeat(4, 1fr); 
    gap: 1.25rem; margin-bottom: 2rem; flex-shrink: 0;
}
.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); cursor: pointer; position: relative; overflow: hidden;
}
.kpi-card.active { border-color: #2563eb; background-color: #f8fbff; }
.kpi-value { font-size: 1.6rem; font-weight: 300; color: #111; }
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; }
.kpi-icon { font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; }

.kpi-card.blue .kpi-value { color: #2563eb; }
.kpi-card.purple .kpi-value { color: #9333ea; }
.kpi-card.green .kpi-value { color: #059669; }
.kpi-card.orange .kpi-value { color: #d97706; }

/* TOOLBAR */
.toolbar-grid {
  background-color: #ffffff; border-radius: 8px; border: 1px solid #e5e7eb;
  padding: 1rem; display: grid; grid-template-columns: 2fr 1fr auto; 
  gap: 1rem; align-items: end; margin-bottom: 1.5rem; flex-shrink: 0;
}
.filter-cell { display: flex; flex-direction: column; gap: 0.3rem; }
.filter-cell label { font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; }
.form-control {
  padding: 0.5rem 0.8rem; font-size: 0.85rem; border: 1px solid #cbd5e1; border-radius: 6px; height: 38px;
}
.input-with-icon { position: relative; width: 100%; }
.input-with-icon i { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 0.9rem; }
.input-with-icon .form-control { padding-left: 2.2rem; }
.btn-clear { width: 38px; height: 38px; border: 1px solid #cbd5e1; background: #f8fafc; border-radius: 6px; color: #64748b; cursor: pointer; }

/* TABELA */
.report-main-wrapper {
  width: 100%; background: white; border-radius: 8px; border: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}
.report-table { width: 100%; border-collapse: collapse; }
.report-table th {
  background: #f8fafc; padding: 0.8rem 1.2rem; text-align: left;
  font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase;
  border-bottom: 1px solid #e2e8f0; position: sticky; top: 0;
}
.report-table td { padding: 0.8rem 1.2rem; border-bottom: 1px solid #f1f5f9; font-size: 0.85rem; color: #334155; vertical-align: middle; }
.report-table tr:hover { background-color: #fcfcfc; }

/* User Info Cell */
.user-info-cell { display: flex; align-items: center; gap: 1rem; }
.user-avatar { width: 36px; height: 36px; border-radius: 50%; background: #e2e8f0; color: #64748b; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.75rem; }
.user-avatar-img { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; }
.user-name-group { display: flex; flex-direction: column; }
.user-full-name { font-weight: 600; color: #1e293b; }
.user-username { font-size: 0.75rem; color: #94a3b8; }

/* Contacts */
.contact-group { display: flex; flex-direction: column; gap: 2px; }
.contact-group span { font-size: 0.8rem; color: #64748b; }
.contact-group i { width: 16px; color: #cbd5e1; }

/* Badge Cargo */
.badge-cargo { font-size: 0.65rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; border: 1px solid #e2e8f0; color: #475569; }
.badge-cargo.ADMIN { background: #faf5ff; color: #9333ea; border-color: #e9d5ff; }
.badge-cargo.CORRETOR { background: #f0fdf4; color: #16a34a; border-color: #bbf7d0; }

/* Status */
.status-pill { display: inline-block; padding: 2px 10px; border-radius: 99px; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; }
.status-green { background: #dcfce7; color: #15803d; }
.status-red { background: #fef2f2; color: #b91c1c; }

.actions-flex { display: flex; gap: 0.5rem; justify-content: flex-end; }
.btn-action { width: 32px; height: 32px; border: none; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.btn-action.primary { background-color: #eff6ff; color: #2563eb; }
.btn-action.danger { background-color: #fff1f2; color: #e11d48; }

.loading-state, .empty-state { text-align: center; padding: 4rem 2rem; color: #94a3b8; }
.spinner { border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%; width: 32px; height: 32px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }

@media (max-width: 1024px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .toolbar-grid { grid-template-columns: 1fr; }
}
</style>