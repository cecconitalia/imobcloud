<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Gestão</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Utilizadores</span>
           </nav>
           
           <h1>Gerenciar Equipe</h1>
        </div>
        
        <div class="actions-area">
            <button class="btn-icon-thin" @click="fetchUsers" title="Atualizar Lista">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            </button>
            
            <router-link :to="{ name: 'corretor-novo' }" class="btn-primary-thin">
              <i class="fas fa-user-plus"></i> Novo Utilizador
            </router-link>
        </div>
      </div>
    </header>

    <div class="kpi-grid">
      <div class="kpi-card blue" :class="{ active: filters.status === '' }" @click="filters.status = ''">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.total }}</span>
          <span class="kpi-label">Total de Usuários</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-users"></i></div>
      </div>

      <div class="kpi-card green" :class="{ active: filters.status === 'active' }" @click="filters.status = 'active'">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.ativos }}</span>
          <span class="kpi-label">Ativos</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-user-check"></i></div>
      </div>

      <div class="kpi-card purple">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.admins }}</span>
          <span class="kpi-label">Administradores</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-user-shield"></i></div>
      </div>

      <div class="kpi-card orange">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.corretores }}</span>
          <span class="kpi-label">Corretores</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-id-badge"></i></div>
      </div>
    </div>

    <div class="toolbar-row">
        <div class="filter-group search-group">
          <label>Buscar</label>
          <div class="input-with-icon">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="filters.search" 
              placeholder="Nome, email ou usuário..." 
              class="form-control"
            >
          </div>
        </div>

        <div class="filter-group">
          <label>Função</label>
          <select v-model="filters.role" class="form-control">
            <option value="">Todas</option>
            <option value="admin">Administrador</option>
            <option value="corretor">Corretor</option>
          </select>
        </div>

        <div class="filter-group small-btn">
            <label>&nbsp;</label>
            <button @click="clearFilters" class="btn-clear" title="Limpar Filtros">
                <i class="fas fa-eraser"></i>
            </button>
        </div>
    </div>

    <main class="report-main-wrapper">
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Carregando equipe...</p>
      </div>

      <div v-else-if="filteredUsers.length === 0" class="empty-state">
        <i class="fas fa-user-slash"></i>
        <p>Nenhum usuário encontrado com os filtros selecionados.</p>
      </div>

      <div v-else class="report-scroll-viewport">
        <table class="report-table">
          <thead>
            <tr>
              <th width="30%">Usuário</th>
              <th width="25%">Contato</th>
              <th width="15%" class="text-center">Função</th>
              <th width="10%" class="text-center">Status</th>
              <th width="15%" class="text-right">Último Login</th>
              <th width="5%" class="text-right">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id">
              <td>
                <div class="user-cell">
                    <div class="user-avatar" :class="getAvatarClass(user)">
                        {{ getUserInitials(user) }}
                    </div>
                    <div class="cell-content">
                        <span class="main-text">{{ getFullName(user) }}</span>
                        <span class="sub-text text-muted">@{{ user.username }}</span>
                    </div>
                </div>
              </td>
              
              <td>
                <div class="cell-content">
                    <span class="main-text text-sm"><i class="far fa-envelope text-muted mr-1"></i> {{ user.email }}</span>
                </div>
              </td>

              <td class="text-center">
                  <span v-if="user.is_superuser" class="badge-type bg-purple">Super Admin</span>
                  <span v-else-if="user.is_admin" class="badge-type bg-blue">Admin</span>
                  <span v-else class="badge-type bg-orange">Corretor</span>
              </td>

              <td class="text-center">
                <span :class="['status-pill', user.is_active ? 'status-green' : 'status-red']">
                  {{ user.is_active ? 'Ativo' : 'Inativo' }}
                </span>
              </td>

              <td class="text-right text-muted text-sm">
                  {{ formatDate(user.last_login) }}
              </td>

              <td class="text-right">
                <div class="actions-flex">
                    <button class="btn-action edit" @click="editUser(user.id)" title="Editar Usuário">
                        <i class="fas fa-pen"></i>
                    </button>
                    <button 
                        class="btn-action delete" 
                        @click="toggleStatus(user)" 
                        :title="user.is_active ? 'Desativar' : 'Ativar'"
                    >
                        <i :class="user.is_active ? 'fas fa-ban' : 'fas fa-check'"></i>
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
import { useRouter } from 'vue-router';
import api from '@/services/api';
import { format, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { useToast } from 'vue-toast-notification';

const router = useRouter();
const toast = useToast();

interface User {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  is_admin?: boolean; 
  last_login: string | null;
}

const users = ref<User[]>([]);
const isLoading = ref(true);
const filters = ref({
    search: '',
    role: '',
    status: ''
});

const kpis = computed(() => {
    const total = users.value.length;
    const ativos = users.value.filter(u => u.is_active).length;
    const admins = users.value.filter(u => u.is_superuser || u.is_admin).length;
    const corretores = total - admins;
    return { total, ativos, admins, corretores };
});

const filteredUsers = computed(() => {
    return users.value.filter(user => {
        const searchLower = filters.value.search.toLowerCase();
        const fullName = `${user.first_name} ${user.last_name}`.toLowerCase();
        
        const matchSearch = !searchLower || 
            fullName.includes(searchLower) || 
            user.username.toLowerCase().includes(searchLower) || 
            user.email.toLowerCase().includes(searchLower);

        let matchRole = true;
        if (filters.value.role === 'admin') matchRole = user.is_superuser || user.is_admin;
        if (filters.value.role === 'corretor') matchRole = !user.is_superuser && !user.is_admin;

        let matchStatus = true;
        if (filters.value.status === 'active') matchStatus = user.is_active;

        return matchSearch && matchRole && matchStatus;
    });
});

const fetchUsers = async () => {
    isLoading.value = true;
    try {
        // CORREÇÃO: Endpoint alterado de /core/users/ para /core/usuarios/
        const response = await api.get('/v1/core/usuarios/');
        users.value = response.data.results || response.data;
    } catch (error) {
        console.error("Erro ao buscar usuários:", error);
        toast.error("Erro ao carregar a lista de usuários.");
    } finally {
        isLoading.value = false;
    }
};

const clearFilters = () => {
    filters.value = { search: '', role: '', status: '' };
};

const editUser = (id: number) => {
    router.push({ name: 'corretor-editar', params: { id } });
};

const toggleStatus = async (user: User) => {
    if (!confirm(`Deseja realmente ${user.is_active ? 'desativar' : 'ativar'} o usuário ${user.username}?`)) return;

    try {
        // CORREÇÃO: Endpoint alterado de /core/users/ para /core/usuarios/
        await api.patch(`/v1/core/usuarios/${user.id}/`, { is_active: !user.is_active });
        user.is_active = !user.is_active;
        toast.success(`Usuário ${user.is_active ? 'ativado' : 'desativado'} com sucesso.`);
    } catch (error) {
        toast.error("Erro ao alterar status do usuário.");
    }
};

const getFullName = (user: User) => {
    const name = `${user.first_name} ${user.last_name}`.trim();
    return name || user.username;
};

const getUserInitials = (user: User) => {
    const first = user.first_name ? user.first_name[0] : user.username[0];
    const last = user.last_name ? user.last_name[0] : '';
    return (first + last).toUpperCase().substring(0, 2);
};

const getAvatarClass = (user: User) => {
    if (user.is_superuser) return 'bg-purple-100 text-purple-600';
    if (user.is_admin) return 'bg-blue-100 text-blue-600';
    return 'bg-orange-100 text-orange-600';
};

const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Nunca';
    try { return format(parseISO(dateString), 'dd/MM/yy HH:mm', { locale: ptBR }); } catch { return '-'; }
};

