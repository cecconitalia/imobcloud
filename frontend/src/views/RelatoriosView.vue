<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// Lista estática de relatórios disponíveis no sistema
// Isso previne o erro de 'map' undefined em chamadas de API falhas
const relatorios = ref([
  {
    id: 'autorizacoes',
    titulo: 'Status de Autorizações',
    descricao: 'Monitore vencimentos de autorizações de venda e aluguel. Identifique contratos expirando.',
    icon: 'i-mdi-file-document-alert',
    rota: '/relatorios/autorizacoes',
    cor_texto: 'text-amber-600',
    cor_fundo: 'bg-amber-50 dark:bg-amber-900/20'
  },
  {
    id: 'financeiro_geral',
    titulo: 'DRE & Financeiro',
    descricao: 'Visão completa de receitas, despesas e lucro líquido do período.',
    icon: 'i-mdi-finance',
    rota: '/financeiro/dre',
    cor_texto: 'text-emerald-600',
    cor_fundo: 'bg-emerald-50 dark:bg-emerald-900/20'
  },
  {
    id: 'inadimplencia',
    titulo: 'Contas a Receber',
    descricao: 'Relatório detalhado de boletos pendentes e inadimplência de locatários.',
    icon: 'i-mdi-account-cash',
    rota: '/financeiro/contas-receber',
    cor_texto: 'text-rose-600',
    cor_fundo: 'bg-rose-50 dark:bg-rose-900/20'
  },
  {
    id: 'vistorias',
    titulo: 'Vistorias Realizadas',
    descricao: 'Histórico de vistorias de entrada e saída, com status e fotos.',
    icon: 'i-mdi-clipboard-check-outline',
    rota: '/vistorias',
    cor_texto: 'text-blue-600',
    cor_fundo: 'bg-blue-50 dark:bg-blue-900/20'
  },
  {
    id: 'captacao',
    titulo: 'Desempenho de Captação',
    descricao: 'Análise de novos imóveis cadastrados e performance de corretores.',
    icon: 'i-mdi-home-analytics',
    rota: '/imoveis',
    cor_texto: 'text-purple-600',
    cor_fundo: 'bg-purple-50 dark:bg-purple-900/20'
  },
  {
    id: 'atendimentos',
    titulo: 'Funil de Vendas',
    descricao: 'Acompanhe leads, oportunidades e conversão em tempo real.',
    icon: 'i-mdi-filter-outline',
    rota: '/funil-vendas',
    cor_texto: 'text-indigo-600',
    cor_fundo: 'bg-indigo-50 dark:bg-indigo-900/20'
  }
]);

const abrirRelatorio = (rota: string) => {
  router.push(rota);
};
</script>

<template>
  <div class="p-6 md:p-10 max-w-7xl mx-auto min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
    
    <header class="mb-10 animate-fade-in-down">
      <h1 class="text-3xl font-bold text-gray-800 dark:text-gray-100 flex items-center gap-3">
        <div class="p-2.5 rounded-xl bg-blue-600 text-white shadow-lg shadow-blue-600/20">
          <div class="i-mdi-chart-box text-2xl"></div>
        </div>
        Central de Relatórios
      </h1>
      <p class="text-gray-500 dark:text-gray-400 mt-2 ml-16 text-lg">
        Inteligência de dados para tomada de decisão estratégica.
      </p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-fade-in-up">
      <div 
        v-for="item in relatorios" 
        :key="item.id"
        @click="abrirRelatorio(item.rota)"
        class="group bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-xl relative overflow-hidden"
      >
        <div class="absolute -top-4 -right-4 opacity-5 group-hover:opacity-10 transition-opacity rotate-12">
           <div :class="[item.icon, 'text-9xl', item.cor_texto]"></div>
        </div>

        <div class="flex items-start gap-5 relative z-10">
          <div :class="['w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-inner', item.cor_fundo, item.cor_texto]">
            <div :class="[item.icon, 'text-3xl']"></div>
          </div>
          
          <div class="flex-1">
            <h3 class="font-bold text-xl text-gray-800 dark:text-gray-100 mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
              {{ item.titulo }}
            </h3>
            <p class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
              {{ item.descricao }}
            </p>
          </div>
        </div>

        <div class="mt-6 flex items-center justify-end">
          <span class="text-xs font-bold uppercase tracking-wider text-gray-400 group-hover:text-blue-600 transition-colors flex items-center gap-1">
            Visualizar
            <div class="i-mdi-arrow-right transition-transform group-hover:translate-x-1"></div>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in-down {
  animation: fadeInDown 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.animate-fade-in-up {
  animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
  animation-delay: 0.1s;
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>