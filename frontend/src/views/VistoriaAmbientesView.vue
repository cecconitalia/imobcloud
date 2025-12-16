<template>
  <div class="page-container">
    
    <header class="premium-header">
      <div class="header-wrapper">
        
        <div class="top-bar">
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb mb-0">
              <li class="breadcrumb-item"><span @click="goBack">Vistorias</span></li>
              <li class="breadcrumb-item active" aria-current="page">Execução #{{ vistoria.id }}</li>
            </ol>
          </nav>
        </div>

        <div class="main-bar">
          <div class="title-section">
            <div class="d-flex align-items-center gap-3">
              <h1 class="page-title">Checklist de Vistoria</h1>
              <span class="status-pill" :class="getTipoClass(vistoria.tipo)">
                {{ vistoria.tipo }}
              </span>
            </div>
            
            <div class="meta-info" v-if="vistoria.imovel_display">
              <div class="meta-item">
                <i class="fas fa-map-marker-alt text-primary"></i>
                {{ vistoria.imovel_display }}
              </div>
              <div class="meta-separator"></div>
              <div class="meta-item">
                <i class="fas fa-file-contract text-muted"></i>
                Contrato #{{ vistoria.contrato }}
              </div>
              <div class="meta-separator"></div>
              <div class="meta-item">
                <i class="far fa-calendar text-muted"></i>
                {{ formatDate(vistoria.data_vistoria) }}
              </div>
            </div>
          </div>

          <div class="actions-section">
            
            <div class="progress-widget" v-if="totalAmbientes > 0">
              <div class="progress-labels">
                <span class="label">Progresso</span>
                <span class="value">{{ totalItens }} itens</span>
              </div>
              <div class="progress-track">
                <div class="progress-fill" style="width: 100%"></div> 
              </div>
            </div>

            <button 
                class="btn-secondary-premium me-2" 
                @click="saveProgress" 
                :disabled="isSavingProgress || vistoria.concluida"
            >
                <span v-if="isSavingProgress" class="spinner-border spinner-border-sm"></span>
                <span v-else><i class="fas fa-save me-2"></i> Salvar Progresso</span>
            </button>
            <button class="btn-secondary-premium me-2" @click="downloadLaudo" :disabled="downloading">
              <span v-if="downloading" class="spinner-border spinner-border-sm"></span>
              <span v-else><i class="fas fa-file-pdf me-2"></i> Baixar Laudo</span>
            </button>

            <button 
                v-if="!vistoria.concluida"
                class="btn-finish-premium btn-concluir me-2" 
                :disabled="isConcluindo"
                @click="concluirVistoria"
            >
                <i v-if="isConcluindo" class="fas fa-spinner fa-spin me-2"></i>
                <i v-else class="fas fa-check-circle me-2"></i>
                {{ isConcluindo ? 'Finalizando...' : 'Concluir Vistoria' }}
            </button>
            
            <button class="btn-finish-premium" @click="openSignatureModal">
              <i class="fas fa-file-signature"></i> 
              <span>Assinaturas</span>
            </button>

          </div>
        </div>
      </div>
    </header>

    <main class="main-content">
      
      <div v-if="loading" class="loading-state">
        <div class="spinner-border text-primary" role="status"></div>
        <p>Carregando checklist...</p>
      </div>

      <div v-else>
        
        <section class="vistoriador-info-card">
            <div v-if="!isEditingVistoriador" class="info-display">
                <i class="fas fa-user-check me-2 text-primary"></i>
                Vistoriador Responsável: 
                <strong>{{ vistoria.realizado_por_nome || 'NÃO DEFINIDO' }}</strong>
                <button v-if="!vistoria.concluida" class="btn-edit-inline" @click="isEditingVistoriador = true">
                    <i class="fas fa-pencil-alt"></i>
                </button>
                <span v-else class="text-success ms-3 fw-bold"><i class="fas fa-lock"></i> Vistoria Concluída</span>
            </div>
            
            <div v-else class="info-edit-mode">
                <input 
                    type="text" 
                    v-model="vistoriadorNome" 
                    placeholder="Nome completo do Vistoriador Responsável"
                >
                <button 
                    class="btn-save-inline" 
                    :disabled="isSavingVistoriador"
                    @click="saveVistoriador"
                >
                    <i v-if="isSavingVistoriador" class="fas fa-spinner fa-spin me-1"></i>
                    Salvar
                </button>
                <button class="btn-cancel-inline" @click="isEditingVistoriador = false">
                    Cancelar
                </button>
            </div>
        </section>
        <section class="card mb-4">
          <div class="card-header">
            <i class="fas fa-info-circle me-2"></i> Observações Gerais (Salvas automaticamente ao perder o foco)
          </div>
          <div class="card-body">
            <textarea 
              v-model="vistoria.observacoes" 
              class="input-styled" 
              rows="3" 
              placeholder="Descreva observações gerais, chaves entregues, etc."
              :disabled="vistoria.concluida"
              @blur="saveGeneralObs"
            ></textarea>
          </div>
        </section>
        
        <div v-if="ambientes.length === 0" class="empty-state-modern">
          <div class="empty-illustration">
            <i class="fas fa-clipboard-list"></i>
          </div>
          <h3>Checklist Vazio</h3>
          <p>Esta vistoria ainda não possui ambientes. Adicione o primeiro cômodo para começar.</p>
          <button class="btn-primary-hero" @click="openAmbienteModal">
            <i class="fas fa-plus"></i> Adicionar Ambiente
          </button>
        </div>

        <div v-else class="checklist-wrapper">
          
          <div v-for="ambiente in ambientes" :key="ambiente.id" class="ambiente-card">
            
            <div class="ambiente-header">
              <div class="d-flex align-items-center gap-3">
                <div class="icon-box">
                  <i class="fas fa-door-open"></i>
                </div>
                <div>
                  <h3 class="ambiente-name">{{ ambiente.nome }}</h3>
                  <span class="ambiente-meta">{{ ambiente.itens ? ambiente.itens.length : 0 }} itens avaliados</span>
                </div>
              </div>
              <button class="btn-icon-subtle danger" @click="deleteAmbiente(ambiente.id)" title="Excluir Ambiente">
                <i class="far fa-trash-alt"></i>
              </button>
            </div>

            <div class="ambiente-body">
              
              <div v-if="ambiente.itens && ambiente.itens.length > 0" class="items-grid">
                <div v-for="item in ambiente.itens" :key="item.id" class="item-row">
                  
                  <div class="item-col-main">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                      <span class="item-title">{{ item.item }}</span>
                      <span class="status-badge-sm" :class="getStatusClass(item.estado)">
                        {{ item.estado }}
                      </span>
                    </div>
                    
                    <p class="item-obs" v-if="item.descricao_avaria">
                      {{ item.descricao_avaria }}
                    </p>
                    <p class="item-obs text-muted" v-else>Nenhuma observação registrada.</p>
                    
                    <div class="mini-gallery" v-if="item.fotos && item.fotos.length > 0">
                      <div v-for="foto in item.fotos" :key="foto.id" class="mini-thumb" @click="viewPhoto(foto.url)">
                        <img :src="foto.url" alt="Foto">
                      </div>
                    </div>
                  </div>

                  <div class="item-col-action">
                    <button class="btn-edit-round" @click="openItemModal(ambiente.id, item)">
                      <i class="fas fa-pencil-alt"></i>
                    </button>
                  </div>
                </div>
              </div>

              <div v-else class="ambiente-empty">
                <p>Nenhum item neste ambiente.</p>
              </div>

              <div class="ambiente-footer">
                <button class="btn-add-item-dashed" @click="openItemModal(ambiente.id, null)">
                  <i class="fas fa-plus"></i> Adicionar Item ao {{ ambiente.nome }}
                </button>
              </div>

            </div>
          </div>

          <div class="add-ambiente-wrapper">
            <button class="btn-add-ambiente-lg" @click="openAmbienteModal">
              <i class="fas fa-plus-circle fa-lg"></i>
              <span>Adicionar Outro Ambiente</span>
            </button>
          </div>

        </div>
      </div>
    </main>
    
    <div v-if="showAmbienteModal" class="modal-overlay">
      <div class="modal-card">
        <div class="modal-top">
          <h4>Novo Ambiente</h4>
          <button @click="showAmbienteModal = false" class="btn-close-icon"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-content-box">
          <label class="input-label">Nome do Cômodo</label>
          <input type="text" class="input-styled" v-model="ambienteForm.nome" placeholder="Ex: Sala de Estar, Cozinha..." autoFocus>
        </div>
        <div class="modal-actions">
          <button class="btn-text" @click="showAmbienteModal = false">Cancelar</button>
          <button class="btn-solid" @click="saveAmbiente">Salvar</button>
        </div>
      </div>
    </div>

    <div v-if="showItemModal" class="modal-overlay">
      <div class="modal-card lg">
        <div class="modal-top">
          <h4>{{ editingItem ? 'Editar Item' : 'Novo Item' }}</h4>
          <button @click="showItemModal = false" class="btn-close-icon"><i class="fas fa-times"></i></button>
        </div>
        
        <div class="modal-content-box scrollable">
          <div class="row g-3">
            <div class="col-12">
              <label class="input-label">Item Avaliado</label>
              <input type="text" class="input-styled" v-model="itemForm.item" placeholder="Ex: Janela, Tomada, Rodapé...">
            </div>

            <div class="col-12">
              <label class="input-label">Estado</label>
              <div class="status-grid">
                <label v-for="st in statusOptions" :key="st.val" class="status-card" :class="{ active: itemForm.estado === st.val }">
                  <input type="radio" v-model="itemForm.estado" :value="st.val" class="d-none">
                  <div class="status-dot" :class="st.class"></div>
                  <span>{{ st.label }}</span>
                </label>
              </div>
            </div>

            <div class="col-12">
              <label class="input-label">Observações</label>
              <textarea class="input-styled" rows="3" v-model="itemForm.descricao_avaria" placeholder="Detalhes..."></textarea>
            </div>

            <div class="col-12">
              <label class="input-label">Fotos</label>
              <div class="photo-upload-area" @click="triggerFileInput">
                <i class="fas fa-camera fa-2x"></i>
                <span v-if="!selectedFile">Toque para adicionar foto</span>
                <span v-else class="text-success">{{ selectedFile.name }}</span>
                <input type="file" ref="fileInput" class="d-none" @change="handleFileUpload" accept="image/*" capture="environment">
              </div>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-text" @click="showItemModal = false">Cancelar</button>
          <button class="btn-solid" @click="saveItem">
             {{ editingItem ? 'Atualizar' : 'Adicionar' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showSignatureModal" class="modal-overlay">
      <div class="modal-card lg">
        <div class="modal-top">
          <h4>Coleta de Assinaturas</h4>
          <button @click="closeSignatureModal" class="btn-close-icon"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-content-box text-center">
          
          <div class="role-selector mb-3">
            <button class="role-btn" :class="{active: signingRole === 'responsavel'}" @click="setSigningRole('responsavel')">
              <i class="fas fa-user-tie me-2"></i> Vistoriador
            </button>
            <button class="role-btn" :class="{active: signingRole === 'locatario'}" @click="setSigningRole('locatario')">
              <i class="fas fa-user me-2"></i> Locatário
            </button>
          </div>

          <p class="text-muted mb-2 small">Assine no quadro abaixo:</p>
          <div class="signature-wrapper">
            <canvas 
              ref="signatureCanvas" 
              class="signature-pad"
              @mousedown="startDrawing" 
              @mousemove="draw" 
              @mouseup="stopDrawing" 
              @mouseleave="stopDrawing"
              @touchstart="startDrawingTouch"
              @touchmove="drawTouch"
              @touchend="stopDrawing"
            ></canvas>
          </div>
          <button class="btn-text text-danger mt-2" @click="clearSignature">
            <i class="fas fa-eraser me-1"></i> Limpar Painel
          </button>

          <div class="mt-3 d-flex justify-content-center gap-4">
            <div :class="vistoria.assinatura_responsavel ? 'text-success' : 'text-muted'">
              <i class="fas" :class="vistoria.assinatura_responsavel ? 'fa-check-circle' : 'fa-circle'"></i> Vistoriador
            </div>
            <div :class="vistoria.assinatura_locatario ? 'text-success' : 'text-muted'">
              <i class="fas" :class="vistoria.assinatura_locatario ? 'fa-check-circle' : 'fa-circle'"></i> Locatário
            </div>
          </div>

        </div>
        <div class="modal-actions">
          <button class="btn-text" @click="closeSignatureModal">Fechar</button>
          <button class="btn-solid" @click="saveSignature" :disabled="isSaving">
            <span v-if="isSaving" class="spinner-border spinner-border-sm me-2"></span>
            Salvar Assinatura
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

    // NOVO: Estado para Vistoriador e Conclusão
    const isEditingVistoriador = ref(false);
    const vistoriadorNome = ref('');
    const isSavingVistoriador = ref(false);
    const isConcluindo = ref(false);
    const isSavingProgress = ref(false); // Para o botão Salvar Progresso
    // FIM NOVO

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
    const isSaving = ref(false);
    const signingRole = ref<'responsavel' | 'locatario'>('locatario');

    const statusOptions = [
      { val: 'NOVO', label: 'Novo', class: 'bg-success' },
      { val: 'BOM', label: 'Bom', class: 'bg-primary' },
      { val: 'REGULAR', label: 'Regular', class: 'bg-warning' },
      { val: 'RUIM', label: 'Ruim', class: 'bg-danger' },
      { val: 'INOPERANTE', label: 'Inoperante', class: 'bg-dark' },
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
        // Inicializa o campo de edição com o valor atual
        vistoriadorNome.value = response.data.realizado_por_nome || ''; 
      } catch (error) {
        console.error("Erro ao carregar vistoria", error);
      } finally {
        loading.value = false;
      }
    };

    // NOVO: Salva o nome do vistoriador (usado no botão editar/salvar)
    const saveVistoriador = async () => {
        if (!vistoriadorNome.value || vistoriadorNome.value.trim() === '') {
            alert("O nome do vistoriador não pode ser vazio.");
            return;
        }
        isSavingVistoriador.value = true;
        try {
            await api.patch(`/v1/vistorias/vistorias/${vistoriaId}/`, {
                realizado_por_nome: vistoriadorNome.value
            });
            isEditingVistoriador.value = false;
            await loadData();
        } catch (error) {
            console.error(error);
            alert("Erro ao salvar nome do vistoriador.");
        } finally {
            isSavingVistoriador.value = false;
        }
    };
    
    // NOVO: Salva observações gerais (chamado no @blur do textarea)
    const saveGeneralObs = async () => {
        if (vistoria.value.concluida) return;

        // O v-model já atualizou o vistoria.value.observacoes
        try {
             await api.patch(`/v1/vistorias/vistorias/${vistoriaId}/`, {
                observacoes: vistoria.value.observacoes
            });
        } catch (error) {
            console.error(error);
            alert("Erro ao salvar observações gerais.");
        }
    };

    // NOVO: Salva o progresso e notifica
    const saveProgress = async () => {
        isSavingProgress.value = true;
        try {
             // Chama o saveGeneralObs para garantir que as últimas observações estejam salvas
             await saveGeneralObs();
             // Notificação simples, pois o saveGeneralObs já fez o PATCH
             alert("Progresso salvo com sucesso!");
        } catch (error) {
            // Se o saveGeneralObs falhou, o erro já foi alertado lá
        } finally {
            isSavingProgress.value = false;
        }
    };
    
    // Conclui a vistoria
    const concluirVistoria = async () => {
        if (!confirm("Tem certeza que deseja CONCLUIR esta vistoria? Ela será marcada como finalizada e pronta para gerar o laudo.")) {
            return;
        }
        
        isConcluindo.value = true;
        try {
            // Garante que o nome do vistoriador e observações gerais estão atualizados
            await api.patch(`/v1/vistorias/vistorias/${vistoriaId}/`, {
                concluida: true,
                observacoes: vistoria.value.observacoes,
                realizado_por_nome: vistoriadorNome.value
            });
            alert("Vistoria concluída e salva!");
            goBack(); // Volta para a lista
        } catch (error) {
            console.error(error);
            alert("Erro ao concluir a vistoria. Tente novamente.");
        } finally {
            isConcluindo.value = false;
        }
    };


    // --- Ambientes e Itens (Mantidas) ---
    const openAmbienteModal = () => {
      // Verifica se a vistoria está concluída para bloquear
      if (vistoria.value.concluida) return alert("Vistoria concluída. Edição bloqueada.");
      ambienteForm.value.nome = '';
      showAmbienteModal.value = true;
    };

    const saveAmbiente = async () => {
      if (!ambienteForm.value.nome) return alert("Informe o nome do ambiente");
      try {
        await api.post('/v1/vistorias/ambientes/', {
          vistoria: vistoriaId,
          nome: ambienteForm.value.nome,
        });
        showAmbienteModal.value = false;
        loadData();
      } catch (error) { alert("Erro ao salvar ambiente"); }
    };

    const deleteAmbiente = async (id: number) => {
      // Verifica se a vistoria está concluída para bloquear
      if (vistoria.value.concluida) return alert("Vistoria concluída. Exclusão bloqueada.");
      if (!confirm("Excluir ambiente e itens?")) return;
      try {
        await api.delete(`/v1/vistorias/ambientes/${id}/`);
        loadData();
      } catch (error) { alert("Erro ao excluir"); }
    };

    const openItemModal = (ambienteId: number, item: any = null) => {
      // Verifica se a vistoria está concluída para bloquear
      if (vistoria.value.concluida) return alert("Vistoria concluída. Edição bloqueada.");
      
      currentAmbienteId.value = ambienteId;
      editingItem.value = item;
      selectedFile.value = null;
      if (item) {
        itemForm.value = { item: item.item, estado: item.estado, descricao_avaria: item.descricao_avaria };
      } else {
        itemForm.value = { item: '', estado: 'BOM', descricao_avaria: '' };
      }
      showItemModal.value = true;
    };

    const triggerFileInput = () => { 
        if (vistoria.value.concluida) return;
        fileInput.value?.click(); 
    };
    const handleFileUpload = (event: Event) => {
      const target = event.target as HTMLInputElement;
      if (target.files && target.files[0]) selectedFile.value = target.files[0];
    };

    const saveItem = async () => {
      if (!itemForm.value.item) return alert("Informe o nome do item");
      try {
        let itemId;
        if (editingItem.value) {
          itemId = editingItem.value.id;
          await api.patch(`/v1/vistorias/itens/${itemId}/`, itemForm.value);
        } else {
          const res = await api.post('/v1/vistorias/itens/', {
            ambiente: currentAmbienteId.value,
            ...itemForm.value
          });
          itemId = res.data.id;
        }

        if (selectedFile.value && itemId) {
          const formData = new FormData();
          formData.append('item', itemId);
          formData.append('foto', selectedFile.value);
          await api.post('/v1/vistorias/fotos/upload-lote/', formData, {
             headers: { 'Content-Type': null } 
          });
        }
        showItemModal.value = false;
        loadData();
      } catch (error) { console.error(error); alert("Erro ao salvar item."); }
    };

    // --- Lógica de Assinatura (Mantida) ---
    const openSignatureModal = async () => {
        showSignatureModal.value = true;
        await nextTick();
        if (signatureCanvas.value) {
            const parent = signatureCanvas.value.parentElement;
            if (parent) {
                signatureCanvas.value.width = parent.clientWidth;
                signatureCanvas.value.height = 200; // Altura fixa
            }
            ctx.value = signatureCanvas.value.getContext('2d');
            if (ctx.value) {
                ctx.value.strokeStyle = "#000000";
                ctx.value.lineWidth = 2;
                ctx.value.lineCap = "round";
            }
        }
    };

    const closeSignatureModal = () => { showSignatureModal.value = false; };

    const setSigningRole = (role: 'responsavel' | 'locatario') => {
        signingRole.value = role;
        clearSignature(); 
    };

    const clearSignature = () => {
        if (ctx.value && signatureCanvas.value) {
            ctx.value.clearRect(0, 0, signatureCanvas.value.width, signatureCanvas.value.height);
        }
    };

    const getPos = (e: any) => {
        const rect = signatureCanvas.value?.getBoundingClientRect();
        if (!rect) return { x: 0, y: 0 };
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        return {
            x: clientX - rect.left,
            y: clientY - rect.top
        };
    };

    const startDrawing = (e: MouseEvent) => { isDrawing.value = true; const pos = getPos(e); ctx.value?.beginPath(); ctx.value?.moveTo(pos.x, pos.y); };
    const draw = (e: MouseEvent) => { if (!isDrawing.value) return; const pos = getPos(e); ctx.value?.lineTo(pos.x, pos.y); ctx.value?.stroke(); };
    const stopDrawing = () => { isDrawing.value = false; };

    const startDrawingTouch = (e: TouchEvent) => { e.preventDefault(); isDrawing.value = true; const pos = getPos(e); ctx.value?.beginPath(); ctx.value?.moveTo(pos.x, pos.y); };
    const drawTouch = (e: TouchEvent) => { e.preventDefault(); if (!isDrawing.value) return; const pos = getPos(e); ctx.value?.lineTo(pos.x, pos.y); ctx.value?.stroke(); };

    const saveSignature = () => {
        if (!signatureCanvas.value) return;
        isSaving.value = true;
        
        signatureCanvas.value.toBlob(async (blob) => {
            if (blob) {
                const formData = new FormData();
                const fieldName = signingRole.value === 'responsavel' ? 'assinatura_responsavel' : 'assinatura_locatario';
                formData.append(fieldName, blob, 'assinatura.png');
                
                try {
                    await api.patch(`/v1/vistorias/vistorias/${vistoriaId}/`, formData, {
                        headers: { 'Content-Type': null }
                    });
                    
                    alert(`Assinatura de ${signingRole.value === 'responsavel' ? 'Vistoriador' : 'Locatário'} salva com sucesso!`);
                    clearSignature();
                    loadData();
                } catch (error) {
                    console.error("Erro ao salvar assinatura", error);
                    alert("Erro ao salvar assinatura.");
                } finally {
                    isSaving.value = false;
                }
            }
        });
    };

    // --- Outros ---
    const downloadLaudo = async () => {
        downloading.value = true;
        try {
            const response = await api.get(`/v1/vistorias/vistorias/${vistoriaId}/gerar-laudo/`, {
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Laudo_Vistoria_${vistoriaId}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error("Erro ao baixar PDF", error);
            alert("Não foi possível gerar o PDF. Tente novamente.");
        } finally {
            downloading.value = false;
        }
    };

    const goBack = () => router.push('/vistorias');
    const formatDate = (d: string) => d ? format(new Date(d), 'dd/MM/yyyy') : '--';
    const viewPhoto = (url: string) => window.open(url, '_blank');

    const getStatusClass = (status: string) => {
        const map: any = { 'NOVO': 's-novo', 'BOM': 's-bom', 'REGULAR': 's-regular', 'RUIM': 's-ruim', 'INOPERANTE': 's-inop' };
        return map[status];
    };

    const getTipoClass = (tipo: string) => {
        if(tipo === 'ENTRADA') return 'type-entrada';
        if(tipo === 'SAIDA') return 'type-saida';
        return 'type-periodica';
    };

    onMounted(loadData);

    return {
      vistoria, ambientes, loading, downloading, totalAmbientes, totalItens,
      isEditingVistoriador, vistoriadorNome, saveVistoriador, isSavingVistoriador, isConcluindo, concluirVistoria, saveGeneralObs, saveProgress, isSavingProgress,
      showAmbienteModal, ambienteForm, openAmbienteModal, saveAmbiente, deleteAmbiente,
      showItemModal, itemForm, editingItem, openItemModal, saveItem, 
      selectedFile, fileInput, triggerFileInput, handleFileUpload,
      // Assinatura
      showSignatureModal, openSignatureModal, closeSignatureModal,
      signatureCanvas, startDrawing, draw, stopDrawing, startDrawingTouch, drawTouch,
      clearSignature, saveSignature, isSaving, 
      signingRole, setSigningRole,
      
      goBack, downloadLaudo,
      getStatusClass, getTipoClass, statusOptions, viewPhoto, formatDate
    };
  }
});
</script>

