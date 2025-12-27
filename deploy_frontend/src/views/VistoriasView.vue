<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Operacional</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Vistorias</span>
           </nav>
           
           <h1>Gestão de Vistorias</h1>
        </div>
        
        <div class="actions-area">
            <button class="btn-icon-thin" @click="fetchVistorias" title="Atualizar Dados">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
            </button>
            
            <button class="btn-primary-thin" @click="navigateToForm">
              <i class="fas fa-plus"></i> Nova Vistoria
            </button>
        </div>
      </div>
    </header>

    <div class="kpi-grid">
      <div class="kpi-card blue">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.total }}</span>
          <span class="kpi-label">Total Listado</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-clipboard-list"></i></div>
      </div>

      <div class="kpi-card orange">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.assinaturasPendentes }}</span>
          <span class="kpi-label">Assinaturas Pendentes</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-file-signature"></i></div>
      </div>

      <div class="kpi-card purple">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.abertas }}</span>
          <span class="kpi-label">Em Aberto/Execução</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-tools"></i></div>
      </div>

      <div class="kpi-card green">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.concluidas }}</span>
          <span class="kpi-label">Concluídas (100%)</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-check-circle"></i></div>
      </div>
    </div>

    <div class="toolbar-grid">
        <div class="filter-cell search-cell">
          <label>Buscar</label>
          <div class="input-with-icon">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="Buscar por imóvel, contrato ou nome..." 
              class="form-control"
              @input="handleSearch"
            >
          </div>
        </div>

        <div class="filter-cell">
          <label>Tipo</label>
          <select v-model="filterTipo" @change="fetchVistorias" class="form-control">
            <option :value="null">Todas as Vistorias</option>
            <option value="ENTRADA">Entrada</option>
            <option value="SAIDA">Saída</option>
            <option value="PERIODICA">Periódica</option>
          </select>
        </div>

        <div class="filter-cell clear-cell">
            <label>&nbsp;</label>
            <button @click="limparFiltros" class="btn-clear" title="Limpar Filtros">
                <i class="fas fa-eraser"></i>
            </button>
        </div>
    </div>

    <main class="content-wrapper">
      
      <div v-if="loading" class="state-container">
        <div class="spinner"></div>
        <p>Carregando vistorias...</p>
      </div>

      <div v-else-if="groupedVistorias.length === 0" class="state-container empty">
        <i class="fas fa-folder-open empty-icon"></i>
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
                <button class="btn-options" title="Mais opções"><i class="fas fa-ellipsis-h"></i></button>
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
                        <span class="dot" :class="group.entrada.assinatura_locatario ? 'dot-green' : 'dot-gray'" title="Locatário">L</span>
                        <span class="dot" :class="group.entrada.assinatura_responsavel ? 'dot-green' : 'dot-gray'" title="Vistoriador">R</span>
                        <span v-if="group.entrada.exige_assinatura_proprietario" class="dot" :class="group.entrada.assinatura_proprietario ? 'dot-green' : 'dot-gray'" title="Locador">P</span>
                    </div>
                </div>

                <div class="actions-row">
                    <button v-if="!group.entrada.concluida" @click="navigateToExecution(group.entrada.id)" class="btn-action primary" title="Editar/Executar">
                        <i class="fas fa-pencil-alt"></i>
                    </button>
                    <button @click="openDetalhesModal(group.entrada.id)" class="btn-action secondary" title="Ver Detalhes">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button v-if="group.entrada.concluida && !isFullySigned(group.entrada)" @click.stop="openAssinaturaModal(group.entrada)" class="btn-action warning" title="Coletar Assinaturas">
                        <i class="fas fa-pen-nib"></i>
                    </button>
                </div>

                <button v-if="group.entrada.concluida && !group.saida && isFullySigned(group.entrada)" class="btn-text-link mt-2" @click="criarSaidaDaEntrada(group.entrada)">
                  Criar Saída <i class="fas fa-arrow-right ml-1"></i>
                </button>
              </div>

              <div v-else class="empty-column"><span>—</span></div>
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
                        <span class="dot" :class="group.saida.assinatura_locatario ? 'dot-green' : 'dot-gray'" title="Locatário">L</span>
                        <span class="dot" :class="group.saida.assinatura_responsavel ? 'dot-green' : 'dot-gray'" title="Vistoriador">R</span>
                        <span v-if="group.saida.exige_assinatura_proprietario" class="dot" :class="group.saida.assinatura_proprietario ? 'dot-green' : 'dot-gray'" title="Locador">P</span>
                    </div>
                </div>

                <div class="actions-row">
                    <button v-if="!group.saida.concluida" @click="navigateToExecution(group.saida.id)" class="btn-action primary" title="Editar">
                        <i class="fas fa-pencil-alt"></i>
                    </button>
                    <button @click="openDetalhesModal(group.saida.id)" class="btn-action secondary" title="Ver Detalhes">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button v-if="group.saida.concluida && !isFullySigned(group.saida)" @click.stop="openAssinaturaModal(group.saida)" class="btn-action warning" title="Coletar Assinaturas">
                        <i class="fas fa-pen-nib"></i>
                    </button>
                </div>
              </div>

              <div v-else class="empty-column"><span>Aguardando</span></div>
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

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api';
import { format } from 'date-fns';
import VistoriaDetalhesModal from '@/components/Vistorias/VistoriaDetalhesModal.vue';
import AssinaturaModal from '@/components/AssinaturaModal.vue'; 

