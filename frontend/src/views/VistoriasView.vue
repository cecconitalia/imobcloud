<template>
  <div class="modern-container">
    
    <header class="view-header">
      <div class="header-content">
        <h2><i class="fas fa-clipboard-check"></i> Gestão de Vistorias</h2>
        <p>Gerencie vistorias de entrada, saída e periódicas.</p>
      </div>
      <button class="btn-primary-custom" @click="navigateToForm(null)">
        <i class="fas fa-plus"></i> Nova Vistoria
      </button>
    </header>

    <div class="filter-card">
      <div class="filter-flex">
        
        <div class="filter-item search-item">
          <label>Buscar</label>
          <div class="input-wrapper">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              placeholder="Pesquisar Imóvel, Contrato..." 
              v-model="searchQuery"
              @input="handleSearch"
            >
          </div>
        </div>

        <div class="filter-item select-item">
          <label>Tipo</label>
          <div class="select-wrapper">
            <select v-model="filterTipo" @change="fetchVistorias">
              <option :value="null">Todos os Tipos</option>
              <option value="ENTRADA">📥 Entrada</option>
              <option value="SAIDA">📤 Saída</option>
              <option value="PERIODICA">🔄 Periódica</option>
            </select>
            <i class="fas fa-chevron-down select-arrow"></i>
          </div>
        </div>

        <div class="filter-item select-item">
          <label>Contrato</label>
          <div class="select-wrapper">
            <select v-model="filterContrato" @change="fetchVistorias">
              <option :value="null">Todos os Contratos</option>
              <option v-for="c in contratos" :key="c.id" :value="c.id">
                #{{ c.id }} - {{ c.imovel_display }}
              </option>
            </select>
            <i class="fas fa-chevron-down select-arrow"></i>
          </div>
        </div>

        <div class="filter-item button-item">
          <label>&nbsp;</label>
          <button class="btn-outline" @click="clearFilters" title="Limpar filtros">
            <i class="fas fa-eraser me-2"></i> Limpar
          </button>
        </div>

      </div>
    </div>

    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p>Buscando dados...</p>
    </div>

    <div v-else-if="vistorias.length === 0" class="state-container empty">
      <i class="fas fa-folder-open"></i>
      <h3>Nenhum resultado encontrado</h3>
      <p>Tente ajustar os filtros acima ou cadastre uma nova vistoria.</p>
      <button class="btn-text" @click="clearFilters">Limpar busca</button>
    </div>

    <div v-else class="cards-grid">
      <div class="vistoria-card" v-for="vistoria in vistorias" :key="vistoria.id">
        
        <div class="card-top">
          <div class="badge" :class="getBadgeClass(vistoria.tipo)">
            {{ getTipoLabel(vistoria.tipo) }}
          </div>
          <div class="card-id">#{{ vistoria.id }}</div>
        </div>

        <div class="card-content">
          <h3 class="card-title" :title="'Contrato #' + vistoria.contrato">
            <i class="fas fa-file-contract"></i> Contrato {{ vistoria.contrato }}
          </h3>
          <p class="card-subtitle text-truncate">
             <i class="fas fa-map-marker-alt me-1"></i> 
             {{ getImovelDisplay(vistoria.contrato) }}
          </p>

          <div class="card-info-row">
            <div class="info-item">
              <span class="label">DATA</span>
              <span class="value">{{ formatDate(vistoria.data_vistoria) }}</span>
            </div>
            <div class="separator"></div>
            <div class="info-item">
              <span class="label">AMBIENTES</span>
              <span class="value">{{ vistoria.ambientes ? vistoria.ambientes.length : 0 }}</span>
            </div>
          </div>

          <div class="card-user">
            <i class="fas fa-user-circle"></i> {{ vistoria.realizado_por_nome || 'Admin' }}
          </div>
        </div>

        <div class="card-actions">
          <button class="btn-primary-custom full-width" @click="openDetalhesModal(vistoria.id)">
            Detalhes
          </button>
          
          <div class="secondary-actions">
            <button class="btn-icon edit" @click="navigateToForm(vistoria.id)" title="Editar">
              <i class="fas fa-edit"></i>
            </button>
            <button class="btn-icon delete" @click="deleteVistoria(vistoria.id)" title="Excluir">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>

      </div>
    </div>

    <VistoriaDetalhesModal 
      :show="showDetalhesModal" 
      :vistoriaId="selectedVistoriaId" 
      @close="closeDetalhesModal"
      @refresh="fetchVistorias"
    />

  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router'; // Importação essencial para redirecionamento
import api from '@/services/api'; 
import { format } from 'date-fns';

import VistoriaDetalhesModal from '@/components/Vistorias/VistoriaDetalhesModal.vue'; 