onMounted(() => {
    fetchUsers();
});
</script>

<style scoped>
/* CONFIGURAÇÃO GERAL */
.page-container {
  min-height: 100vh;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
}

/* HEADER */
.page-header { margin-bottom: 2rem; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }
.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.actions-area { display: flex; gap: 0.75rem; }

/* Botões */
.btn-primary-thin {
  background: #2563eb; color: white; border: none; padding: 0.5rem 1.2rem;
  border-radius: 6px; font-weight: 400; font-size: 0.85rem; cursor: pointer; text-decoration: none;
  display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(37, 99, 235, 0.15);
}
.btn-primary-thin:hover { background: #1d4ed8; transform: translateY(-1px); }

.btn-icon-thin {
  background: white; border: 1px solid #e2e8f0; color: #64748b; width: 34px; height: 34px;
  border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; font-size: 0.8rem;
}
.btn-icon-thin:hover { border-color: #cbd5e1; color: #2563eb; background: #f8fafc; }

/* KPI GRID */
.kpi-grid { 
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
    gap: 1.25rem; margin-bottom: 2rem; 
}
.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: all 0.2s; position: relative; overflow: hidden;
  cursor: pointer;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.04); }
.kpi-card.active { border: 1px solid; }

.kpi-content { display: flex; flex-direction: column; }
.kpi-value { font-size: 1.6rem; font-weight: 300; line-height: 1.1; color: #111; }
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; letter-spacing: 0.05em; }
.kpi-icon { font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; }

