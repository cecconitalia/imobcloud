<script setup lang="ts">
/**
 * IMOBCLOUD - GESTÃO DE VISTORIAS (LISTAGEM AGRUPADA)
 * Engenharia de Software Full Stack Sênior
 * * Atualização: Remoção do botão de PDF (Laudo) da listagem conforme solicitado.
 * O acesso ao laudo deve ser feito através dos detalhes ou outra área específica.
 */
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api';
import { format } from 'date-fns';
import VistoriaDetalhesModal from '@/components/Vistorias/VistoriaDetalhesModal.vue';

// --- Interfaces Estritas ---
interface Vistoria {
  id: number;
  contrato: number;
  tipo: 'ENTRADA' | 'SAIDA' | 'PERIODICA';
  tipo_display: string;
  data_vistoria: string;
  realizado_por_nome: string;
  imovel_display: string;
  concluida: boolean;
  assinatura_responsavel: string | null;
  assinatura_locatario: string | null;
  assinatura_proprietario: string | null;
  exige_assinatura_proprietario: boolean;
}

interface GroupedContract {
  contratoId: number;
  imovelDisplay: string;
  entrada: Vistoria | null;
  saida: Vistoria | null;
  periodicas: Vistoria[];
}

interface ContratoRef {
  id: number;
  imovel_display: string;
}

// --- Estado Reativo ---
const router = useRouter();
const vistorias = ref<Vistoria[]>([]);
const contratos = ref<ContratoRef[]>([]);
const loading = ref<boolean>(true);
const searchQuery = ref<string>('');
const filterTipo = ref<string | null>(null);
const showDetalhesModal = ref<boolean>(false);
const selectedVistoriaId = ref<number | null>(null);

// --- Lógica de Agrupamento por Imóvel ---
const groupedVistorias = computed<GroupedContract[]>(() => {
  if (!vistorias.value || !Array.isArray(vistorias.value)) return [];
  
  const groups: Record<number, GroupedContract> = {};

  vistorias.value.forEach((v) => {
    if (!v || !v.contrato) return;
    const cId = v.contrato;
    
    if (!groups[cId]) {
      const contratoRef = contratos.value.find(c => c.id === cId);
      groups[cId] = {
        contratoId: cId,
        imovelDisplay: contratoRef ? contratoRef.imovel_display : (v.imovel_display || `Contrato #${cId}`),
        entrada: null,
        saida: null,
        periodicas: []
      };
    }

    if (v.tipo === 'ENTRADA') {
      groups[cId].entrada = v;
    } else if (v.tipo === 'SAIDA') {
      groups[cId].saida = v;
    } else {
      groups[cId].periodicas.push(v);
    }
  });

  return Object.values(groups).sort((a, b) => b.contratoId - a.contratoId);
});

// --- Métodos de Dados ---
const fetchContratos = async (): Promise<void> => {
  try {
    const response = await api.get('/v1/contratos/');
    const rawData = response.data.results || response.data;
    contratos.value = rawData.map((c: any) => {
      let display = `Imóvel #${c.imovel}`;
      if (c.imovel_detalhes) {
        if (c.imovel_detalhes.endereco_completo) display = c.imovel_detalhes.endereco_completo;
        else if (c.imovel_detalhes.logradouro) display = `${c.imovel_detalhes.logradouro}, ${c.imovel_detalhes.numero || ''}`;
      }
      return { id: c.id, imovel_display: display };
    });
  } catch (error) {
    console.error('Erro ao carregar contratos:', error);
  }
};

const fetchVistorias = async (): Promise<void> => {
  loading.value = true;
  try {
    const params: any = {};
    if (filterTipo.value) params.tipo = filterTipo.value;
    if (searchQuery.value) params.search = searchQuery.value;

    const response = await api.get('/v1/vistorias/vistorias/', { params });
    const data = response.data;
    vistorias.value = data.results ? data.results : (Array.isArray(data) ? data : []);
  } catch (error) {
    vistorias.value = [];
  } finally {
    loading.value = false;
  }
};

