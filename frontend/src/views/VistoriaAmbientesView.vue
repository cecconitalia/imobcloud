<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-content">
        <button class="btn-back" @click="goBack" title="Voltar">
          <i class="fas fa-arrow-left"></i>
        </button>
        <div class="header-text">
          <div class="d-flex align-items-center gap-2">
            <h1>Checklist de Execução</h1>
            <span class="badge-tipo" :class="getTipoClass(vistoria.tipo)">
                {{ vistoria.tipo }}
            </span>
            <span v-if="vistoria.concluida" class="badge-status locked">
                <i class="fas fa-lock"></i> Concluída
            </span>
          </div>
          <p class="subtitle">
            <i class="far fa-calendar-alt me-1"></i> {{ formatDate(vistoria.data_vistoria) }} 
            <span class="mx-2">•</span> 
            <i class="fas fa-file-contract me-1"></i> Contrato #{{ vistoria.contrato }}
          </p>
        </div>
      </div>
      
      <div class="header-actions">
         <button class="btn-action-outline" @click="downloadLaudo" :disabled="downloading" title="Baixar PDF">
            <i v-if="downloading" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-file-pdf"></i>
            <span class="d-none d-md-inline ms-2">Laudo</span>
         </button>
         
         <button class="btn-action-primary" @click="concluirVistoria" :disabled="vistoria.concluida || isConcluindo">
            <i v-if="isConcluindo" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-check-circle"></i>
            <span class="d-none d-md-inline ms-2">
                {{ vistoria.concluida ? 'Vistoria Fechada' : 'Finalizar e Sair' }}
            </span>
         </button>
      </div>
    </header>

    <main class="main-content">
      
      <div v-if="vistoria.concluida" class="locked-alert">
          <i class="fas fa-lock me-2"></i>
          <strong>Vistoria Concluída:</strong> A edição de itens e ambientes está bloqueada. Apenas a coleta de assinaturas está disponível.
      </div>

      <div v-if="loading" class="loading-container">
        <div class="spinner"></div>
        <p>A carregar checklist...</p>
      </div>

      <div v-else>
        
        <div class="status-dashboard">
            <div class="status-item main-location">
                <i class="fas fa-map-marker-alt icon"></i>
                <div class="text">
                    <label>Imóvel</label>
                    <strong>{{ vistoria.imovel_display || 'Endereço não disponível' }}</strong>
                </div>
            </div>
            
            <div class="status-item progress-area">
                <div class="d-flex justify-content-between mb-1">
                    <label>Progresso da Vistoria</label>
                    <span class="progress-val">{{ totalItens }} itens</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: 100%"></div> 
                </div>
            </div>

            <div class="status-actions">
                <button v-if="!vistoria.concluida" class="btn-dashboard" @click="saveProgress" :disabled="isSavingProgress">
                    <i :class="isSavingProgress ? 'fas fa-spinner fa-spin' : 'fas fa-save'"></i>
                    Salvar
                </button>
                
                <button class="btn-dashboard" @click="openSignatureModal">
                    <i class="fas fa-file-signature"></i>
                    Assinar
                </button>
            </div>
        </div>

        <div class="grid-layout mb-4">
            <div class="info-card">
                <div class="card-label"><i class="fas fa-user-tie"></i> Vistoriador Responsável</div>
                <div class="mt-1">
                    <span class="info-value">{{ vistoria.realizado_por_nome || 'Não informado' }}</span>
                </div>
            </div>

            <div class="info-card">
                <div class="card-label"><i class="fas fa-clipboard"></i> Observações Gerais</div>
                <textarea 
                    v-model="vistoria.observacoes" 
                    class="form-textarea-transparent" 
                    rows="1" 
                    placeholder="Adicione observações gerais aqui..."
                    :disabled="vistoria.concluida"
                    @blur="saveGeneralObs"
                ></textarea>
            </div>
        </div>

        <div v-if="ambientes.length === 0" class="empty-state">
            <div class="empty-icon"><i class="fas fa-door-open"></i></div>
            <h3>Nenhum ambiente adicionado</h3>
            <p>Comece por adicionar as divisões do imóvel (Ex: Sala, Cozinha).</p>
            <button v-if="!vistoria.concluida" class="btn-add-large" @click="openAmbienteModal">
                <i class="fas fa-plus"></i> Criar Primeiro Ambiente
            </button>
        </div>

        <div v-else class="ambientes-list">
            <div v-for="ambiente in ambientes" :key="ambiente.id" class="ambiente-wrapper">
                
                <div class="ambiente-header">
                    <div class="ambiente-title">
                        <i class="fas fa-layer-group text-primary"></i>
                        {{ ambiente.nome }}
                        <span class="counter-badge">{{ ambiente.itens ? ambiente.itens.length : 0 }}</span>
                    </div>
                    <div class="ambiente-tools" v-if="!vistoria.concluida">
                        <button class="btn-tool danger" @click="deleteAmbiente(ambiente.id)" title="Remover Ambiente">
                            <i class="far fa-trash-alt"></i>
                        </button>
                    </div>
                </div>

                <div class="ambiente-content">
                    <div v-if="ambiente.itens && ambiente.itens.length > 0" class="itens-grid">
                        <div v-for="item in ambiente.itens" :key="item.id" class="item-card" @click="openItemModal(ambiente.id, item)">
                            <div class="item-status-stripe" :class="getStatusClass(item.estado)"></div>
                            <div class="item-main">
                                <div class="item-top">
                                    <span class="item-name">{{ item.item }}</span>
                                    <span class="status-tag" :class="getStatusClass(item.estado)">{{ item.estado }}</span>
                                </div>
                                <p class="item-desc" v-if="item.descricao_avaria">{{ item.descricao_avaria }}</p>
                                <p class="item-desc text-muted" v-else>Sem observações.</p>
                                
                                <div class="item-photos" v-if="item.fotos && item.fotos.length">
                                    <i class="fas fa-camera"></i> {{ item.fotos.length }} foto(s)
                                </div>
                            </div>
                            <div class="item-arrow">
                                <i :class="vistoria.concluida ? 'fas fa-eye' : 'fas fa-chevron-right'"></i>
                            </div>
                        </div>
                    </div>
                    <div v-else class="empty-items">
                        <p>Nenhum item avaliado.</p>
                    </div>

                    <button v-if="!vistoria.concluida" class="btn-add-item" @click="openItemModal(ambiente.id, null)">
                        <i class="fas fa-plus-circle"></i> Adicionar Item
                    </button>
                </div>

            </div>

            <button v-if="!vistoria.concluida" class="btn-new-ambiente" @click="openAmbienteModal">
                <i class="fas fa-plus"></i> Novo Ambiente
            </button>
        </div>

      </div>
    </main>

    <div v-if="showAmbienteModal" class="modal-backdrop">
      <div class="modal-window small">
        <div class="modal-h">
          <h4>Novo Ambiente</h4>
          <button @click="showAmbienteModal = false" class="close-modal"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-b">
          <label>Nome da Divisão</label>
          <input type="text" class="form-input" v-model="ambienteForm.nome" placeholder="Ex: Suite Master" autoFocus>
        </div>
        <div class="modal-f">
          <button class="btn-cancel" @click="showAmbienteModal = false">Cancelar</button>
          <button class="btn-confirm" @click="saveAmbiente">Criar</button>
        </div>
      </div>
    </div>

    <div v-if="showItemModal" class="modal-backdrop">
      <div class="modal-window medium">
        <div class="modal-h">
          <h4>{{ editingItem ? (vistoria.concluida ? 'Visualizar Item' : 'Editar Item') : 'Novo Item' }}</h4>
          <button @click="showItemModal = false" class="close-modal"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-b scroll-y">
            <div class="form-group">
                <label>O que está a ser avaliado?</label>
                <input 
                    type="text" class="form-input" v-model="itemForm.item" 
                    placeholder="Ex: Porta, Pintura, Vidros..."
                    :disabled="vistoria.concluida"
                >
            </div>
            
            <div class="form-group">
                <label>Estado de Conservação</label>
                <div v-if="vistoria.concluida" class="p-2 border rounded bg-light fw-bold">
                    {{ statusOptions.find(s => s.val === itemForm.estado)?.label || itemForm.estado }}
                </div>
                <div v-else class="status-selector">
                    <div 
                        v-for="st in statusOptions" 
                        :key="st.val" 
                        class="status-option" 
                        :class="[st.class, { active: itemForm.estado === st.val }]"
                        @click="itemForm.estado = st.val"
                    >
                        {{ st.label }}
                    </div>
                </div>
            </div>

            <div class="form-group">
                <label>Observações / Avarias</label>
                <textarea 
                    class="form-textarea" rows="3" v-model="itemForm.descricao_avaria" 
                    placeholder="Descreva riscos, manchas ou detalhes importantes..."
                    :disabled="vistoria.concluida"
                ></textarea>
            </div>

            <div class="form-group">
                <label>Fotografias</label>
                <div v-if="!vistoria.concluida" class="photo-upload" @click="triggerFileInput">
                    <div class="upload-content" v-if="!selectedFile">
                        <i class="fas fa-camera"></i>
                        <span>Tirar Foto / Carregar</span>
                    </div>
                    <div class="upload-content selected" v-else>
                        <i class="fas fa-check-circle text-success"></i>
                        <span>{{ selectedFile.name }}</span>
                        <small>Pronto para enviar</small>
                    </div>
                    <input type="file" ref="fileInput" class="d-none" @change="handleFileUpload" accept="image/*" capture="environment">
                </div>
                
                <div v-if="editingItem && editingItem.fotos && editingItem.fotos.length" class="existing-photos mt-3">
                    <p class="small text-muted mb-2">Fotos Registradas:</p>
                    <div class="photos-row">
                        <div v-for="foto in editingItem.fotos" :key="foto.id" class="photo-thumb" @click="viewPhoto(foto.url)">
                            <img :src="foto.url">
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="modal-f">
          <button class="btn-cancel" @click="showItemModal = false">Fechar</button>
          <button v-if="!vistoria.concluida" class="btn-confirm" @click="saveItem">{{ editingItem ? 'Guardar' : 'Adicionar' }}</button>
        </div>
      </div>
    </div>

    <div v-if="showSignatureModal" class="modal-backdrop">
      <div class="modal-window medium">
        <div class="modal-h">
          <h4>Assinatura Digital</h4>
          <button @click="closeSignatureModal" class="close-modal"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-b">
            <div class="role-tabs">
                <button :class="{ active: signingRole === 'responsavel' }" @click="setSigningRole('responsavel')">Vistoriador</button>
                <button :class="{ active: signingRole === 'locatario' }" @click="setSigningRole('locatario')">Locatário</button>
                
                <button 
                    v-if="vistoria.exige_assinatura_proprietario"
                    :class="{ active: signingRole === 'proprietario' }" 
                    @click="setSigningRole('proprietario')"
                >Proprietário</button>
            </div>
            
            <div class="signature-box">
                <canvas 
                  ref="signatureCanvas" 
                  class="signature-canvas"
                  @mousedown="startDrawing" @mousemove="draw" @mouseup="stopDrawing" @mouseleave="stopDrawing"
                  @touchstart="startDrawingTouch" @touchmove="drawTouch" @touchend="stopDrawing"
                ></canvas>
                <div class="signature-overlay" v-if="!isDrawing && !hasSignatureContent">Assine aqui</div>
            </div>
            <button class="btn-clear-sig" @click="clearSignature">Limpar Assinatura</button>

            <div class="status-signatures mt-3">
                <span :class="vistoria.assinatura_responsavel ? 'signed' : 'missing'"><i class="fas fa-check"></i> Vistoriador</span>
                <span :class="vistoria.assinatura_locatario ? 'signed' : 'missing'"><i class="fas fa-check"></i> Locatário</span>
                <span v-if="vistoria.exige_assinatura_proprietario" :class="vistoria.assinatura_proprietario ? 'signed' : 'missing'"><i class="fas fa-check"></i> Proprietário</span>
            </div>
        </div>
        <div class="modal-f">
          <button class="btn-cancel" @click="closeSignatureModal">Fechar</button>
          <button class="btn-confirm" @click="saveSignature" :disabled="isSaving">
             <i v-if="isSaving" class="fas fa-spinner fa-spin"></i> Salvar Assinatura
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '@/services/api';
import { format } from 'date-fns';

