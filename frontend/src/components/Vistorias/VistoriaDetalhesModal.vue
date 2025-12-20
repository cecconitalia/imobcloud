<template>
  <div class="modal-backdrop" v-if="show" @click.self="$emit('close')">
    <div class="modal-window">
      
      <div class="modal-header">
        <div class="header-left">
          <span class="badge-type" :class="getTipoClass(vistoria?.tipo)">{{ vistoria?.tipo_display }}</span>
          <h3>Vistoria #{{ vistoria?.id }}</h3>
          <span class="text-muted ms-2" style="font-size: 0.9rem;">
            <i class="far fa-calendar me-1"></i> {{ formatDate(vistoria?.data_vistoria) }}
          </span>
        </div>
        <button class="btn-close" @click="$emit('close')"><i class="fas fa-times"></i></button>
      </div>

      <div class="modal-tabs">
        <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'overview' }" 
            @click="activeTab = 'overview'"
        >
            <i class="fas fa-chart-pie me-2"></i> Visão Geral
        </button>
        <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'checklist' }" 
            @click="activeTab = 'checklist'"
        >
            <i class="fas fa-list-check me-2"></i> Checklist ({{ totalItens }})
        </button>
        <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'gallery' }" 
            @click="activeTab = 'gallery'"
        >
            <i class="fas fa-images me-2"></i> Galeria
        </button>
      </div>

      <div class="modal-content-body" v-if="loading">
         <div class="loading-state"><div class="spinner"></div> Carregando...</div>
      </div>

      <div class="modal-content-body" v-else>
        
        <div v-if="activeTab === 'overview'" class="tab-pane fade-in">
            
            <div class="stats-grid">
                <div class="stat-box">
                    <label>Imóvel / Contrato</label>
                    <div class="val text-truncate" :title="vistoria.imovel_display">
                        <i class="fas fa-map-marker-alt text-primary me-1"></i> {{ vistoria.imovel_display }}
                    </div>
                    <small class="text-muted">Contrato #{{ vistoria.contrato }}</small>
                </div>
                <div class="stat-box">
                    <label>Status Geral</label>
                    <div class="val">
                        <span v-if="vistoria.concluida" class="text-success"><i class="fas fa-check-circle"></i> Concluída</span>
                        <span v-else class="text-warning"><i class="fas fa-clock"></i> Em Andamento</span>
                    </div>
                    <small class="text-muted">{{ vistoria.realizado_por_nome || 'Vistoriador não informado' }}</small>
                </div>
                <div class="stat-box">
                    <label>Resumo de Itens</label>
                    <div class="d-flex gap-3">
                        <div class="text-center">
                            <strong class="d-block text-dark h5 mb-0">{{ totalItens }}</strong>
                            <small class="text-muted" style="font-size: 0.7rem;">TOTAL</small>
                        </div>
                        <div class="text-center">
                            <strong class="d-block text-danger h5 mb-0">{{ itensAvariados }}</strong>
                            <small class="text-muted" style="font-size: 0.7rem;">AVARIAS</small>
                        </div>
                    </div>
                </div>
            </div>

            <div class="section-block">
                <h5 class="section-title"><i class="fas fa-file-signature"></i> Assinaturas Digitais</h5>
                <div class="signatures-container">
                    
                    <div class="sig-card" :class="vistoria.assinatura_responsavel ? 'signed' : 'pending'">
                        <div class="sig-icon">
                            <i :class="vistoria.assinatura_responsavel ? 'fas fa-check' : 'fas fa-pen'"></i>
                        </div>
                        <div class="sig-info">
                            <strong>Vistoriador</strong>
                            <span v-if="vistoria.assinatura_responsavel">Assinado</span>
                            <span v-else>Pendente</span>
                        </div>
                        <button v-if="!vistoria.assinatura_responsavel" class="btn-sig-action" @click="openSignature('responsavel')">Assinar</button>
                    </div>

                    <div class="sig-card" :class="vistoria.assinatura_locatario ? 'signed' : 'pending'">
                        <div class="sig-icon">
                            <i :class="vistoria.assinatura_locatario ? 'fas fa-check' : 'fas fa-pen'"></i>
                        </div>
                        <div class="sig-info">
                            <strong>Locatário</strong>
                            <span v-if="vistoria.assinatura_locatario">Assinado</span>
                            <span v-else>Pendente</span>
                        </div>
                        <button v-if="!vistoria.assinatura_locatario" class="btn-sig-action" @click="openSignature('locatario')">Assinar</button>
                    </div>

                    <div v-if="vistoria.exige_assinatura_proprietario" class="sig-card" :class="vistoria.assinatura_proprietario ? 'signed' : 'pending'">
                        <div class="sig-icon">
                            <i :class="vistoria.assinatura_proprietario ? 'fas fa-check' : 'fas fa-pen'"></i>
                        </div>
                        <div class="sig-info">
                            <strong>Proprietário</strong>
                            <span v-if="vistoria.assinatura_proprietario">Assinado</span>
                            <span v-else>Pendente</span>
                        </div>
                        <button v-if="!vistoria.assinatura_proprietario" class="btn-sig-action" @click="openSignature('proprietario')">Assinar</button>
                    </div>
                    
                    <div v-else class="sig-card disabled">
                        <div class="sig-icon"><i class="fas fa-ban"></i></div>
                        <div class="sig-info">
                            <strong>Proprietário</strong>
                            <span>Não exigido</span>
                        </div>
                    </div>

                </div>
            </div>

            <div class="section-block">
                <h5 class="section-title">Observações Gerais</h5>
                <p class="obs-box">
                    {{ vistoria.observacoes || "Nenhuma observação geral registrada." }}
                </p>
            </div>

        </div>

        <div v-if="activeTab === 'checklist'" class="tab-pane fade-in">
            <div v-if="!vistoria.ambientes || vistoria.ambientes.length === 0" class="empty-tab">
                <i class="fas fa-clipboard-list"></i>
                <p>Nenhum ambiente cadastrado.</p>
            </div>

            <div v-else class="accordion-list">
                <div v-for="ambiente in vistoria.ambientes" :key="ambiente.id" class="acc-item">
                    <div class="acc-header">
                        <span class="acc-title">{{ ambiente.nome }}</span>
                        <span class="badge bg-light text-dark border">{{ ambiente.itens.length }} itens</span>
                    </div>
                    <div class="acc-body">
                        <div v-if="ambiente.itens.length === 0" class="text-muted small fst-italic p-2">Sem itens avaliados.</div>
                        <div v-else class="items-table-wrapper">
                            <table class="items-table">
                                <thead>
                                    <tr>
                                        <th>Item</th>
                                        <th>Estado</th>
                                        <th>Obs/Avarias</th>
                                        <th>Fotos</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="item in ambiente.itens" :key="item.id">
                                        <td class="fw-bold">{{ item.item }}</td>
                                        <td>
                                            <span class="status-dot-badge" :class="getStatusClass(item.estado)">
                                                {{ item.estado }}
                                            </span>
                                        </td>
                                        <td class="text-muted small">{{ item.descricao_avaria || '-' }}</td>
                                        <td>
                                            <div class="d-flex align-items-center gap-1" v-if="item.fotos && item.fotos.length">
                                                <i class="fas fa-camera text-primary"></i> {{ item.fotos.length }}
                                            </div>
                                            <span v-else class="text-muted">-</span>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="activeTab === 'gallery'" class="tab-pane fade-in">
            <div v-if="allPhotos.length === 0" class="empty-tab">
                <i class="fas fa-images"></i>
                <p>Nenhuma foto registrada nesta vistoria.</p>
            </div>
            
            <div v-else class="gallery-grid">
                <div v-for="(photo, idx) in allPhotos" :key="idx" class="gallery-item" @click="viewPhoto(photo.url)">
                    <img :src="photo.url" loading="lazy" />
                    <div class="photo-overlay">
                        <span>{{ photo.ambiente }} - {{ photo.item }}</span>
                    </div>
                </div>
            </div>
        </div>

      </div>

      <div class="modal-footer">
        <a v-if="vistoria.arquivo_laudo_assinado" :href="vistoria.arquivo_laudo_assinado" target="_blank" class="btn-footer secondary">
            <i class="fas fa-download"></i> Baixar Assinado
        </a>
        <button class="btn-footer primary" @click="downloadLaudo" :disabled="downloading">
            <i v-if="downloading" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-file-pdf"></i>
            Gerar PDF
        </button>
      </div>

    </div>

    <AssinaturaModal
        v-if="showSignatureModal"
        :titulo="signatureTitle"
        :termo="signatureTerm"
        :isSaving="isSavingSignature"
        @close="showSignatureModal = false"
        @save="handleSaveSignature"
    />

  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch, computed } from 'vue';