// --- Ações ---
let searchTimeout: ReturnType<typeof setTimeout> | null = null;
const handleSearch = (): void => {
  if (searchTimeout) clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => fetchVistorias(), 500);
};

const navigateToForm = (): void => {
  router.push({ name: 'vistoria-nova' });
};

const navigateToExecution = (id: number): void => {
  router.push({ name: 'vistoria-checklist', params: { id } });
};

const openDetalhesModal = (id: number): void => { 
  selectedVistoriaId.value = id; 
  showDetalhesModal.value = true; 
};

const closeDetalhesModal = (): void => { 
  showDetalhesModal.value = false; 
  selectedVistoriaId.value = null; 
  fetchVistorias(); 
};

const handleDelete = async (id: number): Promise<void> => {
  if (!confirm("Tem certeza que deseja excluir esta vistoria? Esta ação não pode ser desfeita.")) return;
  try {
    await api.delete(`/v1/vistorias/vistorias/${id}/`);
    await fetchVistorias();
  } catch (error: any) {
    alert(error.response?.data?.detail || "Erro ao excluir a vistoria.");
  }
};

const criarSaidaDaEntrada = async (vistoriaEntrada: Vistoria): Promise<void> => {
  if (!confirm(`Gerar a Vistoria de Saída baseada na Entrada #${vistoriaEntrada.id}?`)) return;
  try {
    loading.value = true;
    const payload = { data_vistoria: new Date().toISOString().split('T')[0] };
    const res = await api.post(`/v1/vistorias/vistorias/${vistoriaEntrada.id}/gerar-saida-da-entrada/`, payload);
    navigateToExecution(res.data.id);
  } catch (err: any) {
    alert(err.response?.data?.error || 'Erro ao gerar vistoria de saída.');
    loading.value = false;
  }
};

const formatDate = (dateString: string): string => {
  if (!dateString) return '--/--';
  try { return format(new Date(dateString), 'dd/MM/yyyy'); } catch { return dateString; }
};

onMounted(async () => {
  await fetchContratos();
  await fetchVistorias();
});
</script>

