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
        @click="setFilter('tipo_pessoa', 'FISICA')" 
        :class="{ active: filters.tipo_pessoa === 'FISICA' }"
      >
        <p class="card-value">{{ sumarioClientes.pf }}</p>
        <p class="card-label">Pessoa Física</p>
      </div>

      <div 
        class="card" 
        @click="setFilter('tipo_pessoa', 'JURIDICA')" 
        :class="{ active: filters.tipo_pessoa === 'JURIDICA' }"
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
          <h3 class="cliente-nome">{{ cliente.nome_exibicao || 'Nome não disponível' }}</h3>
          <p class="cliente-contato">{{ cliente.email || 'Email não informado'}}</p>
          <p class="cliente-contato">{{ cliente.telefone || 'Telefone não informado' }}</p>
          <p class="cliente-contato tipo-pessoa">({{ cliente.tipo_pessoa === 'FISICA' ? 'Pessoa Física' : 'Pessoa Jurídica' }})</p>
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
    
    // CORREÇÃO: Adicionada a contagem de Pessoa Física
    const pj = list.filter(c => c.tipo_pessoa === 'JURIDICA').length;
    const pf = list.filter(c => c.tipo_pessoa === 'FISICA').length; 

    sumarioClientes.value = {
        ativos,
        proprietarios,
        interessados,
        pj,
        pf, // Adicionado ao objeto de sumário
        total: list.length
    };
}

function setFilter(key: 'status' | 'tipo_pessoa', value: any) {
    let targetValue = value;

    if (key === 'status') {
        // Se já estiver ativo, desativa, senão ativa
        if (filters.value.status === targetValue) {
             filters.value.status = '';
        } else {
             filters.value.status = targetValue as string;
        }
        filters.value.tipo_pessoa = '';
    } else if (key === 'tipo_pessoa') {
         if (filters.value.tipo_pessoa === targetValue) {
             filters.value.tipo_pessoa = '';
        } else {
             // Mapeia o valor para FISICA ou JURIDICA
             filters.value.tipo_pessoa = targetValue as string;
        }
        filters.value.status = 'ATIVO'; // Mudar filtro de pessoa reseta para ATIVO
    }
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

  // 2. Filtrar por Status (Dropdown/Card)
  if (filters.value.status === 'ATIVO') {
      list = list.filter(c => c.ativo === true);
  } else if (filters.value.status === 'INATIVO') {
      list = list.filter(c => c.ativo === false);
  }
  
  // 3. Filtrar por Tipo de Pessoa (Dropdown/Card)
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
  /* CORREÇÃO: Ajustado para 3 colunas (ATIVO, PF, PJ) */
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
/* CORREÇÃO: Mapeamento de 'FISICA' para o estilo ativo */
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

.btn-primary:hover {
  background-color: #0056b3;
}
</style>