export default defineComponent({
  name: 'VistoriasView',
  components: {
    VistoriaDetalhesModal,
  },
  setup() {
    const router = useRouter(); // Instância do router
    
    const vistorias = ref<any[]>([]);
    const contratos = ref<any[]>([]);
    const loading = ref(true);
    
    // Filtros
    const searchQuery = ref('');
    const filterContrato = ref<number | null>(null);
    const filterTipo = ref<string | null>(null);
    
    // Controle Modal de Detalhes
    const showDetalhesModal = ref(false);
    const selectedVistoriaId = ref<number | null>(null);

    // Formatação
    const formatDate = (dateString: string) => {
        if (!dateString) return '--/--';
        try { return format(new Date(dateString), 'dd/MM/yyyy'); } catch { return dateString; }
    };

    const getBadgeClass = (tipo: string) => {
        switch (tipo) {
            case 'ENTRADA': return 'badge-success';
            case 'SAIDA': return 'badge-danger';
            case 'PERIODICA': return 'badge-info';
            default: return 'badge-default';
        }
    };

    const getTipoLabel = (tipo: string) => {
        switch (tipo) {
            case 'ENTRADA': return 'Entrada';
            case 'SAIDA': return 'Saída';
            case 'PERIODICA': return 'Periódica';
            default: return tipo;
        }
    };

    const getImovelDisplay = (contratoId: number) => {
        const contrato = contratos.value.find(c => c.id === contratoId);
        return contrato ? contrato.imovel_display : 'Imóvel vinculado';
    };

    // Navegação para a nova tela de formulário
    const navigateToForm = (id: number | null) => {
        if (id) {
            // Edição
            router.push({ name: 'vistoria-editar', params: { id } });
        } else {
            // Criação
            router.push({ name: 'vistoria-nova' });
        }
    };

    // Buscas API
    const fetchContratos = async () => {
        try {
            // Chama a rota sem duplicar o sufixo
            const response = await api.get('/v1/contratos/');
            const rawData = response.data.results ? response.data.results : response.data;
            
            contratos.value = rawData.map((c: any) => {
                let display = `Imóvel #${c.imovel}`;
                if (c.imovel_detalhes && c.imovel_detalhes.endereco_completo) {
                    display = c.imovel_detalhes.endereco_completo;
                } else if (c.imovel_detalhes && c.imovel_detalhes.logradouro) {
                    display = c.imovel_detalhes.logradouro;
                }
                return { id: c.id, imovel_display: display };
            });
        } catch (error) { 
            console.error('Erro ao carregar contratos:', error); 
        }
    }

    const fetchVistorias = async () => {
      loading.value = true;
      try {
        const params: any = {};
        if (filterContrato.value) params.contrato = filterContrato.value;
        if (filterTipo.value) params.tipo = filterTipo.value;
        if (searchQuery.value && searchQuery.value.trim() !== '') params.search = searchQuery.value;

        const response = await api.get('/v1/vistorias/vistorias/', { params });
        vistorias.value = response.data.results || response.data;
      } catch (error) { 
          console.error('Erro ao buscar vistorias:', error); 
          vistorias.value = [];
      } 
      finally { loading.value = false; }
    };

    let timeout: any = null;
    const handleSearch = () => {
        clearTimeout(timeout);
        timeout = setTimeout(() => fetchVistorias(), 500);
    };

    const clearFilters = () => {
        searchQuery.value = '';
        filterContrato.value = null;
        filterTipo.value = null;
        fetchVistorias();
    };

    const deleteVistoria = async (id: number) => {
      if (confirm('ATENÇÃO: Excluir esta vistoria apagará todos os ambientes e fotos. Confirmar?')) {
        try {
          await api.delete(`/v1/vistorias/vistorias/${id}/`);
          vistorias.value = vistorias.value.filter(v => v.id !== id);
        } catch (error) { alert('Erro ao excluir vistoria.'); }
      }
    };
    
    // Modais (Apenas Detalhes)
    const openDetalhesModal = (id: number) => { selectedVistoriaId.value = id; showDetalhesModal.value = true; }
    const closeDetalhesModal = () => { showDetalhesModal.value = false; selectedVistoriaId.value = null; fetchVistorias(); }

    onMounted(() => {
        fetchContratos();
        fetchVistorias();
    });

    return {
      vistorias, contratos, loading, searchQuery, filterContrato, filterTipo,
      showDetalhesModal, selectedVistoriaId,
      fetchVistorias, handleSearch, clearFilters, deleteVistoria, 
      openDetalhesModal, closeDetalhesModal, 
      navigateToForm, // Nova função retornada
      formatDate, getBadgeClass, getTipoLabel, getImovelDisplay
    };
  },
});
</script>

<style scoped>
/* =========================================
   ESTILOS MODERNOS
   ========================================= */

.modern-container {
  padding: 24px;
  background-color: #f8f9fa;
  min-height: 100vh;
  font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  color: #333;
}

