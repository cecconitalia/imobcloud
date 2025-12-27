<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Financeiro</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Plano de Contas</span>
           </nav>
           
           <h1>Categorias Financeiras</h1>
        </div>
        
        <div class="actions-area">
            <button class="btn-icon-thin" @click="fetchCategorias" title="Atualizar Dados">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            </button>
            
            <button class="btn-primary-thin" @click="abrirModalNova">
              <i class="fas fa-plus"></i> Nova Categoria
            </button>
        </div>
      </div>
    </header>

    <div class="kpi-grid">
      <div class="kpi-card blue">
        <div class="kpi-content">
          <span class="kpi-value">{{ categorias.length }}</span>
          <span class="kpi-label">Categorias Totais</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-tags"></i></div>
      </div>

      <div class="kpi-card green">
        <div class="kpi-content">
          <span class="kpi-value">{{ stats.receitas }}</span>
          <span class="kpi-label">Tipos de Receita</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-arrow-circle-up"></i></div>
      </div>

      <div class="kpi-card red">
        <div class="kpi-content">
          <span class="kpi-value">{{ stats.despesas }}</span>
          <span class="kpi-label">Tipos de Despesa</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-arrow-circle-down"></i></div>
      </div>

      <div class="kpi-card purple">
        <div class="kpi-content">
          <span class="kpi-value text-sm">{{ stats.mais_usada || 'S/D' }}</span>
          <span class="kpi-label">Mais Utilizada</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-chart-pie"></i></div>
      </div>
    </div>

    <div class="toolbar-grid">
        <div class="filter-cell search-cell">
          <label>Buscar Categoria</label>
          <div class="input-with-icon">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="searchTerm" 
              placeholder="Nome da categoria ou descrição..." 
              class="form-control"
            >
          </div>
        </div>

        <div class="filter-cell">
          <label>Tipo</label>
          <select v-model="filterTipo" class="form-control">
            <option value="">Todas</option>
            <option value="RECEITA">Apenas Receitas</option>
            <option value="DESPESA">Apenas Despesas</option>
          </select>
        </div>

        <div class="filter-cell clear-cell">
            <label>&nbsp;</label>
            <button @click="resetFilters" class="btn-clear" title="Limpar Filtros">
                <i class="fas fa-eraser"></i>
            </button>
        </div>
    </div>

    <main class="report-main-wrapper">
      
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>A carregar categorias...</p>
      </div>

      <div v-else-if="filteredCategorias.length === 0" class="empty-state">
        <i class="fas fa-tag empty-icon"></i>
        <p>Nenhuma categoria encontrada com os filtros aplicados.</p>
      </div>

      <div v-else class="report-scroll-viewport">
        <table class="report-table">
          <thead>
            <tr>
              <th width="8%" class="text-center">Ícone</th>
              <th width="35%">Nome da Categoria</th>
              <th width="20%">Tipo de Fluxo</th>
              <th width="25%">Descrição</th>
              <th width="12%" class="text-right">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="categoria in filteredCategorias" :key="categoria.id">
              <td class="text-center">
                  <div class="cat-icon-wrapper" :class="categoria.tipo === 'RECEITA' ? 'bg-success' : 'bg-danger'">
                      <i :class="categoria.icone || 'fas fa-tag'"></i>
                  </div>
              </td>
              
              <td>
                <span class="font-bold text-slate-700">{{ categoria.nome }}</span>
              </td>
              
              <td>
                <span :class="['type-badge', categoria.tipo === 'RECEITA' ? 'badge-in' : 'badge-out']">
                  {{ categoria.tipo === 'RECEITA' ? 'Receita' : 'Despesa' }}
                </span>
              </td>

              <td class="text-muted text-sm italic">
                  {{ categoria.descricao || 'Sem descrição cadastrada' }}
              </td>

              <td class="text-right">
                <div class="actions-flex">
                    <button @click="editarCategoria(categoria)" class="btn-action primary" title="Editar">
                        <i class="fas fa-pen"></i>
                    </button>
                    <button @click="excluirCategoria(categoria.id)" class="btn-action danger" title="Excluir">
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
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
import { useToast } from 'vue-toast-notification';

interface Categoria {
  id: number;
  nome: string;
  tipo: 'RECEITA' | 'DESPESA';
  descricao?: string;
  icone?: string;
}

const categorias = ref<Categoria[]>([]);
const isLoading = ref(true);
const searchTerm = ref('');
const filterTipo = ref('');
const toast = useToast();

const fetchCategorias = async () => {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/financeiro/categorias/');
    categorias.value = response.data.results || response.data;
  } catch (error) {
    toast.error('Erro ao carregar categorias.');
  } finally {
    isLoading.value = false;
  }
};

const stats = computed(() => {
    return {
        receitas: categorias.value.filter(c => c.tipo === 'RECEITA').length,
        despesas: categorias.value.filter(c => c.tipo === 'DESPESA').length,
        mais_usada: categorias.value[0]?.nome || '' 
    };
});

