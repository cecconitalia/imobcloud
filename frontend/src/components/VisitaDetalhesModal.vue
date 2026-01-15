<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-fade-in" @click.self="$emit('close')">
    <div class="bg-white w-full max-w-2xl rounded-xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden animate-slide-up">
      
      <div class="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
        <div>
          <h2 class="text-lg font-bold text-slate-800 m-0">Detalhes da Visita</h2>
          <p class="text-xs text-slate-500 mt-1 flex items-center gap-2">
             <span class="font-mono bg-slate-200 px-1.5 rounded text-slate-600">#{{ visita?.id }}</span>
             <span class="w-1 h-1 rounded-full bg-slate-300"></span>
             {{ formatarDataExtensa(visita?.data_visita) }}
          </p>
        </div>
        <button @click="$emit('close')" class="w-8 h-8 flex items-center justify-center rounded-full text-slate-400 hover:bg-slate-100 hover:text-red-500 transition-colors cursor-pointer border-none bg-transparent">
          <div class="i-fas-times text-lg" />
        </button>
      </div>

      <div class="p-6 overflow-y-auto flex flex-col gap-6">
        
        <div class="flex items-center justify-between p-3 rounded-lg border" 
             :class="visita?.realizada ? 'bg-emerald-50 border-emerald-100' : 'bg-amber-50 border-amber-100'">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full flex items-center justify-center"
                     :class="visita?.realizada ? 'bg-emerald-100 text-emerald-600' : 'bg-amber-100 text-amber-600'">
                    <div :class="visita?.realizada ? 'i-fas-check' : 'i-fas-clock'" />
                </div>
                <div class="flex flex-col">
                    <span class="text-xs font-bold uppercase tracking-wide" 
                          :class="visita?.realizada ? 'text-emerald-700' : 'text-amber-700'">
                        {{ visita?.realizada ? 'Visita Realizada' : 'Visita Pendente' }}
                    </span>
                    <span class="text-[11px] opacity-80" 
                          :class="visita?.realizada ? 'text-emerald-700' : 'text-amber-700'">
                        {{ visita?.realizada ? 'Concluída em ' + formatarData(visita?.data_assinatura || visita?.data_visita) : 'Aguardando realização' }}
                    </span>
                </div>
            </div>
            
            <div class="flex gap-2">
                <div v-if="visita?.assinatura_cliente" class="px-2 py-1 bg-white/60 rounded border border-emerald-200 text-[10px] font-bold text-emerald-700 flex items-center gap-1">
                    <div class="i-fas-file-signature" /> Cliente OK
                </div>
                <div v-if="visita?.assinatura_corretor" class="px-2 py-1 bg-white/60 rounded border border-emerald-200 text-[10px] font-bold text-emerald-700 flex items-center gap-1">
                    <div class="i-fas-user-tie" /> Corretor OK
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="p-4 rounded-lg border border-slate-200 bg-white">
                <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                    <div class="i-fas-user text-blue-500" /> Cliente
                </h3>
                <div class="flex flex-col gap-1">
                    <span class="font-bold text-slate-700 text-sm">{{ visita?.cliente_obj?.nome || 'Não informado' }}</span>
                    <a v-if="visita?.cliente_obj?.telefone" :href="'tel:'+visita?.cliente_obj?.telefone" class="text-xs text-slate-500 hover:text-blue-600 transition-colors flex items-center gap-1.5 decoration-none">
                        <div class="i-fas-phone text-[10px]" /> {{ visita?.cliente_obj?.telefone }}
                    </a>
                    <a v-if="visita?.cliente_obj?.email" :href="'mailto:'+visita?.cliente_obj?.email" class="text-xs text-slate-500 hover:text-blue-600 transition-colors flex items-center gap-1.5 decoration-none">
                        <div class="i-fas-envelope text-[10px]" /> {{ visita?.cliente_obj?.email }}
                    </a>
                </div>
            </div>

            <div class="p-4 rounded-lg border border-slate-200 bg-white">
                <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                    <div class="i-fas-user-tie text-blue-500" /> Corretor Responsável
                </h3>
                <div class="flex flex-col gap-1">
                    <span class="font-bold text-slate-700 text-sm">{{ visita?.corretor_nome || 'Não atribuído' }}</span>
                    <span class="text-xs text-slate-400">Imobiliária</span>
                </div>
            </div>
        </div>

        <div>
            <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <div class="i-fas-home text-blue-500" /> Imóveis no Roteiro
            </h3>
            <div class="flex flex-col gap-3">
                <div v-for="imovel in visita?.imoveis_obj" :key="imovel.id" class="flex gap-3 p-3 rounded-lg border border-slate-100 bg-slate-50 hover:border-blue-200 transition-colors group">
                    <div class="w-10 h-10 rounded bg-white border border-slate-200 flex items-center justify-center shrink-0 text-slate-300">
                        <div class="i-fas-building" />
                    </div>
                    <div class="flex-1 min-w-0">
                        <div class="flex justify-between items-start">
                            <h4 class="text-sm font-bold text-slate-700 truncate pr-2">{{ imovel.titulo_anuncio || 'Imóvel sem título' }}</h4>
                            <span v-if="imovel.codigo_referencia" class="text-[10px] font-mono bg-white border border-slate-200 px-1.5 rounded text-slate-500">
                                {{ imovel.codigo_referencia }}
                            </span>
                        </div>
                        <p class="text-xs text-slate-500 truncate mt-0.5">
                            {{ imovel.logradouro }}, {{ imovel.numero }} - {{ imovel.bairro }}
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="visita?.observacoes">
            <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Observações</h3>
            <p class="text-sm text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-100 italic">
                "{{ visita.observacoes }}"
            </p>
        </div>

      </div>

      <div class="p-4 bg-slate-50 border-t border-slate-200 flex flex-wrap justify-end gap-3">
        
        <button 
            @click="$emit('close')"
            class="px-4 py-2 rounded-md text-sm font-medium text-slate-600 bg-white border border-slate-300 hover:bg-slate-50 transition-all cursor-pointer"
        >
            Fechar
        </button>

        <button 
            @click="abrirPDF"
            class="px-4 py-2 rounded-md text-sm font-medium text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 hover:text-blue-600 hover:border-blue-300 transition-all cursor-pointer flex items-center gap-2 shadow-sm"
        >
            <div class="i-fas-file-pdf text-red-500" /> Ficha de Visita
        </button>

        <button 
            v-if="!visita?.assinatura_corretor"
            @click="iniciarAssinatura('CORRETOR')"
            class="px-4 py-2 rounded-md text-sm font-medium text-white bg-slate-700 hover:bg-slate-800 transition-all cursor-pointer flex items-center gap-2 shadow-sm"
        >
            <div class="i-fas-pen-nib" /> Assinar como Corretor
        </button>

        <button 
            v-if="!visita?.assinatura_cliente"
            @click="iniciarAssinatura('CLIENTE')"
            class="px-4 py-2 rounded-md text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 transition-all cursor-pointer flex items-center gap-2 shadow-sm shadow-blue-200"
        >
            <div class="i-fas-file-signature" /> Coletar Assinatura do Cliente
        </button>

        <div v-if="visita?.assinatura_cliente && visita?.assinatura_corretor" class="flex items-center gap-2 px-4 py-2 bg-emerald-100 text-emerald-700 rounded-md font-bold text-sm border border-emerald-200 cursor-default">
            <div class="i-fas-check-double" /> Processo Concluído
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { format, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import apiClient from '@/services/api';

const props = defineProps<{
  show: boolean;
  visita: any;
}>();

const emit = defineEmits(['close', 'iniciar-visita']);

function formatarDataExtensa(data: string) {
    if(!data) return '-';
    try {
        return format(parseISO(data), "eeee, d 'de' MMMM 'às' HH:mm", { locale: ptBR });
    } catch { return data; }
}

function formatarData(data: string) {
    if(!data) return '-';
    try { return format(parseISO(data), 'dd/MM/yyyy HH:mm'); } catch { return '-'; }
}

function abrirPDF() {
    if(!props.visita?.id) return;
    const url = `${apiClient.defaults.baseURL}/v1/visitas/${props.visita.id}/pdf/`;
    window.open(url, '_blank');
}

function iniciarAssinatura(tipo: 'CORRETOR' | 'CLIENTE') {
    if(!props.visita) return;
    // Emite evento para o componente pai (VisitasView) abrir o modal de assinatura
    emit('iniciar-visita', {
        visitaId: props.visita.id,
        imoveisIds: props.visita.imoveis_obj?.map((i: any) => i.id) || [],
        tipo: tipo
    });
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.2s ease-out; }
.animate-slide-up { animation: slideUp 0.3s ease-out; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>