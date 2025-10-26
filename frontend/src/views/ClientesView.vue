<template>
  <div class="clientes-container">
    
    <div v-if="sumarioClientes" class="summary-cards">
      <div 
        class="card" 
        @click="setFilter('status', 'ATIVO')" 
        :class="{ active: filters.status === 'ATIVO' }"
      >
        <p class="card-value">{{ sumarioClientes.ativos }}</p>
        <p class="card-label">Clientes Ativos</p>
      </div>
      <div 
        class="card" 
        @click="setFilter('tipo', 'PROPRIETARIO_OU_AMBOS')" 
        :class="{ active: filters.tipo === 'PROPRIETARIO_OU_AMBOS' }"
      >
        <p class="card-value">{{ sumarioClientes.proprietarios }}</p>
        <p class="card-label">Proprietários</p>
      </div>
      <div 
        class="card" 
        @click="setFilter('tipo', 'INTERESSADO_OU_AMBOS')" 
        :class="{ active: filters.tipo === 'INTERESSADO_OU_AMBOS' }"
      >
        <p class="card-value">{{ sumarioClientes.interessados }}</p>
        <p class="card-label">Interessados (Leads)</p>
      </div>
      <div 
        class="card" 
        @click="setFilter('tipo_pessoa', 'PJ')" 
        :class="{ active: filters.tipo_pessoa === 'PJ' }"
      >
        <p class="card-value">{{ sumarioClientes.pj }}</p>
        <p class="card-label">Pessoa Jurídica</p>
      </div>
    </div>
    <div class="search-and-filter-bar">
      <input
        type="text"
        v-model="searchTerm"
        placeholder="Pesquisar por nome, email, documento..."
        class="search-input"
      />
      
      <div class="filter-group">
        <label for="tipo">Tipo:</label>
        <select id="tipo" v-model="filters.tipo">
          <option value="">Todos</option>
          <option value="PROPRIETARIO">Proprietário</option>
          <option value="INTERESSADO">Interessado</option>
          <option value="AMBOS">Ambos</option>
        </select>
      </div>
      
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
          <option value="PF">Física</option>
          <option value="PJ">Jurídica</option>
        </select>
      </div>
      <button @click="goToCreateCliente" class="btn-add">
        <i class="fas fa-plus"></i> Adicionar Cliente
      </button>
    </div>

    <div v-if="isLoading" class="loading-message">A carregar...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="filteredClientes.length > 0" class="clientes-grid">
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
          <h3 class="cliente-nome">{{ cliente.nome_completo || cliente.razao_social || 'Nome não disponível' }}</h3>
          <p class="cliente-contato">{{ cliente.email || 'Email não informado'}}</p>
          <p class="cliente-contato">{{ cliente.telefone || 'Telefone não informado' }}</p>
          <p class="cliente-contato tipo-pessoa">({{ cliente.tipo_pessoa === 'PF' ? 'Pessoa Física' : 'Pessoa Jurídica' }})</p>
        </div>
        <div class="cliente-tags">
          <span v-if="cliente.tipo === 'PROPRIETARIO'" class="tag proprietario">Proprietário</span>
          <span v-if="cliente.tipo === 'INTERESSADO'" class="tag interessado">Interessado</span>
          <span v-if="cliente.tipo === 'AMBOS'" class="tag ambos">Ambos</span>
          <span v-if="!cliente.ativo" class="tag inativo">Inativo</span>
        </div>
      </div>
    </div>
    <div v-else-if="!isLoading && !error" class="empty-message">
      Nenhum cliente encontrado.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';

interface Cliente {
  id: number;
  nome_completo?: string; // PF
  razao_social?: string; // PJ
  tipo_pessoa: 'PF' | 'PJ';
  email?: string;
  telefone?: string;
  documento?: string; // Assumindo que este campo existe para pesquisa
  foto_perfil?: string;
  tipo: 'PROPRIETARIO' | 'INTERESSADO' | 'AMBOS';
  ativo: boolean;
}