export default defineComponent({
  name: 'VistoriaAmbientesView',
  setup() {
    const route = useRoute();
    const router = useRouter();
    const vistoriaId = route.params.id;
    const fileInput = ref<HTMLInputElement | null>(null);

    const loading = ref(true);
    const downloading = ref(false); 
    const vistoria = ref<any>({});
    const ambientes = ref<any[]>([]);

    const isConcluindo = ref(false);
    const isSavingProgress = ref(false);

    // Modais
    const showAmbienteModal = ref(false);
    const showItemModal = ref(false);
    const showSignatureModal = ref(false);

    const ambienteForm = ref({ nome: '' });
    const editingItem = ref<any>(null);
    const currentAmbienteId = ref<number | null>(null);
    const itemForm = ref({ item: '', estado: 'BOM', descricao_avaria: '' });
    const selectedFile = ref<File | null>(null);

    // Assinatura
    const signatureCanvas = ref<HTMLCanvasElement | null>(null);
    const ctx = ref<CanvasRenderingContext2D | null>(null);
    const isDrawing = ref(false);
    const hasSignatureContent = ref(false); 
    const isSaving = ref(false);
    const signingRole = ref<'responsavel' | 'locatario' | 'proprietario'>('locatario');

    const statusOptions = [
      { val: 'NOVO', label: 'Novo', class: 'opt-novo' },
      { val: 'BOM', label: 'Bom', class: 'opt-bom' },
      { val: 'REGULAR', label: 'Regular', class: 'opt-regular' },
      { val: 'RUIM', label: 'Ruim', class: 'opt-ruim' },
      { val: 'INOPERANTE', label: 'Inoperante', class: 'opt-inop' },
    ];

    const totalAmbientes = computed(() => ambientes.value.length);
    const totalItens = computed(() => {
        return ambientes.value.reduce((acc, amb) => acc + (amb.itens ? amb.itens.length : 0), 0);
    });

    const loadData = async () => {
      loading.value = true;
      try {
        const response = await api.get(`/v1/vistorias/vistorias/${vistoriaId}/`);
        vistoria.value = response.data;
        ambientes.value = response.data.ambientes || [];
      } catch (error) {
        console.error(error);
      } finally {
        loading.value = false;
      }
    };

    const saveGeneralObs = async () => {
        if (vistoria.value.concluida) return;
        try { await api.patch(`/v1/vistorias/vistorias/${vistoriaId}/`, { observacoes: vistoria.value.observacoes }); } catch (e) {}
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
        if (!confirm("Ao concluir a vistoria, não será mais possível editar os itens ou ambientes. Deseja continuar?")) return;
        
        isConcluindo.value = true;
        try {
            await api.patch(`/v1/vistorias/vistorias/${vistoriaId}/`, {
                concluida: true,
                observacoes: vistoria.value.observacoes
            });
            alert("Vistoria finalizada com sucesso!");
            router.push('/vistorias');
        } catch (e) { 
            console.error(e);
            alert("Erro ao concluir."); 
        } finally { 
            isConcluindo.value = false; 
        }
    };

    // --- Ambientes ---
    const openAmbienteModal = () => { if(vistoria.value.concluida) return; ambienteForm.value.nome = ''; showAmbienteModal.value = true; };
    const saveAmbiente = async () => {
      if (!ambienteForm.value.nome) return;
      try {
        await api.post('/v1/vistorias/ambientes/', { vistoria: vistoriaId, nome: ambienteForm.value.nome });
        showAmbienteModal.value = false; loadData();
      } catch (e) { alert("Erro ao criar ambiente"); }
    };
    const deleteAmbiente = async (id: number) => {
      if(vistoria.value.concluida) return;
      if(!confirm("Apagar este ambiente e itens?")) return;
      try { await api.delete(`/v1/vistorias/ambientes/${id}/`); loadData(); } catch (e) { alert("Erro ao apagar"); }
    };

    // --- Itens ---
    const openItemModal = (ambId: number, item: any) => {
      // Se concluída e não tem item (adicionar), aborta. Se tem item, abre para visualizar.
      if(vistoria.value.concluida && !item) return;
      
      currentAmbienteId.value = ambId;
      editingItem.value = item;
      selectedFile.value = null;
      if (item) itemForm.value = { item: item.item, estado: item.estado, descricao_avaria: item.descricao_avaria };
      else itemForm.value = { item: '', estado: 'BOM', descricao_avaria: '' };
      showItemModal.value = true;
    };

    const saveItem = async () => {
      if(vistoria.value.concluida) return;
      if (!itemForm.value.item) return alert("Informe o nome do item");
      try {
        let itemId;
        if (editingItem.value) {
          itemId = editingItem.value.id;
          await api.patch(`/v1/vistorias/itens/${itemId}/`, itemForm.value);
        } else {
          const res = await api.post('/v1/vistorias/itens/', { ambiente: currentAmbienteId.value, ...itemForm.value });
          itemId = res.data.id;
        }
        if (selectedFile.value && itemId) {
          const formData = new FormData();
          formData.append('item', itemId);
          formData.append('foto', selectedFile.value);
          await api.post('/v1/vistorias/fotos/upload-lote/', formData, { headers: { 'Content-Type': null } });
        }
        showItemModal.value = false; loadData();
      } catch (e) { alert("Erro ao salvar item"); }
    };

    const triggerFileInput = () => fileInput.value?.click();
    const handleFileUpload = (e: Event) => { const t = e.target as HTMLInputElement; if (t.files) selectedFile.value = t.files[0]; };

    // --- Assinatura ---
    const openSignatureModal = async () => {
        showSignatureModal.value = true;
        await nextTick();
        if (signatureCanvas.value) {
            signatureCanvas.value.width = signatureCanvas.value.offsetWidth;
            signatureCanvas.value.height = 250;
            ctx.value = signatureCanvas.value.getContext('2d');
            if (ctx.value) { ctx.value.lineWidth = 2; ctx.value.lineCap = "round"; }
        }
    };
    const closeSignatureModal = () => showSignatureModal.value = false;
    const setSigningRole = (r: any) => { signingRole.value = r; clearSignature(); };
    const clearSignature = () => {
        if(ctx.value && signatureCanvas.value) ctx.value.clearRect(0,0,signatureCanvas.value.width, signatureCanvas.value.height);
        hasSignatureContent.value = false;
    };
    
    const getPos = (e: any) => {
        const rect = signatureCanvas.value?.getBoundingClientRect();
        return { x: (e.touches ? e.touches[0].clientX : e.clientX) - (rect?.left||0), y: (e.touches ? e.touches[0].clientY : e.clientY) - (rect?.top||0) };
    };
    const startDrawing = (e: any) => { isDrawing.value=true; hasSignatureContent.value=true; const p=getPos(e); ctx.value?.beginPath(); ctx.value?.moveTo(p.x, p.y); };
    const draw = (e: any) => { if(!isDrawing.value) return; const p=getPos(e); ctx.value?.lineTo(p.x, p.y); ctx.value?.stroke(); };
    const stopDrawing = () => isDrawing.value=false;
    const startDrawingTouch = (e: TouchEvent) => { e.preventDefault(); startDrawing(e); };
    const drawTouch = (e: TouchEvent) => { e.preventDefault(); draw(e); };

    const saveSignature = () => {
        if(!hasSignatureContent.value) return alert("Por favor, assine antes de salvar.");
        isSaving.value = true;
        signatureCanvas.value?.toBlob(async (blob) => {
            if(blob) {
                const fd = new FormData();
                const field = signingRole.value === 'responsavel' ? 'assinatura_responsavel' : (signingRole.value === 'proprietario' ? 'assinatura_proprietario' : 'assinatura_locatario');
                fd.append(field, blob, 'sig.png');
                try {
                    await api.patch(`/v1/vistorias/vistorias/${vistoriaId}/`, fd, {
                        headers: { 'Content-Type': undefined }
                    });
                    alert("Assinatura guardada!");
                    clearSignature(); loadData();
                } catch(e) { alert("Erro ao salvar assinatura."); } 
                finally { isSaving.value = false; }
            }
        });
    };

    const downloadLaudo = async () => {
        downloading.value = true;
        try {
            const res = await api.get(`/v1/vistorias/vistorias/${vistoriaId}/gerar-laudo/`, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a'); link.href = url; link.download = `Laudo_${vistoriaId}.pdf`;
            document.body.appendChild(link); link.click(); link.remove();
        } catch (e) { alert("Erro no download."); } finally { downloading.value = false; }
    };

    const goBack = () => router.push('/vistorias');
    const formatDate = (d: string) => d ? format(new Date(d), 'dd/MM/yyyy') : '--';
    const viewPhoto = (url: string) => window.open(url, '_blank');
    const getStatusClass = (s: string) => { const m:any = {'NOVO':'text-success','BOM':'text-primary','REGULAR':'text-warning','RUIM':'text-danger','INOPERANTE':'text-dark'}; return m[s]; };
    const getTipoClass = (t: string) => t==='ENTRADA'?'badge-entrada':(t==='SAIDA'?'badge-saida':'badge-periodica');

    onMounted(loadData);

    return {
        vistoria, ambientes, loading, downloading, totalItens, isConcluindo, isSavingProgress,
        saveGeneralObs, saveProgress, concluirVistoria,
        showAmbienteModal, showItemModal, showSignatureModal, ambienteForm, itemForm, editingItem, selectedFile,
        openAmbienteModal, saveAmbiente, deleteAmbiente, openItemModal, saveItem, triggerFileInput, handleFileUpload,
        signatureCanvas, startDrawing, draw, stopDrawing, startDrawingTouch, drawTouch, clearSignature, saveSignature, isSaving, signingRole, setSigningRole, hasSignatureContent, openSignatureModal, closeSignatureModal,
        goBack, downloadLaudo, formatDate, viewPhoto, getStatusClass, getTipoClass, statusOptions
    };
  }
});
</script>

<style scoped>
/* ===================================
   LAYOUT & HEADER
   =================================== */
.page-container {
  min-height: 100vh;
  background-color: #f8fafc;
  font-family: 'Segoe UI', Roboto, sans-serif;
  padding-bottom: 60px;
}

.page-header {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-content { display: flex; align-items: center; gap: 1rem; }
.btn-back {
  width: 40px; height: 40px; border-radius: 50%; border: 1px solid #e2e8f0;
  background: white; color: #64748b; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.btn-back:hover { background: #f1f5f9; color: #0f172a; }

.header-text h1 { font-size: 1.25rem; font-weight: 700; color: #0f172a; margin: 0; }
.header-text .subtitle { font-size: 0.85rem; color: #64748b; margin: 2px 0 0 0; }

.badge-tipo { font-size: 0.7rem; padding: 2px 8px; border-radius: 4px; font-weight: 700; text-transform: uppercase; }
.badge-entrada { background: #dcfce7; color: #166534; }
.badge-saida { background: #fee2e2; color: #991b1b; }
.badge-periodica { background: #e0f2fe; color: #075985; }

.badge-status.locked { 
    background: #e2e8f0; color: #475569; font-size: 0.7rem; padding: 2px 8px; border-radius: 4px; font-weight: 700; text-transform: uppercase; margin-left: 8px;
}

.header-actions { display: flex; gap: 0.75rem; }
.btn-action-outline, .btn-action-primary {
    padding: 0.5rem 1rem; border-radius: 6px; font-weight: 600; font-size: 0.9rem; cursor: pointer;
    display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.btn-action-outline { border: 1px solid #cbd5e1; background: white; color: #475569; }
.btn-action-outline:hover { background: #f8fafc; border-color: #94a3b8; }
.btn-action-primary { border: none; background: #0f172a; color: white; }
.btn-action-primary:hover { background: #334155; }
.btn-action-primary:disabled { opacity: 0.7; cursor: not-allowed; }

/* Locked Alert */
.locked-alert {
    background: #fffbeb; border: 1px solid #fcd34d; color: #92400e;
    padding: 1rem; margin: 1rem 1.5rem; border-radius: 8px; font-size: 0.9rem;
    display: flex; align-items: center; max-width: 1000px; margin: 1rem auto;
}

/* ===================================
   MAIN CONTENT
   =================================== */
.main-content {
    max-width: 1000px; margin: 1rem auto; padding: 0 1.5rem;
}

/* Status Dashboard */
.status-dashboard {
    background: white; border-radius: 12px; padding: 1.5rem; border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 2rem;
    display: flex; flex-wrap: wrap; gap: 1.5rem; align-items: center;
}
.status-item { flex: 1; min-width: 200px; display: flex; gap: 1rem; align-items: center; }
.main-location .icon { font-size: 1.5rem; color: #3b82f6; background: #eff6ff; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; border-radius: 10px; }
.status-item .text label { display: block; font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: 600; }
.status-item .text strong { display: block; font-size: 0.95rem; color: #0f172a; }

.progress-area { flex: 1.5; display: block; }
.progress-area label { font-size: 0.8rem; font-weight: 600; color: #475569; }
.progress-val { float: right; font-size: 0.8rem; font-weight: 700; color: #3b82f6; }
.progress-bar-bg { width: 100%; height: 8px; background: #f1f5f9; border-radius: 4px; overflow: hidden; margin-top: 5px; }
.progress-bar-fill { height: 100%; background: #3b82f6; }

.status-actions { display: flex; gap: 0.5rem; }
.btn-dashboard {
    background: #f8fafc; border: 1px solid #e2e8f0; color: #475569; padding: 0.5rem 1rem;
    border-radius: 6px; font-size: 0.85rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 0.5rem;
}
.btn-dashboard:hover { background: #f1f5f9; color: #0f172a; border-color: #cbd5e1; }

/* Grid Layout (Info) */
.grid-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.info-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; }
.card-label { font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; display: flex; align-items: center; gap: 0.5rem; }
.info-value { font-weight: 600; color: #334155; }
.btn-icon-small { border: none; background: none; color: #94a3b8; cursor: pointer; }
.btn-icon-small:hover { color: #3b82f6; }
.edit-group { display: flex; gap: 0.5rem; }
.form-input-sm { flex: 1; padding: 4px 8px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 0.9rem; }
.btn-save-sm { background: #10b981; color: white; border: none; border-radius: 4px; padding: 0 8px; cursor: pointer; }
.form-textarea-transparent { width: 100%; background: transparent; border: none; resize: none; font-size: 0.9rem; color: #334155; padding: 0; outline: none; margin-top: 5px; font-weight: 500; }
.form-textarea-transparent:focus { border-bottom: 1px dashed #cbd5e1; }

/* Ambiente List */
.ambientes-list { display: flex; flex-direction: column; gap: 1.5rem; }
.ambiente-wrapper { background: white; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.02); overflow: hidden; }

.ambiente-header {
    background: #fcfcfc; padding: 1rem 1.5rem; border-bottom: 1px solid #f1f5f9;
    display: flex; justify-content: space-between; align-items: center;
}
.ambiente-title { font-size: 1.1rem; font-weight: 700; color: #1e293b; display: flex; align-items: center; gap: 0.75rem; }
.counter-badge { background: #e2e8f0; color: #475569; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; }
.btn-tool { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border-radius: 6px; border: none; background: transparent; cursor: pointer; color: #94a3b8; transition: all 0.2s; }
.btn-tool:hover { background: #f1f5f9; color: #475569; }
.btn-tool.danger:hover { background: #fee2e2; color: #ef4444; }

.ambiente-content { padding: 0; }
.item-card {
    display: flex; align-items: stretch; border-bottom: 1px solid #f1f5f9; cursor: pointer;
    transition: background 0.1s; position: relative;
}
.item-card:hover { background: #f8fafc; }
.item-status-stripe { width: 4px; }
.item-status-stripe.text-success { background: #22c55e; }
.item-status-stripe.text-primary { background: #3b82f6; }
.item-status-stripe.text-warning { background: #f59e0b; }
.item-status-stripe.text-danger { background: #ef4444; }
.item-status-stripe.text-dark { background: #475569; }

.item-main { flex: 1; padding: 1rem 1.5rem; }
.item-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem; }
.item-name { font-weight: 600; color: #334155; font-size: 0.95rem; }
.status-tag { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; padding: 2px 6px; border-radius: 4px; background: #f1f5f9; color: #64748b; }
.item-desc { font-size: 0.85rem; color: #64748b; margin: 0; line-height: 1.4; }
.item-photos { font-size: 0.75rem; color: #3b82f6; margin-top: 0.5rem; font-weight: 600; }
.item-arrow { display: flex; align-items: center; padding-right: 1.5rem; color: #cbd5e1; }

.btn-add-item {
    width: 100%; padding: 1rem; border: none; background: transparent; border-top: 1px solid #f1f5f9;
    color: #64748b; font-weight: 600; font-size: 0.9rem; cursor: pointer; transition: all 0.2s;
}
.btn-add-item:hover { background: #f8fafc; color: #3b82f6; }

.btn-new-ambiente {
    width: 100%; padding: 1rem; border: 2px dashed #cbd5e1; border-radius: 12px;
    background: transparent; color: #64748b; font-weight: 600; cursor: pointer; margin-top: 1rem; transition: all 0.2s;
}
.btn-new-ambiente:hover { border-color: #94a3b8; color: #475569; background: #f1f5f9; }

/* Empty States */
.empty-state { text-align: center; padding: 3rem; background: white; border-radius: 12px; border: 1px solid #e2e8f0; }
.empty-icon { font-size: 2.5rem; color: #cbd5e1; margin-bottom: 1rem; }
.btn-add-large { background: #0f172a; color: white; padding: 0.75rem 1.5rem; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; margin-top: 1rem; }

.empty-items { text-align: center; padding: 2rem; color: #94a3b8; font-size: 0.9rem; }

/* ===================================
   MODAIS
   =================================== */
.modal-backdrop {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5);
    z-index: 2000; display: flex; justify-content: center; align-items: center;
    backdrop-filter: blur(2px);
}
.modal-window {
    background: white; border-radius: 16px; width: 90%; display: flex; flex-direction: column;
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); max-height: 90vh;
}
.modal-window.small { max-width: 400px; }
.modal-window.medium { max-width: 600px; }

.modal-h { padding: 1.25rem 1.5rem; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
.modal-h h4 { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }
.close-modal { background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 1.1rem; }

.modal-b { padding: 1.5rem; overflow-y: auto; flex: 1; }
.form-group { margin-bottom: 1.25rem; }
.form-group label { display: block; font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 0.5rem; }
.form-input, .form-textarea { width: 100%; padding: 0.75rem; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.95rem; }
.form-input:focus, .form-textarea:focus { border-color: #3b82f6; outline: none; ring: 2px solid rgba(59,130,246,0.1); }

.status-selector { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; }
.status-option {
    border: 1px solid #e2e8f0; border-radius: 6px; padding: 0.5rem; text-align: center;
    font-size: 0.85rem; cursor: pointer; font-weight: 600; color: #64748b;
}
.status-option:hover { background: #f8fafc; }
.status-option.active { border-color: transparent; color: white; }
.opt-novo.active { background: #22c55e; }
.opt-bom.active { background: #3b82f6; }
.opt-regular.active { background: #f59e0b; }
.opt-ruim.active { background: #ef4444; }
.opt-inop.active { background: #1e293b; }

.photo-upload {
    border: 2px dashed #cbd5e1; border-radius: 8px; padding: 1.5rem; text-align: center;
    cursor: pointer; background: #f8fafc; transition: all 0.2s;
}
.photo-upload:hover { border-color: #3b82f6; background: #eff6ff; }
.upload-content { display: flex; flex-direction: column; align-items: center; gap: 0.5rem; color: #64748b; }
.photos-row { display: flex; gap: 0.5rem; overflow-x: auto; padding-bottom: 5px; }
.photo-thumb img { width: 60px; height: 60px; object-fit: cover; border-radius: 6px; border: 1px solid #e2e8f0; }

.role-tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; background: #f1f5f9; padding: 4px; border-radius: 8px; }
.role-tabs button { flex: 1; border: none; background: transparent; padding: 0.5rem; font-size: 0.85rem; font-weight: 600; color: #64748b; border-radius: 6px; cursor: pointer; }
.role-tabs button.active { background: white; color: #0f172a; shadow: 0 1px 2px rgba(0,0,0,0.05); }

.signature-box { border: 1px solid #cbd5e1; border-radius: 8px; height: 200px; position: relative; background: #fcfcfc; cursor: crosshair; }
.signature-canvas { width: 100%; height: 100%; }
.signature-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #cbd5e1; font-weight: 700; font-size: 1.5rem; pointer-events: none; opacity: 0.5; }
.btn-clear-sig { width: 100%; padding: 0.5rem; background: #fee2e2; color: #ef4444; border: none; font-weight: 600; font-size: 0.8rem; border-radius: 6px; margin-top: 0.5rem; cursor: pointer; }

.status-signatures { display: flex; justify-content: space-around; font-size: 0.75rem; border-top: 1px solid #f1f5f9; padding-top: 1rem; }
.status-signatures span.signed { color: #22c55e; font-weight: 600; }
.status-signatures span.missing { color: #cbd5e1; }

.modal-f { padding: 1.25rem 1.5rem; border-top: 1px solid #f1f5f9; display: flex; justify-content: flex-end; gap: 0.75rem; background: #fcfcfc; border-bottom-left-radius: 16px; border-bottom-right-radius: 16px; }
.btn-cancel { background: white; border: 1px solid #cbd5e1; color: #64748b; padding: 0.6rem 1.2rem; border-radius: 6px; font-weight: 600; cursor: pointer; }
.btn-confirm { background: #0f172a; border: none; color: white; padding: 0.6rem 1.5rem; border-radius: 6px; font-weight: 600; cursor: pointer; }

@media (max-width: 768px) {
    .page-header { flex-direction: column; align-items: flex-start; gap: 1rem; }
    .header-actions { width: 100%; display: flex; justify-content: stretch; }
    .header-actions button { flex: 1; }
    .grid-layout { grid-template-columns: 1fr; }
    .status-dashboard { flex-direction: column; align-items: stretch; }
}
</style>