<style scoped>
/* =========================================
   ESTILOS GERAIS E RESPONSIVIDADE
   ========================================= */

.page-container {
  min-height: 100vh;
  background-color: #f3f4f6;
  font-family: 'Inter', sans-serif;
  /* Espaço para o cabeçalho fixo */
  padding-top: 100px; 
}

/* --- PREMIUM HEADER --- */
.premium-header {
  position: fixed; top: 0; left: 64px; right: 0; /* Assume sidebar desktop */
  background: white; z-index: 100;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  border-bottom: 1px solid #e5e7eb;
}

.header-wrapper {
  max-width: 1200px; 
  margin: 0 auto; 
  padding: 16px 32px;
}

/* Main Bar (Desktop: Flex horizontal) */
.main-bar { 
    display: flex; 
    justify-content: space-between; 
    align-items: flex-end; 
    flex-wrap: wrap; /* Permite quebrar em telas médias */
}

/* Actions & Progress (Desktop: Horizontal) */
.actions-section { 
    display: flex; 
    align-items: center; 
    gap: 12px; /* Reduzido para telas menores */
    margin-top: 10px; /* Espaço para quando o título é longo */
}


/* --- CONTEÚDO PRINCIPAL --- */
.main-content { 
    max-width: 900px; 
    margin: 0 auto; 
    padding: 0 20px 40px 20px; 
}


