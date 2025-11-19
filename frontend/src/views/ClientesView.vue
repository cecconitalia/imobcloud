<template>
  <div class="page-container">
    
    <div v-if="sumarioClientes" class="dashboard-grid">
      <div 
        class="stat-card clickable-card" 
        @click="resetFilters"
        :class="{ 'active-card': !filters.status && !filters.tipo_pessoa }"
        title="Ver todos os clientes"
      >
        <div class="stat-icon"><i class="fas fa-users"></i></div>
        <div class="stat-info">
            <h3>Total de Clientes</h3>
            <p>{{ sumarioClientes.total }}</p>
        </div>
      </div>

      <div 
        class="stat-card stat-ativo clickable-card" 
        @click="setFilter('status', 'ATIVO')"
        :class="{ 'active-card': filters.status === 'ATIVO' }"
        title="Filtrar apenas ativos"
      >
        <div class="stat-icon"><i class="fas fa-user-check"></i></div>
        <div class="stat-info">
            <h3>Ativos</h3>
            <p>{{ sumarioClientes.ativos }}</p>
        </div>
      </div>

      <div 
        class="stat-card clickable-card" 
        @click="setFilter('tipo_pessoa', 'FISICA')"
        :class="{ 'active-card': filters.tipo_pessoa === 'FISICA' }"
        title="Filtrar Pessoa Física"
      >
        <div class="stat-icon"><i class="fas fa-user"></i></div>
        <div class="stat-info">
            <h3>Pessoa Física</h3>
            <p>{{ sumarioClientes.pf }}</p>
        </div>
      </div>

      <div 
        class="stat-card clickable-card" 
        @click="setFilter('tipo_pessoa', 'JURIDICA')"
        :class="{ 'active-card': filters.tipo_pessoa === 'JURIDICA' }"
        title="Filtrar Pessoa Jurídica"
      >
        <div class="stat-icon"><i class="fas fa-building"></i></div>
        <div class="stat-info">
            <h3>Pessoa Jurídica</h3>
            <p>{{ sumarioClientes.pj }}</p>
        </div>
      </div>
    </div>
    
    <div class="search-and-filter-bar">
      <input
        type="text"
        v-model="searchTerm"
        placeholder="Buscar por nome, email, documento..."
        class="search-input"
      />
      
      <div class="filter-group">
        <label for="status">Status:</label>
        <select id="status" v-model="filters.status">
          <option value="">Todos</option>
          <option value="ATIVO">Ativo</option>
          <option value="INATIVO">Inativo</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label for="tipo_pessoa">Pessoa:</label>
        <select id="tipo_pessoa" v-model="filters.tipo_pessoa">
          <option value="">Todas</option>
          <option value="FISICA">Física</option>
          <option value="JURIDICA">Jurídica</option>
        </select>
      </div>

      <router-link :to="{ name: 'cliente-novo' }" class="btn-add">
        <i class="fas fa-plus"></i> <span class="mobile-hide">Novo Cliente</span>
      </router-link>
    </div>

    <div v-if="isLoading" class="loading-message card">
        <div class="spinner"></div>
        A carregar clientes...
    </div>
    <div v-else-if="error" class="error-message card">{{ error }}</div>

    <div v-else-if="filteredClientes.length === 0" class="empty-state card">
      <div class="empty-icon"><i class="fas fa-users-slash"></i></div>
      <p>Nenhum cliente encontrado com os filtros selecionados.</p>
    </div>

    <div v-else class="clientes-grid">
      <div
        v-for="cliente in filteredClientes"
        :key="cliente.id"
        class="cliente-card"
        @click="editCliente(cliente.id)"
      >
        <div class="cliente-profile-pic">
          <img v-if="cliente.foto_perfil" :src="cliente.foto_perfil" alt="Foto de Perfil" class="profile-img"/>
          <i v-else class="fas fa-user-circle profile-icon"></i>
        </div>
        <div class="cliente-info">
          <h3 class="cliente-nome">{{ cliente.nome_exibicao || 'Nome não disponível' }}</h3>
          <p class="cliente-contato">{{ cliente.email || 'Email não informado'}}</p>
          <p class="cliente-contato">{{ cliente.telefone || 'Telefone não informado' }}</p>
          <p class="cliente-contato tipo-pessoa">
             <i :class="cliente.tipo_pessoa === 'FISICA' ? 'fas fa-user' : 'fas fa-building'"></i>
             {{ cliente.tipo_pessoa === 'FISICA' ? 'Pessoa Física' : 'Pessoa Jurídica' }}
          </p>
        </div>
        <div class="cliente-tags">
          <span v-if="cliente.tipo === 'PROPRIETARIO'" class="tag proprietario">Proprietário</span>
          <span v-if="cliente.tipo === 'INTERESSADO'" class="tag interessado">Interessado</span>
          <span v-if="cliente.tipo === 'AMBOS'" class="tag ambos">Ambos</span>
          <span v-if="!cliente.ativo" class="tag inativo">Inativo</span>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';

