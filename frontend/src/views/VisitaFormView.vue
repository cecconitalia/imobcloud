<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <router-link to="/">Início</router-link>
              <i class="fas fa-chevron-right separator"></i> 
              <router-link to="/visitas">Visitas</router-link>
              <i class="fas fa-chevron-right separator"></i>
              <span class="active">{{ isEditing ? 'Editar' : 'Agendar' }}</span>
           </nav>
           
           <h1>{{ isEditing ? 'Editar Visita' : 'Agendar Nova Visita' }}</h1>
        </div>
      </div>
    </header>

    <div v-if="isLoadingData" class="loading-state">
         <div class="spinner"></div>
         <p>A carregar dados...</p>
    </div>

    <div v-else class="main-content-grid">
      
      <div class="left-column">
        <div class="card form-card">
          <form @submit.prevent="handleSubmit">
            
            <div class="form-section compact-section">
                <h3 class="section-title"><i class="far fa-calendar-alt"></i> Dados do Agendamento</h3>
                
                <div class="form-grid">
                    
                    <div class="form-group full-width">
                        <label>Imóveis a Visitar <span class="required">*</span></label>
                        <v-select
                            v-model="visita.imoveis"
                            :options="imovelOptions"
                            label="label"
                            multiple
                            placeholder="Pesquisar e adicionar imóveis..."
                            class="style-chooser"
                            @search="onImovelSearch"
                        >
                            <template #option="option">
                                <div class="option-content">
                                    <div class="option-title">
                                        {{ option.titulo_anuncio || 'Imóvel sem título' }} 
                                        <span class="badge-code" v-if="option.codigo">{{ option.codigo }}</span>
                                    </div>
                                    <div class="option-subtitle">
                                        <i class="fas fa-map-marker-alt"></i> 
                                        {{ option.logradouro || 'Endereço N/A' }}
                                    </div>
                                </div>
                            </template>
                            <template #no-options>
                                <span class="no-results">Digite para buscar...</span>
                            </template>
                        </v-select>
                        <small v-if="!isEditing" class="helper-text">Selecione todos os imóveis que serão visitados neste agendamento.</small>
                    </div>

                    <div class="form-group full-width">
                        <label>Cliente Interessado <span class="required">*</span></label>
                        <v-select
                            v-model="visita.cliente"
                            :options="clienteOptions"
                            label="label"
                            placeholder="Pesquisar por nome, telefone ou CPF..."
                            class="style-chooser"
                            @search="onClienteSearch"
                            @option:selected="onClienteSelected"
                        >
                            <template #option="option">
                                <div class="option-content">
                                    <div class="option-title">{{ option.label }}</div>
                                    <div class="option-subtitle">
                                        <span v-if="option.telefone"><i class="fas fa-phone-alt"></i> {{ option.telefone }}</span>
                                        <span v-if="option.documento" style="margin-left: 8px;"><i class="far fa-id-card"></i> {{ option.documento }}</span>
                                    </div>
                                </div>
                            </template>
                            <template #no-options>
                                <span class="no-results">Digite para buscar...</span>
                            </template>
                        </v-select>
                    </div>

                    <div class="form-group">
                        <label>Data da Visita <span class="required">*</span></label>
                        <div class="input-wrapper">
                            <i class="far fa-calendar input-icon"></i>
                            <input 
                                type="date" 
                                v-model="visita.data" 
                                required 
                                class="form-input has-icon"
                                :min="minDate"
                            />
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Hora <span class="required">*</span></label>
                        <div class="input-wrapper">
                            <i class="far fa-clock input-icon"></i>
                            <input 
                                type="time" 
                                v-model="visita.hora" 
                                required 
                                class="form-input has-icon"
                            />
                        </div>
                    </div>

                    <div class="form-group full-width">
                        <label>Observações / Instruções</label>
                        <textarea 
                            v-model="visita.observacoes" 
                            rows="3" 
                            class="form-textarea"
                            placeholder="Ex: Levar as chaves do portão lateral; Cliente prefere não estacionar na garagem..."
                        ></textarea>
                    </div>
                </div>
            </div>

            <div class="form-actions-footer">
                <button type="button" @click="handleCancel" class="btn-secondary">
                    Cancelar
                </button>
                <button type="submit" class="btn-primary" :disabled="isSubmitting">
                    <i v-if="isSubmitting" class="fas fa-spinner fa-spin"></i>
                    <span v-else>
                        {{ isEditing ? 'Salvar Alterações' : 'Confirmar Agendamento' }}
                    </span>
                </button>
            </div>
          </form>
        </div>
      </div> 
      
      <div class="right-column">
            
            <div class="card info-card" :class="{ 'empty': visita.imoveis.length === 0 }">
                 <div class="widget-header">
                     <h3 class="widget-title"><i class="fas fa-home"></i> Roteiro ({{ visita.imoveis.length }})</h3>
                 </div>
                 
                 <div v-if="visita.imoveis.length > 0" class="info-content-list">
                     <div v-for="imovel in visita.imoveis" :key="imovel.value" class="imovel-mini-item">
                        <div class="info-main">
                            <h4 class="info-title">{{ imovel.titulo_anuncio || 'Imóvel sem título' }}</h4>
                            <span class="info-code" v-if="imovel.codigo">{{ imovel.codigo }}</span>
                        </div>
                        <p class="info-address">
                            {{ imovel.logradouro || 'Logradouro N/A' }}
                            <span v-if="imovel.bairro">, {{ imovel.bairro }}</span>
                        </p>
                     </div>
                 </div>
                 <div v-else class="empty-state-widget">
                    <p>Selecione um ou mais imóveis para visualizar o roteiro.</p>
                 </div>
            </div>

            <div class="card info-card" :class="{ 'empty': !clienteSelecionado }">
                 <div class="widget-header">
                     <h3 class="widget-title"><i class="fas fa-user"></i> Cliente</h3>
                 </div>
                 
                 <div v-if="clienteSelecionado" class="info-content">
                     <div class="info-main">
                        <h4 class="info-title">{{ clienteSelecionado.label }}</h4>
                     </div>
                     <div class="contact-list">
                        <p v-if="clienteSelecionado.telefone" class="contact-item">
                            <i class="fas fa-phone"></i> {{ clienteSelecionado.telefone }}
                        </p>
                        <p v-if="clienteSelecionado.email" class="contact-item">
                            <i class="fas fa-envelope"></i> {{ clienteSelecionado.email }}
                        </p>
                     </div>
                 </div>
                 <div v-else class="empty-state-widget">
                    <p>Selecione um cliente para ver os detalhes de contato.</p>
                 </div>
            </div>

      </div> 
    </div> 

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';
import { useToast } from 'vue-toast-notification';
import { format, parseISO } from 'date-fns';