// --- Interfaces ---
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

// --- Estado ---
const router = useRouter();
const vistorias = ref<Vistoria[]>([]);
const contratos = ref<ContratoRef[]>([]);
const loading = ref<boolean>(true);
const searchQuery = ref<string>('');
const filterTipo = ref<string | null>(null);

// Modais
const showDetalhesModal = ref<boolean>(false);
const selectedVistoriaId = ref<number | null>(null);
const showAssinaturaModal = ref<boolean>(false);
const isSavingSignature = ref<boolean>(false);
const assinaturaTargetImovel = ref<string>('');
const assinaturaTargetId = ref<number | null>(null);
const assinantesDisponiveis = ref<AssinanteOption[]>([]); 

// --- KPIs Computados ---
const kpis = computed(() => {
  const total = vistorias.value.length;
  const assinaturasPendentes = vistorias.value.filter(v => v.concluida && !isFullySigned(v)).length;
  const concluidas = vistorias.value.filter(v => v.concluida).length;
  const abertas = vistorias.value.filter(v => !v.concluida).length;
  
  return { total, assinaturasPendentes, concluidas, abertas };
});

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

    if (v.tipo === 'ENTRADA') groups[cId].entrada = v;
    else if (v.tipo === 'SAIDA') groups[cId].saida = v;
    else groups[cId].periodicas.push(v);
  });

  return Object.values(groups).sort((a, b) => b.contratoId - a.contratoId);
});

// --- Métodos ---
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
      
      return { 
        id: c.id, 
        imovel_display: display,
        locatario_nome: c.inquilino_detalhes?.nome_display || c.inquilino_detalhes?.nome || 'N/D',
        locador_nome: c.proprietario_detalhes?.nome_display || c.proprietario_detalhes?.nome || 'N/D'
      };
    });
  } catch (error) { console.error('Erro ao carregar contratos:', error); }
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
  } catch (error) { vistorias.value = []; } 
  finally { loading.value = false; }
};

let searchTimeout: ReturnType<typeof setTimeout> | null = null;
const handleSearch = (): void => {
  if (searchTimeout) clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => fetchVistorias(), 500);
};

