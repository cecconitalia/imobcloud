<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1>Gestão de Vistorias</h1>
          <p class="subtitle">Monitore, execute e emita laudos das vistorias de imóveis.</p>
        </div>
      </div>
    </header>

    <main class="main-content">
      <div class="filter-bar">
        <div class="search-group">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            placeholder="Buscar por endereço, inquilino ou ID..." 
            v-model="searchQuery"
            @input="handleSearch"
          >
        </div>

        <div class="filter-group">
          <select v-model="filterTipo" @change="fetchVistorias">
            <option :value="null">Todos os Tipos</option>
            <option value="ENTRADA">Entrada</option>
            <option value="SAIDA">Saída</option>
            <option value="PERIODICA">Periódica</option>
          </select>
          
          <button class="btn-add" @click="navigateToForm(null)">
            <i class="fas fa-plus"></i> Nova Vistoria
          </button>
        </div>
      </div>

      <div v-if="loading" class="state-container">
        <div class="spinner"></div>
        <p>Carregando vistorias...</p>
      </div>

      <div v-else-if="vistorias.length === 0" class="state-container empty">
        <i class="fas fa-folder-open"></i>
        <h3>Nenhuma vistoria encontrada</h3>
        <p>Ajuste os filtros ou inicie uma nova vistoria.</p>
      </div>

      <div v-else class="cards-grid">
        <div 
            class="vistoria-card" 
            v-for="vistoria in vistorias" 
            :key="vistoria.id"
            :class="getBorderClass(vistoria.tipo)"
        >
          
          <div class="card-top">
            <div class="d-flex align-items-center gap-2">
                <span class="type-badge" :class="getBadgeClass(vistoria.tipo)">
                    {{ getTipoLabel(vistoria.tipo) }}
                </span>
                <span class="id-badge">#{{ vistoria.id }}</span>
            </div>
            <div class="date-badge">
                <i class="far fa-calendar-alt"></i> {{ formatDate(vistoria.data_vistoria) }}
            </div>
          </div>

          <div class="card-body">
            <h4 class="address-title" :title="getImovelDisplay(vistoria.contrato)">
                {{ getImovelDisplay(vistoria.contrato) }}
            </h4>
            
            <div class="info-row">
                <i class="fas fa-file-contract"></i> 
                <span>Contrato #{{ vistoria.contrato }}</span>
            </div>
            
            <div class="info-row">
                <i class="fas fa-user-tie"></i> 
                <span>{{ vistoria.realizado_por_nome || 'Vistoriador não informado' }}</span>
            </div>

            <div class="divider"></div>

            <div class="signatures-status">
                <div class="sig-item" :class="{ signed: vistoria.assinatura_responsavel }" title="Vistoriador">
                    <i class="fas fa-user-check"></i> <small>Vist.</small>
                </div>
                <div class="sig-item" :class="{ signed: vistoria.assinatura_locatario }" title="Locatário">
                    <i class="fas fa-user"></i> <small>Loc.</small>
                </div>
                <div 
                    v-if="vistoria.exige_assinatura_proprietario" 
                    class="sig-item" 
                    :class="{ signed: vistoria.assinatura_proprietario }" 
                    title="Proprietário"
                >
                    <i class="fas fa-home"></i> <small>Prop.</small>
                </div>
            </div>
          </div>

          <div class="card-footer">
            <div class="status-text">
                <i v-if="vistoria.concluida" class="fas fa-check-circle text-success"></i>
                <i v-else class="fas fa-clock text-warning"></i>
                {{ vistoria.concluida ? 'Concluída' : 'Em Andamento' }}
            </div>

            <div class="actions">
                <button class="btn-icon" @click="openDetalhesModal(vistoria.id)" title="Visualizar Detalhes">
                    <i class="fas fa-eye"></i>
                </button>
                
                <button 
                    class="btn-action" 
                    :class="vistoria.concluida ? 'btn-secondary' : 'btn-primary'"
                    @click="handleMainAction(vistoria)"
                    :disabled="downloadingId === vistoria.id"
                >
                    <span v-if="downloadingId === vistoria.id">
                        <i class="fas fa-spinner fa-spin"></i> Gerando...
                    </span>
                    <span v-else>
                        <i :class="vistoria.concluida ? 'fas fa-file-pdf' : 'fas fa-arrow-right'"></i>
                        {{ vistoria.concluida ? ' Ver Laudo' : ' Continuar' }}
                    </span>
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

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router'; 
import api from '@/services/api'; 
import { format } from 'date-fns';
import VistoriaDetalhesModal from '@/components/Vistorias/VistoriaDetalhesModal.vue'; 