/* --- MEDIA QUERY: TABLET E MOBILE (Telas <= 768px) --- */
@media (max-width: 768px) {
    .page-container {
        padding-top: 160px; /* Aumenta o espaço para o cabeçalho empilhado */
    }

    .premium-header {
        left: 0; /* Ocupa a largura total na horizontal */
    }

    .header-wrapper {
        padding: 10px 15px;
    }
    
    .main-bar {
        flex-direction: column; /* Empilha o título e as ações */
        align-items: flex-start;
    }

    .title-section {
        width: 100%;
        margin-bottom: 15px;
    }
    
    .actions-section {
        width: 100%;
        flex-direction: column; /* Empilha os botões */
        align-items: stretch;
        gap: 8px; /* Reduz o espaçamento entre botões */
    }

    /* Força os botões a ocuparem 100% da largura */
    .btn-secondary-premium,
    .btn-finish-premium {
        width: 100%;
        text-align: center;
        justify-content: center;
        margin: 0 !important; 
    }
    
    /* Vistoriador Card */
    .vistoriador-info-card {
        padding: 0 15px;
    }
    .info-edit-mode {
        flex-direction: column;
        align-items: stretch;
    }
    .info-edit-mode input,
    .info-edit-mode button {
        width: 100%;
    }

    /* Metainfo fica em coluna ou ajusta */
    .meta-info {
        flex-direction: column;
        align-items: flex-start;
        gap: 5px;
    }
    .meta-separator {
        display: none;
    }
}


