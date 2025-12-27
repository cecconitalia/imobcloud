<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Configurações</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Integrações</span>
           </nav>
           
           <h1>Central de Integrações</h1>
        </div>
        
        <div class="actions-area">
            <button class="btn-icon-thin" @click="refreshAll" title="Atualizar Status">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoadingBancos || isCheckingSocial }"></i>
            </button>
        </div>
      </div>
    </header>

    <div class="kpi-grid">
      <div class="kpi-card blue">
        <div class="kpi-content">
          <span class="kpi-value">{{ bancos.length }}</span>
          <span class="kpi-label">Bancos Configurados</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-university"></i></div>
      </div>

      <div class="kpi-card green" v-if="facebookStatus.connected">
        <div class="kpi-content">
          <span class="kpi-value">Ativo</span>
          <span class="kpi-label">Meta (FB/IG)</span>
        </div>
        <div class="kpi-icon"><i class="fab fa-facebook-f"></i></div>
      </div>
      <div class="kpi-card orange" v-else>
        <div class="kpi-content">
          <span class="kpi-value">Pendente</span>
          <span class="kpi-label">Meta (FB/IG)</span>
        </div>
        <div class="kpi-icon"><i class="fab fa-facebook-f"></i></div>
      </div>

      <div class="kpi-card purple">
        <div class="kpi-content">
          <span class="kpi-value">Ativo</span>
          <span class="kpi-label">Google Calendar</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-calendar-alt"></i></div>
      </div>

      <div class="kpi-card blue">
        <div class="kpi-content">
          <span class="kpi-value">Integrado</span>
          <span class="kpi-label">IA Engine</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-robot"></i></div>
      </div>
    </div>

    <section class="integration-section">
      <div class="section-header">
        <h2><i class="fas fa-share-nodes"></i> Redes Sociais</h2>
        <p>Conecte suas contas para automação de publicações de imóveis.</p>
      </div>

      <div class="social-cards-grid">
        <div class="social-card">
          <div class="social-header">
            <div class="social-icon fb"><i class="fab fa-facebook"></i></div>
            <div class="social-info">
              <h3>Meta (Facebook & Instagram)</h3>
              <span :class="['status-badge', facebookStatus.connected ? 'active' : 'inactive']">
                {{ facebookStatus.connected ? 'Conectado' : 'Desconectado' }}
              </span>
            </div>
          </div>
          <div class="social-body">
            <p v-if="facebookStatus.connected">
              Conectado como: <strong>{{ facebookStatus.pageName }}</strong>
            </p>
            <p v-else class="text-muted">Conecte sua página para publicar imóveis automaticamente no Feed e Stories.</p>
          </div>
          <div class="social-footer">
            <button v-if="!facebookStatus.connected" @click="conectarFacebook" class="btn-primary-thin w-full">
              <i class="fab fa-facebook"></i> Conectar conta Meta
            </button>
            <button v-else @click="desconectarFacebook" class="btn-ghost-danger w-full">
              Desconectar
            </button>
          </div>
        </div>

        <div class="social-card">
          <div class="social-header">
            <div class="social-icon google"><i class="fab fa-google"></i></div>
            <div class="social-info">
              <h3>Google Calendar</h3>
              <span class="status-badge active">Integrado</span>
            </div>
          </div>
          <div class="social-body">
            <p>Sincronize visitas e tarefas do funil diretamente na sua agenda Google.</p>
          </div>
          <div class="social-footer">
            <button class="btn-primary-thin w-full" disabled>
              <i class="fas fa-check"></i> Configurado
            </button>
          </div>
        </div>
      </div>
    </section>

    <section class="integration-section mt-10">
      <div class="section-header">
        <div class="header-with-action">
            <div>
                <h2><i class="fas fa-piggy-bank"></i> Bancos & APIs Financeiras</h2>
                <p>Configure as credenciais para emissão automática de boletos e baixa via API.</p>
            </div>
            <router-link :to="{ name: 'configuracao-banco-nova' }" class="btn-primary-thin">
              <i class="fas fa-plus"></i> Adicionar Banco
            </router-link>
        </div>
      </div>

      <div class="report-main-wrapper">
        <div v-if="isLoadingBancos" class="loading-state">
          <div class="spinner"></div>
          <p>Consultando configurações bancárias...</p>
        </div>

        <div v-else-if="bancos.length === 0" class="empty-state">
          <i class="fas fa-university empty-icon"></i>
          <p>Nenhum banco configurado até o momento.</p>
        </div>

        <div v-else class="report-scroll-viewport">
          <table class="report-table">
            <thead>
              <tr>
                <th width="25%">Banco / Instituição</th>
                <th width="15%">Ambiente</th>
                <th width="30%">Credenciais</th>
                <th width="15%" class="text-center">Status API</th>
                <th width="15%" class="text-right">Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="banco in bancos" :key="banco.id">
                <td>
                  <div class="banco-cell">
                    <div class="banco-logo">
                        <i class="fas fa-building-columns"></i>
                    </div>
                    <div class="banco-info">
                        <span class="banco-nome">{{ banco.nome_banco || 'Banco API' }}</span>
                        <span class="banco-sub">Ag: {{ banco.agencia }} / Cc: {{ banco.conta }}</span>
                    </div>
                  </div>
                </td>

                <td>
                    <span :class="['env-badge', banco.producao ? 'prod' : 'sandbox']">
                        {{ banco.producao ? 'PRODUÇÃO' : 'TESTE/SANDBOX' }}
                    </span>
                </td>

                <td>
                    <div class="credentials-info">
                        <span :title="banco.client_id">ID: {{ banco.client_id.substring(0,12) }}...</span>
                        <span class="cert-status" v-if="banco.certificado_file">
                            <i class="fas fa-certificate text-green"></i> Certificado OK
                        </span>
                    </div>
                </td>

                <td class="text-center">
                    <span class="status-pill status-green">Ativo</span>
                </td>

                <td class="text-right">
                    <div class="actions-flex">
                        <router-link :to="{ name: 'configuracao-banco-editar', params: { id: banco.id } }" class="btn-action primary" title="Editar">
                            <i class="fas fa-pen"></i>
                        </router-link>
                        <button @click="removerBanco(banco.id)" class="btn-action danger" title="Excluir">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