const limparFiltros = () => {
    searchQuery.value = '';
    filterTipo.value = null;
    fetchVistorias();
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

// --- Assinatura ---
const openAssinaturaModal = (vistoria: Vistoria): void => {
  assinaturaTargetId.value = vistoria.id;
  const contratoRef = contratos.value.find(c => c.id === vistoria.contrato);
  assinaturaTargetImovel.value = contratoRef ? contratoRef.imovel_display : (vistoria.imovel_display || 'Imóvel da Vistoria');
  
  const ops: AssinanteOption[] = [
    { label: `Locatário: ${contratoRef ? contratoRef.locatario_nome : 'Locatário'}`, value: 'LOCATARIO', signed: !!vistoria.assinatura_locatario },
    { label: `Vistoriador: ${vistoria.realizado_por_nome || 'Vistoriador'}`, value: 'RESPONSAVEL', signed: !!vistoria.assinatura_responsavel }
  ];

  if (vistoria.exige_assinatura_proprietario) {
    ops.push({ label: `Locador: ${contratoRef ? contratoRef.locador_nome : 'Locador'}`, value: 'PROPRIETARIO', signed: !!vistoria.assinatura_proprietario });
  }

  assinantesDisponiveis.value = ops;
  showAssinaturaModal.value = true;
};

const closeAssinaturaModal = (): void => {
  showAssinaturaModal.value = false;
  assinaturaTargetId.value = null;
  assinantesDisponiveis.value = [];
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
    alert(error.response?.data?.detail || "Erro ao salvar assinatura.");
  } finally { isSavingSignature.value = false; }
};

const criarSaidaDaEntrada = async (vistoriaEntrada: Vistoria): Promise<void> => {
  if (!confirm(`Gerar a Vistoria de Saída baseada na Entrada #${vistoriaEntrada.id}?`)) return;
  try {
    loading.value = true;
    const res = await api.post(`/v1/vistorias/vistorias/${vistoriaEntrada.id}/gerar-saida-da-entrada/`, { data_vistoria: new Date().toISOString().split('T')[0] });
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
  return !!vistoria.assinatura_locatario && !!vistoria.assinatura_responsavel && (!vistoria.exige_assinatura_proprietario || !!vistoria.assinatura_proprietario);
};

onMounted(async () => {
  await fetchContratos();
  await fetchVistorias();
});
</script>

<style scoped>
/* CONFIGURAÇÃO GERAL (PADRONIZADO) */
.page-container {
  min-height: 100vh;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
}

/* HEADER DA PÁGINA (PADRONIZADO) */
.page-header { margin-bottom: 2rem; }
.title-area { display: flex; flex-direction: column; gap: 6px; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }
.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.actions-area { display: flex; gap: 0.75rem; }

/* Botões Estilo Fino */
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

/* KPI GRID (PADRONIZADO) */
.kpi-grid { 
    display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
    gap: 1.25rem; margin-bottom: 2rem; 
}

.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: all 0.2s; position: relative; overflow: hidden;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.04); }

.kpi-content { display: flex; flex-direction: column; }
.kpi-value { font-size: 1.6rem; font-weight: 300; line-height: 1.1; color: #111; }
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; letter-spacing: 0.05em; }
.kpi-icon { font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; }