<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1>Gestão de Vistorias</h1>
          <p class="subtitle">Acompanhe a entrada e saída por imóvel no mesmo painel agrupado.</p>
        </div>
        <div class="header-actions">
          <button class="btn-add active:scale-95" @click="navigateToForm">
            <i class="fas fa-plus"></i> Nova Vistoria
          </button>
        </div>
      </div>
    </header>

    <main class="main-content">
      <div class="filter-bar">
        <div class="search-group">
          <i class="fas fa-search search-icon"></i>
          <input 
            type="text" 
            placeholder="Buscar por endereço, ID ou contrato..." 
            v-model="searchQuery"
            @input="handleSearch"
          >
        </div>

        <div class="filter-group">
          <select v-model="filterTipo" @change="fetchVistorias" class="select-field">
            <option :value="null">Todos os Tipos</option>
            <option value="ENTRADA">Entrada</option>
            <option value="SAIDA">Saída</option>
            <option value="PERIODICA">Periódica</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="state-container">
        <div class="spinner"></div>
        <p>Sincronizando vistorias...</p>
      </div>

      <div v-else-if="groupedVistorias.length === 0" class="state-container empty">
        <i class="fas fa-folder-open empty-icon"></i>
        <h3>Nenhuma vistoria encontrada</h3>
        <p>Ajuste seus filtros ou inicie uma nova vistoria de entrada.</p>
      </div>

      <div v-else class="cards-grid">
        <div 
            class="vistoria-card card-agrupado" 
            v-for="group in groupedVistorias" 
            :key="group.contratoId"
        >
          <div class="card-header-imovel">
            <h4 class="address-title" :title="group.imovelDisplay">
              <i class="fas fa-building inline mr-1 text-blue-500"></i>
              {{ group.imovelDisplay }}
            </h4>
            <span class="contrato-badge">Contrato #{{ group.contratoId }}</span>
          </div>

          <div class="card-body-agrupado">
            <div class="secao-vistoria">
              <div class="secao-header">
                <span class="type-badge bg-emerald-100 text-emerald-700">Entrada</span>
                <div v-if="group.entrada" class="status-indicator" :class="group.entrada.concluida ? 'success' : 'warning'">
                  {{ group.entrada.concluida ? 'OK' : 'Aberto' }}
                </div>
              </div>
              
              <div v-if="group.entrada" class="secao-content">
                <div class="info-row-small">
                  <span>#{{ group.entrada.id }}</span>
                  <span>{{ formatDate(group.entrada.data_vistoria) }}</span>
                </div>
                <div class="secao-actions">
                  <button v-if="!group.entrada.concluida" class="btn-icon" @click="navigateToExecution(group.entrada.id)" title="Editar / Executar">
                    <i class="fas fa-pencil-alt"></i>
                  </button>

                  <button class="btn-icon" @click="openDetalhesModal(group.entrada.id)" title="Visualizar Detalhes">
                    <i class="fas fa-eye"></i>
                  </button>
                  
                  <button v-if="!group.entrada.concluida" class="btn-icon delete" @click="handleDelete(group.entrada.id)" title="Excluir">
                    <i class="fas fa-trash-alt"></i>
                  </button>
                </div>
                
                <button 
                  v-if="group.entrada.concluida && !group.saida"
                  class="btn-shortcut active:scale-95"
                  @click="criarSaidaDaEntrada(group.entrada)"
                >
                  <i class="fas fa-arrow-right"></i> Gerar Saída
                </button>
              </div>
              <div v-else class="secao-empty">
                <small>Sem entrada</small>
              </div>
            </div>

            <div class="divider-v"></div>

            <div class="secao-vistoria">
              <div class="secao-header">
                <span class="type-badge bg-rose-100 text-rose-700">Saída</span>
                <div v-if="group.saida" class="status-indicator" :class="group.saida.concluida ? 'success' : 'warning'">
                  {{ group.saida.concluida ? 'OK' : 'Aberto' }}
                </div>
              </div>

              <div v-if="group.saida" class="secao-content">
                <div class="info-row-small">
                  <span>#{{ group.saida.id }}</span>
                  <span>{{ formatDate(group.saida.data_vistoria) }}</span>
                </div>
                <div class="secao-actions">
                  <button v-if="!group.saida.concluida" class="btn-icon" @click="navigateToExecution(group.saida.id)" title="Editar / Conferir">
                    <i class="fas fa-pencil-alt"></i>
                  </button>

                  <button class="btn-icon" @click="openDetalhesModal(group.saida.id)" title="Visualizar Detalhes">
                    <i class="fas fa-eye"></i>
                  </button>
                  
                  <button v-if="!group.saida.concluida" class="btn-icon delete" @click="handleDelete(group.saida.id)" title="Excluir">
                    <i class="fas fa-trash-alt"></i>
                  </button>
                </div>
              </div>
              <div v-else class="secao-empty">
                <small>Aguardando</small>
              </div>
            </div>
          </div>

          <div v-if="group.periodicas.length > 0" class="card-footer-periodicas">
            <span class="periodica-label"><i class="fas fa-calendar-alt"></i> Outras:</span>
            <div class="periodica-pills">
              <button v-for="p in group.periodicas" :key="p.id" @click="openDetalhesModal(p.id)" class="pill-btn">
                #{{ p.id }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <VistoriaDetalhesModal 
      :show="showDetalhesModal" 
      :vistoriaId="selectedVistoriaId" 
      @close="closeDetalhesModal"
      @refresh="fetchVistorias"
    />

  </div>
</template>

<style scoped>
/* Design System ImobCloud - Vistorias */
.page-container {
  min-height: 100vh;
  background-color: #f8fafc;
  padding-bottom: 80px;
  font-family: 'Inter', sans-serif;
}

.page-header {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
}

