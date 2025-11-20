<template>
  <div class="page-container">
    
    <div v-if="isLoadingData" class="loading-state card">
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
                        <label>Imóvel a Visitar <span class="required">*</span></label>
                        <v-select
                            v-model="visita.imovel"
                            :options="imovelOptions"
                            label="label"
                            placeholder="Pesquisar por código, título ou endereço..."
                            class="style-chooser"
                            @search="onImovelSearch"
                            @option:selected="onImovelSelected"
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
                    <span v-else>{{ isEditing ? 'Atualizar Visita' : 'Confirmar Agendamento' }}</span>
                </button>
            </div>
          </form>
        </div>
      </div> 
      
      <div class="right-column">
            
            <div class="card info-card" :class="{ 'empty': !imovelSelecionado }">
                 <div class="widget-header">
                     <h3 class="widget-title"><i class="fas fa-home"></i> Imóvel Selecionado</h3>
                 </div>
                 
                 <div v-if="imovelSelecionado" class="info-content">
                     <div class="info-main">
                        <h4 class="info-title">{{ imovelSelecionado.titulo_anuncio || 'Imóvel sem título' }}</h4>
                        <span class="info-code" v-if="imovelSelecionado.codigo">Cód: {{ imovelSelecionado.codigo }}</span>
                     </div>
                     <p class="info-address">
                        <i class="fas fa-map-marker-alt"></i>
                        {{ imovelSelecionado.logradouro || 'Logradouro N/A' }}
                        <span v-if="imovelSelecionado.numero">, {{ imovelSelecionado.numero }}</span>
                        <br v-if="imovelSelecionado.bairro">
                        <span v-if="imovelSelecionado.bairro">{{ imovelSelecionado.bairro }}</span>
                        <span v-if="imovelSelecionado.cidade"> - {{ imovelSelecionado.cidade }}</span>
                     </p>
                 </div>
                 <div v-else class="empty-state-widget">
                    <p>Selecione um imóvel para ver os detalhes.</p>
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
                    <p>Selecione um cliente para ver os detalhes.</p>
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

// Interfaces
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

// Dados do Formulário
const visita = ref<{
    imovel: SelectObject | null,
    cliente: SelectObject | null,
    data: string,
    hora: string,
    observacoes: string
}>({
    imovel: null,
    cliente: null,
    data: '',
    hora: '',
    observacoes: ''
});

const imovelOptions = ref<SelectObject[]>([]);
const clienteOptions = ref<SelectObject[]>([]);
const imovelSelecionado = ref<any>(null);
const clienteSelecionado = ref<any>(null);

const minDate = new Date().toISOString().split('T')[0];

// --- Buscas Assíncronas ---

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

// Handlers para Cards Laterais
function onImovelSelected(option: any) { imovelSelecionado.value = option; }
function onClienteSelected(option: any) { clienteSelecionado.value = option; }

