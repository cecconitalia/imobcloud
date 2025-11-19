<template>
  <div class="page-container">
    
    <div class="header-actions">
      <div class="header-title">
        <h2>Contas Bancárias / Caixas</h2>
        <span class="subtitle">Gerencie onde o dinheiro entra e sai</span>
      </div>
      <button @click="adicionarConta" class="btn-add">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
        Nova Conta
      </button>
    </div>

    <div v-if="isLoading" class="state-box loading">
      <div class="spinner"></div>
      <p>A carregar as suas contas...</p>
    </div>

    <div v-else-if="error" class="state-box error">
      <p>{{ error }}</p>
    </div>

    <div v-else class="content-card">
      
      <div class="toolbar">
        <div class="search-wrapper">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="search-icon"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input 
            type="text" 
            v-model="searchTerm" 
            placeholder="Pesquisar por nome..." 
            class="search-input"
          >
        </div>
      </div>

      <div v-if="filteredContas.length === 0" class="empty-state">
        <div class="empty-icon">🏦</div>
        <h3>Nenhuma conta encontrada</h3>
        <p v-if="searchTerm">Não encontramos resultados para "{{ searchTerm }}".</p>
        <p v-else>Cadastre a sua primeira conta bancária ou caixa físico.</p>
      </div>
      
      <div v-else class="table-responsive">
        <table class="modern-table">
          <thead>
            <tr>
              <th>Nome da Conta</th>
              <th>Saldo Atual (Real)</th>
              <th class="actions-col">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="conta in filteredContas" :key="conta.id">
              <td>
                <div class="conta-info">
                  <span class="conta-icon">💰</span>
                  <span class="conta-name">{{ conta.nome }}</span>
                </div>
              </td>
              <td class="font-mono" :class="getSaldoClass(conta.saldo_atual)">
                {{ formatarValor(conta.saldo_atual) }}
              </td>
              <td class="actions-cell">
                <button @click="editarConta(conta.id)" class="btn-icon edit" title="Editar">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                </button>
                <button @click="excluirConta(conta.id)" class="btn-icon delete" title="Excluir">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';

// Interface ajustada para receber o campo calculado do backend
interface Conta {
    id: number;
    nome: string;
    saldo_inicial: number; 
    saldo_atual: number; // <--- Campo corrigido
}

const router = useRouter();
const contas = ref<Conta[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');

async function fetchContas() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get<Conta[]>('/v1/financeiro/contas/');
    contas.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar contas:", err);
    error.value = 'Não foi possível carregar as contas bancárias.';
  } finally {
    isLoading.value = false;
  }
}

const filteredContas = computed(() => {
    let filtered = contas.value;
    
    if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase();
        filtered = filtered.filter(conta =>
            conta.nome.toLowerCase().includes(term)
        );
    }
    return filtered;
});

function formatarValor(valor: number | string): string {
    const num = typeof valor === 'string' ? parseFloat(valor) : valor;
    // Proteção contra NaN
    if (isNaN(num)) return 'R$ 0,00';
    return num.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

// Função auxiliar para colorir o saldo
function getSaldoClass(valor: number): string {
    if (valor > 0) return 'text-green-600';
    if (valor < 0) return 'text-red-600';
    return 'text-gray-600';
}

function adicionarConta() {
    router.push({ name: 'conta-nova' });
}

function editarConta(id: number) {
    router.push({ name: 'conta-editar', params: { id } });
}

async function excluirConta(id: number) {
    if (window.confirm("Tem certeza que deseja excluir esta conta?")) {
        try {
            await apiClient.delete(`/v1/financeiro/contas/${id}/`);
            contas.value = contas.value.filter(c => c.id !== id);
        } catch (err) {
            alert('Não foi possível excluir a conta. Verifique se há transações vinculadas.');
        }
    }
}

onMounted(() => {
    fetchContas();
});
</script>

<style scoped>
.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 40px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: #334155;
}

/* --- Header --- */
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.header-title h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}
.subtitle {
  font-size: 0.875rem;
  color: #64748b;
}

.btn-add {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #0f172a;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-add:hover { background-color: #334155; }

/* --- States --- */
.state-box {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.error { color: #dc2626; background: #fef2f2; border: 1px solid #fecaca; }
.spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #0f172a;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* --- Card & Toolbar --- */
.content-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border: 1px solid #f1f5f9;
  overflow: hidden;
}

.toolbar {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  background-color: #f8fafc;
}

.search-wrapper {
  position: relative;
  max-width: 300px;
}
.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
}
.search-input {
  width: 100%;
  padding: 10px 12px 10px 38px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s;
}
.search-input:focus { border-color: #3b82f6; }

/* --- Table --- */
.table-responsive { overflow-x: auto; }
.modern-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}
.modern-table th {
  background-color: #f8fafc;
  padding: 12px 16px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #64748b;
  border-bottom: 1px solid #e2e8f0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.modern-table td {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
  font-size: 0.95rem;
}
.modern-table tr:last-child td { border-bottom: none; }
.modern-table tr:hover { background-color: #f8fafc; }

.conta-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
.conta-icon {
  font-size: 1.2rem;
  background: #e0f2fe;
  padding: 6px;
  border-radius: 8px;
}
.conta-name { font-weight: 600; }

.font-mono { font-family: 'Courier New', Courier, monospace; font-weight: 600; }
.text-green-600 { color: #16a34a; }
.text-red-600 { color: #dc2626; }
.text-gray-600 { color: #4b5563; }

/* --- Actions --- */
.actions-cell { text-align: right; }
.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: background 0.2s;
  margin-left: 4px;
}
.btn-icon.edit { color: #3b82f6; }
.btn-icon.edit:hover { background: #eff6ff; }
.btn-icon.delete { color: #ef4444; }
.btn-icon.delete:hover { background: #fef2f2; }

/* --- Empty State --- */
.empty-state {
  padding: 40px;
  text-align: center;
  color: #64748b;
}
.empty-icon { font-size: 3rem; margin-bottom: 10px; }
</style>