interface SelectObject { 
    label: string; 
    value: number; 
    [key: string]: any; 
}

const route = useRoute();
const router = useRouter();
const toast = useToast();

const visitaId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!visitaId.value);

const isLoadingData = ref(false);
const isSubmitting = ref(false);

// Estado do Form
const visita = ref<{
    imoveis: SelectObject[], 
    cliente: SelectObject | null,
    data: string,
    hora: string,
    observacoes: string
}>({
    imoveis: [],
    cliente: null,
    data: '',
    hora: '',
    observacoes: ''
});

const imovelOptions = ref<SelectObject[]>([]);
const clienteOptions = ref<SelectObject[]>([]);
const clienteSelecionado = ref<any>(null);

const minDate = new Date().toISOString().split('T')[0];

let searchTimeout: NodeJS.Timeout | null = null;

async function onImovelSearch(search: string, loading: (l: boolean) => void) {
    if (search.length >= 2) {
        if (searchTimeout) clearTimeout(searchTimeout);
        loading(true);
        searchTimeout = setTimeout(async () => {
            try {
                const response = await apiClient.get(`/v1/imoveis/?search=${search}`);
                const results = response.data.results || response.data;
                imovelOptions.value = results.map((i: any) => ({
                    label: i.titulo_codigo || i.titulo_anuncio || `Imóvel #${i.id}`,
                    value: i.id,
                    titulo_anuncio: i.titulo_anuncio,
                    codigo: i.codigo_referencia,
                    logradouro: i.logradouro,
                    numero: i.numero,
                    bairro: i.bairro,
                    cidade: i.cidade
                }));
            } finally { loading(false); }
        }, 400);
    }
}