const filteredCategorias = computed(() => {
  return categorias.value.filter(c => {
    const matchSearch = c.nome.toLowerCase().includes(searchTerm.value.toLowerCase());
    const matchTipo = filterTipo.value === '' || c.tipo === filterTipo.value;
    return matchSearch && matchTipo;
  });
});

const resetFilters = () => { searchTerm.value = ''; filterTipo.value = ''; };

const abrirModalNova = () => { /* Implementar lógica de abertura do modal ou router.push */ };
const editarCategoria = (cat: Categoria) => { /* Implementar lógica de edição */ };

const excluirCategoria = async (id: number) => {
  if (!confirm('Deseja realmente excluir esta categoria?')) return;
  try {
    await apiClient.delete(`/v1/financeiro/categorias/${id}/`);
    toast.success('Categoria removida.');
    fetchCategorias();
  } catch (e) {
    toast.error('Não foi possível excluir (pode haver transações vinculadas).');
  }
};

onMounted(fetchCategorias);
</script>

<style scoped>
/* CONFIGURAÇÃO GERAL (Page Scroll) */
.page-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #fcfcfc;
  font-family: 'Inter', sans-serif;
  padding: 1.5rem 2.5rem;
  box-sizing: border-box;
}

/* HEADER */
.page-header { margin-bottom: 2rem; flex-shrink: 0; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }
.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.actions-area { display: flex; gap: 0.75rem; }

/* Botões Thin */
.btn-primary-thin {
  background: #2563eb; color: white; border: none; padding: 0.5rem 1.2rem;
  border-radius: 6px; font-weight: 400; font-size: 0.85rem; cursor: pointer;
  display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s;
}
.btn-primary-thin:hover { background: #1d4ed8; }
.btn-icon-thin {
  background: white; border: 1px solid #e2e8f0; color: #64748b; width: 34px; height: 34px;
  border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center;
}

/* KPI GRID */
.kpi-grid { 
    display: grid; grid-template-columns: repeat(4, 1fr); 
    gap: 1.25rem; margin-bottom: 2rem; flex-shrink: 0;
}
.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); position: relative; overflow: hidden;
}
.kpi-value { font-size: 1.5rem; font-weight: 300; color: #111; }
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; }
.kpi-icon { font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; }

.kpi-card.blue .kpi-value { color: #2563eb; }
.kpi-card.green .kpi-value { color: #059669; }
.kpi-card.red .kpi-value { color: #dc2626; }
.kpi-card.purple .kpi-value { color: #9333ea; }

/* TOOLBAR */
.toolbar-grid {
  background-color: #ffffff; border-radius: 8px; border: 1px solid #e5e7eb;
  padding: 1rem; display: grid; grid-template-columns: 2fr 1fr auto; 
  gap: 1rem; align-items: end; margin-bottom: 1.5rem; flex-shrink: 0;
}
.filter-cell { display: flex; flex-direction: column; gap: 0.3rem; }
.filter-cell label { font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; }
.form-control {
  padding: 0.5rem 0.8rem; font-size: 0.85rem; border: 1px solid #cbd5e1; border-radius: 6px; height: 38px;
}
.input-with-icon { position: relative; width: 100%; }
.input-with-icon i { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 0.9rem; }
.input-with-icon .form-control { padding-left: 2.2rem; }
.btn-clear { width: 38px; height: 38px; border: 1px solid #cbd5e1; background: #f8fafc; border-radius: 6px; color: #64748b; cursor: pointer; }

/* TABELA */
.report-main-wrapper {
  width: 100%; background: white; border-radius: 8px; border: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}
.report-table { width: 100%; border-collapse: collapse; }
.report-table th {
  background: #f8fafc; padding: 0.8rem 1.2rem; text-align: left;
  font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase;
  border-bottom: 1px solid #e2e8f0; position: sticky; top: 0;
}
.report-table td { padding: 1rem 1.2rem; border-bottom: 1px solid #f1f5f9; font-size: 0.85rem; color: #334155; vertical-align: middle; }
.report-table tr:hover { background-color: #fcfcfc; }

/* Ícone Categoria */
.cat-icon-wrapper { width: 32px; height: 32px; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center; color: white; font-size: 0.8rem; }
.bg-success { background-color: #10b981; }
.bg-danger { background-color: #ef4444; }

/* Badges */
.type-badge { font-size: 0.65rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; }
.badge-in { background: #dcfce7; color: #15803d; }
.badge-out { background: #fee2e2; color: #b91c1c; }

.actions-flex { display: flex; gap: 0.5rem; justify-content: flex-end; }
.btn-action { width: 32px; height: 32px; border: none; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.btn-action.primary { background-color: #eff6ff; color: #2563eb; }
.btn-action.danger { background-color: #fff1f2; color: #e11d48; }

.loading-state, .empty-state { text-align: center; padding: 4rem 2rem; color: #64748b; }
.spinner { border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%; width: 32px; height: 32px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }

@media (max-width: 1024px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .toolbar-grid { grid-template-columns: 1fr; }
}
</style>