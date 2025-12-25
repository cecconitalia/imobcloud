<script setup lang="ts">
/**
 * IMOBCLOUD - GESTÃO DE VISTORIAS (LAYOUT FINAL)
 * Engenharia de Software Full Stack Sênior
 * * Atualização: 
 * - Melhoria visual na Toolbar (Filtros e Botões).
 * - Select customizado e alinhamento perfeito de inputs.
 */
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api';
import { format } from 'date-fns';
import VistoriaDetalhesModal from '@/components/Vistorias/VistoriaDetalhesModal.vue';
import AssinaturaModal from '@/components/AssinaturaModal.vue'; 

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
  leitura_agua: string | null;
  leitura_luz: string | null;
  chaves_devolvidas: string | null;
}

interface GroupedContract {
  contratoId: number;
  imovelDisplay: string;
  locatario: string;
  locador: string;
  entrada: Vistoria | null;
  saida: Vistoria | null;
  periodicas: Vistoria[];
}

interface ContratoRef {
  id: number;
  imovel_display: string;
  locatario_nome: string;
  locador_nome: string;
}

interface AssinanteOption {
  label: string;
  value: string;
  signed?: boolean;
}

// --- Estado Reativo ---
const router = useRouter();
const vistorias = ref<Vistoria[]>([]);
const contratos = ref<ContratoRef[]>([]);
const loading = ref<boolean>(true);
const searchQuery = ref<string>('');
const filterTipo = ref<string | null>(null);

// Modais
const showDetalhesModal = ref<boolean>(false);
const selectedVistoriaId = ref<number | null>(null);

// Estado do Modal de Assinatura
const showAssinaturaModal = ref<boolean>(false);
const isSavingSignature = ref<boolean>(false);
const assinaturaTargetImovel = ref<string>('');
const assinaturaTargetId = ref<number | null>(null);
const assinantesDisponiveis = ref<AssinanteOption[]>([]); 

// --- Lógica de Agrupamento ---
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
        locatario: contratoRef ? contratoRef.locatario_nome : 'Carregando...',
        locador: contratoRef ? contratoRef.locador_nome : 'Carregando...',
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
      
      const locatario = c.inquilino_detalhes?.nome_display || c.inquilino_detalhes?.nome || 'N/D';
      const locador = c.proprietario_detalhes?.nome_display || c.proprietario_detalhes?.nome || 'N/D';

      return { 
        id: c.id, 
        imovel_display: display,
        locatario_nome: locatario,
        locador_nome: locador
      };
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

const navigateToForm = (): void => { router.push({ name: 'vistoria-nova' }); };
const navigateToExecution = (id: number): void => { router.push({ name: 'vistoria-checklist', params: { id } }); };

const openDetalhesModal = (id: number): void => { 
  selectedVistoriaId.value = id; 
  showDetalhesModal.value = true; 
};

const closeDetalhesModal = (): void => { 
  showDetalhesModal.value = false; 
  selectedVistoriaId.value = null; 
  fetchVistorias(); 
};

// --- Lógica de Assinatura ---
const openAssinaturaModal = (vistoria: Vistoria): void => {
  assinaturaTargetId.value = vistoria.id;
  
  const contratoRef = contratos.value.find(c => c.id === vistoria.contrato);
  assinaturaTargetImovel.value = contratoRef ? contratoRef.imovel_display : (vistoria.imovel_display || 'Imóvel da Vistoria');
  
  const nomeLocatario = contratoRef ? contratoRef.locatario_nome : 'Locatário';
  const nomeLocador = contratoRef ? contratoRef.locador_nome : 'Locador';
  const nomeResponsavel = vistoria.realizado_por_nome || 'Vistoriador';

  const ops: AssinanteOption[] = [
    { 
      label: `Locatário: ${nomeLocatario}`, 
      value: 'LOCATARIO',
      signed: !!vistoria.assinatura_locatario
    },
    { 
      label: `Vistoriador: ${nomeResponsavel}`, 
      value: 'RESPONSAVEL',
      signed: !!vistoria.assinatura_responsavel
    }
  ];

  if (vistoria.exige_assinatura_proprietario) {
    ops.push({ 
      label: `Locador: ${nomeLocador}`, 
      value: 'PROPRIETARIO',
      signed: !!vistoria.assinatura_proprietario
    });
  }

  assinantesDisponiveis.value = ops;
  showAssinaturaModal.value = true;
};