async function onClienteSearch(search: string, loading: (l: boolean) => void) {
    if (search.length >= 2) {
        if (searchTimeout) clearTimeout(searchTimeout);
        loading(true);
        searchTimeout = setTimeout(async () => {
            try {
                const response = await apiClient.get(`/v1/clientes/?search=${search}`);
                const results = response.data.results || response.data;
                clienteOptions.value = results.map((c: any) => ({
                    label: c.nome_display || c.nome || c.razao_social || 'Cliente Sem Nome',
                    value: c.id,
                    telefone: c.telefone,
                    email: c.email,
                    documento: c.documento
                }));
            } finally { loading(false); }
        }, 400);
    }
}

function onClienteSelected(option: any) { clienteSelecionado.value = option; }

async function loadInitialData() {
    isLoadingData.value = true;
    try {
        const [imoveisRes, clientesRes] = await Promise.all([
            apiClient.get('/v1/imoveis/lista-simples/'),
            apiClient.get('/v1/clientes/lista-simples/')
        ]);

        const imoveisResults = Array.isArray(imoveisRes.data) ? imoveisRes.data : (imoveisRes.data.results || []);
        imovelOptions.value = imoveisResults.map((i: any) => ({
            label: i.label || i.titulo_anuncio || `Imóvel ${i.codigo_referencia || i.id}`,
            value: i.value || i.id,
            titulo_anuncio: i.titulo_anuncio,
            codigo: i.codigo_referencia,
            logradouro: i.logradouro,
            bairro: i.bairro,
            cidade: i.cidade
        }));

        const clientesResults = Array.isArray(clientesRes.data) ? clientesRes.data : (clientesRes.data.results || []);
        clienteOptions.value = clientesResults.map((c: any) => ({
            label: c.label || c.nome_display || c.nome || c.razao_social || 'Cliente',
            value: c.value || c.id,
            telefone: c.telefone,
            email: c.email,
            documento: c.documento
        }));

        if (isEditing.value && visitaId.value) {
            const visitaRes = await apiClient.get(`/v1/visitas/${visitaId.value}/`);
            const data = visitaRes.data;
            
            const dataHora = parseISO(data.data_visita);
            visita.value.data = format(dataHora, 'yyyy-MM-dd');
            visita.value.hora = format(dataHora, 'HH:mm');
            visita.value.observacoes = data.observacoes;

            if (data.imoveis_obj && Array.isArray(data.imoveis_obj)) {
                visita.value.imoveis = data.imoveis_obj.map((i: any) => {
                    const opt = { 
                        label: i.titulo_anuncio || 'Imóvel', value: i.id, 
                        titulo_anuncio: i.titulo_anuncio, codigo: i.codigo_referencia,
                        logradouro: i.logradouro, numero: i.numero, bairro: i.bairro, cidade: i.cidade 
                    };
                    if (!imovelOptions.value.find(o => o.value === i.id)) imovelOptions.value.unshift(opt);
                    return opt;
                });
            }

            if (data.cliente_obj) {
                const c = data.cliente_obj;
                const opt = { 
                    label: c.nome || c.razao_social || 'Cliente', value: c.id, 
                    telefone: c.telefone, email: c.email 
                };
                visita.value.cliente = opt;
                clienteSelecionado.value = opt;
                if (!clienteOptions.value.find(o => o.value === c.id)) clienteOptions.value.unshift(opt);
            }
        }
    } catch (err) {
        console.error("Erro ao carregar dados:", err);
        toast.error("Falha ao carregar dados iniciais.");
    } finally {
        isLoadingData.value = false;
    }
}