.kpi-card.blue .kpi-value, .kpi-card.blue .kpi-icon { color: #2563eb; }
.kpi-card.green .kpi-value, .kpi-card.green .kpi-icon { color: #059669; }
.kpi-card.orange .kpi-value, .kpi-card.orange .kpi-icon { color: #d97706; }
.kpi-card.purple .kpi-value, .kpi-card.purple .kpi-icon { color: #9333ea; }

/* TOOLBAR (GRID LAYOUT) */
.toolbar-grid {
  background-color: #ffffff; border-radius: 8px; border: 1px solid #e5e7eb;
  padding: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
  display: grid; grid-template-columns: 2fr 1fr auto; 
  gap: 1rem; align-items: end; margin-bottom: 1.5rem; flex-shrink: 0;
}

.filter-cell { display: flex; flex-direction: column; gap: 0.3rem; }
.search-cell { grid-column: span 1; } 
.clear-cell { justify-self: start; }

.filter-cell label { font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; }

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

/* Grid de Cards */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); 
  gap: 1.5rem;
}

/* Estilos Específicos do Card de Vistoria */
.imob-card {
  background: white; border-radius: 8px; border: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); display: flex; flex-direction: column;
  transition: all 0.2s ease; overflow: hidden;
}
.imob-card:hover { transform: translateY(-2px); box-shadow: 0 8px 16px rgba(0,0,0,0.06); border-color: #cbd5e1; }

.card-header { padding: 1rem 1.25rem; border-bottom: 1px solid #f1f5f9; background: #fff; }
.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.badge-contrato { font-size: 0.65rem; font-weight: 700; color: #64748b; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; }
.address-title { font-size: 0.9rem; font-weight: 700; color: #1e293b; margin: 0; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.btn-options { background: none; border: none; color: #94a3b8; cursor: pointer; }

.people-section { padding: 0.75rem 1.25rem; background: #ffffff; display: flex; flex-direction: column; gap: 0.5rem; border-bottom: 1px solid #f1f5f9; }
.person-item { display: flex; align-items: center; gap: 0.75rem; }
.person-icon { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; flex-shrink: 0; }
.person-info { display: flex; flex-direction: column; overflow: hidden; }
.person-label { font-size: 0.65rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; }
.person-name { font-size: 0.85rem; color: #334155; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500;}

.card-body { display: flex; padding: 0; flex: 1; }
.vistoria-column { flex: 1; padding: 1rem; display: flex; flex-direction: column; gap: 0.75rem; }
.vertical-divider { width: 1px; background: #f1f5f9; }

.col-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem; }
.tag-tipo { font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; }
.tag-entrada { color: #059669; }
.tag-saida { color: #e11d48; }

.status-pill { font-size: 0.6rem; padding: 2px 6px; border-radius: 99px; font-weight: 600; }
.status-ok { background: #dcfce7; color: #166534; }
.status-pending { background: #fff7ed; color: #9a3412; }

.vistoria-details { display: flex; flex-direction: column; gap: 0.5rem; }
.detail-row { font-size: 0.8rem; color: #64748b; display: flex; align-items: center; gap: 0.4rem; }

.signatures-mini { display: flex; align-items: center; gap: 0.5rem; margin-top: 0.25rem; }
.sig-dots { display: flex; gap: 4px; }
.dot { width: 18px; height: 18px; border-radius: 50%; font-size: 0.6rem; display: flex; align-items: center; justify-content: center; font-weight: 800; color: white; cursor: help; }
.dot-green { background: #22c55e; }
.dot-gray { background: #e2e8f0; color: #94a3b8; }

.actions-row { display: flex; gap: 0.25rem; margin-top: 0.5rem; }
.btn-action { flex: 1; height: 28px; border-radius: 6px; border: 1px solid transparent; background: #f8fafc; color: #64748b; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; font-size: 0.8rem; }
.btn-action:hover { background: #e2e8f0; color: #334155; }
.btn-action.primary:hover { background: #eff6ff; color: #2563eb; }
.btn-action.warning { color: #d97706; background: #fffbeb; }
.btn-action.warning:hover { background: #fcd34d; color: #92400e; }

.btn-text-link { background: none; border: none; color: #3b82f6; font-size: 0.75rem; font-weight: 600; cursor: pointer; text-align: left; padding: 0; }
.btn-text-link:hover { text-decoration: underline; }

.empty-column { flex: 1; display: flex; align-items: center; justify-content: center; color: #cbd5e1; font-size: 1.5rem; }

.card-footer { background: #f8fafc; padding: 0.75rem 1rem; border-top: 1px solid #f1f5f9; display: flex; align-items: center; gap: 0.5rem; }
.footer-label { font-size: 0.7rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; }
.footer-chips { display: flex; gap: 0.25rem; flex-wrap: wrap; }
.chip { background: white; border: 1px solid #e2e8f0; border-radius: 4px; padding: 2px 6px; font-size: 0.7rem; color: #64748b; cursor: pointer; }
.chip:hover { border-color: #cbd5e1; color: #334155; }

.state-container { text-align: center; padding: 4rem 1rem; color: #94a3b8; }
.spinner { width: 2rem; height: 2rem; border: 3px solid #e2e8f0; border-top-color: #3b82f6; border-radius: 50%; margin: 0 auto 1rem; animation: spin 1s linear infinite; }
@keyframes spin { 100% { transform: rotate(360deg); } }
.empty-icon { font-size: 3rem; opacity: 0.5; margin-bottom: 1rem; }

@media (max-width: 1024px) {
  .page-container { padding: 1rem; }
  .header-main { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .actions-area { width: 100%; justify-content: flex-start; }
  .toolbar-grid { grid-template-columns: 1fr; }
  .card-body { flex-direction: column; }
  .vertical-divider { width: 100%; height: 1px; }
}
</style>