export default defineComponent({
  name: 'VistoriasView',
  components: { VistoriaDetalhesModal },
  setup() {
    const router = useRouter(); 
    const vistorias = ref<any[]>([]);
    const contratos = ref<any[]>([]);
    const loading = ref(true);
    
    // Controle de download individual para o botão não travar a tela toda
    const downloadingId = ref<number | null>(null);
    
    const searchQuery = ref('');
    const filterTipo = ref<string | null>(null);
    const showDetalhesModal = ref(false);
    const selectedVistoriaId = ref<number | null>(null);

    // --- Helpers Visuais ---
    const formatDate = (dateString: string) => {
        if (!dateString) return '--/--';
        try { return format(new Date(dateString), 'dd/MM/yyyy'); } catch { return dateString; }
    };

    const getBadgeClass = (tipo: string) => {
        if(tipo === 'ENTRADA') return 'bg-success-light text-success';
        if(tipo === 'SAIDA') return 'bg-danger-light text-danger';
        return 'bg-info-light text-info';
    };

    const getBorderClass = (tipo: string) => {
        if(tipo === 'ENTRADA') return 'border-left-success';
        if(tipo === 'SAIDA') return 'border-left-danger';
        return 'border-left-info';
    };

    const getTipoLabel = (tipo: string) => {
        if(tipo === 'ENTRADA') return 'Entrada';
        if(tipo === 'SAIDA') return 'Saída';
        return 'Periódica';
    };

    const getImovelDisplay = (contratoId: number) => {
        const contrato = contratos.value.find(c => c.id === contratoId);
        return contrato ? contrato.imovel_display : `Contrato #${contratoId}`;
    };

    // --- Navegação e Ações ---
    const navigateToForm = (id: number | null) => {
        router.push({ name: 'vistoria-nova' });
    };

    // Lógica Central do Botão Principal
    const handleMainAction = (vistoria: any) => {
        if (vistoria.concluida) {
            openLaudo(vistoria.id); // Se concluída, abre o PDF
        } else {
            goToChecklist(vistoria.id); // Se não, vai para o checklist
        }
    };

    const goToChecklist = (id: number) => {
        router.push({ name: 'vistoria-checklist', params: { id } });
    };

    const openLaudo = async (id: number) => {
        downloadingId.value = id; // Ativa spinner no botão específico
        try {
            const response = await api.get(`/v1/vistorias/vistorias/${id}/gerar-laudo/`, { 
                responseType: 'blob' 
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            // Abre o PDF em uma nova aba
            window.open(url, '_blank');
            
            // Opcional: Se quiser forçar download em vez de abrir
            /*
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Laudo_Vistoria_${id}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            */
        } catch (error) {
            console.error(error);
            alert("Erro ao gerar o laudo PDF. Tente novamente.");
        } finally {
            downloadingId.value = null;
        }
    };

    // --- Dados ---
    const fetchContratos = async () => {
        try {
            const response = await api.get('/v1/contratos/');
            const rawData = response.data.results || response.data;
            contratos.value = rawData.map((c: any) => {
                let display = `Imóvel #${c.imovel}`;
                if (c.imovel_detalhes) {
                    if(c.imovel_detalhes.endereco_completo) display = c.imovel_detalhes.endereco_completo;
                    else if(c.imovel_detalhes.logradouro) display = `${c.imovel_detalhes.logradouro}, ${c.imovel_detalhes.numero || ''}`;
                }
                return { id: c.id, imovel_display: display };
            });
        } catch (error) { console.error(error); }
    }

    const fetchVistorias = async () => {
      loading.value = true;
      try {
        const params: any = {};
        if (filterTipo.value) params.tipo = filterTipo.value;
        if (searchQuery.value) params.search = searchQuery.value;

        const response = await api.get('/v1/vistorias/vistorias/', { params });
        vistorias.value = response.data.results || response.data;
      } catch (error) { vistorias.value = []; } 
      finally { loading.value = false; }
    };

    let timeout: any = null;
    const handleSearch = () => {
        clearTimeout(timeout);
        timeout = setTimeout(() => fetchVistorias(), 500);
    };
    
    const openDetalhesModal = (id: number) => { selectedVistoriaId.value = id; showDetalhesModal.value = true; }
    const closeDetalhesModal = () => { showDetalhesModal.value = false; selectedVistoriaId.value = null; fetchVistorias(); }

    onMounted(async () => {
        await fetchContratos();
        fetchVistorias();
    });

    return {
      vistorias, loading, searchQuery, filterTipo,
      showDetalhesModal, selectedVistoriaId, downloadingId,
      fetchVistorias, handleSearch,
      openDetalhesModal, closeDetalhesModal, 
      navigateToForm, goToChecklist, handleMainAction, // Adicionado handleMainAction
      formatDate, getBadgeClass, getBorderClass, getTipoLabel, getImovelDisplay
    };
  },
});
</script>

<style scoped>
/* Layout e Header Padrão */
.page-container {
  min-height: 100vh; background-color: #f3f4f6; font-family: 'Inter', sans-serif; padding-bottom: 60px;
}
.page-header {
  background: white; border-bottom: 1px solid #e5e7eb; padding: 20px 32px; margin-bottom: 24px;
}
.header-text h1 { font-size: 24px; font-weight: 700; color: #111827; margin: 0; }
.subtitle { color: #6b7280; font-size: 14px; margin: 4px 0 0 0; }
.main-content { padding: 0 32px; max-width: 1400px; margin: 0 auto; }

/* Filtros */
.filter-bar {
    display: flex; justify-content: space-between; flex-wrap: wrap; gap: 16px; margin-bottom: 24px;
}
.search-group {
    position: relative; flex: 1; min-width: 280px; max-width: 500px;
}
.search-group i { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #9ca3af; }
.search-group input {
    width: 100%; padding: 10px 12px 10px 36px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px;
}
.filter-group { display: flex; gap: 12px; align-items: center; }
.filter-group select {
    padding: 10px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background: white;
}
.btn-add {
    background: #2563eb; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: background 0.2s;
}
.btn-add:hover { background: #1d4ed8; }

/* Grid de Cards */
.cards-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px;
}

/* Card Style */
.vistoria-card {
    background: white; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    border: 1px solid #e5e7eb; display: flex; flex-direction: column; transition: transform 0.2s, box-shadow 0.2s;
    overflow: hidden; position: relative;
}
.vistoria-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }

/* Bordas Laterais por Tipo */
.border-left-success { border-left: 5px solid #22c55e; }
.border-left-danger { border-left: 5px solid #ef4444; }
.border-left-info { border-left: 5px solid #3b82f6; }

/* Card Top */
.card-top {
    padding: 16px; display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid #f3f4f6;
}
.type-badge {
    font-size: 11px; font-weight: 700; text-transform: uppercase; padding: 2px 8px; border-radius: 4px;
}
.bg-success-light { background: #dcfce7; color: #166534; }
.bg-danger-light { background: #fee2e2; color: #991b1b; }
.bg-info-light { background: #dbeafe; color: #1e40af; }

.id-badge { font-size: 12px; color: #6b7280; font-weight: 600; }
.date-badge { font-size: 12px; color: #4b5563; display: flex; align-items: center; gap: 4px; }

/* Card Body */
.card-body { padding: 16px; flex: 1; }
.address-title {
    font-size: 15px; font-weight: 600; color: #1f2937; margin: 0 0 12px 0;
    line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.info-row { font-size: 13px; color: #6b7280; margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
.divider { height: 1px; background: #f3f4f6; margin: 12px 0; }

/* Assinaturas */
.signatures-status { display: flex; gap: 12px; }
.sig-item {
    display: flex; flex-direction: column; align-items: center; gap: 2px; color: #d1d5db;
}
.sig-item i { font-size: 16px; }
.sig-item small { font-size: 10px; font-weight: 600; }
.sig-item.signed { color: #22c55e; } /* Verde se assinado */

/* Card Footer */
.card-footer {
    padding: 12px 16px; background: #f9fafb; border-top: 1px solid #e5e7eb;
    display: flex; justify-content: space-between; align-items: center;
}
.status-text { font-size: 12px; font-weight: 600; color: #4b5563; display: flex; align-items: center; gap: 6px; }

.actions { display: flex; gap: 8px; }
.btn-icon {
    width: 32px; height: 32px; border: 1px solid #d1d5db; border-radius: 6px; background: white;
    color: #6b7280; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.btn-icon:hover { background: #f3f4f6; color: #1f2937; }

.btn-action {
    padding: 6px 16px; border: none; border-radius: 6px; font-size: 12px; font-weight: 600;
    cursor: pointer; transition: background 0.2s; text-decoration: none; color: white; display: flex; align-items: center; gap: 6px;
}
.btn-primary { background: #3b82f6; }
.btn-primary:hover { background: #2563eb; }
.btn-secondary { background: #6b7280; }
.btn-secondary:hover { background: #4b5563; }
.btn-action:disabled { opacity: 0.7; cursor: not-allowed; }

/* States */
.state-container { text-align: center; padding: 40px; color: #9ca3af; }
.spinner { width: 30px; height: 30px; border: 3px solid #e5e7eb; border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s infinite linear; margin: 0 auto 10px; }
@keyframes spin { 100% { transform: rotate(360deg); } }
</style>