const closeAssinaturaModal = (): void => {
  showAssinaturaModal.value = false;
  assinaturaTargetId.value = null;
  assinaturaTargetImovel.value = '';
  assinantesDisponiveis.value = [];
  isSavingSignature.value = false;
};

const handleAssinaturaSave = async (payload: { signatureData: string, tipoAssinante: string }): Promise<void> => {
  if (!assinaturaTargetId.value) return;

  isSavingSignature.value = true;
  try {
    await api.post(`/v1/vistorias/vistorias/${assinaturaTargetId.value}/assinar/`, {
      assinatura: payload.signatureData,
      tipo_assinante: payload.tipoAssinante 
    });

    alert("Assinatura salva com sucesso!");
    await fetchVistorias(); 
    closeAssinaturaModal();
  } catch (error: any) {
    console.error(error);
    alert(error.response?.data?.detail || "Erro ao salvar assinatura.");
  } finally {
    isSavingSignature.value = false;
  }
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

const isFullySigned = (vistoria: Vistoria): boolean => {
  const assinouLocatario = !!vistoria.assinatura_locatario;
  const assinouResponsavel = !!vistoria.assinatura_responsavel;
  const assinouProprietario = !vistoria.exige_assinatura_proprietario || !!vistoria.assinatura_proprietario;
  return assinouLocatario && assinouResponsavel && assinouProprietario;
};

const getTooltip = (role: string, signed: boolean, name: string) => {
    return `${role}: ${name} (${signed ? 'Assinado' : 'Pendente'})`;
};

onMounted(async () => {
  await fetchContratos();
  await fetchVistorias();
});
</script>

<template>
  <div class="page-container">
    
    <main class="main-content">
      
      <div class="filter-toolbar">
        <div class="search-container">
          <i class="fas fa-search search-icon"></i>
          <input 
            type="text" 
            placeholder="Buscar por imóvel, contrato ou nome..." 
            v-model="searchQuery"
            @input="handleSearch"
            class="search-input"
          >
        </div>

        <div class="toolbar-actions">
          
          <div class="custom-select-wrapper">
            <i class="fas fa-filter filter-icon-inset"></i>
            <select v-model="filterTipo" @change="fetchVistorias" class="select-field">
              <option :value="null">Todas as Vistorias</option>
              <option value="ENTRADA">Entrada</option>
              <option value="SAIDA">Saída</option>
              <option value="PERIODICA">Periódica</option>
            </select>
            <i class="fas fa-chevron-down arrow-icon"></i>
          </div>

          <button class="btn-add active:scale-95" @click="navigateToForm">
            <i class="fas fa-plus"></i> <span>Nova Vistoria</span>
          </button>
        </div>
      </div>

      <div v-if="loading" class="state-container">
        <div class="spinner"></div>
        <p>Atualizando dados...</p>
      </div>

      <div v-else-if="groupedVistorias.length === 0" class="state-container empty">
        <i class="fas fa-clipboard-list empty-icon"></i>
        <h3>Nenhuma vistoria encontrada</h3>
        <p class="text-sm mt-2 text-slate-400">Tente ajustar a busca ou inicie um novo processo.</p>
      </div>

      <div v-else class="cards-grid">
        <div 
            class="imob-card" 
            v-for="group in groupedVistorias" 
            :key="group.contratoId"
        >
          <div class="card-header">
            <div class="header-row">
                <span class="badge-contrato">Contrato #{{ group.contratoId }}</span>
                <button class="btn-options"><i class="fas fa-ellipsis-h"></i></button>
            </div>
            <h4 class="address-title" :title="group.imovelDisplay">
              {{ group.imovelDisplay }}
            </h4>
          </div>

          <div class="people-section">
            <div class="person-item" :title="group.locatario">
                <div class="person-icon bg-blue-50 text-blue-600">
                    <i class="fas fa-user"></i>
                </div>
                <div class="person-info">
                    <span class="person-label">Locatário</span>
                    <span class="person-name">{{ group.locatario }}</span>
                </div>
            </div>
            <div class="person-item" :title="group.locador">
                <div class="person-icon bg-purple-50 text-purple-600">
                    <i class="fas fa-key"></i>
                </div>
                <div class="person-info">
                    <span class="person-label">Locador</span>
                    <span class="person-name">{{ group.locador }}</span>
                </div>
            </div>
          </div>

          <div class="card-body">
            
            <div class="vistoria-column column-entrada">
              <div class="col-header">
                <span class="tag-tipo tag-entrada">Entrada</span>
                <span v-if="group.entrada" class="status-pill" :class="group.entrada.concluida ? 'status-ok' : 'status-pending'">
                    {{ group.entrada.concluida ? 'Concluída' : 'Aberta' }}
                </span>
              </div>
              
              <div v-if="group.entrada" class="vistoria-details">
                <div class="detail-row">
                    <i class="far fa-calendar text-slate-400"></i>
                    <span>{{ formatDate(group.entrada.data_vistoria) }}</span>
                </div>
                
                <div class="signatures-mini">
                    <div class="sig-dots">
                        <span class="dot" 
                              :class="group.entrada.assinatura_locatario ? 'dot-green' : 'dot-gray'" 
                              :title="getTooltip('Locatário', !!group.entrada.assinatura_locatario, group.locatario)">L</span>
                        
                        <span class="dot" 
                              :class="group.entrada.assinatura_responsavel ? 'dot-green' : 'dot-gray'" 
                              :title="getTooltip('Vistoriador', !!group.entrada.assinatura_responsavel, group.entrada.realizado_por_nome)">R</span>
                        
                        <span v-if="group.entrada.exige_assinatura_proprietario"
                              class="dot" 
                              :class="group.entrada.assinatura_proprietario ? 'dot-green' : 'dot-gray'" 
                              :title="getTooltip('Locador', !!group.entrada.assinatura_proprietario, group.locador)">P</span>
                    </div>
                </div>

                <div class="actions-row">
                    <button v-if="!group.entrada.concluida" @click="navigateToExecution(group.entrada.id)" class="btn-action primary" title="Editar">
                        <i class="fas fa-pencil-alt"></i>
                    </button>
                    <button @click="openDetalhesModal(group.entrada.id)" class="btn-action secondary" title="Ver Detalhes">
                        <i class="fas fa-eye"></i>
                    </button>
                    
                    <button v-if="group.entrada.concluida && !isFullySigned(group.entrada)" 
                            @click.stop="openAssinaturaModal(group.entrada)" 
                            class="btn-action warning" 
                            title="Coletar Assinaturas">
                        <i class="fas fa-pen-nib"></i>
                    </button>
                </div>

                <button 
                  v-if="group.entrada.concluida && !group.saida && isFullySigned(group.entrada)"
                  class="btn-text-link mt-2"
                  @click="criarSaidaDaEntrada(group.entrada)"
                >
                  Criar Saída <i class="fas fa-arrow-right ml-1"></i>
                </button>
              </div>

              <div v-else class="empty-column">
                <span>—</span>
              </div>
            </div>

            <div class="vertical-divider"></div>

            <div class="vistoria-column column-saida">
              <div class="col-header">
                <span class="tag-tipo tag-saida">Saída</span>
                <span v-if="group.saida" class="status-pill" :class="group.saida.concluida ? 'status-ok' : 'status-pending'">
                    {{ group.saida.concluida ? 'Concluída' : 'Aberta' }}
                </span>
              </div>

              <div v-if="group.saida" class="vistoria-details">
                <div class="detail-row">
                    <i class="far fa-calendar text-slate-400"></i>
                    <span>{{ formatDate(group.saida.data_vistoria) }}</span>
                </div>

                <div class="signatures-mini">
                    <div class="sig-dots">
                        <span class="dot" 
                              :class="group.saida.assinatura_locatario ? 'dot-green' : 'dot-gray'" 
                              :title="getTooltip('Locatário', !!group.saida.assinatura_locatario, group.locatario)">L</span>
                        
                        <span class="dot" 
                              :class="group.saida.assinatura_responsavel ? 'dot-green' : 'dot-gray'" 
                              :title="getTooltip('Vistoriador', !!group.saida.assinatura_responsavel, group.saida.realizado_por_nome)">R</span>

                        <span v-if="group.saida.exige_assinatura_proprietario"
                              class="dot" 
                              :class="group.saida.assinatura_proprietario ? 'dot-green' : 'dot-gray'" 
                              :title="getTooltip('Locador', !!group.saida.assinatura_proprietario, group.locador)">P</span>
                    </div>
                </div>

                <div class="actions-row">
                    <button v-if="!group.saida.concluida" @click="navigateToExecution(group.saida.id)" class="btn-action primary" title="Editar">
                        <i class="fas fa-pencil-alt"></i>
                    </button>
                    <button @click="openDetalhesModal(group.saida.id)" class="btn-action secondary" title="Ver Detalhes">
                        <i class="fas fa-eye"></i>
                    </button>
                    
                    <button v-if="group.saida.concluida && !isFullySigned(group.saida)" 
                            @click.stop="openAssinaturaModal(group.saida)" 
                            class="btn-action warning" 
                            title="Coletar Assinaturas">
                        <i class="fas fa-pen-nib"></i>
                    </button>
                </div>
              </div>

              <div v-else class="empty-column">
                <span>Aguardando</span>
              </div>
            </div>
          </div>

          <div v-if="group.periodicas.length > 0" class="card-footer">
            <span class="footer-label"><i class="fas fa-history mr-1"></i> Periódicas:</span>
            <div class="footer-chips">
              <button v-for="p in group.periodicas" :key="p.id" @click="openDetalhesModal(p.id)" class="chip">
                {{ formatDate(p.data_vistoria) }}
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

    <AssinaturaModal
        v-if="showAssinaturaModal"
        titulo="Coletar Assinatura"
        termo="Declaro que estou de acordo com o estado do imóvel conforme vistoria apresentada."
        :enderecoImovel="assinaturaTargetImovel"
        :assinantesDisponiveis="assinantesDisponiveis"
        :isSaving="isSavingSignature"
        @close="closeAssinaturaModal"
        @save="handleAssinaturaSave"
    />

  </div>
</template>

<style scoped>
/* --- Configurações da Página --- */
.page-container {
  min-height: 100vh;
  background-color: #f8fafc;
  padding-bottom: 80px;
  padding-top: 1.5rem;
  font-family: 'Inter', sans-serif;
  color: #334155;
}

.main-content {
  padding: 0 1rem;
  max-width: 1400px;
  margin: 0 auto;
}

@media (min-width: 640px) {
  .main-content { padding: 0 1.5rem; }
}

/* --- TOOLBAR DE FILTROS & AÇÕES (MODERNIZADA) --- */
.filter-toolbar {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
  width: 100%;
  
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Container de Busca */
.search-container {
  position: relative;
  width: 100%;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 0.9rem;
  pointer-events: none;
}

.search-input {
  box-sizing: border-box; 
  width: 100%; 
  height: 44px; /* Altura unificada */
  padding: 0 1rem 0 2.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  outline: none;
  font-size: 0.9rem;
  color: #334155;
  transition: all 0.2s ease;
}
.search-input:focus {
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Linha de Ações (Filtro + Botão) */
.toolbar-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: 100%;
}

@media (min-width: 640px) {
  .toolbar-actions {
    flex-direction: row;
    width: auto;
  }
}

/* Dropdown Customizado */
.custom-select-wrapper {
  position: relative;
  flex: 1;
  min-width: 180px;
}

.filter-icon-inset {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  font-size: 0.85rem;
  pointer-events: none;
}

.arrow-icon {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 0.75rem;
  pointer-events: none;
}

.select-field {
  appearance: none; /* Remove seta nativa do browser */
  -webkit-appearance: none;
  -moz-appearance: none;
  box-sizing: border-box;
  width: 100%;
  height: 44px; /* Altura unificada */
  padding: 0 2.5rem 0 2.5rem; /* Espaço para ícones */
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  font-size: 0.9rem;
  color: #334155;
  cursor: pointer;
  outline: none;
  transition: all 0.2s;
  font-weight: 500;
}
.select-field:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
.select-field:hover {
  border-color: #cbd5e1;
}

/* Botão Nova Vistoria (Melhorado) */
.btn-add {
  height: 44px; /* Altura unificada */
  background: #2563eb; /* Azul um pouco mais forte */
  color: white;
  border: none;
  padding: 0 1.25rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  display: flex; align-items: center; justify-content: center; gap: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
  white-space: nowrap;
}
.btn-add:hover { 
  background: #1d4ed8; 
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(37, 99, 235, 0.3);
}
.btn-add:active {
  transform: translateY(0);
}

/* Media Query Desktop para Toolbar */
@media (min-width: 1024px) {
  .filter-toolbar {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1.25rem;
  }
  
  .search-container {
    max-width: 400px;
  }
}

/* --- Grid de Cards --- */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
  gap: 1.5rem;
}

/* --- Card Styles --- */
.imob-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  overflow: hidden;
}

