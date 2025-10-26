<template>
  <div class="clientes-container">
    <div class="search-and-filter-bar">
      <input
        type="text"
        v-model="searchTerm"
        placeholder="Pesquisar por nome, email, documento..."
        class="search-input"
      />
      </div>

    <div v-if="isLoading" class="loading-message">A carregar...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="clientes.length > 0" class="clientes-grid">
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
  foto_perfil?: string;
  tipo: 'PROPRIETARIO' | 'INTERESSADO' | 'AMBOS';
  ativo: boolean;
}

const clientes = ref<Cliente[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');
const router = useRouter();

async function fetchClientes() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get<Cliente[]>('/v1/clientes/');
    clientes.value = response.data;
  } catch (err: any) {
    console.error("Erro ao buscar clientes:", err);
    error.value = err.response?.data?.detail || 'Não foi possível carregar os clientes.';
  } finally {
    isLoading.value = false;
  }
}

const filteredClientes = computed(() => {
  if (!searchTerm.value) {
    return clientes.value;
  }
  const lowerSearch = searchTerm.value.toLowerCase();
  return clientes.value.filter(cliente =>
    (cliente.nome_completo?.toLowerCase().includes(lowerSearch)) ||
    (cliente.razao_social?.toLowerCase().includes(lowerSearch)) ||
    (cliente.email?.toLowerCase().includes(lowerSearch)) ||
    (cliente.telefone?.includes(searchTerm.value)) // Telefone geralmente não precisa de lowercase
    // Adicionar busca por CPF/CNPJ se o campo existir na interface Cliente
  );
});

function editCliente(id: number) {
  router.push({ name: 'cliente-editar', params: { id } });
}

onMounted(fetchClientes);
</script>

<style scoped>
.clientes-container {
  padding: 0; /* Espaçamento removido */
}

/* Regras .view-header, .header-actions removidas */

.search-and-filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  /* CORREÇÃO APLICADA AQUI */
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

.btn-primary { /* Estilo do botão que foi removido do header */
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