// --- Carregamento Inicial ---
async function loadInitialData() {
    isLoadingData.value = true;
    try {
        const [imoveisRes, clientesRes] = await Promise.all([
            apiClient.get('/v1/imoveis/lista-simples/'),
            apiClient.get('/v1/clientes/lista-simples/')
        ]);

        imovelOptions.value = imoveisRes.data.map((i: any) => ({
            label: i.titulo_anuncio || `Imóvel ${i.codigo_referencia || i.id}`,
            value: i.id,
            titulo_anuncio: i.titulo_anuncio,
            codigo: i.codigo_referencia,
            logradouro: i.logradouro,
            bairro: i.bairro,
            cidade: i.cidade
        }));

        clienteOptions.value = clientesRes.data.map((c: any) => ({
            label: c.nome_display || c.nome || c.razao_social || 'Cliente',
            value: c.id,
            telefone: c.telefone,
            email: c.email,
            documento: c.documento
        }));

        // Se Edição
        if (isEditing.value && visitaId.value) {
            const visitaRes = await apiClient.get(`/v1/visitas/${visitaId.value}/`);
            const data = visitaRes.data;
            
            const dataHora = parseISO(data.data_visita);
            visita.value.data = format(dataHora, 'yyyy-MM-dd');
            visita.value.hora = format(dataHora, 'HH:mm');
            visita.value.observacoes = data.observacoes;

            if (data.imovel_obj) {
                const i = data.imovel_obj;
                const opt = { 
                    label: i.titulo_anuncio || 'Imóvel', value: i.id, 
                    titulo_anuncio: i.titulo_anuncio, codigo: i.codigo_referencia,
                    logradouro: i.logradouro, numero: i.numero, bairro: i.bairro, cidade: i.cidade 
                };
                visita.value.imovel = opt;
                imovelSelecionado.value = opt;
                if (!imovelOptions.value.find(o => o.value === i.id)) imovelOptions.value.unshift(opt);
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

// *** HELPER CRÍTICO ***
function getId(item: any): number | null {
    if (!item) return null;
    if (typeof item === 'object' && 'value' in item) return item.value; // Objeto v-select
    if (typeof item === 'number') return item; // Já é ID
    return null;
}

async function handleSubmit() {
    // Valida e extrai ID
    const imovelId = getId(visita.value.imovel);
    const clienteId = getId(visita.value.cliente);

    if (!imovelId) {
        toast.warning("Por favor, selecione um Imóvel na lista.");
        return;
    }
    if (!clienteId) {
        toast.warning("Por favor, selecione um Cliente na lista.");
        return;
    }
    if (!visita.value.data || !visita.value.hora) {
        toast.warning("Informe a Data e Hora da visita.");
        return;
    }

    isSubmitting.value = true;
    
    const dataHoraCombinada = `${visita.value.data}T${visita.value.hora}:00`;

    // Payload com IDs puros
    const payload = {
        imovel: imovelId, 
        cliente: clienteId,
        data_visita: dataHoraCombinada,
        observacoes: visita.value.observacoes
    };

    try {
        if (isEditing.value) {
            await apiClient.put(`/v1/visitas/${visitaId.value}/`, payload);
            toast.success("Visita atualizada com sucesso!");
        } else {
            await apiClient.post('/v1/visitas/', payload);
            toast.success("Visita agendada com sucesso!");
        }
        router.push({ name: 'visitas' });
    } catch (err: any) {
        console.error("Erro ao salvar:", err.response?.data || err);
        let msg = "Erro ao salvar visita.";
        if (err.response?.data && typeof err.response.data === 'object') {
             const keys = Object.keys(err.response.data);
             if (keys.length > 0) msg = `${keys[0]}: ${err.response.data[keys[0]]}`;
        }
        toast.error(msg);
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
/* Layout Base */
.page-container { 
    padding: 0.5rem; 
    background-color: #f4f7f6; 
    min-height: 100vh;
}

/* Grid Principal */
.main-content-grid { 
    display: grid; 
    grid-template-columns: 1fr 320px; 
    gap: 1rem; 
    align-items: start; 
    margin-top: 0; 
}
@media (max-width: 992px) { .main-content-grid { grid-template-columns: 1fr; } }

/* Cards Genéricos */
.card {
  background-color: #fff; 
  border-radius: 10px; 
  box-shadow: 0 4px 12px rgba(0,0,0,0.04);
  padding: 1.5rem; 
  border: 1px solid #eaedf0;
}

/* Formulário Esquerdo */
.form-card { min-height: 400px; }
.compact-section { margin-bottom: 0; }
.section-title {
    font-size: 1.1rem; color: #2c3e50; margin-bottom: 1rem; padding-bottom: 0.5rem;
    border-bottom: 2px solid #f0f2f5; font-weight: 700; display: flex; align-items: center; gap: 0.6rem;
}

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.3rem; }
.full-width { grid-column: 1 / -1; }

label { font-weight: 600; font-size: 0.8rem; color: #495057; }
.required { color: #e74c3c; }

/* Inputs & Estilos */
.input-wrapper { position: relative; }
.input-icon {
    position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #adb5bd; font-size: 0.9rem; pointer-events: none;
}
.form-input, .form-textarea {
    width: 100%; padding: 0.55rem 0.75rem; border: 1px solid #ced4da; border-radius: 6px;
    font-size: 0.9rem; transition: border-color 0.2s; background-color: #fff; box-sizing: border-box;
    font-family: inherit;
}
.form-input.has-icon { padding-left: 2.2rem; }
.form-input:focus, .form-textarea:focus { 
    border-color: #3498db; outline: none; box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}
.form-textarea { resize: vertical; min-height: 80px; }

/* V-Select Custom */
.style-chooser :deep(.vs__dropdown-toggle) {
    border: 1px solid #ced4da; border-radius: 6px; padding: 4px 0 5px 0;
}
.style-chooser :deep(.vs__search) { margin-top: 0; font-size: 0.9rem; }

/* Footer Actions */
.form-actions-footer {
    display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #f0f2f5;
}
.btn-primary, .btn-secondary {
    padding: 0.6rem 1.5rem; border-radius: 6px; border: none; font-weight: 600; cursor: pointer; font-size: 0.9rem; display: flex; align-items: center; gap: 0.5rem;
}
.btn-primary { background-color: #007bff; color: white; }
.btn-primary:hover { background-color: #0056b3; transform: translateY(-1px); }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #5a6268; }

/* Coluna Direita (Cards Informativos) */
.info-card { padding: 1.2rem; margin-bottom: 1rem; border-left: 4px solid #007bff; }
.info-card.empty { border-left-color: #e9ecef; }

.widget-header { margin-bottom: 0.8rem; padding-bottom: 0.5rem; border-bottom: 1px solid #f0f2f5; }
.widget-title { font-size: 0.95rem; font-weight: 700; margin: 0; color: #495057; }

.info-content { display: flex; flex-direction: column; gap: 0.5rem; }
.info-title { font-size: 1rem; font-weight: 700; color: #2c3e50; margin: 0; line-height: 1.3; }
.info-code { background-color: #e9ecef; color: #495057; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; font-weight: 700; display: inline-block; margin-top: 4px; }
.info-address { font-size: 0.85rem; color: #6c757d; line-height: 1.4; margin: 0; }
.info-address i { color: #007bff; margin-right: 4px; }

.contact-list { margin-top: 0.5rem; }
.contact-item { font-size: 0.85rem; color: #343a40; margin: 4px 0; display: flex; align-items: center; gap: 8px; }
.contact-item i { color: #adb5bd; width: 16px; text-align: center; }

.empty-state-widget { text-align: center; color: #adb5bd; font-size: 0.85rem; padding: 1rem 0; font-style: italic; }

/* Loading */
.loading-state { text-align: center; padding: 4rem; color: #6c757d; }
.spinner { border: 3px solid #e9ecef; border-top: 3px solid #007bff; border-radius: 50%; width: 40px; height: 40px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* V-Select Dropdown Slots */
.option-content { display: flex; flex-direction: column; }
.option-title { font-weight: 600; font-size: 0.9rem; color: #343a40; }
.option-subtitle { font-size: 0.75rem; color: #6c757d; display: flex; align-items: center; }
.badge-code { background-color: #e9ecef; padding: 0 4px; border-radius: 3px; font-size: 0.7rem; font-weight: 700; margin-left: 6px; }
</style>