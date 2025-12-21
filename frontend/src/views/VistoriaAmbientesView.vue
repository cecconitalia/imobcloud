<script setup lang="ts">
/**
 * IMOBCLOUD - EXECUÇÃO DE VISTORIA
 * Correção Final: Upload de Fotos e Tratamento de Erros
 */

import { ref, onMounted, computed, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '@/services/api';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

// --- Interfaces ---
interface Foto { id: number; url: string; }

interface ItemVistoria {
  id: number | null;
  item: string;
  estado: 'NOVO' | 'BOM' | 'REGULAR' | 'RUIM' | 'INOPERANTE';
  descricao_avaria: string;
  fotos: Foto[];
  estado_referencia_entrada?: string; 
  descricao_referencia_entrada?: string;
}

interface Ambiente {
  id: number;
  nome: string;
  itens: ItemVistoria[];
  isCollapsed?: boolean;
}

interface Vistoria {
  id: number;
  contrato: number;
  tipo: string;
  data_vistoria: string;
  observacoes: string;
  imovel_display: string;
  exige_assinatura_proprietario: boolean;
  assinatura_locatario: string | null;
  assinatura_responsavel: string | null;
  assinatura_proprietario: string | null;
  leitura_agua?: string;
  leitura_luz?: string;
  leitura_gas?: string;
  chaves_devolvidas?: string;
  concluida: boolean;
}

// --- Estado ---
const route = useRoute();
const router = useRouter();
const vistoriaId = route.params.id as string;
const fileInput = ref<HTMLInputElement | null>(null);

const loading = ref(true);
const downloading = ref(false); 
const vistoria = ref<Partial<Vistoria>>({});
const ambientes = ref<Ambiente[]>([]);
const entradaRef = ref<any>(null);

const isConcluindo = ref(false);
const isSavingProgress = ref(false);
const activeTab = ref<'checklist' | 'medidores' | 'chaves'>('checklist');

// Modais
const showAmbienteModal = ref(false);
const showItemModal = ref(false);

const ambienteForm = ref({ nome: '' });
const editingItem = ref<ItemVistoria | null>(null);
const currentAmbienteId = ref<number | null>(null);
const itemForm = ref<ItemVistoria>({ id: null, item: '', estado: 'BOM', descricao_avaria: '', fotos: [] });
const selectedFile = ref<File | null>(null);

// Opções de Status
const statusOptions = [
  { val: 'NOVO', label: 'Novo', color: '#10b981' },
  { val: 'BOM', label: 'Bom', color: '#3b82f6' },
  { val: 'REGULAR', label: 'Regular', color: '#f59e0b' },
  { val: 'RUIM', label: 'Ruim', color: '#ef4444' },
  { val: 'INOPERANTE', label: 'Inop.', color: '#64748b' },
];

// Computados
const totalItens = computed(() => ambientes.value.reduce((acc, amb) => acc + (amb.itens ? amb.itens.length : 0), 0));

const progressPercent = computed(() => {
    if (totalItens.value === 0) return 0;
    const itensPreenchidos = ambientes.value.reduce((acc, amb) => acc + amb.itens.filter(i => i.estado).length, 0);
    return Math.round((itensPreenchidos / totalItens.value) * 100);
});

// --- Métodos de Dados ---
const loadData = async () => {
  loading.value = true;
  try {
    const response = await api.get(`/v1/vistorias/vistorias/${vistoriaId}/`);
    vistoria.value = response.data;
    
    ambientes.value = (response.data.ambientes || []).map((amb: Ambiente) => ({ 
        ...amb, 
        isCollapsed: false 
    }));

    if (vistoria.value.tipo === 'SAIDA') {
       await loadReferenciaEntrada(vistoria.value.contrato || 0);
    }

  } catch (error) {
    console.error("Erro ao carregar dados:", error);
  } finally {
    loading.value = false;
  }
};

const loadReferenciaEntrada = async (contratoId: number) => {
    try {
        const refRes = await api.get(`/v1/vistorias/vistorias/`, {
            params: { contrato: contratoId, tipo: 'ENTRADA', concluida: true }
        });
        const lastEntry = refRes.data.results ? refRes.data.results[0] : refRes.data[0];
        if (lastEntry) {
            const fullEntry = await api.get(`/v1/vistorias/vistorias/${lastEntry.id}/`);
            entradaRef.value = fullEntry.data;
            cruzarDados();
        }
    } catch (e) { console.error("Erro ref entrada", e); }
};

const cruzarDados = () => {
    if (!entradaRef.value) return;
    ambientes.value.forEach(ambSaida => {
        const ambEntrada = entradaRef.value.ambientes.find((a: any) => a.nome.toLowerCase() === ambSaida.nome.toLowerCase());
        if (ambEntrada) {
            ambSaida.itens.forEach(itemSaida => {
                if (itemSaida.estado_referencia_entrada) return;
                const itemEntrada = ambEntrada.itens.find((i: any) => i.item.toLowerCase() === itemSaida.item.toLowerCase());
                if (itemEntrada) {
                    itemSaida.estado_referencia_entrada = itemEntrada.estado;
                    itemSaida.descricao_referencia_entrada = itemEntrada.descricao_avaria;
                }
            });
        }
    });
};

const isEstadoPior = (item: ItemVistoria) => {
    if (!item.estado_referencia_entrada) return false;
    const ordem = ['NOVO', 'BOM', 'REGULAR', 'RUIM', 'INOPERANTE'];
    return ordem.indexOf(item.estado) > ordem.indexOf(item.estado_referencia_entrada as any);
};

// --- Salvamento e Finalização ---
const saveGeneralObs = async () => {
  if (vistoria.value.concluida) return;
  try { 
      await api.patch(`/v1/vistorias/vistorias/${vistoriaId}/`, {
          observacoes: vistoria.value.observacoes,
          leitura_agua: vistoria.value.leitura_agua,
          leitura_luz: vistoria.value.leitura_luz,
          leitura_gas: vistoria.value.leitura_gas,
          chaves_devolvidas: vistoria.value.chaves_devolvidas
      }); 
  } catch (e) { console.error(e); }
};

const saveProgress = async () => { 
    isSavingProgress.value = true; 
    try { await saveGeneralObs(); alert("Progresso salvo!"); } finally { isSavingProgress.value = false; } 
};

const concluirVistoria = async () => {
    if (vistoria.value.concluida) {
        router.push('/vistorias');
        return;
    }

    if (!confirm("Tem certeza que deseja finalizar a vistoria? A edição será bloqueada.")) return;
    
    isConcluindo.value = true;
    try {
        await saveGeneralObs();
        await api.patch(`/v1/vistorias/vistorias/${vistoriaId}/`, { concluida: true });
        alert("Vistoria finalizada com sucesso!");
        router.push('/vistorias');
    } catch (e) {
        alert("Erro ao finalizar vistoria.");
        console.error(e);
    } finally {
        isConcluindo.value = false;
    }
};

// --- Gestão de Ambientes e Itens ---
const openAmbienteModal = () => { if(vistoria.value.concluida) return; ambienteForm.value.nome = ''; showAmbienteModal.value = true; };
const saveAmbiente = async () => {
  if (!ambienteForm.value.nome) return;
  try { await api.post('/v1/vistorias/ambientes/', { vistoria: vistoriaId, nome: ambienteForm.value.nome }); showAmbienteModal.value = false; loadData(); } catch (e) { alert("Erro ao criar"); }
};
const deleteAmbiente = async (id: number) => { if(!confirm("Apagar ambiente?")) return; try { await api.delete(`/v1/vistorias/ambientes/${id}/`); loadData(); } catch (e) { alert("Erro"); } };
const toggleCollapse = (amb: Ambiente) => { amb.isCollapsed = !amb.isCollapsed; };

const openItemModal = (ambId: number, item: any) => {
  currentAmbienteId.value = ambId; 
  editingItem.value = item; 
  selectedFile.value = null; // Reseta arquivo selecionado
  
  if (item) {
      itemForm.value = { ...item };
  } else {
      itemForm.value = { id: null, item: '', estado: 'BOM', descricao_avaria: '', fotos: [] };
  }
  showItemModal.value = true;
};

// === FUNÇÃO DE SALVAR ITEM ===
const saveItem = async () => {
  if (!itemForm.value.item) return alert("Informe o nome do item");
  
  try {
    let itemId = editingItem.value?.id;
    const payload = { 
        ambiente: currentAmbienteId.value, 
        item: itemForm.value.item, 
        estado: itemForm.value.estado, 
        descricao_avaria: itemForm.value.descricao_avaria 
    };

    // 1. Salva ou Atualiza o Item (JSON)
    if (itemId) { 
        await api.patch(`/v1/vistorias/itens/${itemId}/`, payload); 
    } else { 
        const res = await api.post('/v1/vistorias/itens/', payload); 
        itemId = res.data.id; 
    }
    
    // 2. Upload da Imagem (Multipart)
    // Verifica se há arquivo E se temos um ID válido
    if (selectedFile.value && itemId) {
      const fd = new FormData();
      
      // ORDEM IMPORTANTE: Alguns backends preferem campos não-arquivo primeiro
      fd.append('item', String(itemId)); 
      fd.append('imagem', selectedFile.value);
      
      console.log('Enviando foto para item:', itemId, selectedFile.value.name); // Debug

      await api.post('/v1/vistorias/fotos/', fd, {
          headers: {
              'Content-Type': 'multipart/form-data'
          }
      });
    }
    
    showItemModal.value = false; 
    loadData();
  } catch (e: any) { 
      console.error("Erro no saveItem:", e);
      let msg = "Erro ao salvar item.";
      
      if (e.response) {
          if (e.response.status === 500) {
              msg = "Erro interno no servidor ao processar a imagem. Tente uma imagem menor ou contate o suporte.";
          } else if (e.response.data && e.response.data.detail) {
              msg = e.response.data.detail;
          } else if (e.response.data && typeof e.response.data === 'object') {
              // Tenta pegar a primeira mensagem de erro disponível
              const keys = Object.keys(e.response.data);
              if (keys.length > 0) msg = `${keys[0]}: ${e.response.data[keys[0]]}`;
          }
      }
      alert(msg); 
  }
};

const triggerFileInput = () => fileInput.value?.click();
const handleFileUpload = (e: Event) => { 
    const t = e.target as HTMLInputElement; 
    if (t.files && t.files.length > 0) {
        selectedFile.value = t.files[0]; 
    }
};

// --- PDF e Utils ---
const downloadLaudo = async () => {
    downloading.value = true;
    try {
        const res = await api.get(`/v1/vistorias/vistorias/${vistoriaId}/gerar-laudo/`, { responseType: 'blob' });
        window.open(window.URL.createObjectURL(new Blob([res.data], {type: 'application/pdf'})), '_blank');
    } catch (e) { alert("Erro PDF"); } finally { downloading.value = false; }
};

const goBack = () => router.push('/vistorias');
const viewPhoto = (url: string) => window.open(url, '_blank');

onMounted(loadData);
</script>

<template>
  <div class="vistoria-page">
    
    <header class="header-fixed">
      <div class="header-content">
        <div class="header-left">
          <button @click="goBack" class="btn-back"><i class="fas fa-arrow-left"></i></button>
          <div>
            <h1>Vistoria de {{ vistoria.tipo }}</h1>
            <p class="subtitle">{{ vistoria.imovel_display }}</p>
          </div>
        </div>
        <div class="header-actions">
           <button @click="downloadLaudo" :disabled="downloading" class="btn-icon" title="PDF">
              <i v-if="!downloading" class="fas fa-print"></i>
              <i v-else class="fas fa-spinner fa-spin"></i>
           </button>
           <button @click="concluirVistoria" :disabled="vistoria.concluida || isConcluindo" class="btn-action primary">
              <i v-if="!isConcluindo" class="fas fa-check"></i>
              <i v-else class="fas fa-spinner fa-spin"></i>
              <span>{{ vistoria.concluida ? 'Concluída' : (isConcluindo ? 'Finalizando...' : 'Finalizar') }}</span>
           </button>
        </div>
      </div>
      <div class="progress-container">
        <div class="progress-bar" :style="{ width: `${progressPercent}%` }"></div>
      </div>
    </header>

    <div class="tabs">
        <button v-for="tab in [{id:'checklist', l:'Checklist', i:'fa-list'}, {id:'medidores', l:'Medidores', i:'fa-tachometer-alt'}, {id:'chaves', l:'Chaves', i:'fa-key'}]"
            :key="tab.id" @click="activeTab = tab.id as any" class="tab-item" :class="{ active: activeTab === tab.id }">
            <i class="fas" :class="tab.i"></i> {{ tab.l }}
        </button>
    </div>

    <main class="main-content">
      <div v-if="loading" class="loading-state"><i class="fas fa-circle-notch fa-spin"></i> Carregando...</div>
      
      <div v-else>
        
        <div v-if="activeTab === 'checklist'" class="tab-panel">
           <div class="card summary-card">
              <div class="summary-text">
                 <h3>Progresso</h3>
                 <p>{{ totalItens }} itens vistoriados</p>
              </div>
              <div class="summary-percent">{{ progressPercent }}%</div>
              <button v-if="!vistoria.concluida" @click="saveProgress" class="btn-link" :disabled="isSavingProgress">
                  {{ isSavingProgress ? 'Salvando...' : 'Salvar Manualmente' }}
              </button>
           </div>

           <div class="ambientes-list">
              <div v-if="ambientes.length === 0" class="empty-state">
                  <i class="fas fa-home"></i><p>Nenhum ambiente.</p>
                  <button v-if="!vistoria.concluida" @click="openAmbienteModal" class="btn-action secondary">Criar Ambiente</button>
              </div>

              <div v-for="ambiente in ambientes" :key="ambiente.id" class="ambiente-container">
                 <div class="ambiente-header" @click="toggleCollapse(ambiente)">
                    <div class="ambiente-title">
                        <i class="fas fa-door-open"></i><span>{{ ambiente.nome }}</span>
                        <span class="count-badge">{{ ambiente.itens?.length || 0 }}</span>
                    </div>
                    <div class="ambiente-controls">
                        <button v-if="!vistoria.concluida" @click.stop="deleteAmbiente(ambiente.id)" class="btn-icon-small trash"><i class="fas fa-trash"></i></button>
                        <i class="fas fa-chevron-down arrow" :class="{ rotated: !ambiente.isCollapsed }"></i>
                    </div>
                 </div>

                 <div v-show="!ambiente.isCollapsed" class="ambiente-body">
                    <div v-for="item in ambiente.itens" :key="item.id || 0" @click="openItemModal(ambiente.id, item)" class="item-card">
                       <div class="status-strip" :class="item.estado"></div>
                       <div class="item-content">
                          <div class="item-main">
                             <span class="item-name">{{ item.item }}</span>
                             <span class="item-badge" :class="item.estado">{{ item.estado }}</span>
                          </div>
                          
                          <div v-if="item.estado_referencia_entrada" class="comparison-box" :class="{ alert: isEstadoPior(item) }">
                             <div class="comp-col"><span class="comp-label">Entrada</span><span class="comp-value">{{ item.estado_referencia_entrada }}</span></div>
                             <div class="comp-arrow"><i class="fas fa-arrow-right"></i></div>
                             <div class="comp-col"><span class="comp-label">Saída</span><span class="comp-value">{{ item.estado }}</span></div>
                             <div v-if="isEstadoPior(item)" class="worse-alert"><i class="fas fa-exclamation-triangle"></i> Piorou</div>
                          </div>

                          <div v-if="item.descricao_avaria" class="item-avaria"><i class="fas fa-comment-dots"></i> {{ item.descricao_avaria }}</div>
                          <div class="item-meta">
                             <div class="photos-indicator" v-if="item.fotos && item.fotos.length"><i class="fas fa-camera"></i> {{ item.fotos.length }} fotos</div>
                             <span class="action-text">Editar ></span>
                          </div>
                       </div>
                    </div>
                    <button v-if="!vistoria.concluida" @click="openItemModal(ambiente.id, null)" class="btn-add-item"><i class="fas fa-plus"></i> Novo Item</button>
                 </div>
              </div>
              <button v-if="!vistoria.concluida" @click="openAmbienteModal" class="btn-dashed"><i class="fas fa-plus-circle"></i> Novo Ambiente</button>
           </div>
        </div>

        <div v-if="activeTab === 'medidores'" class="tab-panel">
           <div class="card form-card">
              <h3>Leituras</h3>
              <div class="form-group"><label>Água</label><div class="input-wrapper"><i class="fas fa-tint icon-water"></i><input v-model="vistoria.leitura_agua" type="text" :disabled="vistoria.concluida"></div></div>
              <div class="form-group"><label>Luz</label><div class="input-wrapper"><i class="fas fa-bolt icon-energy"></i><input v-model="vistoria.leitura_luz" type="text" :disabled="vistoria.concluida"></div></div>
              <div class="form-group"><label>Gás</label><div class="input-wrapper"><i class="fas fa-fire icon-gas"></i><input v-model="vistoria.leitura_gas" type="text" :disabled="vistoria.concluida"></div></div>
              <button v-if="!vistoria.concluida" @click="saveGeneralObs" class="btn-action primary full-width">Salvar</button>
           </div>
        </div>

        <div v-if="activeTab === 'chaves'" class="tab-panel">
           <div class="card form-card">
              <h3>Chaves</h3>
              <textarea v-model="vistoria.chaves_devolvidas" rows="6" class="std-textarea" placeholder="Descreva as chaves..." :disabled="vistoria.concluida"></textarea>
              <button v-if="!vistoria.concluida" @click="saveGeneralObs" class="btn-action primary full-width">Salvar</button>
           </div>
        </div>
      </div>
    </main>

    <div v-if="showAmbienteModal" class="modal-overlay">
       <div class="modal-card small">
          <h3>Novo Ambiente</h3>
          <input v-model="ambienteForm.nome" type="text" class="std-input" placeholder="Ex: Sala" autoFocus />
          <div class="modal-buttons">
             <button @click="showAmbienteModal = false" class="btn-action secondary">Cancelar</button>
             <button @click="saveAmbiente" class="btn-action primary">Criar</button>
          </div>
       </div>
    </div>

    <div v-if="showItemModal" class="modal-overlay" @click.self="showItemModal = false">
       <div class="modal-sheet">
          <div class="sheet-header"><h3>{{ editingItem ? 'Editar' : 'Novo' }} Item</h3><button @click="showItemModal = false" class="close-btn"><i class="fas fa-times"></i></button></div>
          <div class="sheet-content">
             <div class="form-group"><label>Nome</label><input v-model="itemForm.item" class="std-input" placeholder="Ex: Porta" :disabled="vistoria.concluida" /></div>
             <div class="form-group">
                <label>Estado</label>
                <div class="status-grid">
                   <button v-for="opt in statusOptions" :key="opt.val" @click="!vistoria.concluida && (itemForm.estado = opt.val as any)" class="status-btn" :class="{ selected: itemForm.estado === opt.val }" :style="{ '--status-color': opt.color }" :disabled="vistoria.concluida">{{ opt.label }}</button>
                </div>
             </div>
             <div class="form-group"><label>Obs</label><textarea v-model="itemForm.descricao_avaria" rows="3" class="std-textarea" :disabled="vistoria.concluida"></textarea></div>
             
             <div class="form-group">
                <label>Fotos</label>
                <div class="photos-grid">
                    <div v-if="!vistoria.concluida" class="photo-add" @click="triggerFileInput">
                        <i class="fas fa-camera mb-1"></i>
                        <span>Add</span>
                    </div>
                    
                    <div v-for="foto in editingItem?.fotos" :key="foto.id" class="photo-item" @click="viewPhoto(foto.url)">
                        <img :src="foto.url" />
                    </div>
                    
                    <input type="file" ref="fileInput" class="hidden" accept="image/*" @change="handleFileUpload" />
                </div>
                
                <div v-if="selectedFile" class="mt-2 p-2 bg-blue-50 text-blue-700 text-xs rounded flex justify-between items-center border border-blue-100">
                    <span class="truncate"><i class="fas fa-file-image me-1"></i> {{ selectedFile.name }}</span>
                    <button @click="selectedFile = null" class="text-blue-500 hover:text-blue-700 fw-bold px-2">X</button>
                </div>
             </div>
          </div>
          <div class="sheet-footer">
              <button v-if="!vistoria.concluida" @click="saveItem" class="btn-action primary full-width">
                  {{ selectedFile ? 'Salvar e Enviar Foto' : 'Salvar Item' }}
              </button>
          </div>
       </div>
    </div>

  </div>
</template>

<style scoped>
/* CORES E VARIAVEIS */
.vistoria-page {
  --primary: #2563eb; --primary-dark: #1e40af; --bg-page: #f8fafc; --bg-card: #ffffff;
  --border: #e2e8f0; --text-main: #334155; --text-light: #64748b; --success: #10b981; --danger: #ef4444; --warning: #f59e0b;
  font-family: system-ui, -apple-system, sans-serif; background-color: var(--bg-page); color: var(--text-main); min-height: 100vh; padding-bottom: 80px;
}

/* HEADER & TABS */
.header-fixed { position: sticky; top: 0; background: white; border-bottom: 1px solid var(--border); z-index: 50; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
.header-content { display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; max-width: 800px; margin: 0 auto; }
.header-left { display: flex; align-items: center; gap: 12px; }
.btn-back { background: none; border: none; font-size: 1.2rem; color: var(--text-light); cursor: pointer; }
.header-left h1 { margin: 0; font-size: 1rem; font-weight: 700; text-transform: uppercase; }
.subtitle { margin: 0; font-size: 0.8rem; color: var(--text-light); }
.header-actions { display: flex; gap: 8px; align-items: center; }
.btn-icon { background: #f1f5f9; width: 36px; height: 36px; border-radius: 50%; border: none; cursor: pointer; color: var(--text-main); display: flex; align-items: center; justify-content: center; }
.progress-container { height: 3px; background: #e2e8f0; width: 100%; }
.progress-bar { height: 100%; background: var(--success); transition: width 0.3s ease; }

.tabs { background: white; display: flex; border-bottom: 1px solid var(--border); position: sticky; top: 60px; z-index: 40; }
.tab-item { flex: 1; padding: 12px; background: none; border: none; font-weight: 600; color: var(--text-light); border-bottom: 3px solid transparent; cursor: pointer; }
.tab-item.active { color: var(--primary); border-bottom-color: var(--primary); background: #eff6ff; }

/* MAIN & CARDS */
.main-content { padding: 16px; max-width: 800px; margin: 0 auto; }
.card { background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border); padding: 16px; margin-bottom: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.03); }
.summary-card { display: flex; justify-content: space-between; align-items: center; background: linear-gradient(to right, #ffffff, #f8fafc); }
.summary-text h3 { margin: 0; font-size: 1rem; } .summary-text p { margin: 0; color: var(--text-light); font-size: 0.85rem; }
.summary-percent { font-size: 1.5rem; font-weight: 800; color: var(--primary); }
.btn-link { background: none; border: none; color: var(--primary); font-size: 0.8rem; font-weight: 600; cursor: pointer; text-decoration: underline; }
.empty-state { text-align: center; padding: 40px; color: var(--text-light); border: 2px dashed var(--border); border-radius: 12px; background: white; margin-bottom: 20px; }
.empty-state i { font-size: 2rem; margin-bottom: 10px; display: block; opacity: 0.5; }

/* AMBIENTES & ITENS */
.ambiente-container { background: white; border-radius: 12px; border: 1px solid var(--border); margin-bottom: 16px; overflow: hidden; }
.ambiente-header { padding: 14px; background: #f8fafc; display: flex; justify-content: space-between; align-items: center; cursor: pointer; border-bottom: 1px solid var(--border); }
.ambiente-title { font-weight: 700; display: flex; align-items: center; gap: 8px; text-transform: uppercase; font-size: 0.9rem; }
.count-badge { background: white; border: 1px solid var(--border); padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; }
.ambiente-controls { display: flex; align-items: center; gap: 10px; }
.btn-icon-small { background: none; border: none; cursor: pointer; color: var(--text-light); }
.arrow { transition: transform 0.3s; } .arrow.rotated { transform: rotate(180deg); }

.item-card { position: relative; padding: 16px 16px 16px 20px; border-bottom: 1px solid var(--border); cursor: pointer; background: white; }
.status-strip { position: absolute; left: 0; top: 0; bottom: 0; width: 5px; }
.status-strip.NOVO { background: #10b981; } .status-strip.BOM { background: #3b82f6; } .status-strip.REGULAR { background: #f59e0b; } .status-strip.RUIM { background: #ef4444; } .status-strip.INOPERANTE { background: #64748b; }
.item-main { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.item-name { font-weight: 600; font-size: 1rem; }
.item-badge { font-size: 0.7rem; padding: 3px 8px; border-radius: 4px; font-weight: 700; background: #f1f5f9; color: var(--text-light); border: 1px solid var(--border); }

/* DIFF VIEW */
.comparison-box { background: #f8fafc; border: 1px solid var(--border); border-radius: 8px; padding: 8px 12px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; font-size: 0.8rem; }
.comparison-box.alert { border-color: #fecaca; background: #fef2f2; }
.comp-col { display: flex; flex-direction: column; } .comp-label { font-size: 0.7rem; color: var(--text-light); font-weight: 700; text-transform: uppercase; } .comp-value { font-weight: 600; }
.worse-alert { color: var(--danger); font-weight: 800; font-size: 0.75rem; text-transform: uppercase; display: flex; align-items: center; gap: 4px; }

.item-avaria { font-size: 0.85rem; color: var(--text-light); background: #fff1f2; padding: 8px; border-radius: 6px; margin-bottom: 8px; }
.item-meta { display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-light); }
.photos-indicator { color: var(--primary); font-weight: 600; } .action-text { color: var(--primary); font-weight: 600; opacity: 0.7; }
.btn-add-item { width: 100%; padding: 12px; background: white; border: none; color: var(--text-light); font-weight: 600; cursor: pointer; text-transform: uppercase; font-size: 0.8rem; }
.btn-dashed { width: 100%; border: 2px dashed var(--border); background: none; padding: 16px; border-radius: 12px; color: var(--text-light); font-weight: 600; cursor: pointer; margin-top: 10px; }

/* FORM & INPUTS */
.form-card { padding: 20px; } .form-group { margin-bottom: 16px; } .form-group label { display: block; font-size: 0.8rem; font-weight: 700; color: var(--text-light); margin-bottom: 6px; text-transform: uppercase; }
.input-wrapper { position: relative; } .input-wrapper i { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; } .input-wrapper i.icon-water { color: #3b82f6; } .input-wrapper i.icon-energy { color: #f59e0b; } .input-wrapper i.icon-gas { color: #ef4444; }
.std-input, .std-textarea, .input-wrapper input { width: 100%; padding: 12px; border: 1px solid var(--border); border-radius: 8px; font-size: 1rem; outline: none; box-sizing: border-box; }
.input-wrapper input { padding-left: 36px; font-weight: 600; font-family: monospace; }

/* BOTOES */
.btn-action { padding: 10px 20px; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; font-size: 0.9rem; display: flex; align-items: center; justify-content: center; gap: 8px; }
.btn-action:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-action.primary { background: var(--text-main); color: white; } .btn-action.secondary { background: #f1f5f9; color: var(--text-main); }
.full-width { width: 100%; }

/* MODALS */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(3px); }
.modal-card { background: white; border-radius: 16px; padding: 24px; width: 90%; max-width: 500px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); } .modal-card.small { max-width: 350px; text-align: center; }
.modal-buttons { display: flex; gap: 10px; margin-top: 20px; }
.modal-sheet { background: white; width: 100%; height: 95vh; position: fixed; bottom: 0; border-radius: 24px 24px 0 0; display: flex; flex-direction: column; max-width: 600px; }
@media(min-width: 600px) { .modal-sheet { height: auto; max-height: 85vh; position: relative; bottom: auto; border-radius: 16px; } }
.sheet-header { padding: 16px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
.close-btn { background: #f1f5f9; border: none; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; }
.sheet-content { padding: 20px; overflow-y: auto; flex: 1; } .sheet-footer { padding: 16px; border-top: 1px solid var(--border); background: #f8fafc; border-radius: 0 0 24px 24px; }

.status-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.status-btn { padding: 12px 4px; background: white; border: 1px solid var(--border); border-radius: 8px; font-weight: 600; color: var(--text-light); cursor: pointer; font-size: 0.8rem; display: flex; flex-direction: column; align-items: center; gap: 4px; }
.status-btn::before { content: ''; width: 8px; height: 8px; border-radius: 50%; background: var(--status-color); }
.status-btn.selected { border-color: var(--status-color); background: #f8fafc; color: var(--text-main); box-shadow: 0 0 0 1px var(--status-color); }

.photos-grid { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 8px; }
.photo-add, .photo-item { width: 70px; height: 70px; border-radius: 8px; overflow: hidden; cursor: pointer; position: relative; }
.photo-add { border: 2px dashed var(--border); display: flex; flex-direction: column; align-items: center; justify-content: center; color: var(--text-light); font-size: 0.75rem; font-weight: 600; }
.photo-item img { width: 100%; height: 100%; object-fit: cover; }
.hidden { display: none; }
</style>