import { useToast } from 'vue-toast-notification';

const toast = useToast();
const bancos = ref<any[]>([]);
const isLoadingBancos = ref(true);
const isCheckingSocial = ref(false);

const facebookStatus = ref({
  connected: false,
  pageName: '',
});

const refreshAll = () => {
    fetchBancos();
    checkSocialStatus();
};

const fetchBancos = async () => {
  isLoadingBancos.value = true;
  try {
    const response = await apiClient.get('/v1/boletos/configuracoes-banco/');
    bancos.value = response.data.results || response.data;
  } catch (error) {
    console.error('Erro ao buscar bancos:', error);
  } finally {
    isLoadingBancos.value = false;
  }
};

const checkSocialStatus = async () => {
    // Simulação ou chamada real ao backend
    isCheckingSocial.value = true;
    try {
        const response = await apiClient.get('/v1/publicacoes/status-conexoes/');
        facebookStatus.value = response.data.facebook;
    } catch (e) {
        console.warn("Módulo de publicações não configurado.");
    } finally {
        isCheckingSocial.value = false;
    }
};

const removerBanco = async (id: number) => {
    if(!confirm("Tem certeza que deseja remover esta configuração bancária?")) return;
    try {
        await apiClient.delete(`/v1/boletos/configuracoes-banco/${id}/`);
        toast.success("Configuração removida.");
        fetchBancos();
    } catch (e) {
        toast.error("Erro ao remover configuração.");
    }
};

const conectarFacebook = () => {
    // Lógica de redirecionamento para o fluxo OAuth do Facebook
    toast.info("Redirecionando para o Facebook...");
    window.location.href = `${apiClient.defaults.baseURL}/v1/publicacoes/facebook/login/`;
};

const desconectarFacebook = async () => {
    if(!confirm("Deseja realmente desconectar sua conta Meta?")) return;
    try {
        await apiClient.post('/v1/publicacoes/facebook/logout/');
        facebookStatus.value.connected = false;
        toast.success("Conta desconectada.");
    } catch (e) {
        toast.error("Erro ao desconectar.");
    }
};

onMounted(refreshAll);
</script>

<style scoped>
/* CONFIGURAÇÃO GERAL (Page Scroll) */
.page-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #fcfcfc;
  font-family: 'Inter', sans-serif;
  padding: 1.5rem 2.5rem;
  box-sizing: border-box;
}

/* HEADER */
.page-header { margin-bottom: 2rem; flex-shrink: 0; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }
.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.actions-area { display: flex; gap: 0.75rem; }

