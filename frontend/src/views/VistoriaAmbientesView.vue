<script setup lang="ts">
/**
 * IMOBCLOUD - EXECUÇÃO DE VISTORIA (INTERFACE RENOVADA)
 * Engenharia de Software Full Stack Sênior
 * * Changelog de Layout:
 * - Introdução de 'Summary Card' com progresso visual.
 * - Cards de itens com borda semântica (cor baseada no estado).
 * - Comparativo de Entrada vs Saída com destaque visual.
 * - Inputs e botões otimizados para toque (Mobile First).
 */

import { ref, onMounted, computed, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '@/services/api';
import { format } from 'date-fns';

// --- Interfaces ---
interface Foto {
  id: number;
  url: string;
}

interface ItemVistoria {
  id: number | null;
  item: string;
  estado: 'NOVO' | 'BOM' | 'REGULAR' | 'RUIM' | 'INOPERANTE';
  descricao_avaria: string;
  fotos: Foto[];
  // Dados de Referência (Apenas frontend/Join)
  estado_referencia_entrada?: string;
  descricao_referencia_entrada?: string;
  conferido?: boolean;
}

interface Ambiente {
  id: number;
  nome: string;
  itens: ItemVistoria[];
}

interface Vistoria {
  id: number;
  contrato: number;
  tipo: string;
  data_vistoria: string;
  observacoes: string;
  realizado_por_nome: string;
  concluida: boolean;
  imovel_display: string;
  exige_assinatura_proprietario: boolean;
  assinatura_locatario: string | null;
  assinatura_responsavel: string | null;
  assinatura_proprietario: string | null;
  leitura_agua?: string;
  leitura_luz?: string;
  leitura_gas?: string;
  chaves_devolvidas?: string;
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
const entradaRef = ref<any>(null); // Dados da vistoria de entrada para comparação

const isConcluindo = ref(false);
const isSavingProgress = ref(false);
const activeTab = ref<'checklist' | 'medidores' | 'chaves'>('checklist');

// Modais
const showAmbienteModal = ref(false);
const showItemModal = ref(false);
const showSignatureModal = ref(false);

const ambienteForm = ref({ nome: '' });
const editingItem = ref<ItemVistoria | null>(null);
const currentAmbienteId = ref<number | null>(null);
const itemForm = ref<ItemVistoria>({ id: null, item: '', estado: 'BOM', descricao_avaria: '', fotos: [] });
const selectedFile = ref<File | null>(null);

// Assinatura
const signatureCanvas = ref<HTMLCanvasElement | null>(null);
const ctx = ref<CanvasRenderingContext2D | null>(null);
const isDrawing = ref(false);
const hasSignatureContent = ref(false); 
const isSaving = ref(false);
const signingRole = ref<'responsavel' | 'locatario' | 'proprietario'>('locatario');

// Configurações Visuais
const statusOptions = [
  { val: 'NOVO', label: 'Novo', class: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
  { val: 'BOM', label: 'Bom', class: 'bg-blue-50 text-blue-700 border-blue-200' },
  { val: 'REGULAR', label: 'Regular', class: 'bg-amber-50 text-amber-700 border-amber-200' },
  { val: 'RUIM', label: 'Ruim', class: 'bg-rose-50 text-rose-700 border-rose-200' },
  { val: 'INOPERANTE', label: 'Inop.', class: 'bg-slate-100 text-slate-700 border-slate-300' },
];

const totalItens = computed(() => {
  return ambientes.value.reduce((acc, amb) => acc + (amb.itens ? amb.itens.length : 0), 0);
});

// --- Métodos de Dados ---
const loadData = async () => {
  loading.value = true;
  try {
    const response = await api.get(`/v1/vistorias/vistorias/${vistoriaId}/`);
    vistoria.value = response.data;
    ambientes.value = response.data.ambientes || [];

    // Se for SAÍDA, buscar entrada para comparação
    if (vistoria.value.tipo === 'SAIDA') {
       await loadReferenciaEntrada(vistoria.value.contrato);
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
    } catch (e) { console.error("Erro ao carregar referência", e); }
};

const cruzarDados = () => {
    if (!entradaRef.value) return;
    ambientes.value.forEach(ambSaida => {
        const ambEntrada = entradaRef.value.ambientes.find((a: any) => a.nome.toLowerCase() === ambSaida.nome.toLowerCase());
        if (ambEntrada) {
            ambSaida.itens.forEach(itemSaida => {
                const itemEntrada = ambEntrada.itens.find((i: any) => i.item.toLowerCase() === itemSaida.item.toLowerCase());
                if (itemEntrada) {
                    itemSaida.estado_referencia_entrada = itemEntrada.estado;
                    itemSaida.descricao_referencia_entrada = itemEntrada.descricao_avaria;
                }
            });
        }
    });
};

const saveGeneralObs = async () => {
  if (vistoria.value.concluida) return;
  // Salva dados gerais (obs + medidores)
  const payload = {
      observacoes: vistoria.value.observacoes,
      leitura_agua: vistoria.value.leitura_agua,
      leitura_luz: vistoria.value.leitura_luz,
      leitura_gas: vistoria.value.leitura_gas,
      chaves_devolvidas: vistoria.value.chaves_devolvidas
  };
  try { await api.patch(`/v1/vistorias/vistorias/${vistoriaId}/`, payload); } catch (e) {}
};

const saveProgress = async () => {
  isSavingProgress.value = true;
  try { await saveGeneralObs(); alert("Progresso salvo com sucesso!"); } finally { isSavingProgress.value = false; }
};

const concluirVistoria = async () => {
  if (vistoria.value.concluida) {
    router.push('/vistorias');
    return;
  }
  showSignatureModal.value = true;
};

const finalizeAndClose = async () => {
    if (!confirm("Tem certeza que deseja finalizar a vistoria? A edição será bloqueada.")) return;
    isConcluindo.value = true;
    try {
        await api.patch(`/v1/vistorias/vistorias/${vistoriaId}/`, {
            concluida: true,
            observacoes: vistoria.value.observacoes
        });
        alert("Vistoria finalizada com sucesso!");
        router.push('/vistorias');
    } catch (e) {
        alert("Erro ao concluir vistoria.");
    } finally {
        isConcluindo.value = false;
    }
}

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
  if(!confirm("Apagar este ambiente e todos os itens?")) return;
  try { await api.delete(`/v1/vistorias/ambientes/${id}/`); loadData(); } catch (e) { alert("Erro ao apagar"); }
};

// --- Itens ---
const openItemModal = (ambId: number, item: any) => {
  // Permite abrir modal apenas para visualizar se concluída
  currentAmbienteId.value = ambId;
  editingItem.value = item;
  selectedFile.value = null;
  if (item) {
      itemForm.value = { ...item };
  } else {
      if(vistoria.value.concluida) return; // Não cria novo se concluída
      itemForm.value = { id: null, item: '', estado: 'BOM', descricao_avaria: '', fotos: [] };
  }
  showItemModal.value = true;
};

const saveItem = async () => {
  if(vistoria.value.concluida) return;
  if (!itemForm.value.item) return alert("Informe o nome do item");
  
  try {
    let itemId;
    const payload = {
        ambiente: currentAmbienteId.value,
        item: itemForm.value.item,
        estado: itemForm.value.estado,
        descricao_avaria: itemForm.value.descricao_avaria
    };

    if (editingItem.value && editingItem.value.id) {
      itemId = editingItem.value.id;
      await api.patch(`/v1/vistorias/itens/${itemId}/`, payload);
    } else {
      const res = await api.post('/v1/vistorias/itens/', payload);
      itemId = res.data.id;
    }

    if (selectedFile.value && itemId) {
      const formData = new FormData();
      formData.append('item', String(itemId));
      formData.append('imagem', selectedFile.value);
      await api.post('/v1/vistorias/fotos/', formData);
    }
    
    showItemModal.value = false; 
    loadData();
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
        signatureCanvas.value.height = 200;
        ctx.value = signatureCanvas.value.getContext('2d');
        if (ctx.value) { 
            ctx.value.lineWidth = 2; 
            ctx.value.lineCap = "round"; 
            ctx.value.strokeStyle = "#000";
        }
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
    return { 
        x: (e.touches ? e.touches[0].clientX : e.clientX) - (rect?.left||0), 
        y: (e.touches ? e.touches[0].clientY : e.clientY) - (rect?.top||0) 
    };
};
const startDrawing = (e: any) => { isDrawing.value=true; hasSignatureContent.value=true; const p=getPos(e); ctx.value?.beginPath(); ctx.value?.moveTo(p.x, p.y); };
const draw = (e: any) => { if(!isDrawing.value) return; const p=getPos(e); ctx.value?.lineTo(p.x, p.y); ctx.value?.stroke(); };
const stopDrawing = () => isDrawing.value=false;

const saveSignature = () => {
    if(!hasSignatureContent.value) return alert("Por favor, assine antes de salvar.");
    isSaving.value = true;
    signatureCanvas.value?.toBlob(async (blob) => {
        if(blob) {
            const fd = new FormData();
            const field = signingRole.value === 'responsavel' ? 'assinatura_responsavel' : (signingRole.value === 'proprietario' ? 'assinatura_proprietario' : 'assinatura_locatario');
            fd.append(field, blob, 'sig.png');
            try {
                await api.patch(`/v1/vistorias/vistorias/${vistoriaId}/`, fd);
                alert("Assinatura salva!");
                clearSignature(); 
                loadData();
            } catch(e) { alert("Erro ao salvar assinatura."); } 
            finally { isSaving.value = false; }
        }
    });
};

const downloadLaudo = async () => {
    downloading.value = true;
    try {
        const res = await api.get(`/v1/vistorias/vistorias/${vistoriaId}/gerar-laudo/`, { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([res.data], {type: 'application/pdf'}));
        window.open(url, '_blank');
    } catch (e) { alert("Erro ao gerar PDF."); } finally { downloading.value = false; }
};

const goBack = () => router.push('/vistorias');
const formatDate = (d: string) => d ? format(new Date(d), 'dd/MM/yyyy') : '--';
const viewPhoto = (url: string) => window.open(url, '_blank');
const getStatusClass = (s: string) => { 
    const opt = statusOptions.find(o => o.val === s);
    return opt ? opt.class : 'bg-gray-100 text-gray-600 border-gray-200';
};
const getTipoClass = (t: string) => t==='ENTRADA'?'bg-emerald-100 text-emerald-700':(t==='SAIDA'?'bg-rose-100 text-rose-700':'bg-sky-100 text-sky-700');

onMounted(loadData);
</script>

<template>
  <div class="min-h-screen bg-slate-50 pb-20 font-sans text-slate-800">
    
    <header class="sticky top-0 z-40 bg-white border-b border-slate-200 px-4 h-16 flex items-center justify-between shadow-sm">
      <div class="flex items-center gap-3">
        <button @click="goBack" class="p-2 rounded-full hover:bg-slate-100 active:scale-95 transition-all text-slate-500">
          <i class="fas fa-arrow-left text-lg"></i>
        </button>
        <div>
          <h1 class="text-sm font-bold leading-none text-slate-900">Checklist de Execução</h1>
          <div class="flex items-center gap-2 mt-1">
             <span :class="['text-[10px] font-bold px-2 py-0.5 rounded uppercase', getTipoClass(vistoria.tipo || '')]">
                {{ vistoria.tipo }}
             </span>
             <span v-if="vistoria.concluida" class="text-[10px] font-bold px-2 py-0.5 rounded uppercase bg-slate-200 text-slate-600 flex items-center gap-1">
                <i class="fas fa-lock text-[10px]"></i> Fechada
             </span>
          </div>
        </div>
      </div>
      
      <div class="flex items-center gap-2">
         <button @click="downloadLaudo" :disabled="downloading" class="p-2 text-slate-500 hover:text-blue-600 active:scale-95 transition-all" title="Baixar Laudo">
            <i v-if="!downloading" class="fas fa-file-alt text-lg"></i>
            <i v-else class="fas fa-spinner fa-spin text-lg"></i>
         </button>
         
         <button 
            @click="concluirVistoria" 
            :disabled="vistoria.concluida || isConcluindo"
            class="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-lg text-xs font-bold uppercase hover:bg-slate-800 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
         >
            <i class="fas fa-check-circle"></i>
            <span class="hidden sm:inline">{{ vistoria.concluida ? 'Concluída' : 'Finalizar' }}</span>
         </button>
      </div>
    </header>

    <div class="bg-white border-b border-slate-200 flex sticky top-16 z-30 overflow-x-auto no-scrollbar">
       <button 
         v-for="tab in [{id:'checklist', icon:'fa-tasks', label:'Checklist'}, {id:'medidores', icon:'fa-bolt', label:'Medidores'}, {id:'chaves', icon:'fa-key', label:'Chaves'}]"
         :key="tab.id"
         @click="activeTab = tab.id as any"
         :class="['flex-1 min-w-[100px] py-3 text-xs font-bold uppercase tracking-wide border-b-2 transition-all flex flex-col items-center gap-1', activeTab === tab.id ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-400 hover:text-slate-600']"
       >
         <i :class="['fas', tab.icon, 'text-sm']"></i>
         {{ tab.label }}
       </button>
    </div>

    <main class="max-w-3xl mx-auto p-4 space-y-6">
      
      <div v-if="loading" class="flex flex-col items-center justify-center py-12 text-slate-400">
        <div class="w-8 h-8 border-4 border-slate-200 border-t-blue-500 rounded-full animate-spin mb-4"></div>
        <p class="text-sm font-medium">Sincronizando dados...</p>
      </div>

      <div v-else>
        
        <div v-if="activeTab === 'checklist'" class="space-y-4">
           
           <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
              <div class="flex justify-between items-start mb-4">
                 <div>
                    <h2 class="text-sm font-bold text-slate-800">{{ vistoria.imovel_display }}</h2>
                    <p class="text-xs text-slate-500">Contrato #{{ vistoria.contrato }}</p>
                 </div>
                 <div class="text-right">
                    <span class="block text-xl font-bold text-blue-600">{{ totalItens }}</span>
                    <span class="text-[10px] text-slate-400 uppercase font-bold">Itens</span>
                 </div>
              </div>
              <button v-if="!vistoria.concluida" @click="saveProgress" :disabled="isSavingProgress" class="w-full py-2.5 bg-slate-100 text-slate-600 rounded-xl text-xs font-bold uppercase hover:bg-slate-200 active:scale-95 transition-all">
                 <i class="fas fa-save mr-2"></i> Salvar Estado Atual
              </button>
           </div>

           <div v-if="ambientes.length === 0" class="text-center py-12 bg-white rounded-2xl border border-dashed border-slate-300">
              <div class="w-14 h-14 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-3 text-slate-300 text-2xl"><i class="fas fa-home"></i></div>
              <p class="text-sm text-slate-500 font-medium">Nenhum ambiente cadastrado</p>
              <button v-if="!vistoria.concluida" @click="openAmbienteModal" class="mt-4 px-5 py-2 bg-blue-600 text-white rounded-lg text-xs font-bold uppercase shadow-lg shadow-blue-200 active:scale-95">Adicionar Ambiente</button>
           </div>

           <div v-else class="space-y-4">
              <div v-for="ambiente in ambientes" :key="ambiente.id" class="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
                 <div class="px-5 py-3 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
                    <h3 class="font-bold text-slate-700 text-sm uppercase tracking-wide flex items-center gap-2">
                       <i class="fas fa-door-open text-blue-400"></i> {{ ambiente.nome }}
                    </h3>
                    <div class="flex items-center gap-2">
                       <span class="text-[10px] font-bold bg-white px-2 py-1 rounded border border-slate-200 text-slate-500">{{ ambiente.itens?.length || 0 }}</span>
                       <button v-if="!vistoria.concluida" @click="deleteAmbiente(ambiente.id)" class="w-7 h-7 flex items-center justify-center rounded hover:bg-red-50 text-slate-400 hover:text-red-500 transition-all"><i class="fas fa-trash-alt text-xs"></i></button>
                    </div>
                 </div>

                 <div class="divide-y divide-slate-50">
                    <div v-for="item in ambiente.itens" :key="item.id || 0" @click="openItemModal(ambiente.id, item)" class="p-4 hover:bg-blue-50/30 transition-colors cursor-pointer group">
                       <div class="flex items-start gap-3">
                          <div :class="['w-1.5 self-stretch rounded-full flex-shrink-0', getStatusClass(item.estado).split(' ')[0].replace('bg-', 'bg-')]"></div>
                          
                          <div class="flex-1 min-w-0">
                             <div class="flex justify-between items-start mb-1">
                                <span class="text-sm font-bold text-slate-800">{{ item.item }}</span>
                                <span :class="['text-[9px] font-bold px-2 py-0.5 rounded border uppercase', getStatusClass(item.estado)]">{{ item.estado }}</span>
                             </div>

                             <div v-if="item.estado_referencia_entrada" class="mb-2 p-2 bg-slate-50 rounded-lg border border-slate-100 flex gap-2 items-center">
                                <i class="fas fa-history text-slate-400 text-xs"></i>
                                <div class="flex-1">
                                   <p class="text-[10px] text-slate-500 uppercase font-bold leading-none">Entrada</p>
                                   <p class="text-xs font-medium text-slate-700">{{ item.estado_referencia_entrada }}</p>
                                </div>
                             </div>

                             <p v-if="item.descricao_avaria" class="text-xs text-slate-600 bg-red-50 p-2 rounded border border-red-100">
                                <i class="fas fa-exclamation-circle text-red-400 mr-1"></i> {{ item.descricao_avaria }}
                             </p>
                             <p v-else class="text-[11px] text-slate-300 italic">Sem observações</p>

                             <div v-if="item.fotos && item.fotos.length" class="mt-2 flex items-center gap-1 text-[10px] font-bold text-blue-600">
                                <i class="fas fa-camera"></i> {{ item.fotos.length }} foto(s)
                             </div>
                          </div>
                          
                          <i class="fas fa-chevron-right text-slate-200 group-hover:text-blue-400 self-center"></i>
                       </div>
                    </div>

                    <button v-if="!vistoria.concluida" @click="openItemModal(ambiente.id, null)" class="w-full py-3 text-xs font-bold text-slate-400 hover:text-blue-600 hover:bg-slate-50 transition-all flex items-center justify-center gap-2">
                       <i class="fas fa-plus-circle"></i> Adicionar Item ao Ambiente
                    </button>
                 </div>
              </div>

              <button v-if="!vistoria.concluida" @click="openAmbienteModal" class="w-full py-4 border-2 border-dashed border-slate-300 rounded-2xl text-slate-400 font-bold text-xs uppercase hover:border-blue-400 hover:text-blue-500 transition-all active:scale-95 bg-transparent">
                 <i class="fas fa-folder-plus mr-2"></i> Adicionar Outro Ambiente
              </button>
           </div>
        </div>

        <div v-if="activeTab === 'medidores'" class="space-y-4 animate-in">
           <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-6">
              <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest border-b border-slate-100 pb-2">Leituras Finais</h3>
              
              <div class="space-y-4">
                 <div class="group">
                    <label class="text-[10px] font-bold text-slate-500 uppercase ml-1">Água (m³)</label>
                    <div class="relative mt-1">
                       <i class="fas fa-tint absolute left-4 top-1/2 -translate-y-1/2 text-blue-400"></i>
                       <input v-model="vistoria.leitura_agua" type="text" placeholder="000000" class="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl font-mono font-bold text-slate-700 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none" :disabled="vistoria.concluida">
                    </div>
                 </div>

                 <div class="group">
                    <label class="text-[10px] font-bold text-slate-500 uppercase ml-1">Energia (kWh)</label>
                    <div class="relative mt-1">
                       <i class="fas fa-bolt absolute left-4 top-1/2 -translate-y-1/2 text-amber-400"></i>
                       <input v-model="vistoria.leitura_luz" type="text" placeholder="000000" class="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl font-mono font-bold text-slate-700 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none" :disabled="vistoria.concluida">
                    </div>
                 </div>

                 <div class="group">
                    <label class="text-[10px] font-bold text-slate-500 uppercase ml-1">Gás (m³)</label>
                    <div class="relative mt-1">
                       <i class="fas fa-fire absolute left-4 top-1/2 -translate-y-1/2 text-rose-400"></i>
                       <input v-model="vistoria.leitura_gas" type="text" placeholder="000000" class="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl font-mono font-bold text-slate-700 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none" :disabled="vistoria.concluida">
                    </div>
                 </div>
              </div>
              
              <button v-if="!vistoria.concluida" @click="saveGeneralObs" class="w-full py-3 bg-slate-900 text-white rounded-xl text-xs font-bold uppercase active:scale-95">Salvar Leituras</button>
           </div>
        </div>

        <div v-if="activeTab === 'chaves'" class="space-y-4 animate-in">
           <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
              <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest border-b border-slate-100 pb-2">Controle de Devolução</h3>
              <label class="text-[10px] font-bold text-slate-500 uppercase block">Relação de Itens</label>
              <textarea v-model="vistoria.chaves_devolvidas" rows="6" class="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-700 focus:ring-2 focus:ring-blue-500 outline-none resize-none" placeholder="Descreva chaves, controles e tags..." :disabled="vistoria.concluida"></textarea>
              <button v-if="!vistoria.concluida" @click="saveGeneralObs" class="w-full py-3 bg-slate-900 text-white rounded-xl text-xs font-bold uppercase active:scale-95">Salvar Controle</button>
           </div>
        </div>

      </div>
    </main>

    <div v-if="showAmbienteModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
       <div class="bg-white rounded-2xl w-full max-w-xs p-6 shadow-2xl animate-in zoom-in duration-200">
          <div class="flex justify-between items-center mb-4">
             <h3 class="font-bold text-sm uppercase text-slate-500 tracking-widest">Novo Ambiente</h3>
             <button @click="showAmbienteModal = false" class="text-slate-400 hover:text-slate-600"><i class="fas fa-times"></i></button>
          </div>
          <input v-model="ambienteForm.nome" type="text" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-bold text-center mb-6 focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Ex: Sala de Estar" autoFocus />
          <div class="flex gap-3">
             <button @click="showAmbienteModal = false" class="flex-1 py-3 bg-slate-100 text-slate-500 rounded-xl text-xs font-bold uppercase hover:bg-slate-200">Cancelar</button>
             <button @click="saveAmbiente" class="flex-1 py-3 bg-blue-600 text-white rounded-xl text-xs font-bold uppercase hover:bg-blue-700 shadow-lg shadow-blue-200">Criar</button>
          </div>
       </div>
    </div>

    <div v-if="showItemModal" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
       <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" @click="showItemModal = false"></div>
       <div class="relative bg-white w-full max-w-lg rounded-t-[2rem] sm:rounded-[2rem] shadow-2xl flex flex-col max-h-[90vh] animate-in slide-in-from-bottom duration-300">
          
          <div class="p-6 border-b border-slate-100 flex items-center justify-between shrink-0">
             <h3 class="font-bold text-slate-800 uppercase text-xs tracking-widest">{{ editingItem ? 'Editar Detalhes' : 'Novo Registro' }}</h3>
             <button @click="showItemModal = false" class="w-8 h-8 flex items-center justify-center bg-slate-50 rounded-full text-slate-400 hover:bg-slate-100"><i class="fas fa-times"></i></button>
          </div>

          <div class="p-6 overflow-y-auto space-y-6 custom-scrollbar">
             <div class="space-y-2">
                <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Descrição do Item</label>
                <input v-model="itemForm.item" type="text" class="w-full px-4 py-3 bg-slate-50 border-none rounded-xl text-sm font-bold text-slate-700 focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Ex: Pintura, Porta, Janela..." :disabled="vistoria.concluida" />
             </div>

             <div class="space-y-2">
                <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Estado de Conservação</label>
                <div class="grid grid-cols-2 gap-2">
                   <button v-for="opt in statusOptions" :key="opt.val" 
                      @click="!vistoria.concluida && (itemForm.estado = opt.val as any)"
                      :class="['py-3 rounded-xl text-[10px] font-black uppercase border-2 transition-all', itemForm.estado === opt.val ? opt.class : 'bg-white text-slate-400 border-slate-100 hover:bg-slate-50']"
                      :disabled="vistoria.concluida"
                   >
                      {{ opt.label }}
                   </button>
                </div>
             </div>

             <div class="space-y-2">
                <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Avarias / Notas</label>
                <textarea v-model="itemForm.descricao_avaria" rows="3" class="w-full p-4 bg-slate-50 border-none rounded-xl text-sm font-medium text-slate-700 focus:ring-2 focus:ring-blue-500 outline-none resize-none" placeholder="Descreva detalhes..." :disabled="vistoria.concluida"></textarea>
             </div>

             <div class="space-y-4">
                <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1 block text-center">Evidências Fotográficas</label>
                
                <div v-if="!vistoria.concluida" @click="triggerFileInput" class="border-2 border-dashed border-slate-200 rounded-2xl p-6 flex flex-col items-center justify-center text-slate-400 hover:bg-slate-50 hover:border-blue-300 hover:text-blue-500 cursor-pointer transition-all">
                   <div v-if="!selectedFile">
                      <i class="fas fa-camera mb-2 text-2xl"></i>
                      <span class="text-[10px] font-bold uppercase">Tirar Foto / Anexar</span>
                   </div>
                   <div v-else class="text-emerald-600 flex flex-col items-center">
                      <i class="fas fa-check-circle mb-2 text-2xl"></i>
                      <span class="text-xs font-bold">{{ selectedFile.name }}</span>
                   </div>
                   <input type="file" ref="fileInput" class="hidden" accept="image/*" @change="handleFileUpload" />
                </div>

                <div v-if="editingItem?.fotos?.length" class="flex gap-2 justify-center flex-wrap">
                   <div v-for="foto in editingItem.fotos" :key="foto.id" @click="viewPhoto(foto.url)" class="w-20 h-20 rounded-2xl bg-slate-100 overflow-hidden border border-slate-200 cursor-zoom-in relative group">
                      <img :src="foto.url" class="w-full h-full object-cover" />
                   </div>
                </div>
             </div>
          </div>

          <div class="p-6 border-t border-slate-100 flex gap-3 bg-white shrink-0">
             <button @click="showItemModal = false" class="flex-1 py-4 bg-slate-100 text-slate-500 rounded-2xl text-[10px] font-bold uppercase hover:bg-slate-200">Fechar</button>
             <button v-if="!vistoria.concluida" @click="saveItem" class="flex-[2] py-4 bg-blue-600 text-white rounded-2xl text-[10px] font-bold uppercase hover:bg-blue-700 shadow-xl shadow-blue-200 active:scale-95 transition-all">Salvar Registro</button>
          </div>
       </div>
    </div>

    <div v-if="showSignatureModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
       <div class="bg-white rounded-[2.5rem] w-full max-w-md p-8 shadow-2xl animate-in zoom-in duration-200 flex flex-col max-h-[90vh]">
          <div class="flex justify-between items-center mb-6">
             <h3 class="font-black text-xs uppercase tracking-[0.2em] text-slate-400">Coleta de Assinatura</h3>
             <button @click="closeSignatureModal" class="text-slate-400 hover:text-slate-600"><i class="fas fa-times"></i></button>
          </div>

          <div class="flex p-1 bg-slate-100 rounded-2xl mb-6">
             <button @click="setSigningRole('locatario')" :class="['flex-1 py-3 text-[10px] font-bold uppercase rounded-xl transition-all', signingRole==='locatario'?'bg-white shadow-sm text-slate-900':'text-slate-400']">Locatário</button>
             <button @click="setSigningRole('responsavel')" :class="['flex-1 py-3 text-[10px] font-bold uppercase rounded-xl transition-all', signingRole==='responsavel'?'bg-white shadow-sm text-slate-900':'text-slate-400']">Vistoriador</button>
             <button v-if="vistoria.exige_assinatura_proprietario" @click="setSigningRole('proprietario')" :class="['flex-1 py-3 text-[10px] font-bold uppercase rounded-xl transition-all', signingRole==='proprietario'?'bg-white shadow-sm text-slate-900':'text-slate-400']">Proprietário</button>
          </div>

          <div class="border-2 border-slate-100 rounded-3xl bg-slate-50 h-56 relative overflow-hidden touch-none mb-6 shadow-inner">
             <canvas 
                ref="signatureCanvas" 
                class="w-full h-full cursor-crosshair"
                @mousedown="startDrawing" @mousemove="draw" @mouseup="stopDrawing" @mouseleave="stopDrawing"
                @touchstart.prevent="startDrawing" @touchmove.prevent="draw" @touchend.prevent="stopDrawing"
             ></canvas>
             <div v-if="!hasSignatureContent" class="absolute inset-0 flex items-center justify-center pointer-events-none text-slate-300 font-bold uppercase tracking-widest text-[10px]">Assine Aqui</div>
          </div>

          <div class="flex justify-around mb-6 border-t border-slate-100 pt-4">
             <div class="flex flex-col items-center gap-1">
                <div :class="['w-3 h-3 rounded-full', vistoria.assinatura_locatario ? 'bg-emerald-400' : 'bg-slate-200']"></div>
                <span class="text-[9px] font-bold uppercase text-slate-400">Locatário</span>
             </div>
             <div class="flex flex-col items-center gap-1">
                <div :class="['w-3 h-3 rounded-full', vistoria.assinatura_responsavel ? 'bg-emerald-400' : 'bg-slate-200']"></div>
                <span class="text-[9px] font-bold uppercase text-slate-400">Vistoriador</span>
             </div>
          </div>

          <div class="flex gap-3 mt-auto">
             <button @click="clearSignature" class="flex-1 py-4 bg-white border border-slate-200 text-rose-500 rounded-2xl text-[10px] font-black uppercase hover:bg-rose-50">Limpar</button>
             <button @click="saveSignature" :disabled="isSaving" class="flex-[2] py-4 bg-slate-900 text-white rounded-2xl text-[10px] font-black uppercase hover:bg-slate-800 disabled:opacity-50 shadow-xl">
                {{ isSaving ? 'Salvando...' : 'Confirmar' }}
             </button>
          </div>
          
          <button v-if="!vistoria.concluida" @click="finalizeAndClose" class="w-full mt-4 py-3 text-emerald-600 font-bold text-[10px] uppercase hover:bg-emerald-50 rounded-xl transition-all">
             Concluir Tudo e Fechar
          </button>
       </div>
    </div>

  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #E2E8F0; border-radius: 10px; }

.animate-in { animation-duration: 0.2s; animation-fill-mode: both; }
.zoom-in { animation-name: zoomIn; }
.slide-in-from-bottom { animation-name: slideInBottom; }

@keyframes zoomIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
@keyframes slideInBottom { from { transform: translateY(100%); } to { transform: translateY(0); } }

canvas { touch-action: none; }
</style>