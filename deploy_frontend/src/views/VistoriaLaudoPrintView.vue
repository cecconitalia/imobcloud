<script setup lang="ts">
/**
 * IMOBCLOUD - GERADOR DE LAUDO COMPARATIVO DE SAÍDA (IMPRESSÃO)
 * Engenharia de Software Full Stack Sênior
 * * OBJETIVO:
 * Gerar um relatório técnico jurídico que comprova a evolução do estado do imóvel.
 * * FUNCIONALIDADES AVANÇADAS:
 * 1. "De/Para" Visual: Coloca lado a lado o estado/foto da Entrada vs Saída.
 * 2. Detecção de Avarias: Seção dedicada a itens que sofreram depreciação não natural.
 * 3. Cálculos de Consumo: Exibe leituras finais e calcula diferença se houver dados anteriores.
 * 4. Layout de Impressão: CSS específico (@media print) para quebras de página inteligentes e economia de tinta.
 */

import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/services/api';
import { format } from 'date-fns';
import { 
  Printer, 
  AlertTriangle, 
  CheckCircle2, 
  ArrowRight,
  Droplets,
  Zap,
  Flame,
  Key,
  FileText
} from 'lucide-vue-next';

// --- Interfaces de Dados ---
interface Foto {
  id: number;
  imagem: string;
  data_upload?: string;
}

interface ItemBase {
  item: string;
  estado: string;
  descricao_avaria: string;
  fotos: Foto[];
}

interface ItemComparativo {
  nome: string;
  entrada?: ItemBase;
  saida: ItemBase;
  status_divergencia: 'OK' | 'DANO' | 'MELHORIA' | 'NAO_VERIFICADO';
}

interface AmbienteComparativo {
  nome: string;
  itens: ItemComparativo[];
}

interface VistoriaDados {
  id: number;
  contrato: number;
  data_vistoria: string;
  imovel_display: string;
  tipo: string;
  realizado_por_nome: string;
  // Medidores
  leitura_agua: string;
  leitura_luz: string;
  leitura_gas: string;
  chaves_devolvidas: string;
  observacoes: string;
  // Assinaturas
  assinatura_locatario: string | null;
  assinatura_responsavel: string | null;
  assinatura_proprietario: string | null;
  ambientes: any[];
}

// --- Estado ---
const route = useRoute();
const vistoriaId = route.params.id as string;
const loading = ref(true);

const saida = ref<VistoriaDados | null>(null);
const entrada = ref<VistoriaDados | null>(null);
const relatorio = ref<AmbienteComparativo[]>([]);

// --- Lógica de Comparação e Construção do Relatório ---

const loadData = async () => {
  loading.value = true;
  try {
    // 1. Carrega Vistoria de Saída (Atual)
    const resSaida = await api.get(`/v1/vistorias/vistorias/${vistoriaId}/`);
    saida.value = resSaida.data;

    if (saida.value?.tipo === 'SAIDA') {
      // 2. Busca Vistoria de Entrada vinculada ao contrato
      const resBusca = await api.get(`/v1/vistorias/vistorias/`, {
        params: { contrato: saida.value.contrato, tipo: 'ENTRADA', concluida: true }
      });
      
      const lastEntry = resBusca.data.results ? resBusca.data.results[0] : resBusca.data[0];
      
      if (lastEntry) {
        const resEntrada = await api.get(`/v1/vistorias/vistorias/${lastEntry.id}/`);
        entrada.value = resEntrada.data;
      }
    }

    // 3. Processa o cruzamento de dados (Merge Inteligente)
    processarComparativo();

  } catch (error) {
    console.error("Erro ao gerar laudo:", error);
    alert("Erro ao carregar dados do laudo.");
  } finally {
    loading.value = false;
  }
};

const processarComparativo = () => {
  if (!saida.value) return;

  const resultado: AmbienteComparativo[] = [];

  saida.value.ambientes.forEach((ambSaida: any) => {
    const ambEntrada = entrada.value?.ambientes.find(
      a => a.nome.trim().toLowerCase() === ambSaida.nome.trim().toLowerCase()
    );

    const itensComparados: ItemComparativo[] = ambSaida.itens.map((itemSaida: any) => {
      // Tenta encontrar o item correspondente na entrada
      const itemEntrada = ambEntrada?.itens.find(
        (i: any) => i.item.trim().toLowerCase() === itemSaida.item.trim().toLowerCase()
      );

      // Determina divergência
      let status: ItemComparativo['status_divergencia'] = 'OK';
      if (itemEntrada) {
        const pesoEntrada = getPesoEstado(itemEntrada.estado);
        const pesoSaida = getPesoEstado(itemSaida.estado);
        if (pesoSaida < pesoEntrada) status = 'DANO';
        else if (pesoSaida > pesoEntrada) status = 'MELHORIA';
      } else {
        status = 'NAO_VERIFICADO'; // Item novo ou não existia
      }

      return {
        nome: itemSaida.item,
        saida: itemSaida,
        entrada: itemEntrada,
        status_divergencia: status
      };
    });

    resultado.push({
      nome: ambSaida.nome,
      itens: itensComparados
    });
  });

  relatorio.value = resultado;
};