.imob-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
  border-color: #cbd5e1;
}

/* Header */
.card-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #f1f5f9;
  background: linear-gradient(to bottom, #ffffff, #fafafa);
}

.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.badge-contrato {
  font-size: 0.65rem; font-weight: 700; color: #64748b;
  background: #f1f5f9; padding: 2px 6px; border-radius: 4px; text-transform: uppercase;
}
.btn-options { background: none; border: none; color: #94a3b8; cursor: pointer; }

/* Fonte menor solicitada */
.address-title {
  font-size: 0.875rem; 
  font-weight: 700; 
  color: #1e293b;
  line-height: 1.4;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  margin: 0;
}

/* Pessoas */
.people-section {
  padding: 0.75rem 1.25rem;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.person-item { display: flex; align-items: center; gap: 0.75rem; }
.person-icon {
  width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; flex-shrink: 0;
}
.person-info { display: flex; flex-direction: column; overflow: hidden; }
.person-label { font-size: 0.65rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; }
.person-name { font-size: 0.85rem; color: #334155; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500;}

/* Corpo */
.card-body {
  display: flex;
  padding: 0;
  flex: 1;
}

.vistoria-column {
  flex: 1;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.vertical-divider { width: 1px; background: #f1f5f9; }

.col-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem; }
.tag-tipo { font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; }
.tag-entrada { color: #059669; }
.tag-saida { color: #e11d48; }

.status-pill {
  font-size: 0.6rem; padding: 2px 6px; border-radius: 99px; font-weight: 600;
}
.status-ok { background: #dcfce7; color: #166534; }
.status-pending { background: #fff7ed; color: #9a3412; }

.vistoria-details { display: flex; flex-direction: column; gap: 0.5rem; }
.detail-row { font-size: 0.8rem; color: #64748b; display: flex; align-items: center; gap: 0.4rem; }

.signatures-mini { display: flex; align-items: center; gap: 0.5rem; margin-top: 0.25rem; }
.sig-dots { display: flex; gap: 4px; }
.dot {
  width: 18px; height: 18px; border-radius: 50%; font-size: 0.6rem;
  display: flex; align-items: center; justify-content: center; font-weight: 800; color: white;
  cursor: help; 
}
.dot-green { background: #22c55e; box-shadow: 0 1px 2px rgba(34, 197, 94, 0.3); }
.dot-gray { background: #e2e8f0; color: #94a3b8; }

.actions-row { display: flex; gap: 0.25rem; margin-top: 0.5rem; }
.btn-action {
  flex: 1;
  height: 28px;
  border-radius: 6px;
  border: 1px solid transparent;
  background: #f8fafc;
  color: #64748b;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
  font-size: 0.8rem;
}
.btn-action:hover { background: #e2e8f0; color: #334155; }
.btn-action.warning { color: #d97706; background: #fffbeb; }
.btn-action.warning:hover { background: #fcd34d; color: #92400e; }

.btn-text-link {
  background: none; border: none; color: #3b82f6; font-size: 0.75rem; font-weight: 600;
  cursor: pointer; text-align: left; padding: 0;
}
.btn-text-link:hover { text-decoration: underline; }

.empty-column {
  flex: 1; display: flex; align-items: center; justify-content: center; color: #cbd5e1; font-size: 1.5rem;
}

.card-footer {
  background: #f8fafc;
  padding: 0.75rem 1rem;
  border-top: 1px solid #f1f5f9;
  display: flex; align-items: center; gap: 0.5rem;
}
.footer-label { font-size: 0.7rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; }
.footer-chips { display: flex; gap: 0.25rem; flex-wrap: wrap; }
.chip {
  background: white; border: 1px solid #e2e8f0; border-radius: 4px; padding: 2px 6px;
  font-size: 0.7rem; color: #64748b; cursor: pointer;
}
.chip:hover { border-color: #cbd5e1; color: #334155; }

/* --- States --- */
.state-container { text-align: center; padding: 4rem 1rem; color: #94a3b8; }
.spinner { 
  width: 2rem; height: 2rem; border: 3px solid #e2e8f0; border-top-color: #3b82f6; 
  border-radius: 50%; margin: 0 auto 1rem; animation: spin 1s linear infinite; 
}
@keyframes spin { 100% { transform: rotate(360deg); } }
.empty-icon { font-size: 3rem; opacity: 0.5; margin-bottom: 1rem; }

/* Responsive adjustments */
@media (max-width: 640px) {
  .card-body { flex-direction: column; }
  .vertical-divider { width: 100%; height: 1px; }
}
</style>