.kpi-card.blue.active { background-color: #f8fbff; border-color: #3b82f6; }
.kpi-card.blue .kpi-value, .kpi-card.blue .kpi-icon { color: #2563eb; }
.kpi-card.green.active { background-color: #f3fdf8; border-color: #10b981; }
.kpi-card.green .kpi-value, .kpi-card.green .kpi-icon { color: #059669; }
.kpi-card.purple .kpi-value, .kpi-card.purple .kpi-icon { color: #9333ea; }
.kpi-card.orange .kpi-value, .kpi-card.orange .kpi-icon { color: #d97706; }

/* TOOLBAR */
.toolbar-row {
  background-color: #ffffff;
  border-radius: 8px; border: 1px solid #e5e7eb;
  padding: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
  display: flex; flex-wrap: wrap; gap: 1rem; align-items: flex-end;
  margin-bottom: 1.5rem;
}

.filter-group { flex: 1; display: flex; flex-direction: column; gap: 0.3rem; min-width: 160px; }
.search-group { flex: 2; min-width: 260px; }
.small-btn { flex: 0 0 auto; min-width: auto; }
.filter-group label { font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; }

.input-with-icon { position: relative; width: 100%; }
.input-with-icon i { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 0.9rem; }

.form-control {
  width: 100%; padding: 0.5rem 0.8rem; font-size: 0.85rem;
  border: 1px solid #cbd5e1; border-radius: 6px; background-color: #fff; color: #334155;
  outline: none; height: 38px; box-sizing: border-box; transition: all 0.2s;
}
.input-with-icon .form-control { padding-left: 2.2rem; }
.form-control:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1); }

.btn-clear {
    width: 38px; height: 38px; border: 1px solid #cbd5e1; background: #f8fafc;
    border-radius: 6px; color: #64748b; cursor: pointer;
    display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.btn-clear:hover { background: #fee2e2; color: #ef4444; border-color: #fca5a5; }

/* TABELA */
.report-main-wrapper {
  background: white; border-radius: 8px; border: 1px solid #e5e7eb;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
  display: flex; flex-direction: column; overflow: hidden;
}
.report-scroll-viewport { width: 100%; overflow-x: auto; }

.report-table { width: 100%; border-collapse: collapse; min-width: 800px; }
.report-table th {
  background: #f8fafc; padding: 0.8rem 1.2rem; text-align: left;
  font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em;
  border-bottom: 1px solid #e2e8f0;
}
.report-table td {
  padding: 0.8rem 1.2rem; border-bottom: 1px solid #f1f5f9;
  font-size: 0.85rem; color: #334155; vertical-align: middle;
}
.report-table tr:hover { background-color: #fcfcfc; }

.cell-content { display: flex; flex-direction: column; }
.main-text { font-weight: 600; color: #1e293b; }
.sub-text { font-size: 0.75rem; color: #64748b; }

.user-cell { display: flex; align-items: center; gap: 0.8rem; }
.user-avatar {
    width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.8rem; flex-shrink: 0;
}
.bg-purple-100 { background-color: #f3e8ff; } .text-purple-600 { color: #9333ea; }
.bg-blue-100 { background-color: #dbeafe; } .text-blue-600 { color: #2563eb; }
.bg-orange-100 { background-color: #ffedd5; } .text-orange-600 { color: #ea580c; }

.badge-type {
  font-size: 0.65rem; font-weight: 600; padding: 3px 8px; border-radius: 4px; 
  text-transform: uppercase; letter-spacing: 0.02em; display: inline-block;
}
.bg-purple { background: #f3e8ff; color: #7e22ce; }
.bg-blue { background: #e0f2fe; color: #0369a1; }
.bg-orange { background: #ffedd5; color: #c2410c; }

.status-pill {
  display: inline-block; padding: 2px 10px; border-radius: 99px;
  font-size: 0.7rem; font-weight: 600; text-align: center; text-transform: uppercase;
}
.status-green { background: #dcfce7; color: #15803d; }
.status-red { background: #fef2f2; color: #ef4444; }

.actions-flex { display: flex; gap: 0.5rem; justify-content: flex-end; }
.btn-action {
  width: 30px; height: 30px; border: none; border-radius: 6px; cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: all 0.2s; font-size: 0.8rem;
}
.btn-action.edit { background-color: #eff6ff; color: #2563eb; }
.btn-action.edit:hover { background-color: #2563eb; color: #fff; }
.btn-action.delete { background-color: #fff1f2; color: #e11d48; }
.btn-action.delete:hover { background-color: #e11d48; color: #fff; }

.text-right { text-align: right; }
.text-center { text-align: center; }
.text-muted { color: #94a3b8; }
.mr-1 { margin-right: 0.25rem; }

.loading-state, .empty-state { text-align: center; padding: 4rem 2rem; color: #64748b; }
.spinner {
  border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%;
  width: 32px; height: 32px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

@media (max-width: 1024px) {
  .page-container { padding: 1rem; }
  .header-main { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .actions-area { width: 100%; justify-content: flex-start; }
  .toolbar-row { flex-direction: column; align-items: stretch; }
  .filter-group, .search-group { width: 100%; }
}
</style>