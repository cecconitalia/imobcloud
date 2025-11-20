<template>
  <div class="page-container">
    
    <div v-if="!isLoading" class="dashboard-grid">
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-calendar-check"></i></div>
        <div class="stat-info">
            <h3>Total de Visitas</h3>
            <p>{{ stats.total }}</p>
        </div>
      </div>
      <div class="stat-card stat-blue">
        <div class="stat-icon"><i class="fas fa-clock"></i></div>
        <div class="stat-info">
            <h3>Pendentes</h3>
            <p>{{ stats.pendentes }}</p>
        </div>
      </div>
      <div class="stat-card stat-green">
        <div class="stat-icon"><i class="fas fa-check-circle"></i></div>
        <div class="stat-info">
            <h3>Realizadas</h3>
            <p>{{ stats.realizadas }}</p>
        </div>
      </div>
      <div class="stat-card stat-purple">
        <div class="stat-icon"><i class="fas fa-calendar-day"></i></div>
        <div class="stat-info">
            <h3>Para Hoje</h3>
            <p>{{ stats.hoje }}</p>
        </div>
      </div>
    </div>

    <div class="search-and-filter-bar">
      <input 
        type="text" 
        v-model="searchTerm" 
        placeholder="Buscar por cliente, imóvel ou bairro..." 
        class="search-input"
      />
      
      <div class="filter-group">
        <label for="status">Status:</label>
        <select id="status" v-model="filterStatus">
          <option value="">Todos</option>
          <option value="PENDENTE">Pendente</option>
          <option value="REALIZADA">Realizada</option>
        </select>
      </div>

      <router-link :to="{ name: 'visita-nova' }" class="btn-add">
        <i class="fas fa-plus"></i> <span class="mobile-hide">Agendar Visita</span>
      </router-link>
    </div>

    <div v-if="isLoading" class="loading-message card">
      <div class="spinner"></div>
      <p>A carregar visitas...</p>
    </div>
    <div v-else-if="error" class="error-message card">{{ error }}</div>
    
    <div v-else-if="filteredVisitas.length === 0" class="empty-state card">
      <div class="empty-icon"><i class="far fa-calendar-times"></i></div>
      <p>Nenhuma visita encontrada com os filtros selecionados.</p>
    </div>

    <div v-else class="visitas-grid">
      <div 
        v-for="visita in filteredVisitas" 
        :key="visita.id" 
        class="visita-card"
        :class="{ 'border-realizada': visita.realizada }"
      >
        <div class="card-top-bar">
           <div class="badges-left">
               <span class="visita-id">#{{ visita.id }}</span>
               <span class="date-badge">
                  <i class="far fa-calendar-alt"></i> {{ formatarData(visita.data_visita) }}
               </span>
           </div>
           <div class="badges-right">
               <span :class="['status-pill', visita.realizada ? 'status-realizada' : 'status-pendente']">
                  <i :class="visita.realizada ? 'fas fa-check-circle' : 'far fa-clock'"></i>
                  {{ visita.realizada ? 'Realizada' : 'Pendente' }}
               </span>
           </div>
        </div>
        
        <div class="card-body">
          <div class="imovel-section">
             <h4 class="imovel-title" :title="visita.imovel_obj?.titulo_anuncio || 'Imóvel'">
                {{ visita.imovel_obj?.titulo_anuncio || 'Imóvel sem título' }}
             </h4>
             <p class="imovel-address">
                <i class="fas fa-map-marker-alt text-muted"></i> 
                {{ visita.imovel_obj?.logradouro }}, {{ visita.imovel_obj?.numero }}
             </p>
             <small class="text-muted">{{ visita.imovel_obj?.bairro }} - {{ visita.imovel_obj?.cidade }}</small>
          </div>

          <div class="time-highlight">
              <i class="far fa-clock"></i> {{ formatarHora(visita.data_visita) }}
          </div>

          <div class="pessoas-container">
              <div class="pessoa-row">
                 <div class="pessoa-avatar avatar-cliente">
                    <i class="fas fa-user"></i>
                 </div>
                 <div class="pessoa-info">
                    <span class="pessoa-role">Cliente Interessado</span>
                    <span class="pessoa-name" :title="visita.cliente_obj?.nome">
                        {{ visita.cliente_obj?.nome || 'Nome não informado' }}
                    </span>
                 </div>
              </div>
          </div>
        </div>
        
        <div class="card-actions">
          <div class="actions-left">
            <button 
                v-if="!visita.realizada"
                @click="abrirModalAssinatura(visita)" 
                class="btn-pill btn-sign"
                title="Colher Assinatura no Local"
            >
                <i class="fas fa-file-signature"></i> Assinar
            </button>
            <span v-else class="signed-badge">
                <i class="fas fa-file-contract"></i> Assinado
            </span>
          </div>

          <div class="actions-right">
              <router-link :to="`/visitas/editar/${visita.id}`" class="btn-mini" title="Editar">
                <i class="fas fa-pen"></i>
              </router-link>
              <button @click="handleDeletar(visita.id)" class="btn-mini btn-delete-mini" title="Cancelar">
                <i class="fas fa-trash"></i>
              </button>
          </div>
        </div>
      </div>
    </div>

    <AssinaturaModal
        v-if="showAssinaturaModal"
        :enderecoImovel="visitaParaAssinar?.imovel_obj?.logradouro"
        :isSaving="isSavingSignature"
        @close="fecharModalAssinatura"
        @save="salvarAssinatura"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