interface Cliente {
  id: number;
  nome_exibicao: string;
  nome?: string;
  razao_social?: string;
  tipo_pessoa: 'FISICA' | 'JURIDICA';
  email?: string;
  telefone?: string;
  documento?: string;
  foto_perfil?: string;
  tipo: 'PROPRIETARIO' | 'INTERESSADO' | 'AMBOS';
  ativo: boolean;
}

const clientes = ref<Cliente[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');
const router = useRouter();

const sumarioClientes = ref<any>(null);

const filters = ref({
    status: 'ATIVO',
    tipo_pessoa: '',
});

async function fetchClientes() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get<Cliente[]>('/v1/clientes/');
    clientes.value = response.data;
    calculateSummary(clientes.value);
  } catch (err: any) {
    console.error("Erro ao buscar clientes:", err);
    error.value = err.response?.data?.detail || 'Não foi possível carregar os clientes.';
  } finally {
    isLoading.value = false;
  }
}

function calculateSummary(list: Cliente[]) {
    const ativos = list.filter(c => c.ativo).length;
    const proprietarios = list.filter(c => c.tipo === 'PROPRIETARIO' || c.tipo === 'AMBOS').length;
    const interessados = list.filter(c => c.tipo === 'INTERESSADO' || c.tipo === 'AMBOS').length;
    
    const pj = list.filter(c => c.tipo_pessoa === 'JURIDICA').length;
    const pf = list.filter(c => c.tipo_pessoa === 'FISICA').length; 

    sumarioClientes.value = {
        ativos,
        proprietarios,
        interessados,
        pj,
        pf, 
        total: list.length
    };
}

function setFilter(key: 'status' | 'tipo_pessoa', value: string) {
    if (key === 'status') {
        // Toggle
        if (filters.value.status === value) {
             filters.value.status = '';
        } else {
             filters.value.status = value;
        }
        filters.value.tipo_pessoa = ''; // Reseta o outro filtro
    } else if (key === 'tipo_pessoa') {
         if (filters.value.tipo_pessoa === value) {
             filters.value.tipo_pessoa = '';
        } else {
             filters.value.tipo_pessoa = value;
        }
        filters.value.status = ''; // Reseta o status para ver todos desse tipo
    }
}

function resetFilters() {
    filters.value.status = '';
    filters.value.tipo_pessoa = '';
    searchTerm.value = '';
}

const filteredClientes = computed(() => {
  let list = clientes.value;
  const lowerSearch = searchTerm.value.toLowerCase();
  
  // 1. Filtrar por termo de busca
  if (lowerSearch) {
      list = list.filter(cliente =>
        (cliente.nome_exibicao?.toLowerCase().includes(lowerSearch)) ||
        (cliente.nome?.toLowerCase().includes(lowerSearch)) ||
        (cliente.razao_social?.toLowerCase().includes(lowerSearch)) ||
        (cliente.email?.toLowerCase().includes(lowerSearch)) ||
        (cliente.telefone?.includes(searchTerm.value)) ||
        (cliente.documento?.includes(searchTerm.value)) 
      );
  }

  // 2. Filtrar por Status
  if (filters.value.status === 'ATIVO') {
      list = list.filter(c => c.ativo === true);
  } else if (filters.value.status === 'INATIVO') {
      list = list.filter(c => c.ativo === false);
  }
  
  // 3. Filtrar por Tipo de Pessoa
  if (filters.value.tipo_pessoa === 'JURIDICA') {
      list = list.filter(c => c.tipo_pessoa === 'JURIDICA');
  } else if (filters.value.tipo_pessoa === 'FISICA') {
      list = list.filter(c => c.tipo_pessoa === 'FISICA');
  }
  
  return list;
});