import api from '@/services/api';
import { formatDate } from '@/utils/formatters';
import AssinaturaModal from '@/components/AssinaturaModal.vue';

export default defineComponent({
  name: 'VistoriaDetalhesModal',
  components: { AssinaturaModal },
  props: {
    show: { type: Boolean, required: true },
    vistoriaId: { type: Number, default: null },
  },
  emits: ['close', 'refresh'],
  setup(props, { emit }) {
    const vistoria = ref<any>(null);
    const loading = ref(false);
    const downloading = ref(false);
    const activeTab = ref('overview'); // overview, checklist, gallery

    // Assinatura
    const showSignatureModal = ref(false);
    const signatureType = ref<'locatario' | 'responsavel' | 'proprietario' | null>(null);
    const signatureTitle = ref('');
    const signatureTerm = ref('');
    const isSavingSignature = ref(false);

    const fetchDetalhes = async () => {
        if (!props.vistoriaId) return;
        loading.value = true;
        try {
            const response = await api.get(`/v1/vistorias/vistorias/${props.vistoriaId}/`);
            vistoria.value = response.data;
        } catch (error) {
            console.error('Erro:', error);
        } finally {
            loading.value = false;
        }
    };

    watch(() => props.show, (newVal) => {
        if (newVal) {
            activeTab.value = 'overview';
            fetchDetalhes();
        }
    });

    // --- Computed Helpers ---
    const totalItens = computed(() => {
        if (!vistoria.value?.ambientes) return 0;
        return vistoria.value.ambientes.reduce((acc: number, amb: any) => acc + amb.itens.length, 0);
    });

    const itensAvariados = computed(() => {
        if (!vistoria.value?.ambientes) return 0;
        let count = 0;
        vistoria.value.ambientes.forEach((amb: any) => {
            count += amb.itens.filter((i: any) => ['RUIM', 'INOPERANTE', 'REGULAR'].includes(i.estado)).length;
        });
        return count;
    });

    const allPhotos = computed(() => {
        if (!vistoria.value?.ambientes) return [];
        const photos: any[] = [];
        vistoria.value.ambientes.forEach((amb: any) => {
            amb.itens.forEach((item: any) => {
                if (item.fotos) {
                    item.fotos.forEach((f: any) => {
                        photos.push({ url: f.url || f.imagem, ambiente: amb.nome, item: item.item });
                    });
                }
            });
        });
        return photos;
    });

    // --- Actions ---
    const getStatusClass = (status: string) => {
        const map: any = { 'NOVO': 's-success', 'BOM': 's-primary', 'REGULAR': 's-warning', 'RUIM': 's-danger', 'INOPERANTE': 's-dark' };
        return map[status] || 's-secondary';
    };

    const getTipoClass = (tipo: string) => {
        if(tipo === 'ENTRADA') return 'badge-entrada';
        if(tipo === 'SAIDA') return 'badge-saida';
        return 'badge-periodica';
    };

    const downloadLaudo = async () => {
        downloading.value = true;
        try {
            const res = await api.get(`/v1/vistorias/vistorias/${props.vistoriaId}/gerar-laudo/`, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a'); link.href = url; link.download = `Laudo_${props.vistoriaId}.pdf`;
            document.body.appendChild(link); link.click(); link.remove();
        } catch (e) { alert("Erro ao gerar PDF."); } finally { downloading.value = false; }
    };

    // --- Assinatura Logic ---
    const openSignature = (type: 'locatario' | 'responsavel' | 'proprietario') => {
        signatureType.value = type;
        if (type === 'locatario') {
            signatureTitle.value = "Assinatura do Locatário";
            signatureTerm.value = "Declaro estar de acordo com o estado do imóvel descrito neste laudo.";
        } else if (type === 'responsavel') {
            signatureTitle.value = "Assinatura do Vistoriador";
            signatureTerm.value = "Declaro que realizei a vistoria e as informações são verdadeiras.";
        } else {
            signatureTitle.value = "Assinatura do Proprietário";
            signatureTerm.value = "Declaro estar ciente e de acordo com o laudo apresentado.";
        }
        showSignatureModal.value = true;
    };

    const handleSaveSignature = async (base64Image: string) => {
        if (!vistoria.value || !signatureType.value) return;
        isSavingSignature.value = true;
        
        const res = await fetch(base64Image);
        const blob = await res.blob();
        
        const formData = new FormData();
        if (signatureType.value === 'locatario') formData.append('assinatura_locatario', blob, 'sig.png');
        else if (signatureType.value === 'responsavel') formData.append('assinatura_responsavel', blob, 'sig.png');
        else formData.append('assinatura_proprietario', blob, 'sig.png');

        try {
            await api.patch(`/v1/vistorias/vistorias/${vistoria.value.id}/`, formData, { headers: { 'Content-Type': undefined } });
            showSignatureModal.value = false;
            fetchDetalhes();
        } catch (e) { alert("Erro ao salvar assinatura."); } 
        finally { isSavingSignature.value = false; }
    };

    const viewPhoto = (url: string) => window.open(url, '_blank');

    return {
        vistoria, loading, downloading, activeTab, formatDate,
        totalItens, itensAvariados, allPhotos,
        getStatusClass, getTipoClass, downloadLaudo, viewPhoto,
        // Assinatura
        showSignatureModal, signatureTitle, signatureTerm, isSavingSignature, openSignature, handleSaveSignature
    };
  }
});
</script>

<style scoped>
/* Modal Base */
.modal-backdrop {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.6); backdrop-filter: blur(3px);
    z-index: 1050; display: flex; justify-content: center; align-items: center;
}
.modal-window {
    background: #f8fafc; width: 95%; max-width: 900px; height: 90vh;
    border-radius: 12px; display: flex; flex-direction: column; overflow: hidden;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* Header */
.modal-header {
    background: white; padding: 1rem 1.5rem; border-bottom: 1px solid #e2e8f0;
    display: flex; justify-content: space-between; align-items: center;
}
.header-left h3 { margin: 0.25rem 0 0 0; font-size: 1.25rem; font-weight: 700; color: #1e293b; }
.btn-close { background: none; border: none; font-size: 1.25rem; color: #94a3b8; cursor: pointer; }
.btn-close:hover { color: #ef4444; }

.badge-type { font-size: 0.7rem; padding: 2px 8px; border-radius: 4px; font-weight: 700; text-transform: uppercase; }
.badge-entrada { background: #dcfce7; color: #166534; }
.badge-saida { background: #fee2e2; color: #991b1b; }
.badge-periodica { background: #e0f2fe; color: #075985; }

/* Tabs */
.modal-tabs {
    display: flex; background: white; padding: 0 1.5rem; border-bottom: 1px solid #e2e8f0;
}
.tab-btn {
    padding: 1rem; border: none; background: transparent; color: #64748b; font-weight: 600;
    border-bottom: 2px solid transparent; cursor: pointer; transition: all 0.2s;
}
.tab-btn:hover { color: #3b82f6; }
.tab-btn.active { color: #3b82f6; border-bottom-color: #3b82f6; }

/* Content Body */
.modal-content-body { flex: 1; overflow-y: auto; padding: 1.5rem; }
.loading-state { text-align: center; padding: 3rem; color: #94a3b8; }
.spinner { width: 30px; height: 30px; border: 3px solid #e2e8f0; border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 10px; }
@keyframes spin { to { transform: rotate(360deg); } }

/* TAB 1: VISÃO GERAL */
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
.stat-box { background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0; }
.stat-box label { display: block; font-size: 0.75rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; margin-bottom: 0.5rem; }
.stat-box .val { font-weight: 600; color: #334155; font-size: 0.95rem; margin-bottom: 0.25rem; }

.section-block { margin-bottom: 2rem; }
.section-title { font-size: 1rem; font-weight: 700; color: #1e293b; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e2e8f0; }

/* Assinaturas */
.signatures-container { display: flex; flex-wrap: wrap; gap: 1rem; }
.sig-card {
    flex: 1; min-width: 200px; background: white; border: 1px solid #e2e8f0; border-radius: 8px;
    padding: 1rem; display: flex; align-items: center; gap: 1rem; transition: all 0.2s;
}
.sig-card.signed { border-color: #22c55e; background: #f0fdf4; }
.sig-card.pending { border-color: #f59e0b; background: #fffbeb; }
.sig-card.disabled { opacity: 0.6; background: #f8fafc; }

.sig-icon { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
.signed .sig-icon { background: #22c55e; color: white; }
.pending .sig-icon { background: #f59e0b; color: white; }
.disabled .sig-icon { background: #e2e8f0; color: #94a3b8; }

.sig-info { flex: 1; display: flex; flex-direction: column; }
.sig-info strong { font-size: 0.9rem; color: #334155; }
.sig-info span { font-size: 0.75rem; color: #64748b; }

.btn-sig-action {
    border: none; background: white; border: 1px solid #cbd5e1; padding: 0.4rem 0.8rem;
    border-radius: 6px; font-size: 0.8rem; font-weight: 600; cursor: pointer; color: #475569;
}
.btn-sig-action:hover { background: #f1f5f9; color: #0f172a; }

.obs-box { background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0; color: #475569; font-size: 0.9rem; }

/* TAB 2: CHECKLIST */
.empty-tab { text-align: center; padding: 4rem; color: #94a3b8; }
.empty-tab i { font-size: 3rem; margin-bottom: 1rem; opacity: 0.5; }

.accordion-list { display: flex; flex-direction: column; gap: 1rem; }
.acc-item { background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; }
.acc-header { background: #f8fafc; padding: 0.75rem 1rem; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; font-weight: 600; color: #334155; }
.items-table-wrapper { overflow-x: auto; }
.items-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.items-table th { text-align: left; padding: 0.75rem 1rem; background: #fff; color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; border-bottom: 1px solid #f1f5f9; }
.items-table td { padding: 0.75rem 1rem; border-bottom: 1px solid #f1f5f9; color: #475569; vertical-align: middle; }
.items-table tr:last-child td { border-bottom: none; }

.status-dot-badge { padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; color: white; display: inline-block; }
.s-success { background: #22c55e; }
.s-primary { background: #3b82f6; }
.s-warning { background: #f59e0b; }
.s-danger { background: #ef4444; }
.s-dark { background: #334155; }
.s-secondary { background: #94a3b8; }

/* TAB 3: GALERIA */
.gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 1rem; }
.gallery-item {
    aspect-ratio: 1; border-radius: 8px; overflow: hidden; position: relative; cursor: pointer; border: 1px solid #e2e8f0;
}
.gallery-item img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
.gallery-item:hover img { transform: scale(1.05); }
.photo-overlay {
    position: absolute; bottom: 0; left: 0; width: 100%; background: rgba(0,0,0,0.6);
    color: white; font-size: 0.7rem; padding: 4px 8px; text-align: center;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

/* Footer */
.modal-footer {
    background: white; border-top: 1px solid #e2e8f0; padding: 1rem 1.5rem;
    display: flex; justify-content: flex-end; gap: 1rem;
}
.btn-footer {
    padding: 0.6rem 1.2rem; border-radius: 6px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s;
}
.btn-footer.secondary { background: white; border: 1px solid #cbd5e1; color: #475569; text-decoration: none; font-size: 0.9rem;}
.btn-footer.secondary:hover { background: #f8fafc; border-color: #94a3b8; }
.btn-footer.primary { background: #0f172a; border: none; color: white; }
.btn-footer.primary:hover { background: #334155; }
.btn-footer:disabled { opacity: 0.7; cursor: not-allowed; }

@media (max-width: 600px) {
    .modal-window { width: 100%; height: 100%; border-radius: 0; }
    .stats-grid { grid-template-columns: 1fr; }
    .signatures-container { flex-direction: column; }
    .modal-tabs { overflow-x: auto; }
    .tab-btn { white-space: nowrap; }
}
</style>