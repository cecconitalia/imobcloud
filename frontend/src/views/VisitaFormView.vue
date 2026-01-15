<template>
  <div class="min-h-screen bg-gray-50 p-4 md:p-8 font-sans text-slate-700">
    
    <header class="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
      <div class="flex flex-col gap-2">
        <nav class="flex items-center gap-2 text-xs font-medium text-slate-400 uppercase tracking-wide">
          <router-link to="/" class="hover:text-primary-600 transition-colors decoration-none">Início</router-link>
          <div class="i-fas-chevron-right text-[10px]" />
          <router-link to="/visitas" class="hover:text-primary-600 transition-colors decoration-none">Visitas</router-link>
          <div class="i-fas-chevron-right text-[10px]" />
          <span class="text-primary-600 font-bold">{{ isEditing ? 'Editar' : 'Agendar' }}</span>
        </nav>
        <h1 class="text-2xl md:text-3xl font-light text-slate-800 tracking-tight m-0">
          {{ isEditing ? 'Editar Visita' : 'Agendar Nova Visita' }}
        </h1>
      </div>
    </header>

    <div v-if="isLoadingData" class="flex flex-col items-center justify-center py-16 text-slate-400">
         <div class="w-10 h-10 border-3 border-slate-200 border-t-blue-600 rounded-full animate-spin mb-4" />
         <p class="text-sm font-medium">A carregar dados...</p>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-[1fr_350px] gap-6 items-start">
      
      <div class="bg-white rounded-lg border border-slate-200 shadow-sm p-6">
        <form @submit.prevent="handleSubmit" class="flex flex-col gap-6">
            
            <div class="flex flex-col gap-4">
                <div class="flex items-center gap-2 pb-2 border-b border-slate-100 mb-2">
                    <div class="i-far-calendar-alt text-blue-600 text-lg" />
                    <h3 class="text-lg font-semibold text-slate-800 m-0">Dados do Agendamento</h3>
                </div>
                
                <div class="flex flex-col gap-5">
                    
                    <div class="flex flex-col gap-1.5">
                        <label class="text-sm font-bold text-slate-600">Imóveis a Visitar <span class="text-red-500">*</span></label>
                        <div class="[&_.vs__dropdown-toggle]:!border-slate-300 [&_.vs__dropdown-toggle]:!rounded-md [&_.vs__dropdown-toggle]:!pb-1 [&_.vs__search]:!text-sm [&_.vs__search]:!text-slate-700">
                            <v-select
                                v-model="visita.imoveis"
                                :options="imovelOptions"
                                label="label"
                                multiple
                                placeholder="Pesquisar e adicionar imóveis..."
                                @search="onImovelSearch"
                            >
                                <template #option="option">
                                    <div class="py-1">
                                        <div class="font-bold text-slate-700 flex items-center gap-2 text-sm">
                                            {{ option.titulo_anuncio || 'Imóvel sem título' }} 
                                            <span v-if="option.codigo" class="bg-slate-100 text-slate-500 text-[10px] px-1.5 py-0.5 rounded border border-slate-200 font-mono">{{ option.codigo }}</span>
                                        </div>
                                        <div class="text-xs text-slate-500 flex items-center gap-1 mt-0.5">
                                            <div class="i-fas-map-marker-alt text-[10px]" /> 
                                            {{ option.logradouro || 'Endereço N/A' }}
                                        </div>
                                    </div>
                                </template>
                                <template #no-options>
                                    <span class="text-sm text-slate-400 p-2">Digite para buscar...</span>
                                </template>
                            </v-select>
                        </div>
                        <small v-if="!isEditing" class="text-xs text-slate-400">Selecione todos os imóveis que serão visitados neste agendamento.</small>
                    </div>

                    <div class="flex flex-col gap-1.5">
                        <label class="text-sm font-bold text-slate-600">Cliente Interessado <span class="text-red-500">*</span></label>
                        <div class="[&_.vs__dropdown-toggle]:!border-slate-300 [&_.vs__dropdown-toggle]:!rounded-md [&_.vs__dropdown-toggle]:!pb-1 [&_.vs__search]:!text-sm [&_.vs__search]:!text-slate-700">
                            <v-select
                                v-model="visita.cliente"
                                :options="clienteOptions"
                                label="label"
                                placeholder="Pesquisar por nome, telefone ou CPF..."
                                @search="onClienteSearch"
                                @option:selected="onClienteSelected"
                            >
                                <template #option="option">
                                    <div class="py-1">
                                        <div class="font-bold text-slate-700 text-sm">{{ option.label }}</div>
                                        <div class="text-xs text-slate-500 flex items-center gap-3 mt-0.5">
                                            <span v-if="option.telefone" class="flex items-center gap-1"><div class="i-fas-phone-alt text-[10px]" /> {{ option.telefone }}</span>
                                            <span v-if="option.documento" class="flex items-center gap-1"><div class="i-far-id-card text-[10px]" /> {{ option.documento }}</span>
                                        </div>
                                    </div>
                                </template>
                                <template #no-options>
                                    <span class="text-sm text-slate-400 p-2">Digite para buscar...</span>
                                </template>
                            </v-select>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                        <div class="flex flex-col gap-1.5">
                            <label class="text-sm font-bold text-slate-600">Data da Visita <span class="text-red-500">*</span></label>
                            <div class="relative">
                                <div class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 i-far-calendar text-sm" />
                                <input 
                                    type="date" 
                                    v-model="visita.data" 
                                    required 
                                    class="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 rounded-md focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition-all text-slate-700 bg-white"
                                    :min="minDate"
                                />
                            </div>
                        </div>

                        <div class="flex flex-col gap-1.5">
                            <label class="text-sm font-bold text-slate-600">Hora <span class="text-red-500">*</span></label>
                            <div class="relative">
                                <div class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 i-far-clock text-sm" />
                                <input 
                                    type="time" 
                                    v-model="visita.hora" 
                                    required 
                                    class="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 rounded-md focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition-all text-slate-700 bg-white"
                                />
                            </div>
                        </div>
                    </div>

                    <div class="flex flex-col gap-1.5">
                        <label class="text-sm font-bold text-slate-600">Observações / Instruções</label>
                        <textarea 
                            v-model="visita.observacoes" 
                            rows="3" 
                            class="w-full px-3 py-2 text-sm border border-slate-300 rounded-md focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition-all text-slate-700 bg-white resize-y min-h-[80px]"
                            placeholder="Ex: Levar as chaves do portão lateral; Cliente prefere não estacionar na garagem..."
                        ></textarea>
                    </div>
                </div>
            </div>

            <div class="flex justify-end gap-3 pt-4 border-t border-slate-50 mt-2">
                <button 
                    type="button" 
                    @click="handleCancel" 
                    class="px-4 py-2 rounded-md text-sm font-medium text-slate-600 bg-slate-50 hover:bg-slate-100 transition-colors border border-slate-200 cursor-pointer flex items-center gap-2"
                >
                    Cancelar
                </button>
                <button 
                    type="submit" 
                    class="flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 shadow-sm hover:shadow transition-all disabled:opacity-70 disabled:cursor-not-allowed border-none cursor-pointer" 
                    :disabled="isSubmitting"
                >
                    <div v-if="isSubmitting" class="i-fas-spinner animate-spin" />
                    <span>{{ isEditing ? 'Salvar Alterações' : 'Confirmar Agendamento' }}</span>
                </button>
            </div>
        </form>
      </div> 
      
      <div class="flex flex-col gap-6">
            
            <div class="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden flex flex-col transition-all" :class="{ 'opacity-60 grayscale': visita.imoveis.length === 0 }">
                 <div class="px-4 py-3 bg-slate-50 border-b border-slate-100 flex items-center gap-2">
                     <div class="i-fas-home text-blue-600" />
                     <h3 class="text-sm font-bold text-slate-700 m-0">Roteiro ({{ visita.imoveis.length }})</h3>
                 </div>
                 
                 <div v-if="visita.imoveis.length > 0" class="max-h-[300px] overflow-y-auto p-4 flex flex-col gap-3">
                     <div v-for="imovel in visita.imoveis" :key="imovel.value" class="pb-3 border-b border-slate-50 last:border-0 last:pb-0">
                        <div class="flex items-center gap-2 mb-1">
                            <h4 class="text-sm font-bold text-slate-800 line-clamp-1" :title="imovel.titulo_anuncio">
                                {{ imovel.titulo_anuncio || 'Imóvel sem título' }}
                            </h4>
                            <span v-if="imovel.codigo" class="bg-slate-100 text-slate-500 text-[10px] px-1.5 py-0.5 rounded border border-slate-200 font-mono shrink-0">
                                {{ imovel.codigo }}
                            </span>
                        </div>
                        <p class="text-xs text-slate-500 line-clamp-2 leading-relaxed">
                            {{ imovel.logradouro || 'Logradouro N/A' }}
                            <span v-if="imovel.bairro">, {{ imovel.bairro }}</span>
                        </p>
                     </div>
                 </div>
                 <div v-else class="p-8 text-center text-slate-400 text-xs italic bg-slate-50/50">
                    Selecione um ou mais imóveis para visualizar o roteiro.
                 </div>
            </div>

            <div class="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden flex flex-col transition-all" :class="{ 'opacity-60 grayscale': !clienteSelecionado }">
                 <div class="px-4 py-3 bg-slate-50 border-b border-slate-100 flex items-center gap-2">
                     <div class="i-fas-user text-blue-600" />
                     <h3 class="text-sm font-bold text-slate-700 m-0">Cliente</h3>
                 </div>
                 
                 <div v-if="clienteSelecionado" class="p-4">
                     <div class="mb-3 pb-2 border-b border-slate-50">
                        <h4 class="text-base font-bold text-slate-800">{{ clienteSelecionado.label }}</h4>
                     </div>
                     <div class="flex flex-col gap-2.5 text-sm text-slate-600">
                        <p v-if="clienteSelecionado.telefone" class="flex items-center gap-2.5">
                            <div class="w-6 h-6 rounded bg-green-50 flex items-center justify-center shrink-0">
                                <div class="i-fas-phone text-green-600 text-xs" /> 
                            </div>
                            {{ clienteSelecionado.telefone }}
                        </p>
                        <p v-if="clienteSelecionado.email" class="flex items-center gap-2.5 break-all">
                            <div class="w-6 h-6 rounded bg-blue-50 flex items-center justify-center shrink-0">
                                <div class="i-fas-envelope text-blue-600 text-xs" /> 
                            </div>
                            {{ clienteSelecionado.email }}
                        </p>
                     </div>
                 </div>
                 <div v-else class="p-8 text-center text-slate-400 text-xs italic bg-slate-50/50">
                    Selecione um cliente para ver os detalhes de contato.
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