function editCliente(id: number) {
  router.push({ name: 'cliente-editar', params: { id } });
}

onMounted(fetchClientes);
</script>

<style scoped>
.page-container {
  padding: 0;
}

/* ================================================== */
/* 1. Dashboard Grid (Estilo Padronizado) */
/* ================================================== */
.dashboard-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem; margin-bottom: 2rem;
}
.stat-card {
  background-color: #fff; border: 1px solid transparent; border-radius: 12px; padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04); display: flex; align-items: center; gap: 1rem;
  transition: transform 0.2s ease, border-color 0.2s;
}
.clickable-card { cursor: pointer; }
.clickable-card:hover { transform: translateY(-3px); }

/* Feedback visual de filtro ativo */
.active-card {
    border-color: #007bff;
    background-color: #f8fbff;
    box-shadow: 0 6px 12px rgba(0, 123, 255, 0.15);
}

.stat-icon {
    width: 50px; height: 50px; border-radius: 12px; background-color: #e7f1ff; color: #0d6efd;
    display: flex; align-items: center; justify-content: center; font-size: 1.5rem;
}
.stat-ativo .stat-icon { background-color: #d1e7dd; color: #198754; }
.stat-info h3 { font-size: 0.8rem; color: #6c757d; font-weight: 600; margin: 0; text-transform: uppercase; }
.stat-info p { font-size: 1.5rem; font-weight: 700; color: #212529; margin: 0; }
.stat-ativo p { color: #198754; }


/* ================================================== */
/* 2. Barra de Filtros (Padronizada) */
/* ================================================== */
.search-and-filter-bar {
  display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem;
  align-items: center; background-color: transparent; padding: 0; box-shadow: none;
}
.search-input {
  padding: 10px; border: 1px solid #ccc; border-radius: 5px; width: 100%; max-width: 350px; 
  box-sizing: border-box; font-family: system-ui, sans-serif; font-size: 0.95rem;
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
/* 3. Grid de Clientes & Componentes de Estado */
/* ================================================== */
.loading-message, .error-message, .empty-state {
  text-align: center; padding: 4rem 2rem; color: #6c757d;
  background-color: #fff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}
.empty-icon { font-size: 3rem; color: #dee2e6; margin-bottom: 1rem; }
.error-message { color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; }
.spinner {
  border: 3px solid #e9ecef; border-top: 3px solid #0d6efd; border-radius: 50%;
  width: 40px; height: 40px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }


.clientes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.5rem; padding-bottom: 2rem;
}

.cliente-card {
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.04);
  border: 1px solid rgba(0,0,0,0.05);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  position: relative;
}

.cliente-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.1);
  border-color: rgba(0,123,255, 0.2);
}

.cliente-profile-pic {
  width: 80px; height: 80px; border-radius: 50%; overflow: hidden;
  margin-bottom: 1rem; background-color: #e9ecef;
  display: flex; justify-content: center; align-items: center;
  border: 3px solid #fff;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.profile-img { width: 100%; height: 100%; object-fit: cover; }
.profile-icon { font-size: 40px; color: #adb5bd; }

.cliente-info { margin-bottom: 1rem; width: 100%; }

.cliente-nome {
  font-size: 1.1rem; font-weight: 700; margin: 0 0 0.5rem 0; color: #343a40;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.cliente-contato {
  margin: 0.25rem 0; color: #6c757d; font-size: 0.9rem;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.cliente-contato.tipo-pessoa {
    font-size: 0.8rem; margin-top: 0.5rem; color: #007bff; font-weight: 500;
    background-color: #e7f1ff; display: inline-block; padding: 2px 8px; border-radius: 10px;
}
.cliente-contato.tipo-pessoa i { margin-right: 4px; }

.cliente-tags {
  display: flex; flex-wrap: wrap; justify-content: center; gap: 0.5rem;
  margin-top: auto; width: 100%;
}

.tag {
  padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 700;
  color: #fff; text-transform: uppercase;
}
.tag.proprietario { background-color: #198754; }
.tag.interessado { background-color: #0d6efd; }
.tag.ambos { background-color: #6f42c1; }
.tag.inativo { background-color: #6c757d; }

</style>