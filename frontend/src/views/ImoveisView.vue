<template>
  <div class="page-container">
    
    <main class="main-content">
      
      <div v-if="sumarioImoveis" class="dashboard-grid">
        <div class="stat-card stat-a-venda" @click="setFilter('status', 'A_VENDA')" :class="{ active: filters.status === 'A_VENDA' }">
          <div class="stat-icon"><i class="fas fa-hand-holding-usd"></i></div>
          <div class="stat-info">
              <h3>À Venda</h3>
              <p>{{ sumarioImoveis.a_venda }}</p>
          </div>
        </div>
        <div class="stat-card stat-para-alugar" @click="setFilter('status', 'PARA_ALUGAR')" :class="{ active: filters.status === 'PARA_ALUGAR' }">
          <div class="stat-icon"><i class="fas fa-home"></i></div>
          <div class="stat-info">
              <h3>Para Alugar</h3>
              <p>{{ sumarioImoveis.para_alugar }}</p>
          </div>
        </div>
        <div class="stat-card stat-concluidos" @click="setFilter('status', 'VENDIDO_OU_ALUGADO')" :class="{ active: filters.status === 'VENDIDO_OU_ALUGADO' }">
          <div class="stat-icon"><i class="fas fa-check-circle"></i></div>
          <div class="stat-info">
              <h3>Fechados (Mês)</h3>
              <p>{{ sumarioImoveis.vendidos_e_alugados }}</p>
          </div>
        </div>
        <div class="stat-card stat-total" @click="setFilter('status', '')" :class="{ active: filters.status === '' && !searchQuery }">
          <div class="stat-icon"><i class="fas fa-warehouse"></i></div>
          <div class="stat-info">
              <h3>Total na Carteira</h3>
              <p>{{ imoveis.length }}</p>
          </div>
        </div>
      </div>

      <div class="search-and-filter-wrapper">
        <div class="search-and-filter-bar">
          
          <div class="filter-group search-group">
            <label>Buscar</label>
            <div class="input-with-icon">
              <i class="fas fa-search"></i>
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="Código, título, cidade..." 
                class="search-input"
              />
            </div>
          </div>
          
          <div class="filter-group">
            <label for="cidade">Cidade</label>
            <select id="cidade" v-model="filters.cidade">
              <option value="">Todas</option>
              <option v-for="cidade in cidadesOptions" :key="cidade" :value="cidade">
                {{ cidade }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label for="bairro">Bairro</label>
            <select id="bairro" v-model="filters.bairro">
              <option value="">Todos</option>
              <option v-for="bairro in bairrosOptions" :key="bairro" :value="bairro">
                {{ bairro }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label for="tipo">Tipo</label>
            <select id="tipo" v-model="filters.tipo">
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

          <div class="filter-group small-select">
            <label for="quartos">Quartos</label>
            <select id="quartos" v-model="filters.quartos">
              <option value="">Qtd</option>
              <option value="1">1+</option>
              <option value="2">2+</option>
              <option value="3">3+</option>
              <option value="4">4+</option>
            </select>
          </div>

          <div class="filter-group">
            <label for="finalidade">Finalidade</label>
            <select id="finalidade" v-model="filters.finalidade">
              <option value="">Todas</option>
              <option value="RESIDENCIAL">Residencial</option>
              <option value="COMERCIAL">Comercial</option>
              <option value="INDUSTRIAL">Industrial</option>
              <option value="RURAL">Rural</option>
            </select>
          </div>

          <div class="filter-group">
            <label for="status">Status</label>
            <select id="status" v-model="filters.status">
              <option value="">Todos</option>
              <option value="A_VENDA">À Venda</option>
              <option value="PARA_ALUGAR">Para Alugar</option>
              <option value="VENDIDO">Vendido</option>
              <option value="ALUGADO">Alugado</option>
              <option value="EM_CONSTRUCAO">Em Construção</option>
              <option value="DESATIVADO">Desativado</option>
            </select>
          </div>

          <div class="button-group">
            <button @click="goToCreateImovel" class="btn-add">
              <i class="fas fa-plus"></i> Novo
            </button>
          </div>

        </div>
      </div>

      <div v-if="isLoading" class="loading-message">
        <div class="spinner"></div>
        A carregar imóveis...
      </div>
      <div v-else-if="filteredImoveis.length === 0" class="empty-message card">
        <div class="empty-icon"><i class="fas fa-folder-open"></i></div>
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
                      {{ imovel.bairro }}, {{ imovel.cidade }} - {{ imovel.estado }}
                  </p>
                  <p class="imovel-address">
                      <i class="fas fa-ruler-combined text-muted"></i> 
                      {{ imovel.area_total }} m² | 
                      <i class="fas fa-bed text-muted ml-10"></i> {{ imovel.quartos }} Qts / {{ imovel.suites }} Suítes
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
                  <div class="data-value" :class="imovel.possui_exclusividade ? 'text-danger' : 'text-muted'">
                      <i :class="imovel.possui_exclusividade ? 'fas fa-lock' : 'fas fa-unlock'"></i> 
                      {{ imovel.possui_exclusividade ? 'SIM' : 'NÃO' }}
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
                  <i class="fas fa-edit"></i> Editar Dados
              </button>
              <button @click="router.push({ name: 'imovel-imagens', params: { id: imovel.id } })" class="btn-pill btn-images">
                  <i class="fas fa-images"></i> Imagens
              </button>
            </div>

            <div class="actions-right">
                <button @click="handleVisualizarAutorizacao(imovel.id)" class="btn-mini btn-info" title="Autorização PDF">
                  <i class="fas fa-file-pdf"></i>
                </button>
                <button @click="confirmInativar(imovel.id)" class="btn-mini btn-delete-mini" title="Inativar/Excluir">
                  <i class="fas fa-trash-alt"></i>
                </button>
            </div>
          </div>
        </div>
      </div>
    </main>
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
let debounceTimeout: number | undefined = undefined;

// --- FUNÇÕES DE API ---
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
    console.error("Erro ao inativar imóvel:", error);
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

// --- LÓGICA DE FILTROS/SUMÁRIO ---
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

// --- FUNÇÕES DE FORMATO E UI ---
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
    case 'DESATIVADO': return 'fas fa-trash-alt';
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
  if (!data) return '—';
  try { return format(parseISO(data), 'dd/MM/yy', { locale: ptBR }); } catch { return 'Inválida'; }
}

function goToCreateImovel() { router.push({ name: 'imovel-novo' }); }
function editImovel(id: number) { router.push({ name: 'imovel-editar', params: { id } }); }
function confirmInativar(id: number) {
  if (confirm('Tem certeza que deseja INATIVAR este imóvel?')) inativarImovel(id);
}

onMounted(() => { fetchImoveis(); });
</script>

<style scoped>
/* ================================================== */
/* 1. Layout Geral */
/* ================================================== */
.page-container {
  min-height: 100vh;
  background-color: #f3f4f6;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
}

.main-content {
    /* Espaçamento ajustado para não colar no topo */
    padding: 1.5rem 2rem 2.5rem 2rem;
}

.empty-message { text-align: center; padding: 4rem 2rem; color: #6c757d; }
.empty-icon { font-size: 3rem; color: #dee2e6; margin-bottom: 1rem; }
.loading-message { text-align: center; padding: 2rem; font-size: 1.2rem; color: #6c757d; }
.spinner { border: 3px solid #e9ecef; border-top: 3px solid #0d6efd; border-radius: 50%; width: 40px; height: 40px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* ================================================== */
/* 2. Dashboard Stats */
/* ================================================== */
.dashboard-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem; margin-bottom: 1.5rem;
}
.stat-card {
  background-color: #fff; border: none; border-radius: 12px; padding: 1.5rem;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04); display: flex; align-items: center; gap: 1rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease; cursor: pointer;
}
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08); }
.stat-card.active { border: 2px solid #007bff; }

.stat-icon { width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: 700; }
.stat-info h3 { font-size: 0.8rem; color: #616161; font-weight: 600; margin: 0; text-transform: uppercase; letter-spacing: 0.5px; }
.stat-info p { font-size: 1.55rem; font-weight: 700; color: #212121; margin: 0; line-height: 1.2; }

.stat-a-venda .stat-icon { background-color: #E3F2FD; color: #2196F3; } 
.stat-a-venda .stat-info p { color: #1976D2; }
.stat-para-alugar .stat-icon { background-color: #E0F2F1; color: #00838F; } 
.stat-para-alugar .stat-info p { color: #00695C; }
.stat-concluidos .stat-icon { background-color: #FBEFF2; color: #C2185B; }
.stat-concluidos .stat-info p { color: #880E4F; }
.stat-total .stat-icon { background-color: #F5F5F5; color: #424242; } 
.stat-total .stat-info p { color: #212121; }

/* ================================================== */
/* 3. Search & Filter Bar (MODERNIZADO E CORRIGIDO) */
/* ================================================== */
.search-and-filter-wrapper {
  margin-bottom: 2rem;
}

.search-and-filter-bar {
  background-color: #ffffff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  padding: 1.25rem;
  box-shadow: 0 2px 6px rgba(0,0,0,0.03);
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end; /* Alinha inputs e botões pela base */
  position: relative;
  z-index: 10; /* Garante que dropdowns fiquem por cima dos cards */
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1;
  min-width: 140px; /* Largura mínima razoável */
}

.search-group {
  flex: 2; /* Busca ocupa mais espaço */
  min-width: 220px;
}

.small-select {
  flex: 0 0 80px; /* Campo quartos menor */
  min-width: 80px;
}

.filter-group label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.input-with-icon {
  position: relative;
  width: 100%;
}
.input-with-icon i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
  font-size: 0.9rem;
}

.search-input, select {
  width: 100%;
  padding: 0.6rem 0.8rem;
  font-size: 0.9rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background-color: #fff;
  color: #374151;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  height: 40px; /* Altura fixa para alinhar */
  box-sizing: border-box;
}

.search-input { padding-left: 2.2rem; }

.search-input:focus, select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.button-group {
  display: flex;
  align-items: flex-end;
  padding-bottom: 1px; /* Ajuste fino de alinhamento */
}

.btn-add {
  background-color: #2563eb;
  color: white;
  padding: 0 1.25rem;
  height: 40px; /* Mesma altura dos inputs */
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
  white-space: nowrap;
}
.btn-add:hover { background-color: #1d4ed8; transform: translateY(-1px); }

/* ================================================== */
/* 4. Grid de Imóveis */
/* ================================================== */
.imoveis-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.5rem; padding-bottom: 2rem;
}

.imovel-card {
  background-color: #fff; border-radius: 12px; border: 1px solid rgba(0,0,0,0.06);
  box-shadow: 0 4px 12px rgba(0,0,0,0.03); display: flex; flex-direction: column;
  transition: all 0.3s ease; position: relative; overflow: hidden;
  /* z-index normal para não brigar com filtros */
}
.imovel-card:hover { transform: translateY(-3px); box-shadow: 0 8px 18px rgba(0,0,0,0.06); }

/* Detalhes do Card */
.card-top-bar {
    padding: 0.85rem 1.25rem; display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid #f0f2f5; background: #fff; cursor: pointer;
}
.badges-left, .badges-right { display: flex; align-items: center; gap: 8px; }
.imovel-id { font-size: 0.75rem; font-weight: 800; color: #374151; background: #f3f4f6; padding: 3px 8px; border-radius: 6px; }
.tipo-badge { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; padding: 3px 8px; border-radius: 6px; color: #495057; background-color: #f8f9fa; border: 1px solid #e5e7eb; }
.status-pill { padding: 0.35em 0.85em; border-radius: 50px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; display: flex; align-items: center; gap: 5px; }
.status-ativo { background-color: #d1fae5; color: #065f46; }
.status-concluido { background-color: #e0f2fe; color: #1e40af; }
.status-pendente { background-color: #fef3c7; color: #92400e; }
.status-inativo { background-color: #f3f4f6; color: #6b7280; }

.card-body { padding: 0; flex-grow: 1; display: flex; flex-direction: column; }
.imovel-section { display: flex; padding: 1.25rem 1.25rem 0.75rem; cursor: pointer; }
.imovel-info-text { flex-grow: 1; min-width: 0; }
.card-image-container { width: 100px; height: 100px; border-radius: 8px; overflow: hidden; margin-right: 1rem; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08); flex-shrink: 0; }
.imovel-image { width: 100%; height: 100%; object-fit: cover; }
.imovel-title { font-size: 1.05rem; font-weight: 700; color: #111827; margin: 0 0 0.25rem 0; line-height: 1.4; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.imovel-address { font-size: 0.85rem; color: #6b7280; margin: 0; display: flex; align-items: center; gap: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ml-10 { margin-left: 10px; }

.datas-grid { display: flex; align-items: center; justify-content: space-between; padding: 0.6rem 1.25rem; background-color: #f8fafc; border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9; }
.data-col { display: flex; flex-direction: column; gap: 2px; }
.data-label { font-size: 0.65rem; color: #9ca3af; font-weight: 600; text-transform: uppercase; }
.data-value { font-size: 0.85rem; font-weight: 600; color: #374151; display: flex; align-items: center; gap: 6px; }
.data-divider { width: 1px; height: 24px; background-color: #e2e8f0; }
.text-muted { color: #9ca3af; }
.text-danger { color: #ef4444; }

.pessoas-container { padding: 1rem 1.25rem; display: flex; flex-direction: column; gap: 0.5rem; }
.pessoa-row { display: flex; align-items: center; gap: 0.85rem; }
.pessoa-avatar { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; flex-shrink: 0; }
.avatar-proprietario { background-color: #f3e8ff; color: #9333ea; }
.role-proprietario { color: #9333ea; }
.pessoa-info { display: flex; flex-direction: column; overflow: hidden; }
.pessoa-role { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; margin-bottom: 1px; }
.pessoa-name { font-size: 0.9rem; color: #1f2937; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.valor-footer { margin-top: auto; padding: 0.85rem 1.25rem; display: flex; justify-content: space-between; align-items: center; background-color: #111827; color: #fff; }
.valor-label { font-size: 0.75rem; color: #9ca3af; font-weight: 500; text-transform: uppercase; }
.valor-amount { font-size: 1.1rem; font-weight: 700; color: #fff; }

.card-actions { padding: 0.85rem 1.25rem; background-color: #fff; display: flex; justify-content: space-between; align-items: center; gap: 1rem; }
.actions-left { display: flex; gap: 0.5rem; }
.actions-right { display: flex; gap: 0.25rem; }
.btn-pill { border: none; border-radius: 6px; padding: 0.4rem 0.85rem; font-size: 0.8rem; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s; }
.btn-edit-detail { background-color: #eff6ff; color: #1e40af; }
.btn-edit-detail:hover { background-color: #dbeafe; }
.btn-images { background-color: #f0fdf4; color: #16a34a; }
.btn-images:hover { background-color: #dcfce7; }
.btn-mini { width: 32px; height: 32px; border-radius: 6px; border: 1px solid transparent; background: transparent; color: #9ca3af; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s; }
.btn-mini:hover { background-color: #f3f4f6; color: #374151; }
.btn-delete-mini:hover { background-color: #fee2e2; color: #dc2626; }
.btn-info { color: #17a2b8; }
.btn-info:hover { background-color: #e0faff; }

@media (max-width: 1024px) {
  .search-and-filter-bar { flex-direction: column; align-items: stretch; gap: 0.8rem; }
  .filter-group, .search-group, .small-select { width: 100%; min-width: auto; }
  .button-group { width: 100%; }
  .btn-add { width: 100%; justify-content: center; }
}
</style>