const clientes = ref<Cliente[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');
const router = useRouter();

// Variável para armazenar os dados do sumário
const sumarioClientes = ref<any>(null);

// NOVO: Estrutura explícita para os filtros de dropdown
const filters = ref({
    tipo: '', // PROPRIETARIO, INTERESSADO, AMBOS, PROPRIETARIO_OU_AMBOS, INTERESSADO_OU_AMBOS
    status: 'ATIVO', // ATIVO | INATIVO | TODOS
    tipo_pessoa: '', // PF | PJ
});
// FIM NOVO

async function fetchClientes() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get<Cliente[]>('/v1/clientes/');
    clientes.value = response.data;
    // Calcular sumário após buscar clientes
    calculateSummary(clientes.value);
  } catch (err: any) {
    console.error("Erro ao buscar clientes:", err);
    error.value = err.response?.data?.detail || 'Não foi possível carregar os clientes.';
  } finally {
    isLoading.value = false;
  }
}

// Função para calcular o sumário (MANTIDA)
function calculateSummary(list: Cliente[]) {
    const ativos = list.filter(c => c.ativo).length;
    const proprietarios = list.filter(c => c.tipo === 'PROPRIETARIO' || c.tipo === 'AMBOS').length;
    const interessados = list.filter(c => c.tipo === 'INTERESSADO' || c.tipo === 'AMBOS').length;
    const pj = list.filter(c => c.tipo_pessoa === 'PJ').length;

    sumarioClientes.value = {
        ativos,
        proprietarios,
        interessados,
        pj,
        total: list.length
    };
}

// NOVO: Função para definir o filtro através do clique nos cards
function setFilter(key: 'tipo' | 'status' | 'tipo_pessoa', value: any) {
    
    let targetKey = key;
    let targetValue = value;

    // Se o filtro vier do card e for Proprietário/Interessado, ajusta o valor do filtro
    if (key === 'tipo' && (value === 'PROPRIETARIO_OU_AMBOS' || value === 'INTERESSADO_OU_AMBOS')) {
        // Se o valor atual do filtro já for esse, zera o filtro, senão aplica
        if (filters.value.tipo === targetValue) {
            filters.value.tipo = '';
        } else {
            filters.value.tipo = targetValue as string;
        }
        // Limpar outros filtros que não são de Tipo
        filters.value.status = 'ATIVO';
        filters.value.tipo_pessoa = '';

    } else if (key === 'status') {
        if (filters.value.status === targetValue) {
             filters.value.status = '';
        } else {
             filters.value.status = targetValue as string;
        }
        // Limpar outros filtros
        filters.value.tipo = '';
        filters.value.tipo_pessoa = '';
    } else if (key === 'tipo_pessoa') {
         if (filters.value.tipo_pessoa === targetValue) {
             filters.value.tipo_pessoa = '';
        } else {
             filters.value.tipo_pessoa = targetValue as string;
        }
        // Limpar outros filtros
        filters.value.tipo = '';
        filters.value.status = 'ATIVO';
    }
}
// FIM NOVO


const filteredClientes = computed(() => {
  let list = clientes.value;
  const lowerSearch = searchTerm.value.toLowerCase();
  
  // 1. Filtrar por termo de busca
  if (lowerSearch) {
      list = list.filter(cliente =>
        (cliente.nome_completo?.toLowerCase().includes(lowerSearch)) ||
        (cliente.razao_social?.toLowerCase().includes(lowerSearch)) ||
        (cliente.email?.toLowerCase().includes(lowerSearch)) ||
        (cliente.telefone?.includes(searchTerm.value)) ||
        (cliente.documento?.includes(searchTerm.value)) // Assumindo campo documento existe
      );
  }

  // 2. Filtrar por Status (Dropdown/Card)
  if (filters.value.status === 'ATIVO') {
      list = list.filter(c => c.ativo === true);
  } else if (filters.value.status === 'INATIVO') {
      list = list.filter(c => c.ativo === false);
  }
  
  // 3. Filtrar por Tipo de Pessoa (Dropdown/Card)
  if (filters.value.tipo_pessoa === 'PJ') {
      list = list.filter(c => c.tipo_pessoa === 'PJ');
  } else if (filters.value.tipo_pessoa === 'PF') {
      list = list.filter(c => c.tipo_pessoa === 'PF');
  }

  // 4. Filtrar por Tipo de Cliente (Dropdown/Card)
  if (filters.value.tipo === 'PROPRIETARIO') {
      list = list.filter(c => c.tipo === 'PROPRIETARIO');
  } else if (filters.value.tipo === 'INTERESSADO') {
      list = list.filter(c => c.tipo === 'INTERESSADO');
  } else if (filters.value.tipo === 'AMBOS') {
      list = list.filter(c => c.tipo === 'AMBOS');
  } else if (filters.value.tipo === 'PROPRIETARIO_OU_AMBOS') {
      list = list.filter(c => c.tipo === 'PROPRIETARIO' || c.tipo === 'AMBOS');
  } else if (filters.value.tipo === 'INTERESSADO_OU_AMBOS') {
      list = list.filter(c => c.tipo === 'INTERESSADO' || c.tipo === 'AMBOS');
  }
  
  return list;
});

