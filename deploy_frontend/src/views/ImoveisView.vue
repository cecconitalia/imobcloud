<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Imóveis</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Gerenciar Carteira</span>
           </nav>
           
           <h1>Gerenciar Imóveis</h1>
        </div>
        
        <div class="actions-area">
            <button class="btn-icon-thin" @click="fetchImoveis" title="Atualizar Lista">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            </button>
            
            <button @click="goToCreateImovel" class="btn-primary-thin">
              <i class="fas fa-plus"></i> Novo Imóvel
            </button>
        </div>
      </div>
    </header>

    <div class="kpi-grid" v-if="sumarioImoveis">
      <div class="kpi-card blue" :class="{ active: filters.status === 'A_VENDA' }" @click="setFilter('status', 'A_VENDA')">
        <div class="kpi-content">
          <span class="kpi-value">{{ sumarioImoveis.a_venda }}</span>
          <span class="kpi-label">À Venda</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-hand-holding-usd"></i></div>
      </div>

      <div class="kpi-card orange" :class="{ active: filters.status === 'PARA_ALUGAR' }" @click="setFilter('status', 'PARA_ALUGAR')">
        <div class="kpi-content">
          <span class="kpi-value">{{ sumarioImoveis.para_alugar }}</span>
          <span class="kpi-label">Para Alugar</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-key"></i></div>
      </div>

      <div class="kpi-card green" :class="{ active: filters.status === 'VENDIDO_OU_ALUGADO' }" @click="setFilter('status', 'VENDIDO_OU_ALUGADO')">
        <div class="kpi-content">
          <span class="kpi-value">{{ sumarioImoveis.vendidos_e_alugados }}</span>
          <span class="kpi-label">Fechados (Mês)</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-check-circle"></i></div>
      </div>

      <div class="kpi-card purple" :class="{ active: filters.status === '' }" @click="setFilter('status', '')">
        <div class="kpi-content">
          <span class="kpi-value">{{ imoveis.length }}</span>
          <span class="kpi-label">Total na Carteira</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-warehouse"></i></div>
      </div>
    </div>

    <div class="toolbar-row">
        <div class="filter-group search-group">
          <label>Buscar</label>
          <div class="input-with-icon">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="Código, título, cidade..." 
              class="form-control"
            >
          </div>
        </div>

        <div class="filter-group">
          <label>Cidade</label>
          <select v-model="filters.cidade" class="form-control">
            <option value="">Todas</option>
            <option v-for="cidade in cidadesOptions" :key="cidade" :value="cidade">
              {{ cidade }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>Bairro</label>
          <select v-model="filters.bairro" class="form-control">
            <option value="">Todos</option>
            <option v-for="bairro in bairrosOptions" :key="bairro" :value="bairro">
              {{ bairro }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>Tipo</label>
          <select v-model="filters.tipo" class="form-control">
            <option value="">Todos</option>
            <option value="CASA">Casa</option>
            <option value="APARTAMENTO">Apartamento</option>
            <option value="TERRENO">Terreno</option>
            <option value="SALA_COMERCIAL">Sala Comercial</option>
            <option value="GALPAO">Galpão</option>
            <option value="RURAL">Rural</option>
            <option value="OUTRO">Outro</option>
          </select>
        </div>

        <div class="filter-group" style="min-width: 100px;">
          <label>Quartos</label>
          <select v-model="filters.quartos" class="form-control">
            <option value="">Qtd</option>
            <option value="1">1+</option>
            <option value="2">2+</option>
            <option value="3">3+</option>
            <option value="4">4+</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Status</label>
          <select v-model="filters.status" class="form-control">
            <option value="">Todos</option>
            <option value="A_VENDA">À Venda</option>
            <option value="PARA_ALUGAR">Para Alugar</option>
            <option value="VENDIDO">Vendido</option>
            <option value="ALUGADO">Alugado</option>
            <option value="EM_CONSTRUCAO">Em Construção</option>
            <option value="DESATIVADO">Desativado</option>
          </select>
        </div>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Carregando imóveis...</p>
    </div>
    
    <div v-else-if="filteredImoveis.length === 0" class="empty-state">
      <i class="fas fa-folder-open empty-icon"></i>
      <p>Nenhum imóvel encontrado para os filtros e pesquisa aplicados.</p>
    </div>
    
    <div v-else class="imoveis-grid">
      <div v-for="imovel in filteredImoveis" :key="imovel.id" class="imovel-card">
        
        <div class="card-top-bar" @click="editImovel(imovel.id)">
           <div class="badges-left">
               <span class="imovel-id">#{{ imovel.codigo_referencia }}</span>
               <span :class="['tipo-badge', imovel.finalidade === 'VENDA' ? 'tipo-venda' : 'tipo-aluguel']">
                  {{ imovel.finalidade }} ({{ imovel.tipo }})
               </span>
           </div>
           <div class="badges-right">
               <span :class="['status-pill', getStatusClass(imovel.status)]">
                  <i :class="getStatusIcon(imovel.status)"></i>
                  {{ formatStatus(imovel.status) }}
               </span>
           </div>
        </div>
        
        <div class="card-body">
          <div class="imovel-section" @click="editImovel(imovel.id)">
             <div class="card-image-container">
                 <img 
                    :src="getPrincipalImage(imovel.imagens)" 
                    alt="Imagem do Imóvel" 
                    class="imovel-image"
                 />
             </div>
             
             <div class="imovel-info-text">
                <h4 class="imovel-title" :title="imovel.titulo_anuncio">
                    {{ imovel.titulo_anuncio || 'Imóvel sem título' }}
                </h4>
                <p class="imovel-address">
                    <i class="fas fa-map-marker-alt text-muted"></i> 
                    {{ imovel.bairro }}, {{ imovel.cidade }}
                </p>
                <p class="imovel-specs">
                    <span><i class="fas fa-ruler-combined"></i> {{ imovel.area_total }} m²</span>
                    <span v-if="imovel.quartos"><i class="fas fa-bed"></i> {{ imovel.quartos }} Qts</span>
                    <span v-if="imovel.suites"><i class="fas fa-bath"></i> {{ imovel.suites }} Suítes</span>
                </p>
             </div>
          </div>

          <div class="datas-grid">
             <div class="data-col">
                <span class="data-label">Captação</span>
                <div class="data-value text-muted">
                    <i class="far fa-calendar-alt"></i> {{ formatarData(imovel.data_captacao) }}
                </div>
             </div>
             <div class="data-divider"></div>
             <div class="data-col">
                <span class="data-label">Exclusividade</span>
                <div class="data-value" :class="imovel.possui_exclusividade ? 'text-blue' : 'text-muted'">
                    <i :class="imovel.possui_exclusividade ? 'fas fa-lock' : 'fas fa-unlock'"></i> 
                    {{ imovel.possui_exclusividade ? 'Sim' : 'Não' }}
                </div>
             </div>
          </div>

          <div class="pessoas-container">
              <div class="pessoa-row">
                 <div class="pessoa-avatar avatar-proprietario">
                    <i class="fas fa-user-shield"></i>
                 </div>
                 <div class="pessoa-info">
                    <span class="pessoa-role role-proprietario">Proprietário</span>
                    <span class="pessoa-name" :title="imovel.proprietario_detalhes?.nome_display">
                        {{ imovel.proprietario_detalhes?.nome_display || '—' }}
                    </span>
                 </div>
              </div>
          </div>
        </div>
        
        <div class="valor-footer">
           <span class="valor-label">{{ imovel.status === 'A_VENDA' ? 'Valor Venda' : 'Valor Aluguel' }}</span>
           <span class="valor-amount">{{ imovel.valor_venda ? formatCurrency(imovel.valor_venda) : formatCurrency(imovel.valor_aluguel) }}</span>
        </div>

        <div class="card-actions">
          <div class="actions-left">
            <button @click="editImovel(imovel.id)" class="btn-pill btn-edit-detail">
                <i class="fas fa-pen"></i> Editar
            </button>
            <button @click="router.push({ name: 'imovel-imagens', params: { id: imovel.id } })" class="btn-pill btn-images">
                <i class="fas fa-camera"></i> Fotos
            </button>
          </div>

          <div class="actions-right">
              <button @click="handleVisualizarAutorizacao(imovel.id)" class="btn-mini btn-info" title="Autorização PDF">
                <i class="fas fa-file-pdf"></i>
              </button>
              <button @click="confirmInativar(imovel.id)" class="btn-mini btn-delete-mini" title="Inativar/Excluir">
                <i class="fas fa-trash"></i>
              </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';
import { formatCurrency } from '@/utils/formatters';
import { format, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';

const router = useRouter();
const imoveis = ref<any[]>([]);
const isLoading = ref(true);
const searchQuery = ref('');
const filters = ref({
  tipo: '',
  finalidade: '',
  status: '',
  cidade: '',
  bairro: '',
  quartos: '',
});

const sumarioImoveis = ref<any>(null); 
const defaultImage = 'https://via.placeholder.com/400x300.png?text=Sem+imagem';

// --- ACTIONS ---
async function fetchImoveis() {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/imoveis/');
    imoveis.value = response.data;
    calculateSummary(imoveis.value);
  } catch (error) {
    console.error("Erro ao carregar imóveis:", error);
  } finally {
    isLoading.value = false;
  }
}

async function inativarImovel(id: number) {
  try {
    await apiClient.patch(`/v1/imoveis/${id}/`, { status: 'DESATIVADO' });
    const index = imoveis.value.findIndex(imovel => imovel.id === id);
    if (index !== -1) {
      imoveis.value[index].status = 'DESATIVADO';
    }
    calculateSummary(imoveis.value);
    alert('Imóvel inativado com sucesso!');
  } catch (error) {
    alert('Ocorreu um erro ao inativar o imóvel.');
  }
}

async function handleVisualizarAutorizacao(imovelId: number) {
  try {
    const response = await apiClient.get(`/v1/imoveis/${imovelId}/gerar-autorizacao-pdf/`, { responseType: 'blob' });
    const file = new Blob([response.data], { type: 'application/pdf' });
    const fileURL = URL.createObjectURL(file);
    window.open(fileURL, '_blank');
    setTimeout(() => URL.revokeObjectURL(fileURL), 10000);
  } catch (error: any) {
    alert("Falha ao gerar o PDF da Autorização.");
  }
}

// --- FILTERS & SUMMARY ---
function calculateSummary(list: any[]) {
    const a_venda = list.filter(i => i.status === 'A_VENDA').length;
    const para_alugar = list.filter(i => i.status === 'PARA_ALUGAR').length;
    const vendidos_e_alugados = list.filter(i => i.status === 'VENDIDO' || i.status === 'ALUGADO').length; 
    sumarioImoveis.value = { a_venda, para_alugar, vendidos_e_alugados };
}

function setFilter(key: keyof typeof filters.value, value: string) {
    if (filters.value[key] === value) filters.value[key] = '';
    else filters.value[key] = value;
}

const cidadesOptions = computed(() => {
  const cidades = imoveis.value.map(i => i.cidade).filter(c => c);
  return [...new Set(cidades)].sort();
});

const bairrosOptions = computed(() => {
  let lista = imoveis.value;
  if (filters.value.cidade) lista = lista.filter(i => i.cidade === filters.value.cidade);
  const bairros = lista.map(i => i.bairro).filter(b => b);
  return [...new Set(bairros)].sort();
});

const filteredImoveis = computed(() => {
  return imoveis.value.filter(imovel => {
    const searchLower = searchQuery.value.toLowerCase();
    const matchesSearch = searchQuery.value
      ? (imovel.codigo_referencia?.toLowerCase().includes(searchLower) ||
         imovel.titulo_anuncio?.toLowerCase().includes(searchLower) ||
         imovel.cidade?.toLowerCase().includes(searchLower))
      : true;
    
    let matchesStatus = true;
    if (filters.value.status !== '') {
        if (filters.value.status === 'VENDIDO_OU_ALUGADO') matchesStatus = (imovel.status === 'VENDIDO' || imovel.status === 'ALUGADO');
        else matchesStatus = imovel.status === filters.value.status;
    }

    const matchesFilters = 
      (filters.value.tipo === '' || imovel.tipo === filters.value.tipo) &&
      (filters.value.finalidade === '' || imovel.finalidade === filters.value.finalidade) &&
      (filters.value.cidade === '' || imovel.cidade === filters.value.cidade) &&
      (filters.value.bairro === '' || imovel.bairro === filters.value.bairro) &&
      (filters.value.quartos === '' || imovel.quartos >= parseInt(filters.value.quartos)) &&
      matchesStatus; 
      
    return matchesSearch && matchesFilters;
  });
});

// --- UI HELPERS ---
function getPrincipalImage(imagens: any[]): string {
  if (!imagens || imagens.length === 0) return defaultImage;
  const principal = imagens.find(img => img.principal);
  return principal ? principal.imagem : imagens[0].imagem;
}

function getStatusClass(status: string) {
    switch (status) {
        case 'A_VENDA': case 'PARA_ALUGAR': return 'status-ativo';
        case 'VENDIDO': case 'ALUGADO': return 'status-concluido';
        case 'EM_CONSTRUCAO': return 'status-pendente';
        case 'DESATIVADO': return 'status-inativo';
        default: return 'status-default';
    }
}

function getStatusIcon(status: string) {
  switch (status) {
    case 'A_VENDA': return 'fas fa-tag';
    case 'PARA_ALUGAR': return 'fas fa-building';
    case 'VENDIDO': return 'fas fa-flag-checkered';
    case 'ALUGADO': return 'fas fa-key';
    case 'EM_CONSTRUCAO': return 'fas fa-hard-hat';
    case 'DESATIVADO': return 'fas fa-ban';
    default: return 'fas fa-info-circle';
  }
}

const formatStatus = (status: string) => {
  switch (status) {
    case 'A_VENDA': return 'À Venda';
    case 'PARA_ALUGAR': return 'Alugar';
    case 'VENDIDO': return 'Vendido';
    case 'ALUGADO': return 'Alugado';
    case 'EM_CONSTRUCAO': return 'Em Obra';
    case 'DESATIVADO': return 'Inativo';
    default: return status;
  }
};

function formatarData(data: string | null | undefined): string {
  if (!data) return '-';
  try { return format(parseISO(data), 'dd/MM/yy', { locale: ptBR }); } catch { return '-'; }
}

function goToCreateImovel() { router.push({ name: 'imovel-novo' }); }
function editImovel(id: number) { router.push({ name: 'imovel-editar', params: { id } }); }
function confirmInativar(id: number) {
  if (confirm('Tem certeza que deseja INATIVAR este imóvel?')) inativarImovel(id);
}

onMounted(() => { fetchImoveis(); });
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

/* Botões Estilo Fino (PADRONIZADO) */
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

.kpi-card.orange.active { background-color: #fffdf5; border-color: #f59e0b; }
.kpi-card.orange .kpi-value, .kpi-card.orange .kpi-icon { color: #d97706; }

.kpi-card.purple.active { background-color: #faf5ff; border-color: #9333ea; }
.kpi-card.purple .kpi-value, .kpi-card.purple .kpi-icon { color: #9333ea; }

/* TOOLBAR (PADRONIZADO) */
.toolbar-row {
  background-color: #ffffff; border-radius: 8px; border: 1px solid #e5e7eb;
  padding: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
  display: flex; flex-wrap: wrap; gap: 1rem; align-items: flex-end;
  margin-bottom: 1.5rem;
}

.filter-group { flex: 1; display: flex; flex-direction: column; gap: 0.3rem; min-width: 140px; }
.search-group { flex: 2; min-width: 220px; }
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

/* GRID DE IMÓVEIS */
.imoveis-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem; padding-bottom: 2rem;
}

.imovel-card {
  background-color: #fff; border-radius: 8px; border: 1px solid #e5e7eb;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); display: flex; flex-direction: column;
  transition: all 0.2s ease; position: relative; overflow: hidden;
}
.imovel-card:hover { transform: translateY(-2px); box-shadow: 0 8px 16px rgba(0,0,0,0.06); border-color: #cbd5e1; }

/* Card Top Bar */
.card-top-bar {
    padding: 0.8rem 1rem; display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid #f1f5f9; background: #fff; cursor: pointer;
}
.badges-left, .badges-right { display: flex; align-items: center; gap: 8px; }

.imovel-id {
    font-size: 0.7rem; font-weight: 700; color: #64748b;
    background: #f1f5f9; padding: 2px 6px; border-radius: 4px;
}
.tipo-badge {
    font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
    padding: 2px 6px; border-radius: 4px; color: #475569; background-color: #f8fafc; border: 1px solid #e2e8f0;
}
.status-pill {
    padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 700;
    text-transform: uppercase; display: flex; align-items: center; gap: 4px;
}
.status-ativo { background-color: #dcfce7; color: #166534; }
.status-concluido { background-color: #e0f2fe; color: #1e40af; }
.status-pendente { background-color: #fef9c3; color: #854d0e; }
.status-inativo { background-color: #f1f5f9; color: #64748b; }

/* Card Body */
.card-body { padding: 0; flex-grow: 1; display: flex; flex-direction: column; }

.imovel-section { display: flex; padding: 1rem; cursor: pointer; gap: 1rem; }
.imovel-info-text { flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.3rem; }

.card-image-container { 
    width: 90px; height: 90px; border-radius: 6px; overflow: hidden; 
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); flex-shrink: 0; 
}
.imovel-image { width: 100%; height: 100%; object-fit: cover; }

.imovel-title { 
    font-size: 0.95rem; font-weight: 700; color: #1e293b; margin: 0; 
    line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.imovel-address { 
    font-size: 0.8rem; color: #64748b; margin: 0; 
    display: flex; align-items: center; gap: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; 
}
.imovel-specs {
    font-size: 0.75rem; color: #334155; font-weight: 500; display: flex; gap: 10px; align-items: center; margin-top: auto;
}
.imovel-specs i { color: #94a3b8; }

.datas-grid { 
    display: flex; align-items: center; justify-content: space-between; 
    padding: 0.5rem 1rem; background-color: #f8fafc; 
    border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9; 
}
.data-col { display: flex; flex-direction: column; gap: 1px; }
.data-label { font-size: 0.65rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; }
.data-value { font-size: 0.75rem; font-weight: 600; color: #475569; display: flex; align-items: center; gap: 5px; }
.data-divider { width: 1px; height: 20px; background-color: #e2e8f0; }
.text-blue { color: #2563eb; }

.pessoas-container { padding: 0.8rem 1rem; }
.pessoa-row { display: flex; align-items: center; gap: 0.75rem; }
.pessoa-avatar { 
    width: 30px; height: 30px; border-radius: 6px; display: flex; 
    align-items: center; justify-content: center; font-size: 0.8rem; flex-shrink: 0; 
}
.avatar-proprietario { background-color: #f3e8ff; color: #9333ea; }
.role-proprietario { color: #9333ea; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; margin-bottom: 1px; }
.pessoa-info { display: flex; flex-direction: column; overflow: hidden; }
.pessoa-name { font-size: 0.85rem; color: #334155; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* Footer & Actions */
.valor-footer { 
    margin-top: auto; padding: 0.6rem 1rem; display: flex; justify-content: space-between; align-items: center; 
    background-color: #1e293b; color: #fff; 
}
.valor-label { font-size: 0.7rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; }
.valor-amount { font-size: 1rem; font-weight: 700; color: #fff; }

.card-actions { 
    padding: 0.75rem 1rem; background-color: #fff; 
    display: flex; justify-content: space-between; align-items: center; gap: 1rem; 
}
.actions-left { display: flex; gap: 0.5rem; }
.actions-right { display: flex; gap: 0.25rem; }

.btn-pill { 
    border: none; border-radius: 4px; padding: 0.35rem 0.75rem; font-size: 0.75rem; font-weight: 600; 
    cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s; 
}
.btn-edit-detail { background-color: #eff6ff; color: #1e40af; }
.btn-edit-detail:hover { background-color: #dbeafe; }
.btn-images { background-color: #f0fdf4; color: #15803d; }
.btn-images:hover { background-color: #dcfce7; }

.btn-mini { 
    width: 28px; height: 28px; border-radius: 4px; border: 1px solid transparent; background: transparent; 
    color: #94a3b8; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s; font-size: 0.8rem;
}
.btn-mini:hover { background-color: #f1f5f9; color: #334155; }
.btn-delete-mini:hover { background-color: #fef2f2; color: #ef4444; }
.btn-info:hover { background-color: #eff6ff; color: #2563eb; }

.loading-state, .empty-state { text-align: center; padding: 4rem 2rem; color: #64748b; }
.empty-icon { font-size: 2.5rem; color: #e2e8f0; margin-bottom: 1rem; }
.spinner { width: 32px; height: 32px; border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .page-container { padding: 1rem; }
  .header-main { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .actions-area { width: 100%; justify-content: flex-start; }
  .toolbar-row { flex-direction: column; align-items: stretch; }
}
</style>