/* Botões Estilo Thin */
.btn-primary-thin {
  background: #2563eb; color: white; border: none; padding: 0.5rem 1.2rem;
  border-radius: 6px; font-weight: 400; font-size: 0.85rem; cursor: pointer; text-decoration: none;
  display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s;
}
.btn-primary-thin:hover { background: #1d4ed8; transform: translateY(-1px); }
.btn-icon-thin {
  background: white; border: 1px solid #e2e8f0; color: #64748b; width: 34px; height: 34px;
  border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center;
}

/* KPI GRID */
.kpi-grid { 
    display: grid; grid-template-columns: repeat(4, 1fr); 
    gap: 1.25rem; margin-bottom: 3rem; flex-shrink: 0;
}
.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); position: relative; overflow: hidden;
}
.kpi-value { font-size: 1.5rem; font-weight: 300; color: #111; }
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; }
.kpi-icon { font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; }

/* SECTIONS */
.integration-section { margin-bottom: 2rem; }
.section-header { margin-bottom: 1.5rem; }
.section-header h2 { font-size: 1.2rem; color: #1e293b; font-weight: 700; display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.25rem; }
.section-header p { font-size: 0.9rem; color: #64748b; }
.header-with-action { display: flex; justify-content: space-between; align-items: flex-end; }

/* SOCIAL CARDS */
.social-cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem; }
.social-card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.02); }
.social-header { display: flex; gap: 1rem; align-items: center; }
.social-icon { width: 48px; height: 48px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; color: white; }
.social-icon.fb { background: #1877f2; }
.social-icon.google { background: #ea4335; }
.social-info h3 { font-size: 1rem; font-weight: 700; color: #1e293b; margin: 0; }
.status-badge { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; padding: 2px 6px; border-radius: 4px; }
.status-badge.active { background: #dcfce7; color: #15803d; }
.status-badge.inactive { background: #f1f5f9; color: #64748b; }
.social-body p { font-size: 0.85rem; color: #475569; line-height: 1.5; margin: 0; }
.social-footer { margin-top: auto; padding-top: 1rem; border-top: 1px solid #f1f5f9; }
.btn-ghost-danger { background: #fef2f2; color: #dc2626; border: none; padding: 0.5rem; border-radius: 6px; font-size: 0.8rem; cursor: pointer; font-weight: 500; }

/* TABELA DE BANCOS */
.report-main-wrapper { width: 100%; background: white; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02); overflow: hidden; }
.report-table { width: 100%; border-collapse: collapse; }
.report-table th { background: #f8fafc; padding: 0.8rem 1.2rem; text-align: left; font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; }
.report-table td { padding: 1rem 1.2rem; border-bottom: 1px solid #f1f5f9; font-size: 0.85rem; color: #334155; vertical-align: middle; }

.banco-cell { display: flex; align-items: center; gap: 1rem; }
.banco-logo { width: 36px; height: 36px; background: #f1f5f9; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #64748b; }
.banco-nome { display: block; font-weight: 600; color: #1e293b; }
.banco-sub { font-size: 0.75rem; color: #94a3b8; }

.env-badge { font-size: 0.65rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; }
.env-badge.prod { background: #fef9c3; color: #854d0e; }
.env-badge.sandbox { background: #e0f2fe; color: #0369a1; }

.credentials-info { display: flex; flex-direction: column; gap: 2px; font-size: 0.75rem; color: #64748b; font-family: monospace; }
.cert-status { font-weight: 600; font-family: 'Inter', sans-serif; }

.status-pill { display: inline-block; padding: 2px 10px; border-radius: 99px; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; }
.status-green { background: #dcfce7; color: #15803d; }

.actions-flex { display: flex; gap: 0.5rem; justify-content: flex-end; }
.btn-action { width: 32px; height: 32px; border: none; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.btn-action.primary { background-color: #eff6ff; color: #2563eb; }
.btn-action.danger { background-color: #fff1f2; color: #e11d48; }

/* UTILS */
.w-full { width: 100%; justify-content: center; }
.mt-10 { margin-top: 2.5rem; }
.text-green { color: #10b981; }

.loading-state, .empty-state { text-align: center; padding: 4rem 2rem; color: #94a3b8; }
.spinner { border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%; width: 32px; height: 32px; animation: spin 1s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }

@media (max-width: 1024px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .social-cards-grid { grid-template-columns: 1fr; }
}
</style>