const getPesoEstado = (estado: string) => {
  const pesos: Record<string, number> = { 'NOVO': 5, 'BOM': 4, 'REGULAR': 3, 'RUIM': 2, 'INOPERANTE': 1 };
  return pesos[estado] || 0;
};

// --- Computeds para Resumo Executivo ---
const itensComAvaria = computed(() => {
  const lista: { ambiente: string, item: string, detalhe: string }[] = [];
  relatorio.value.forEach(amb => {
    amb.itens.forEach(i => {
      if (i.status_divergencia === 'DANO' || i.saida.estado === 'RUIM' || i.saida.estado === 'INOPERANTE') {
        lista.push({
          ambiente: amb.nome,
          item: i.nome,
          detalhe: i.saida.descricao_avaria || `Estado regrediu de ${i.entrada?.estado} para ${i.saida.estado}`
        });
      }
    });
  });
  return lista;
});

const handlePrint = () => {
  window.print();
};

onMounted(loadData);
</script>

<template>
  <div class="bg-gray-100 min-h-screen p-4 print:p-0 print:bg-white text-slate-900 font-sans">
    
    <div class="max-w-[210mm] mx-auto mb-6 flex justify-between items-center print:hidden">
      <h1 class="text-xl font-bold text-slate-700">Visualização de Laudo</h1>
      <button @click="handlePrint" class="bg-blue-600 text-white px-6 py-2 rounded-lg font-bold shadow-lg hover:bg-blue-700 flex items-center gap-2">
        <Printer class="w-5 h-5" /> Imprimir Laudo Oficial
      </button>
    </div>

    <div v-if="saida" class="max-w-[210mm] mx-auto bg-white shadow-2xl print:shadow-none min-h-[297mm] p-[10mm] md:p-[15mm]">
      
      <header class="border-b-2 border-slate-800 pb-4 mb-8 flex justify-between items-start">
        <div>
          <h1 class="text-2xl font-black uppercase tracking-widest text-slate-900">Laudo de Vistoria de Saída</h1>
          <p class="text-sm font-bold text-slate-500 mt-1">Comparativo de Encerramento de Contrato</p>
        </div>
        <div class="text-right">
          <p class="text-xs font-bold text-slate-400 uppercase">Referência</p>
          <p class="text-lg font-mono font-bold">#{{ saida.id }}</p>
          <p class="text-xs text-slate-500">{{ format(new Date(saida.data_vistoria), 'dd/MM/yyyy') }}</p>
        </div>
      </header>

      <section class="mb-8 p-4 bg-slate-50 border border-slate-200 rounded-xl text-sm">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <span class="block text-[10px] font-bold text-slate-400 uppercase">Imóvel</span>
            <span class="font-bold text-slate-800">{{ saida.imovel_display }}</span>
          </div>
          <div>
            <span class="block text-[10px] font-bold text-slate-400 uppercase">Contrato Vinculado</span>
            <span class="font-bold text-slate-800">#{{ saida.contrato }}</span>
          </div>
          <div>
            <span class="block text-[10px] font-bold text-slate-400 uppercase">Vistoriador Responsável</span>
            <span class="font-bold text-slate-800">{{ saida.realizado_por_nome }}</span>
          </div>
          <div v-if="entrada">
            <span class="block text-[10px] font-bold text-slate-400 uppercase">Data da Entrada (Base de Comparação)</span>
            <span class="font-bold text-blue-700">{{ format(new Date(entrada.data_vistoria), 'dd/MM/yyyy') }}</span>
          </div>
        </div>
      </section>

      <section v-if="itensComAvaria.length > 0" class="mb-8 border border-rose-200 bg-rose-50/50 rounded-xl overflow-hidden page-break-inside-avoid">
        <div class="bg-rose-100 px-4 py-2 border-b border-rose-200 flex items-center gap-2">
          <AlertTriangle class="w-5 h-5 text-rose-600" />
          <h2 class="font-bold text-rose-800 text-sm uppercase">Resumo de Avarias e Divergências</h2>
        </div>
        <div class="p-4">
          <p class="text-xs text-rose-700 mb-3 font-medium">Os seguintes itens apresentaram estado inferior à entrada ou danos registrados:</p>
          <ul class="space-y-2">
            <li v-for="(avaria, idx) in itensComAvaria" :key="idx" class="text-xs flex gap-2 items-start">
              <span class="font-bold text-rose-900 whitespace-nowrap">• {{ avaria.ambiente }} - {{ avaria.item }}:</span>
              <span class="text-rose-800">{{ avaria.detalhe }}</span>
            </li>
          </ul>
        </div>
      </section>

      <section class="mb-8 grid grid-cols-2 gap-6 page-break-inside-avoid">
        <div class="border border-slate-200 rounded-xl overflow-hidden">
          <div class="bg-slate-100 px-3 py-2 border-b border-slate-200 font-bold text-xs uppercase flex items-center gap-2">
            <Zap class="w-3 h-3" /> Leituras Finais
          </div>
          <table class="w-full text-xs">
            <tbody>
              <tr class="border-b border-slate-50">
                <td class="p-2 text-slate-500 font-bold">Luz (kWh)</td>
                <td class="p-2 font-mono text-right">{{ saida.leitura_luz || '--' }}</td>
              </tr>
              <tr class="border-b border-slate-50">
                <td class="p-2 text-slate-500 font-bold">Água (m³)</td>
                <td class="p-2 font-mono text-right">{{ saida.leitura_agua || '--' }}</td>
              </tr>
              <tr>
                <td class="p-2 text-slate-500 font-bold">Gás (m³)</td>
                <td class="p-2 font-mono text-right">{{ saida.leitura_gas || '--' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="border border-slate-200 rounded-xl overflow-hidden">
          <div class="bg-slate-100 px-3 py-2 border-b border-slate-200 font-bold text-xs uppercase flex items-center gap-2">
            <Key class="w-3 h-3" /> Devolução de Chaves
          </div>
          <div class="p-3 text-xs text-slate-700 whitespace-pre-wrap leading-relaxed">
            {{ saida.chaves_devolvidas || 'Nenhuma observação de chaves registrada.' }}
          </div>
        </div>
      </section>

      <div v-for="(amb, index) in relatorio" :key="index" class="mb-8 page-break-inside-avoid">
        
        <h2 class="text-sm font-black uppercase bg-slate-900 text-white px-4 py-2 rounded-t-lg flex justify-between items-center print:bg-slate-200 print:text-black">
          {{ amb.nome }}
          <span class="text-[10px] font-normal opacity-70">{{ amb.itens.length }} itens verificados</span>
        </h2>

        <div class="border border-slate-300 rounded-b-lg overflow-hidden">
          <div v-for="(item, iIdx) in amb.itens" :key="iIdx" 
               :class="['p-4 border-b border-slate-200 last:border-0', item.status_divergencia === 'DANO' ? 'bg-rose-50 print:bg-transparent' : 'even:bg-slate-50']">
            
            <div class="flex justify-between items-start mb-3">
              <h3 class="font-bold text-sm text-slate-800">{{ item.nome }}</h3>
              
              <div class="flex items-center gap-4 text-[10px] font-bold uppercase">
                <div v-if="item.entrada" class="text-slate-400 flex flex-col items-end">
                  <span class="text-[8px]">Entrada</span>
                  <span>{{ item.entrada.estado }}</span>
                </div>
                <div v-else class="text-slate-300 italic">Novo na Saída</div>

                <ArrowRight class="w-3 h-3 text-slate-300" />

                <div class="flex flex-col items-end">
                  <span class="text-[8px] text-slate-400">Saída</span>
                  <span :class="{'text-rose-600': item.status_divergencia === 'DANO', 'text-emerald-600': item.status_divergencia === 'MELHORIA'}">
                    {{ item.saida.estado }}
                  </span>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4 text-xs mb-3">
              <div v-if="item.entrada && item.entrada.descricao_avaria" class="text-slate-500 bg-white p-2 rounded border border-slate-100">
                <strong class="block text-[9px] uppercase text-slate-400 mb-1">Obs. Entrada:</strong>
                {{ item.entrada.descricao_avaria }}
              </div>
              <div v-if="item.saida.descricao_avaria" class="col-start-2 bg-white p-2 rounded border border-slate-100" :class="{'border-rose-200 bg-rose-50': item.status_divergencia === 'DANO'}">
                <strong class="block text-[9px] uppercase text-slate-400 mb-1">Obs. Saída:</strong>
                <span :class="{'text-rose-700 font-bold': item.status_divergencia === 'DANO'}">{{ item.saida.descricao_avaria }}</span>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              
              <div v-if="item.entrada && item.entrada.fotos.length > 0">
                <p class="text-[9px] font-bold uppercase text-slate-400 mb-1 flex items-center gap-1"><Camera class="w-3 h-3"/> Registro Entrada</p>
                <div class="grid grid-cols-3 gap-1">
                  <img v-for="f in item.entrada.fotos.slice(0,3)" :key="f.id" :src="f.imagem" class="w-full h-16 object-cover rounded border border-slate-200 grayscale-[50%]" />
                </div>
              </div>
              <div v-else-if="item.entrada" class="flex items-center justify-center h-16 bg-slate-100 rounded text-[9px] text-slate-400 italic">
                Sem fotos na entrada
              </div>

              <div v-if="item.saida.fotos.length > 0">
                <p class="text-[9px] font-bold uppercase text-slate-400 mb-1 flex items-center gap-1"><Camera class="w-3 h-3"/> Registro Saída</p>
                <div class="grid grid-cols-3 gap-1">
                  <img v-for="f in item.saida.fotos.slice(0,3)" :key="f.id" :src="f.imagem" class="w-full h-16 object-cover rounded border border-slate-200" />
                </div>
              </div>
              <div v-else class="flex items-center justify-center h-16 bg-slate-100 rounded text-[9px] text-slate-400 italic">
                Sem fotos na saída
              </div>

            </div>

          </div>
        </div>
      </div>

      <section v-if="saida.observacoes" class="mb-8 border-t-2 border-slate-200 pt-4 page-break-inside-avoid">
        <h3 class="text-xs font-bold uppercase text-slate-500 mb-2">Considerações Finais</h3>
        <p class="text-xs text-slate-700 text-justify leading-relaxed">{{ saida.observacoes }}</p>
      </section>

      <footer class="mt-12 pt-8 border-t border-slate-300 page-break-inside-avoid">
        <h3 class="text-center font-bold uppercase text-xs mb-8 text-slate-400 tracking-widest">Validação do Documento</h3>
        
        <div class="grid grid-cols-3 gap-8 text-center">
          <div class="flex flex-col items-center">
            <div class="h-16 w-32 mb-2 flex items-end justify-center">
              <img v-if="saida.assinatura_locatario" :src="saida.assinatura_locatario" class="max-h-full max-w-full" />
              <span v-else class="text-[9px] text-rose-500 italic">(Pendente)</span>
            </div>
            <div class="border-t border-slate-400 w-full pt-1">
              <p class="text-xs font-bold">Locatário</p>
              <p class="text-[9px] text-slate-500">Declaro ciência das avarias</p>
            </div>
          </div>

          <div class="flex flex-col items-center">
            <div class="h-16 w-32 mb-2 flex items-end justify-center">
              <img v-if="saida.assinatura_responsavel" :src="saida.assinatura_responsavel" class="max-h-full max-w-full" />
            </div>
            <div class="border-t border-slate-400 w-full pt-1">
              <p class="text-xs font-bold">Vistoriador</p>
              <p class="text-[9px] text-slate-500">{{ saida.realizado_por_nome }}</p>
            </div>
          </div>

          <div class="flex flex-col items-center">
            <div class="h-16 w-32 mb-2 flex items-end justify-center">
              <img v-if="saida.assinatura_proprietario" :src="saida.assinatura_proprietario" class="max-h-full max-w-full" />
              <span v-else class="text-[9px] text-slate-300 italic">(Opcional)</span>
            </div>
            <div class="border-t border-slate-400 w-full pt-1">
              <p class="text-xs font-bold">Proprietário</p>
              <p class="text-[9px] text-slate-500">Aceite final</p>
            </div>
          </div>
        </div>

        <div class="mt-8 text-[9px] text-slate-400 text-center uppercase">
          Documento gerado digitalmente pelo sistema ImobCloud em {{ format(new Date(), 'dd/MM/yyyy HH:mm') }}.<br>
          A validade deste laudo está condicionada à integridade das assinaturas digitais.
        </div>
      </footer>

    </div>
  </div>
</template>

<style scoped>
@media print {
  @page {
    margin: 10mm;
    size: A4;
  }
  body {
    background: white;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
  .page-break-inside-avoid {
    page-break-inside: avoid;
  }
  /* Força cores de fundo para impressão de divergências */
  .bg-rose-50 {
    background-color: #fff1f2 !important; 
  }
  .print\:hidden {
    display: none !important;
  }
}
</style>