function getId(item: any): number | null {
    if (!item) return null;
    if (typeof item === 'object' && 'value' in item) return item.value; 
    if (typeof item === 'number') return item;
    return null;
}

async function handleSubmit() {
    if (visita.value.imoveis.length === 0) {
        toast.warning("Selecione pelo menos um imóvel.");
        return;
    }
    const clienteId = getId(visita.value.cliente);
    if (!clienteId) {
        toast.warning("Selecione um cliente.");
        return;
    }
    if (!visita.value.data || !visita.value.hora) {
        toast.warning("Informe a data e hora.");
        return;
    }

    isSubmitting.value = true;
    
    const imoveisIds = visita.value.imoveis.map(i => getId(i)).filter(id => id !== null);
    const dataHoraCombinada = `${visita.value.data}T${visita.value.hora}:00`;

    const payload = {
        imoveis: imoveisIds, 
        cliente: clienteId,
        data_visita: dataHoraCombinada,
        observacoes: visita.value.observacoes
    };

    try {
        if (isEditing.value) {
            await apiClient.put(`/v1/visitas/${visitaId.value}/`, payload);
            toast.success("Agendamento atualizado!");
        } else {
            await apiClient.post('/v1/visitas/', payload);
            toast.success("Agendamento criado com sucesso!");
        }
        router.push({ name: 'visitas' });
    } catch (err: any) {
        console.error("Erro ao salvar:", err.response?.data || err);
        toast.error("Erro ao salvar agendamento.");
    } finally {
        isSubmitting.value = false;
    }
}

function handleCancel() {
    router.push({ name: 'visitas' });
}

onMounted(loadInitialData);
</script>

<style scoped>
/* =========================================================
   1. GERAL & HEADER (PADRÃO LISTAS)
   ========================================================= */
.page-container {
  min-height: 100vh;
  background-color: #fcfcfc; /* Fundo cinza claro padrão */
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
  display: flex;
  flex-direction: column;
}

/* Header & Breadcrumb */
.page-header { margin-bottom: 2rem; }

.title-area { display: flex; flex-direction: column; gap: 6px; }
.title-area h1 {
  font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em;
}

