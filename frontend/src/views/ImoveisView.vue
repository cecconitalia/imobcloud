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
          <span class="kpi-label">Total Carteira</span>
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
            <option v-for="cidade in cidadesOptions" :key="cidade" :value="cidade">{{ cidade }}</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Bairro</label>
          <select v-model="filters.bairro" class="form-control">
            <option value="">Todos</option>
            <option v-for="bairro in bairrosOptions" :key="bairro" :value="bairro">{{ bairro }}</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Tipo</label>
          <select v-model="filters.tipo" class="form-control">
            <option value="">Todos</option>
            <option value="CASA">Casa</option>
            <option value="APARTAMENTO">Apartamento</option>
            <option value="TERRENO">Terreno</option>
            <option value="SALA_COMERCIAL">Sala</option>
            <option value="GALPAO">Galpão</option>
            <option value="RURAL">Rural</option>
          </select>
        </div>

        <div class="filter-group" style="min-width: 80px;">
          <label>Quartos</label>
          <select v-model="filters.quartos" class="form-control">
            <option value="">Qtd</option>
            <option value="1">1+</option>
            <option value="2">2+</option>
            <option value="3">3+</option>
            <option value="4">4+</option>
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
        <p>Carregando imóveis...</p>
      </div>
      
      <div v-else-if="filteredImoveis.length === 0" class="empty-state">
        <i class="fas fa-filter"></i>
        <p>Nenhum imóvel encontrado com os filtros selecionados.</p>
      </div>

      <div v-else class="report-scroll-viewport">
        <table class="report-table">
          <thead>
            <tr>
              <th width="8%">Ref.</th>
              <th width="25%">Imóvel</th>
              <th width="20%">Localização</th>
              <th width="15%">Detalhes</th>
              <th width="12%">Valor</th>
              <th width="10%">Status</th>
              <th width="10%" class="text-right">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="imovel in filteredImoveis" :key="imovel.id" class="clickable-row" @click="editImovel(imovel.id)">
              
              <td>
                <span class="ref-badge">#{{ imovel.codigo_referencia || imovel.id }}</span>
              </td>

              <td>
                 <div class="cell-imovel-main">
                    <div class="imovel-thumb">
                        <img :src="getPrincipalImage(imovel.imagens)" alt="Imóvel" loading="lazy">
                    </div>
                    <div class="imovel-texts">
                        <span class="imovel-title" :title="imovel.titulo_anuncio">{{ imovel.titulo_anuncio || 'Sem título' }}</span>
                        <span class="imovel-type">{{ imovel.tipo }} • {{ imovel.finalidade }}</span>
                    </div>
                 </div>
              </td>

              <td>
                 <div class="cell-local">
                    <span class="local-bairro">{{ imovel.bairro || 'Bairro N/D' }}</span>
                    <span class="local-cidade">{{ imovel.cidade }}</span>
                    <span class="local-end text-muted" :title="imovel.logradouro">{{ imovel.logradouro }}</span>
                 </div>
              </td>

              <td>
                 <div class="cell-specs">
                    <span v-if="imovel.area_total" title="Área Total"><i class="fas fa-ruler-combined"></i> {{ imovel.area_total }}m²</span>
                    <span v-if="imovel.quartos" title="Quartos"><i class="fas fa-bed"></i> {{ imovel.quartos }}</span>
                    <span v-if="imovel.suites" title="Suítes"><i class="fas fa-bath"></i> {{ imovel.suites }}</span>
                    <span v-if="imovel.vagas" title="Vagas"><i class="fas fa-car"></i> {{ imovel.vagas }}</span>
                 </div>
              </td>

              <td>
                 <div class="cell-valor">
                    <span class="valor-main">
                        {{ imovel.finalidade === 'VENDA' ? formatCurrency(imovel.valor_venda) : formatCurrency(imovel.valor_aluguel) }}
                    </span>
                    <span class="valor-sub" v-if="imovel.condominio && imovel.condominio > 0">
                        Cond: {{ formatCurrency(imovel.condominio) }}
                    </span>
                 </div>
              </td>

              <td>
                 <span :class="['badge-status', getStatusClass(imovel.status)]">
                    {{ formatStatus(imovel.status) }}
                 </span>
                 <div v-if="imovel.possui_exclusividade" class="exclusividade-tag">
                    <i class="fas fa-lock"></i> Exclusivo
                 </div>
              </td>

              <td class="text-right" @click.stop>
                <div class="actions-flex">
                    <button class="btn-action edit" @click="editImovel(imovel.id)" title="Editar">
                        <i class="fas fa-pen"></i>
                    </button>
                    <button class="btn-action photos" @click="router.push({ name: 'imovel-imagens', params: { id: imovel.id } })" title="Fotos">
                        <i class="fas fa-camera"></i>
                    </button>
                    <button class="btn-action pdf" @click="handleVisualizarAutorizacao(imovel.id)" title="Autorização (PDF)">
                        <i class="fas fa-file-pdf"></i>
                    </button>
                    <button class="btn-action delete" @click="confirmInativar(imovel.id)" title="Inativar/Excluir">
                        <i class="fas fa-trash"></i>
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
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';
import { formatCurrency } from '@/utils/formatters';

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
const defaultImage = 'https://via.placeholder.com/150x150.png?text=Sem+Foto';

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