import { format, isSameDay, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import AssinaturaModal from '@/components/AssinaturaModal.vue';
import { useToast } from 'vue-toast-notification';

const visitas = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');
const filterStatus = ref('');
const toast = useToast();

// Estado do Modal
const showAssinaturaModal = ref(false);
const visitaParaAssinar = ref<any>(null);
const isSavingSignature = ref(false);

// --- Computed Stats ---
const stats = computed(() => {
    const total = visitas.value.length;
    const realizadas = visitas.value.filter(v => v.realizada).length;
    const pendentes = total - realizadas;
    
    const hojeDate = new Date();
    const hoje = visitas.value.filter(v => {
        try {
            return isSameDay(parseISO(v.data_visita), hojeDate);
        } catch { return false; }
    }).length;

    return { total, realizadas, pendentes, hoje };
});

// --- Filtros ---
const filteredVisitas = computed(() => {
  return visitas.value.filter(visita => {
    const searchLower = searchTerm.value.toLowerCase();
    const statusMatch = !filterStatus.value || 
        (filterStatus.value === 'REALIZADA' && visita.realizada) ||
        (filterStatus.value === 'PENDENTE' && !visita.realizada);
    
    const textMatch = !searchLower ||
        (visita.cliente_obj?.nome?.toLowerCase() || '').includes(searchLower) ||
        (visita.imovel_obj?.titulo_anuncio?.toLowerCase() || '').includes(searchLower) ||
        (visita.imovel_obj?.logradouro?.toLowerCase() || '').includes(searchLower) ||
        (visita.imovel_obj?.bairro?.toLowerCase() || '').includes(searchLower);

    return statusMatch && textMatch;
  });
});

// --- Formatadores ---
function formatarData(data: string) { 
    try { return format(parseISO(data), 'dd/MM/yyyy', { locale: ptBR }); } 
    catch { return '-'; }
}
function formatarHora(data: string) { 
    try { return format(parseISO(data), 'HH:mm'); } 
    catch { return '-'; }
}

// --- Ações de API ---
async function fetchVisitas() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/v1/visitas/');
    visitas.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar visitas:", err);
    error.value = 'Não foi possível carregar as visitas.';
  } finally {
    isLoading.value = false;
  }
}

async function handleDeletar(visitaId: number) {
  if (!window.confirm('Tem a certeza de que deseja cancelar este agendamento?')) return;
  try {
    await apiClient.delete(`/v1/visitas/${visitaId}/`);
    visitas.value = visitas.value.filter(v => v.id !== visitaId);
    toast.success('Agendamento cancelado.');
  } catch (error) {
    toast.error("Erro ao cancelar agendamento.");
  }
}

// --- Lógica de Assinatura ---
function abrirModalAssinatura(visita: any) {
    visitaParaAssinar.value = visita;
    showAssinaturaModal.value = true;
}