.breadcrumb {
  display: flex; align-items: center; gap: 6px;
  font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;
}
.breadcrumb a { color: #94a3b8; text-decoration: none; transition: color 0.2s; }
.breadcrumb a:hover { color: #2563eb; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }

.header-main { display: flex; justify-content: space-between; align-items: flex-end; }

/* =========================================================
   2. GRID LAYOUT
   ========================================================= */
.main-content-grid { 
    display: grid; 
    grid-template-columns: 1fr 320px; 
    gap: 1.5rem; 
    align-items: start; 
}
@media (max-width: 1100px) { .main-content-grid { grid-template-columns: 1fr; } }

/* =========================================================
   3. CARDS & FORMS
   ========================================================= */
.card {
  background-color: #fff; 
  border-radius: 8px; /* Borda mais sutil */
  box-shadow: 0 1px 2px rgba(0,0,0,0.03); /* Sombra mais leve */
  padding: 1.5rem; 
  border: 1px solid #e5e7eb; /* Borda mais clara */
}
.form-card { min-height: 400px; }

.form-section { margin-bottom: 1.5rem; }
.section-title {
    font-size: 1rem; color: #1f2937; margin-bottom: 1.2rem; padding-bottom: 0.5rem;
    border-bottom: 1px solid #f1f5f9; font-weight: 600; display: flex; align-items: center; gap: 0.6rem;
}
.compact-section { margin-bottom: 0; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.full-width { grid-column: 1 / -1; }

label { font-weight: 500; font-size: 0.85rem; color: #4b5563; }
.required { color: #ef4444; }
.helper-text { font-size: 0.75rem; color: #9ca3af; margin-top: 2px; }

/* Inputs */
.input-wrapper { position: relative; }
.input-icon {
    position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #9ca3af; font-size: 0.85rem; pointer-events: none;
}
.form-input, .form-textarea {
    width: 100%; padding: 0.6rem 0.75rem; border: 1px solid #d1d5db; border-radius: 6px;
    font-size: 0.9rem; transition: all 0.2s; background-color: #fff; box-sizing: border-box; color: #1f2937; font-family: inherit;
}
.form-input.has-icon { padding-left: 2.2rem; }
.form-input:focus, .form-textarea:focus { 
    border-color: #3b82f6; outline: none; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}
.form-textarea { resize: vertical; min-height: 80px; }

/* V-Select Styles */
.style-chooser :deep(.vs__dropdown-toggle) {
    border: 1px solid #d1d5db; border-radius: 6px; padding: 4px 0 5px 0;
}
.style-chooser :deep(.vs__search) { margin-top: 0; font-size: 0.9rem; color: #1f2937; }

/* Footer Actions */
.form-actions-footer {
    display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #f1f5f9;
}
.btn-primary, .btn-secondary {
    padding: 0.5rem 1.2rem; border-radius: 6px; border: none; font-weight: 500; cursor: pointer; font-size: 0.85rem; display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s;
}
.btn-primary { background-color: #2563eb; color: white; box-shadow: 0 1px 2px rgba(37, 99, 235, 0.1); }
.btn-primary:hover { background-color: #1d4ed8; transform: translateY(-1px); }
.btn-secondary { background-color: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; }
.btn-secondary:hover { background-color: #f1f5f9; border-color: #cbd5e1; color: #334155; }

/* =========================================================
   4. INFO CARDS (COLUNA DIREITA)
   ========================================================= */
.info-card { padding: 1.2rem; margin-bottom: 1rem; border-left: 3px solid #2563eb; }
.info-card.empty { border-left-color: #e5e7eb; }

.widget-header { margin-bottom: 0.8rem; padding-bottom: 0.5rem; border-bottom: 1px solid #f1f5f9; }
.widget-title { font-size: 0.9rem; font-weight: 600; margin: 0; color: #374151; }

.info-content-list { display: flex; flex-direction: column; gap: 0.8rem; max-height: 300px; overflow-y: auto; }
.imovel-mini-item { padding-bottom: 0.8rem; border-bottom: 1px solid #f3f4f6; }
.imovel-mini-item:last-child { border-bottom: none; padding-bottom: 0; }

.info-content { display: flex; flex-direction: column; gap: 0.5rem; }
.info-title { font-size: 0.9rem; font-weight: 600; color: #1f2937; margin: 0; line-height: 1.3; }
.info-code { background-color: #f3f4f6; color: #4b5563; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; font-weight: 600; display: inline-block; margin-top: 4px; border: 1px solid #e5e7eb; }
.info-address { font-size: 0.8rem; color: #6b7280; line-height: 1.4; margin: 0; }

.contact-list { margin-top: 0.5rem; }
.contact-item { font-size: 0.8rem; color: #4b5563; margin: 4px 0; display: flex; align-items: center; gap: 8px; }
.contact-item i { color: #9ca3af; width: 16px; text-align: center; }

.empty-state-widget { text-align: center; color: #9ca3af; font-size: 0.8rem; padding: 1rem 0; font-style: italic; }

/* Loading */
.loading-state { text-align: center; padding: 4rem; color: #64748b; }
.spinner { border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%; width: 32px; height: 32px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* Badges inside Select */
.option-content { display: flex; flex-direction: column; }
.option-title { font-weight: 500; font-size: 0.9rem; color: #1f2937; }
.option-subtitle { font-size: 0.75rem; color: #6b7280; display: flex; align-items: center; }
.badge-code { background-color: #f3f4f6; padding: 0 4px; border-radius: 3px; font-size: 0.7rem; font-weight: 600; margin-left: 6px; border: 1px solid #e5e7eb; }

@media (max-width: 1024px) {
  .page-container { padding: 1rem; }
}
</style>