function editCliente(id: number) {
  router.push({ name: 'cliente-editar', params: { id } });
}

function goToCreateCliente() { 
    router.push({ name: 'cliente-novo' });
}

onMounted(fetchClientes);
</script>

<style scoped>
.clientes-container {
  padding: 0;
}

/* ESTILOS DO DASHBOARD (REUTILIZADOS DE IMOVEISVIEW) */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}
.card {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  text-align: center;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 12px rgba(0,0,0,0.1);
}
.card.active {
    border-color: #007bff;
    box-shadow: 0 6px 10px rgba(0, 123, 255, 0.2);
}
.card-value {
  font-size: 2.5rem;
  font-weight: bold;
  margin: 0;
  color: #007bff;
}
.card-label {
  margin: 0.5rem 0 0 0;
  color: #6c757d;
  font-size: 0.9rem;
}
/* FIM ESTILOS DO DASHBOARD */

.search-and-filter-bar {
  display: flex;
  flex-wrap: wrap; 
  justify-content: flex-start;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  background-color: transparent;
  padding: 0;
  box-shadow: none;
  border-radius: 0;
}

.search-input {
  padding: 10px 15px;
  border: 1px solid #ccc;
  border-radius: 5px;
  width: 100%;
  max-width: 400px;
  box-sizing: border-box;
  font-size: 1rem;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
}

/* NOVOS ESTILOS PARA FILTROS DE DROPDOWN */
.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: #555;
  white-space: nowrap;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 0.95rem;
  background-color: #f8f9fa;
  min-width: 120px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
}
/* FIM NOVOS ESTILOS */

/* Estilo do botão Adicionar Cliente (MANTIDO) */
.btn-add {
  background-color: #007bff;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s ease;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: auto; 
  width: auto;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
}

.btn-add:hover {
  background-color: #0056b3;
}


.loading-message, .error-message, .empty-message {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: #6c757d;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
}

.empty-message {
   margin-top: 1rem;
   background-color: #fff;
   padding: 2rem;
   border-radius: 8px;
   box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}


.clientes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.5rem;
}

.cliente-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.07);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
}

.cliente-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

.cliente-profile-pic {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  margin-bottom: 1rem;
  background-color: #e9ecef;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 2px solid #007bff;
}

.profile-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-icon {
  font-size: 40px;
  color: #6c757d;
}

.cliente-info {
  margin-bottom: 1rem;
}

.cliente-nome {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  color: #343a40;
}

.cliente-contato {
  margin: 0.2rem 0;
  color: #6c757d;
  font-size: 0.9rem;
  word-break: break-all;
}
.cliente-contato.tipo-pessoa {
    font-style: italic;
    font-size: 0.8rem;
    margin-top: 0.4rem;
}

.cliente-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.5rem;
  margin-top: auto;
  padding-top: 1rem;
}

.tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
  color: #fff;
}

.tag.proprietario { background-color: #198754; }
.tag.interessado { background-color: #0d6efd; }
.tag.ambos { background-color: #6f42c1; }
.tag.inativo { background-color: #6c757d; }

.btn-primary { 
  background-color: #007bff;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  text-decoration: none;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
}

.btn-primary i {
  margin-right: 8px;
}

.btn-primary:hover {
  background-color: #0056b3;
}
</style>