/* =========================================
   Estilos do Novo Bloco Vistoriador
   ========================================= */
.vistoriador-info-card {
    max-width: 900px;
    margin: 10px auto 20px auto;
    padding: 0 20px;
}
.info-display {
    padding: 10px;
    background: #eef;
    border-radius: 6px;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 5px;
    font-weight: 500;
}
.btn-edit-inline {
    background: none;
    border: none;
    color: #3b82f6;
    margin-left: 10px;
    cursor: pointer;
    font-size: 12px;
}
.info-edit-mode {
    display: flex;
    gap: 10px;
    align-items: center;
    padding: 10px;
    background: #fff;
    border: 1px solid #ccc;
    border-radius: 6px;
}
.info-edit-mode input {
    flex-grow: 1;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 14px;
}
.btn-save-inline {
    background: #10b981;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 4px;
    cursor: pointer;
}
.btn-cancel-inline {
    background: #ccc;
    border: none;
    padding: 8px 15px;
    border-radius: 4px;
    cursor: pointer;
}

/* =========================================
   Estilos de Componentes (Fixos)
   ========================================= */

/* --- PREMIUM HEADER --- */
.top-bar { margin-bottom: 8px; }
.breadcrumb-item { font-size: 12px; color: #6b7280; }
.breadcrumb-item span { cursor: pointer; transition: color 0.2s; }
.breadcrumb-item span:hover { color: #3b82f6; text-decoration: underline; }
.breadcrumb-item.active { color: #111827; font-weight: 500; }

.title-section h1 {
  font-size: 24px; font-weight: 700; color: #111827; margin: 0; letter-spacing: -0.5px;
}

.status-pill {
  font-size: 11px; font-weight: 700; text-transform: uppercase; padding: 4px 10px;
  border-radius: 20px; letter-spacing: 0.5px;
}
.type-entrada { background: #dcfce7; color: #15803d; }
.type-saida { background: #fee2e2; color: #b91c1c; }
.type-periodica { background: #e0f2fe; color: #0369a1; }

.meta-info {
  display: flex; align-items: center; gap: 12px; margin-top: 8px; flex-wrap: wrap;
}
.meta-item { font-size: 13px; color: #4b5563; display: flex; align-items: center; gap: 6px; }


/* Actions & Progress */
.progress-widget { min-width: 140px; }
.progress-labels { display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px; }
.progress-labels .label { color: #9ca3af; font-weight: 600; text-transform: uppercase; }
.progress-labels .value { color: #111827; font-weight: 700; }
.progress-track { width: 100%; height: 6px; background: #f3f4f6; border-radius: 3px; overflow: hidden; }
.progress-fill { height: 100%; background: #3b82f6; border-radius: 3px; }

/* Botões */
.btn-finish-premium {
  background: #111827; color: white; border: none; padding: 12px 24px;
  border-radius: 8px; font-weight: 600; display: flex; align-items: center; gap: 8px;
  transition: all 0.2s; box-shadow: 0 4px 12px rgba(0,0,0,0.1); cursor: pointer;
}
.btn-finish-premium:hover { background: #000; transform: translateY(-1px); }
.btn-concluir {
    background-color: #10b981 !important; /* Verde Concluir */
    border: 1px solid #10b981 !important;
}
.btn-concluir:hover { background-color: #0d9475 !important; }


.btn-secondary-premium {
  background: white; border: 1px solid #d1d5db; color: #374151; padding: 12px 20px;
  border-radius: 8px; font-weight: 600; display: flex; align-items: center; gap: 8px;
  transition: all 0.2s; cursor: pointer;
}
.btn-secondary-premium:hover { background: #f9fafb; border-color: #9ca3af; }

/* --- CONTENT --- */
/* Empty State */
.empty-state-modern {
  text-align: center; padding: 80px 20px;
  background: white; border-radius: 16px; border: 2px dashed #e5e7eb;
}
.empty-illustration {
  font-size: 48px; color: #d1d5db; margin-bottom: 16px;
  background: #f9fafb; width: 100px; height: 100px; line-height: 100px;
  border-radius: 50%; margin: 0 auto 24px auto;
}
.empty-state-modern h3 { font-size: 18px; font-weight: 600; color: #111827; }
.btn-primary-hero {
  background: #3b82f6; color: white; border: none; padding: 12px 28px;
  border-radius: 8px; font-weight: 600; margin-top: 24px; cursor: pointer;
  transition: background 0.2s;
}
.btn-primary-hero:hover { background: #2563eb; }

/* Cards Ambiente */
.ambiente-card {
  background: white; border-radius: 12px; border: 1px solid #e5e7eb;
  margin-bottom: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); overflow: hidden;
}
.ambiente-header {
  padding: 16px 24px; border-bottom: 1px solid #f3f4f6; background: #ffffff;
  display: flex; justify-content: space-between; align-items: center;
}
.icon-box {
  width: 40px; height: 40px; background: #f0f9ff; color: #0284c7;
  border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px;
}
.ambiente-name { margin: 0; font-size: 16px; font-weight: 700; color: #1e293b; }
.ambiente-meta { font-size: 12px; color: #64748b; }

.btn-icon-subtle {
  width: 32px; height: 32px; border-radius: 6px; border: none; background: transparent;
  color: #94a3b8; cursor: pointer; transition: all 0.2s;
}
.btn-icon-subtle:hover { background: #f1f5f9; color: #475569; }
.btn-icon-subtle.danger:hover { background: #fee2e2; color: #ef4444; }

/* Item Row */
.item-row {
  display: flex; padding: 16px 24px; border-bottom: 1px solid #f1f5f9;
  transition: background 0.1s;
}
.item-row:hover { background: #fcfcfc; }
.item-row:last-child { border-bottom: none; }

.item-col-main { flex: 1; padding-right: 16px; }
.item-title { font-weight: 600; font-size: 14px; color: #334155; }

.status-badge-sm {
  font-size: 10px; font-weight: 700; text-transform: uppercase; padding: 2px 8px;
  border-radius: 4px; letter-spacing: 0.5px;
}
.s-novo { background: #dcfce7; color: #166534; }
.s-bom { background: #dbeafe; color: #1e40af; }
.s-regular { background: #fef9c3; color: #854d0e; }
.s-ruim { background: #fee2e2; color: #991b1b; }
.s-inop { background: #1e293b; color: #fff; }

.item-obs { font-size: 13px; color: #64748b; margin: 4px 0; line-height: 1.5; }

/* Mini Gallery */
.mini-gallery { display: flex; gap: 8px; margin-top: 10px; }
.mini-thumb {
  width: 40px; height: 40px; border-radius: 6px; overflow: hidden;
  border: 1px solid #e2e8f0; cursor: pointer; transition: transform 0.2s;
}
.mini-thumb:hover { transform: scale(1.1); border-color: #3b82f6; }
.mini-thumb img { width: 100%; height: 100%; object-fit: cover; }

.btn-edit-round {
  width: 36px; height: 36px; border-radius: 50%; border: 1px solid #e2e8f0;
  background: white; color: #64748b; display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.2s;
}
.btn-edit-round:hover { border-color: #3b82f6; color: #3b82f6; }

/* Add Item Footer */
.ambiente-footer { padding: 12px 24px; background: #f8fafc; border-top: 1px solid #f1f5f9; }
.btn-add-item-dashed {
  width: 100%; padding: 12px; border: 1px dashed #cbd5e1; background: transparent;
  border-radius: 8px; font-size: 13px; font-weight: 600; color: #64748b;
  cursor: pointer; transition: all 0.2s;
}
.btn-add-item-dashed:hover { background: #eff6ff; border-color: #93c5fd; color: #2563eb; }

/* Global Add Button */
.add-ambiente-wrapper { text-align: center; margin-top: 32px; padding-bottom: 40px; }
.btn-add-ambiente-lg {
  background: transparent; border: 2px dashed #cbd5e1; color: #64748b;
  padding: 16px 40px; border-radius: 12px; font-weight: 600; font-size: 15px;
  cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 10px;
}
.btn-add-ambiente-lg:hover { border-color: #64748b; color: #1e293b; background: #f1f5f9; }

/* Card Styling */
.card { border: 1px solid #e2e8f0; border-radius: 8px; background: #fff; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05); }
.card-header { 
    background: #f8fafc; border-bottom: 1px solid #e2e8f0; padding: 12px 16px; 
    font-size: 16px; font-weight: 600; color: #111827; border-top-left-radius: 8px; border-top-right-radius: 8px;
}
.card-body { padding: 16px; }

/* ================= MODAIS ================= */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0,0,0,0.5); backdrop-filter: blur(4px); z-index: 1050;
  display: flex; justify-content: center; align-items: center;
}

.modal-card {
  background: white; width: 90%; max-width: 420px; border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); overflow: hidden;
  animation: modalPop 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.modal-card.lg { max-width: 600px; }

@keyframes modalPop { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }

.modal-top {
  padding: 20px 24px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center;
  background: #ffffff;
}
.modal-top h4 { margin: 0; font-size: 18px; font-weight: 700; color: #1e293b; }
.btn-close-icon { background: none; border: none; font-size: 18px; color: #94a3b8; cursor: pointer; }

.modal-content-box { padding: 24px; max-height: 70vh; overflow-y: auto; }
.modal-content-box.scrollable { padding-right: 18px; }

.input-label { font-size: 13px; font-weight: 600; color: #334155; margin-bottom: 8px; display: block; }
.input-styled {
  width: 100%; padding: 12px; border: 1px solid #cbd5e1; border-radius: 8px;
  font-size: 14px; color: #1e293b; transition: all 0.2s;
}
.input-styled:focus { border-color: #3b82f6; outline: none; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }

/* Status Grid */
.status-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.status-card {
  border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; cursor: pointer;
  display: flex; flex-direction: column; align-items: center; gap: 8px; transition: all 0.2s;
}
.status-card:hover { background: #f8fafc; border-color: #cbd5e1; }
.status-card.active { border-color: #3b82f6; background: #eff6ff; box-shadow: 0 0 0 1px #3b82f6; }
.status-card span { font-size: 12px; font-weight: 600; color: #475569; }
.status-dot { width: 12px; height: 12px; border-radius: 50%; }

/* Photo Upload */
.photo-upload-area {
  border: 2px dashed #cbd5e1; border-radius: 12px; padding: 32px;
  text-align: center; cursor: pointer; background: #f8fafc; transition: all 0.2s;
  display: flex; flex-direction: column; align-items: center; gap: 12px;
}
.photo-upload-area:hover { border-color: #3b82f6; background: #eff6ff; }
.photo-upload-area i { color: #94a3b8; }
.photo-upload-area span { font-size: 14px; color: #64748b; font-weight: 500; }

.modal-actions {
  padding: 20px 24px; border-top: 1px solid #f1f5f9; background: #f8fafc;
  display: flex; justify-content: flex-end; gap: 12px;
}
.btn-text { background: none; border: none; font-weight: 600; color: #64748b; cursor: pointer; padding: 10px 20px; }
.btn-solid { background: #111827; color: white; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; }
.btn-solid:hover { background: #000; }

/* CANVAS DE ASSINATURA */
.signature-wrapper {
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
  background: #fff;
  cursor: crosshair;
  overflow: hidden;
  margin-bottom: 10px;
}
.signature-pad {
  width: 100%;
  display: block;
  touch-action: none; /* Importante para não rolar a tela no celular */
}

/* SELETOR DE ROLE (QUEM ASSINA) */
.role-selector {
  display: flex;
  justify-content: center;
  gap: 12px;
}
.role-btn {
  border: 1px solid #e5e7eb;
  background: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
}
.role-btn:hover { background: #f9fafb; }
.role-btn.active {
  background: #eff6ff;
  border-color: #3b82f6;
  color: #2563eb;
  box-shadow: 0 0 0 1px #3b82f6;
}
</style>