// Interfaces para Tipagem
interface IOption {
    label: string;
    value: number;
    [key: string]: any;
}

interface IVisitaForm {
    imoveis: IOption[];
    cliente: IOption | null;
    data: string;
    hora: string;
    observacoes: string;
}

const route = useRoute();
const router = useRouter();
const toast = useToast();

const visitaId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!visitaId.value);

const isLoadingData = ref(false);
const isSubmitting = ref(false);

// Estado do Formulário
const visita = ref<IVisitaForm>({
    imoveis: [],
    cliente: null,
    data: '',
    hora: '',
    observacoes: ''
});

const imovelOptions = ref<IOption[]>([]);
const clienteOptions = ref<IOption[]>([]);
const clienteSelecionado = ref<IOption | null>(null);

const minDate = new Date().toISOString().split('T')[0];

let searchTimeout: NodeJS.Timeout | null = null;

// --- Buscas Assíncronas ---

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

function onClienteSelected(option: IOption) { 
    clienteSelecionado.value = option; 
}

// --- Carregamento Inicial ---

async function loadInitialData() {
    isLoadingData.value = true;
    try {
        // Carrega listas simples iniciais
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

        // Se for Edição, carrega dados da visita
        if (isEditing.value && visitaId.value) {
            const visitaRes = await apiClient.get(`/v1/visitas/${visitaId.value}/`);
            const data = visitaRes.data;
            
            try {
                const dataHora = parseISO(data.data_visita);
                visita.value.data = format(dataHora, 'yyyy-MM-dd');
                visita.value.hora = format(dataHora, 'HH:mm');
            } catch { /* data invalida */ }
            
            visita.value.observacoes = data.observacoes || '';

            if (data.imoveis_obj && Array.isArray(data.imoveis_obj)) {
                visita.value.imoveis = data.imoveis_obj.map((i: any) => {
                    const opt = { 
                        label: i.titulo_anuncio || 'Imóvel', value: i.id, 
                        titulo_anuncio: i.titulo_anuncio, codigo: i.codigo_referencia,
                        logradouro: i.logradouro, numero: i.numero, bairro: i.bairro, cidade: i.cidade 
                    };
                    // Adiciona à lista de opções se não existir
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

// --- Submit ---

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
        const msg = err.response?.data?.detail || "Erro ao salvar agendamento.";
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