function fecharModalAssinatura() {
    showAssinaturaModal.value = false;
    visitaParaAssinar.value = null;
}

async function salvarAssinatura(base64Image: string) {
    if (!visitaParaAssinar.value) return;
    isSavingSignature.value = true;

    // Geolocalização
    let localizacao = '';
    if (navigator.geolocation) {
        try {
            const position = await new Promise<GeolocationPosition>((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 4000 });
            });
            localizacao = `${position.coords.latitude}, ${position.coords.longitude}`;
        } catch { 
            localizacao = 'Localização indisponível'; 
        }
    }

    const res = await fetch(base64Image);
    const blob = await res.blob();
    const file = new File([blob], "assinatura.png", { type: "image/png" });

    const formData = new FormData();
    formData.append('assinatura_cliente', file);
    formData.append('realizada', 'true');
    formData.append('data_assinatura', new Date().toISOString());
    if(localizacao) formData.append('localizacao_assinatura', localizacao);

    try {
        const response = await apiClient.patch(`/v1/visitas/${visitaParaAssinar.value.id}/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        const index = visitas.value.findIndex(v => v.id === visitaParaAssinar.value.id);
        if (index !== -1) {
            visitas.value[index] = { ...visitas.value[index], ...response.data };
        }
        
        toast.success("Visita confirmada com sucesso!");
        fecharModalAssinatura();
    } catch (error) {
        toast.error("Erro ao salvar assinatura.");
    } finally {
        isSavingSignature.value = false;
    }
}

onMounted(() => {
  fetchVisitas();
});
</script>

<style scoped>
/* ================================================== */
/* 1. Layout Geral (Igual Contratos) */
/* ================================================== */
.page-container { padding: 0; }

/* ================================================== */
/* 2. Dashboard Stats */
/* ================================================== */
.dashboard-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem; margin-bottom: 2rem;
}
.stat-card {
  background-color: #fff; border: none; border-radius: 12px; padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04); display: flex; align-items: center; gap: 1rem;
  transition: transform 0.2s ease;
}
.stat-card:hover { transform: translateY(-3px); }
.stat-icon {
    width: 50px; height: 50px; border-radius: 12px; background-color: #e7f1ff; color: #0d6efd;
    display: flex; align-items: center; justify-content: center; font-size: 1.5rem;
}
.stat-blue .stat-icon { background-color: #e0f2fe; color: #0284c7; }
.stat-green .stat-icon { background-color: #dcfce7; color: #166534; }
.stat-purple .stat-icon { background-color: #f3e8ff; color: #9333ea; }

.stat-info h3 { font-size: 0.8rem; color: #6c757d; font-weight: 600; margin: 0; text-transform: uppercase; }
.stat-info p { font-size: 1.5rem; font-weight: 700; color: #212529; margin: 0; }

/* ================================================== */
/* 3. Filtros */
/* ================================================== */
.search-and-filter-bar {
  display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem;
  align-items: center; background-color: transparent; padding: 0; box-shadow: none;
}
.search-input {
  padding: 10px; border: 1px solid #ccc; border-radius: 5px; width: 100%; max-width: 350px; box-sizing: border-box;
}
.filter-group { display: flex; align-items: center; gap: 0.5rem; }
.filter-group label { font-weight: 500; color: #555; white-space: nowrap; }
.filter-group select {
  padding: 8px 12px; border: 1px solid #ccc; border-radius: 5px; font-size: 0.95rem;
  background-color: #f8f9fa; min-width: 120px;
}
.btn-add {
  background-color: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 5px;
  cursor: pointer; font-weight: bold; transition: background-color 0.3s ease; font-size: 0.95rem;
  display: flex; align-items: center; gap: 0.5rem; margin-left: auto; width: auto; text-decoration: none;
}
.btn-add:hover { background-color: #0056b3; }
.mobile-hide { display: inline; }
@media (max-width: 768px) {
  .search-and-filter-bar { flex-direction: column; align-items: stretch; }
  .search-input { max-width: 100%; }
  .btn-add { margin-left: 0; justify-content: center; }
}

/* ================================================== */
/* 4. Grid de Visitas */
/* ================================================== */
.visitas-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem; padding-bottom: 2rem;
}

.visita-card {
  background-color: #fff; border-radius: 12px; border: 1px solid rgba(0,0,0,0.06);
  box-shadow: 0 4px 12px rgba(0,0,0,0.03); display: flex; flex-direction: column;
  transition: all 0.3s ease; position: relative; overflow: hidden;
}
.visita-card:hover { transform: translateY(-5px); box-shadow: 0 12px 24px rgba(0,0,0,0.08); }
.border-realizada { border-left: 4px solid #10b981; }

/* Header */
.card-top-bar {
    padding: 0.85rem 1.25rem; display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid #f0f2f5; background: #fff;
}
.badges-left, .badges-right { display: flex; align-items: center; gap: 8px; }

.visita-id {
    font-size: 0.75rem; font-weight: 800; color: #6b7280;
    background: #f3f4f6; padding: 3px 8px; border-radius: 6px;
}
.date-badge {
    font-size: 0.8rem; color: #4b5563; font-weight: 600; display: flex; align-items: center; gap: 5px;
}
.status-pill {
    padding: 0.35em 0.85em; border-radius: 50px; font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; display: flex; align-items: center; gap: 5px;
}
.status-pendente { background-color: #eff6ff; color: #1e40af; }
.status-realizada { background-color: #dcfce7; color: #166534; }

/* Body */
.card-body { padding: 0; flex-grow: 1; display: flex; flex-direction: column; }

/* Imovel Info */
.imovel-section { padding: 1.25rem 1.25rem 0.75rem; }
.imovel-title {
    font-size: 1rem; font-weight: 700; color: #111827; margin: 0 0 0.25rem 0;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.imovel-address {
    font-size: 0.85rem; color: #6b7280; margin: 0;
    display: flex; align-items: center; gap: 6px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

/* Time Highlight */
.time-highlight {
    background-color: #f8fafc; border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9;
    padding: 0.5rem 1.25rem; font-weight: 700; color: #0d6efd; font-size: 0.9rem;
    display: flex; align-items: center; gap: 6px;
}

/* Pessoas */
.pessoas-container { padding: 1rem 1.25rem; }
.pessoa-row { display: flex; align-items: center; gap: 0.85rem; }
.pessoa-avatar {
    width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; flex-shrink: 0;
}
.avatar-cliente { background-color: #fef3c7; color: #d97706; }
.pessoa-info { display: flex; flex-direction: column; overflow: hidden; }
.pessoa-role { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; margin-bottom: 1px; color: #d97706; }
.pessoa-name { font-size: 0.9rem; color: #1f2937; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* Actions */
.card-actions {
    padding: 0.85rem 1.25rem; background-color: #fff; border-top: 1px solid #f0f2f5;
    display: flex; justify-content: space-between; align-items: center; gap: 1rem;
}
.actions-left { display: flex; gap: 0.5rem; }
.actions-right { display: flex; gap: 0.25rem; }

/* Buttons */
.btn-pill {
    border: none; border-radius: 6px; padding: 0.4rem 0.85rem; font-size: 0.8rem; font-weight: 600;
    cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s;
}
.btn-sign { background-color: #e0f2fe; color: #0369a1; }
.btn-sign:hover { background-color: #bae6fd; }

.signed-badge {
    display: inline-flex; align-items: center; gap: 5px; font-size: 0.8rem; 
    color: #10b981; font-weight: 600; background-color: #ecfdf5; padding: 4px 8px; border-radius: 6px;
}

.btn-mini {
    width: 32px; height: 32px; border-radius: 6px; border: 1px solid transparent; background: transparent;
    color: #9ca3af; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s;
}
.btn-mini:hover { background-color: #f3f4f6; color: #374151; }
.btn-delete-mini:hover { background-color: #fee2e2; color: #dc2626; }

/* Utils */
.text-muted { color: #9ca3af; }
.loading-message, .error-message, .empty-state { text-align: center; padding: 4rem 2rem; color: #6c757d; }
.empty-icon { font-size: 3rem; color: #dee2e6; margin-bottom: 1rem; }
.spinner {
  border: 3px solid #e9ecef; border-top: 3px solid #007bff; border-radius: 50%;
  width: 40px; height: 40px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>