function clearFilters() {
    searchQuery.value = '';
    filters.value = { tipo: '', finalidade: '', status: '', cidade: '', bairro: '', quartos: '' };
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

/* HEADER DA PÁGINA */
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

/* KPI GRID */
.kpi-grid { 
    display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
    gap: 1.25rem; margin-bottom: 2rem; 
}
.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); cursor: pointer; transition: all 0.2s;
  position: relative; overflow: hidden;
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

/* TOOLBAR */
.toolbar-row {
  background-color: #ffffff; border-radius: 8px; border: 1px solid #e5e7eb;
  padding: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
  display: flex; flex-wrap: wrap; gap: 1rem; align-items: flex-end;
  margin-bottom: 1.5rem;
}
.filter-group { flex: 1; display: flex; flex-direction: column; gap: 0.3rem; min-width: 140px; }
.search-group { flex: 2; min-width: 200px; }
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
.report-table { width: 100%; border-collapse: collapse; min-width: 900px; }
.report-table th {
  background: #f8fafc; padding: 0.8rem 1.2rem; text-align: left;
  font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em;
  border-bottom: 1px solid #e2e8f0;
}
.report-table td {
  padding: 0.8rem 1.2rem; border-bottom: 1px solid #f1f5f9;
  font-size: 0.85rem; color: #334155; vertical-align: middle;
}
.clickable-row { cursor: pointer; transition: background 0.1s; }
.clickable-row:hover { background-color: #fcfcfc; }

/* Células Customizadas */
.ref-badge { 
    background: #f1f5f9; color: #475569; padding: 3px 6px; 
    border-radius: 4px; font-weight: 700; font-size: 0.7rem; 
}

.cell-imovel-main { display: flex; align-items: center; gap: 12px; }
.imovel-thumb { 
    width: 40px; height: 40px; border-radius: 4px; overflow: hidden; flex-shrink: 0; border: 1px solid #e2e8f0; 
}
.imovel-thumb img { width: 100%; height: 100%; object-fit: cover; }
.imovel-texts { display: flex; flex-direction: column; gap: 2px; }
.imovel-title { font-weight: 600; color: #1e293b; font-size: 0.85rem; line-height: 1.2; }
.imovel-type { font-size: 0.7rem; color: #64748b; text-transform: uppercase; }

.cell-local { display: flex; flex-direction: column; gap: 1px; }
.local-bairro { font-weight: 600; color: #334155; }
.local-cidade { font-size: 0.75rem; color: #64748b; }
.local-end { font-size: 0.7rem; }

.cell-specs { display: flex; gap: 8px; color: #64748b; font-size: 0.75rem; font-weight: 500; }
.cell-specs i { color: #94a3b8; }

.cell-valor { display: flex; flex-direction: column; align-items: flex-start; }
.valor-main { font-weight: 700; color: #2563eb; }
.valor-sub { font-size: 0.7rem; color: #94a3b8; }

.badge-status {
  font-size: 0.65rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; 
  text-transform: uppercase; letter-spacing: 0.02em; display: inline-block;
}
.status-ativo { background: #dcfce7; color: #15803d; }
.status-concluido { background: #e0f2fe; color: #1d4ed8; }
.status-pendente { background: #fef9c3; color: #854d0e; }
.status-inativo { background: #f3f4f6; color: #6b7280; }

.exclusividade-tag {
    font-size: 0.6rem; color: #9333ea; margin-top: 2px; font-weight: 600; 
    display: flex; align-items: center; gap: 3px;
}

/* Ações */
.actions-flex { display: flex; gap: 0.5rem; justify-content: flex-end; }
.btn-action {
  width: 32px; height: 32px; border: none; border-radius: 6px; cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: all 0.2s;
  background: transparent; color: #94a3b8; border: 1px solid transparent;
}
.btn-action:hover { background-color: #f1f5f9; color: #334155; border-color: #e2e8f0; }

.btn-action.edit:hover { background-color: #eff6ff; color: #2563eb; }
.btn-action.photos:hover { background-color: #f0fdf4; color: #16a34a; }
.btn-action.pdf:hover { background-color: #fff1f2; color: #e11d48; }
.btn-action.delete:hover { background-color: #fef2f2; color: #ef4444; }

.text-muted { color: #94a3b8; }
.loading-state, .error-message, .empty-state { text-align: center; padding: 4rem 2rem; color: #64748b; }
.spinner { width: 32px; height: 32px; border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }

@media (max-width: 1024px) {
  .page-container { padding: 1rem; }
  .header-main { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .actions-area { width: 100%; justify-content: flex-start; }
  .toolbar-row { flex-direction: column; align-items: stretch; }
}
</style>