.header-content {
  max-width: 1600px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-text h1 { font-size: 1.5rem; font-weight: 800; color: #0f172a; margin: 0; letter-spacing: -0.025em; }
.subtitle { color: #64748b; font-size: 0.875rem; margin-top: 0.25rem; }

.btn-add {
  background: #2563eb;
  color: white;
  border: none;
  padding: 0.625rem 1.25rem;
  border-radius: 0.75rem;
  font-weight: 600;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
}

.main-content {
  padding: 0 2rem;
  max-width: 1600px;
  margin: 0 auto;
}

/* Filtros */
.filter-bar {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 2rem;
}

.search-group {
  position: relative;
  flex: 1;
  max-width: 600px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
}

.search-group input {
  width: 100%;
  padding: 0.625rem 1rem 0.625rem 2.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  background: white;
  outline: none;
  transition: border-color 0.2s;
}

.search-group input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.select-field {
  padding: 0.625rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  background: white;
}

/* --- GRID DE 4 COLUNAS --- */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 1.5rem;
}

/* Breakpoints para a grade responsiva */
@media (min-width: 640px) { .cards-grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1024px) { .cards-grid { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 1440px) { .cards-grid { grid-template-columns: repeat(4, 1fr); } }

/* Estilo do Card Agrupado */
.vistoria-card {
  background: white;
  border-radius: 1rem;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.vistoria-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px -5px rgba(0,0,0,0.1);
  border-color: #cbd5e1;
}

.card-header-imovel {
  padding: 1.25rem;
  background: #f8fafc;
  border-bottom: 1px solid #f1f5f9;
}

.address-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.contrato-badge {
  font-size: 0.625rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  margin-top: 0.375rem;
  display: block;
}

.card-body-agrupado {
  display: flex;
  padding: 1.25rem;
  gap: 1rem;
  flex: 1;
}

.secao-vistoria {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.secao-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.type-badge {
  font-size: 0.5625rem;
  font-weight: 800;
  text-transform: uppercase;
  padding: 0.125rem 0.375rem;
  border-radius: 0.375rem;
}

.status-indicator {
  font-size: 0.625rem;
  font-weight: 800;
}
.status-indicator.success { color: #10b981; }
.status-indicator.warning { color: #f59e0b; }

.secao-content { display: flex; flex-direction: column; gap: 0.5rem; }

.info-row-small {
  font-size: 0.6875rem;
  color: #64748b;
  display: flex;
  justify-content: space-between;
  font-weight: 600;
}

.secao-actions { display: flex; gap: 0.375rem; }

.btn-icon {
  width: 1.75rem;
  height: 1.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: #f1f5f9;
  color: #2563eb;
  border-color: #3b82f6;
}

.btn-icon.delete:hover {
  background: #fef2f2;
  color: #ef4444;
  border-color: #fecaca;
}

.btn-shortcut {
  margin-top: 0.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.4375rem;
  border-radius: 0.5rem;
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.2);
}

.secao-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  border-radius: 0.5rem;
  border: 1px dashed #e2e8f0;
  color: #94a3b8;
  min-height: 60px;
  font-size: 0.6875rem;
  font-style: italic;
}

.divider-v { width: 1px; background: #f1f5f9; }

.card-footer-periodicas {
  padding: 0.75rem 1.25rem;
  border-top: 1px solid #f1f5f9;
  background: #fafafa;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.periodica-label {
  font-weight: 800;
  color: #94a3b8;
  text-transform: uppercase;
  font-size: 0.5625rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.periodica-pills { display: flex; gap: 0.375rem; overflow-x: auto; }
.pill-btn {
  background: white;
  border: 1px solid #e2e8f0;
  padding: 0.125rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.6875rem;
  font-weight: 700;
  cursor: pointer;
  color: #64748b;
  white-space: nowrap;
}

/* States */
.state-container { text-align: center; padding: 5rem; color: #94a3b8; }
.spinner { width: 2rem; height: 2rem; border: 3px solid #e2e8f0; border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s infinite linear; margin: 0 auto 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }

.empty-icon { font-size: 3rem; margin-bottom: 1rem; opacity: 0.5; }

.active\:scale-95:active { transform: scale(0.95); }
</style>