/* --- HEADER --- */
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}
.view-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 4px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}
.view-header h2 i { color: #3498db; }
.view-header p { color: #7f8c8d; margin: 0; font-size: 14px; }

/* --- FILTROS (FLEXBOX) --- */
.filter-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
  margin-bottom: 24px;
}

.filter-flex {
  display: flex;
  flex-wrap: wrap; 
  gap: 16px;
  align-items: flex-end; 
}

.search-item { flex: 2; min-width: 250px; }
.select-item { flex: 1; min-width: 180px; }
.button-item { flex: 0 0 auto; }

.filter-item label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #95a5a6;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Wrapper para Inputs com Ícones */
.input-wrapper, .select-wrapper { position: relative; width: 100%; }
.input-wrapper i {
  position: absolute; left: 12px; top: 50%; transform: translateY(-50%);
  color: #bdc3c7; pointer-events: none;
}
.select-arrow {
  position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
  color: #bdc3c7; pointer-events: none; font-size: 12px;
}

/* Inputs e Selects com ALTURA FIXA */
.input-wrapper input, select {
  width: 100%; padding: 0 12px 0 36px; 
  border: 1px solid #e0e0e0; border-radius: 6px;
  font-size: 14px; color: #34495e; background-color: #fff;
  height: 42px; line-height: 42px;
  appearance: none; -webkit-appearance: none;
  box-sizing: border-box;
}
select { padding-left: 12px; padding-right: 30px; }

.input-wrapper input:focus, select:focus {
  border-color: #3498db; outline: none;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

/* --- BOTÕES --- */
.btn-primary-custom {
  background-color: #3498db; color: white; border: none; padding: 0 24px;
  border-radius: 6px; font-weight: 600; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  transition: background 0.2s; height: 42px;
}
.btn-primary-custom:hover { background-color: #2980b9; }

.btn-outline {
  background: white; border: 1px solid #bdc3c7; color: #7f8c8d;
  padding: 0 24px; border-radius: 6px; cursor: pointer;
  font-weight: 600; height: 42px; display: flex;
  align-items: center; justify-content: center;
  transition: all 0.2s; white-space: nowrap; width: 100%;
}
.btn-outline:hover { background: #f8f9fa; border-color: #95a5a6; color: #2c3e50; }

.btn-icon {
  width: 36px; height: 36px; border-radius: 6px; border: 1px solid #eee;
  background: white; color: #95a5a6; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.btn-icon:hover { transform: translateY(-2px); box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.btn-icon.edit:hover { border-color: #f1c40f; color: #f39c12; }
.btn-icon.delete:hover { border-color: #e74c3c; color: #c0392b; }

.btn-text {
    background: none; border: none; color: #3498db; 
    text-decoration: underline; cursor: pointer; font-weight: 600;
}

/* --- GRID DE CARDS --- */
.cards-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 24px;
}

.vistoria-card {
  background: white; border-radius: 12px; overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
  transition: transform 0.2s, box-shadow 0.2s; display: flex; flex-direction: column;
  border: 1px solid #f0f0f0;
}
.vistoria-card:hover {
  transform: translateY(-4px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.08);
}

.card-top {
  padding: 16px; background: #fafafa; border-bottom: 1px solid #eee;
  display: flex; justify-content: space-between; align-items: center;
}
.card-id { font-size: 12px; font-weight: 700; color: #bdc3c7; }

/* Badges */
.badge {
  padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.5px;
}
.badge-success { background: #dcfce7; color: #166534; }
.badge-danger { background: #fee2e2; color: #991b1b; }
.badge-info { background: #e0f2fe; color: #075985; }
.badge-default { background: #f3f4f6; color: #4b5563; }

.card-content { padding: 20px; flex-grow: 1; }
.card-title {
  font-size: 16px; font-weight: 700; color: #2c3e50; margin: 0 0 6px 0;
  display: flex; align-items: center; gap: 8px;
}
.card-title i { color: #95a5a6; font-size: 14px; }
.card-subtitle { font-size: 13px; color: #7f8c8d; margin: 0 0 20px 0; }

.card-info-row {
  display: flex; align-items: center; background: #f8fafc; border: 1px solid #e2e8f0;
  border-radius: 8px; padding: 12px; margin-bottom: 16px;
}
.info-item { flex: 1; text-align: center; }
.separator { width: 1px; height: 24px; background: #e2e8f0; margin: 0 10px; }
.info-item .label { display: block; font-size: 10px; font-weight: 700; color: #94a3b8; }
.info-item .value { font-size: 14px; font-weight: 600; color: #334155; }

.card-user {
  font-size: 13px; color: #64748b; display: flex; align-items: center;
  gap: 6px; justify-content: flex-end; font-weight: 500;
}

.card-actions {
  padding: 16px; border-top: 1px solid #f0f0f0; display: flex; gap: 12px; background: #fff;
}
.full-width { flex: 1; }
.secondary-actions { display: flex; gap: 8px; }

/* --- ESTADOS --- */
.state-container { text-align: center; padding: 80px 0; color: #94a3b8; }
.state-container i { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
.state-container h3 { color: #475569; font-size: 18px; margin-bottom: 8px; }
.spinner {
  border: 3px solid #f3f3f3; border-top: 3px solid #3498db; border-radius: 50%;
  width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 16px auto;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>