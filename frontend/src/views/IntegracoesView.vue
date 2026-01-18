<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Gestão</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Integrações</span>
           </nav>
           <h1>Central de Conectividade</h1>
        </div>
        
        <div class="actions-area">
            <button class="btn-icon-thin" @click="fetchStatus" title="Atualizar Status">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            </button>
        </div>
      </div>
    </header>

    <div class="integration-grid">
        
        <div class="card integration-card">
            <div class="card-status-bar" :class="statusGoogle ? 'bg-green' : 'bg-gray'"></div>
            <div class="card-content">
                <div class="icon-wrapper google">
                    <i class="fab fa-google"></i>
                </div>
                <div class="info-wrapper">
                    <h3>Google Calendar</h3>
                    <p>Sincronize tarefas e visitas do CRM com sua agenda pessoal.</p>
                    
                    <div v-if="statusGoogle" class="status-badge active">
                        <i class="fas fa-check-circle"></i> Conectado
                    </div>
                    <div v-else class="status-badge inactive">
                        <i class="fas fa-times-circle"></i> Desconectado
                    </div>
                </div>
            </div>
            <div class="card-actions">
                <button v-if="!statusGoogle" @click="connectGoogle" class="btn-primary-thin full">
                    Conectar Conta
                </button>
                <button v-else @click="disconnectGoogle" class="btn-danger-thin full">
                    Desconectar
                </button>
            </div>
        </div>

    </div>

    <div class="info-footer">
        <p><i class="fas fa-info-circle"></i> Outras integrações (Redes Sociais, IA, Bancos) são gerenciadas exclusivamente pelo painel administrativo.</p>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import { useAuthStore } from '@/stores/auth';
import { useToast } from 'vue-toast-notification';

const toast = useToast();
const authStore = useAuthStore();
const isLoading = ref(false);
const statusGoogle = ref(false);

// --- BUSCAR STATUS ---
const fetchStatus = async () => {
    isLoading.value = true;
    try {
        // Verifica se o usuário tem o token do Google salvo
        const userRes = await api.get('/v1/core/usuarios/me/');
        statusGoogle.value = !!userRes.data.google_calendar_token;
    } catch (error) {
        console.error("Erro ao atualizar status:", error);
        toast.error("Não foi possível verificar o status da integração.");
    } finally {
        isLoading.value = false;
    }
};

// --- AÇÕES ---
const connectGoogle = () => {
    const token = authStore.token || localStorage.getItem('authToken');
    
    let baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
    
    // Remove barra final se houver
    if (baseUrl.endsWith('/')) {
        baseUrl = baseUrl.slice(0, -1);
    }
    
    // Remove /api do final se existir (para evitar duplicação na montagem)
    if (baseUrl.endsWith('/api')) {
        baseUrl = baseUrl.slice(0, -4);
    }

    // Monta a URL correta apontando para o backend
    const targetUrl = `${baseUrl}/api/v1/google-calendar-auth/?token=${token}`;
    
    console.log("Redirecionando para:", targetUrl);
    window.location.href = targetUrl;
};

const disconnectGoogle = async () => {
    if(!confirm("Deseja realmente desconectar o Google Calendar?")) return;
    
    try {
        await api.post('/v1/core/usuarios/disconnect-google/'); 
        statusGoogle.value = false;
        toast.success("Desconectado com sucesso.");
    } catch (e) {
        toast.error("Erro ao desconectar. Tente novamente.");
    }
};

onMounted(() => {
    fetchStatus();
});
</script>

<style scoped>
/* CONFIGURAÇÃO GERAL */
.page-container {
  min-height: 100vh;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
}

/* HEADER */
.page-header { margin-bottom: 2rem; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }
.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.actions-area { display: flex; gap: 0.75rem; }

/* GRID DE CARDS */
.integration-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); /* Responsivo mas limita largura */
    gap: 1.5rem;
    max-width: 1000px; /* Limita largura total para não ficar esticado se tiver só 1 card */
}

/* CARD DESIGN */
.integration-card {
    background: white; border-radius: 8px; border: 1px solid #e5e7eb;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    display: flex; flex-direction: column; overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.integration-card:hover { transform: translateY(-2px); box-shadow: 0 8px 16px rgba(0,0,0,0.06); }

.card-status-bar { height: 4px; width: 100%; }
.bg-green { background-color: #10b981; }
.bg-gray { background-color: #e5e7eb; }

.card-content { padding: 1.5rem; flex: 1; display: flex; align-items: flex-start; gap: 1rem; }

.icon-wrapper {
    width: 48px; height: 48px; border-radius: 10px; display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem; flex-shrink: 0;
}
.icon-wrapper.google { background-color: #fff2f2; color: #db4437; }

.info-wrapper h3 { margin: 0 0 0.5rem 0; font-size: 1rem; font-weight: 600; color: #1f2937; }
.info-wrapper p { margin: 0 0 1rem 0; font-size: 0.85rem; color: #6b7280; line-height: 1.4; }

.status-badge {
    display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 99px;
    font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em;
}
.status-badge.active { background-color: #d1fae5; color: #065f46; }
.status-badge.inactive { background-color: #f3f4f6; color: #6b7280; }

.card-actions {
    padding: 1rem 1.5rem; background-color: #f9fafb; border-top: 1px solid #f3f4f6;
}

/* BOTÕES */
.btn-primary-thin {
  background: #2563eb; color: white; border: none; padding: 0.5rem 1.2rem;
  border-radius: 6px; font-weight: 500; font-size: 0.85rem; cursor: pointer; text-decoration: none;
  display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem; transition: all 0.2s;
}
.btn-primary-thin:hover { background: #1d4ed8; }
.btn-primary-thin.full { width: 100%; }

.btn-danger-thin {
  background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; padding: 0.5rem 1.2rem;
  border-radius: 6px; font-weight: 500; font-size: 0.85rem; cursor: pointer;
  width: 100%; transition: all 0.2s;
}
.btn-danger-thin:hover { background: #fee2e2; border-color: #fca5a5; }

.btn-icon-thin {
  background: white; border: 1px solid #e2e8f0; color: #64748b; width: 32px; height: 32px;
  border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; font-size: 0.8rem;
}
.btn-icon-thin:hover { border-color: #cbd5e1; color: #2563eb; background: #f8fafc; }

/* INFO FOOTER */
.info-footer {
    margin-top: 2rem;
    padding: 1rem;
    background-color: #f8fafc;
    border: 1px dashed #cbd5e1;
    border-radius: 6px;
    color: #64748b;
    font-size: 0.8rem;
    display: flex;
    align-items: center;
}
.info-footer i { margin-right: 8px; color: #94a3b8; font-size: 1rem; }

@media (max-width: 768px) {
    .page-container { padding: 1rem; }
    .header-main { flex-direction: column; align-items: flex-start; gap: 1rem; }
    .btn-primary-thin { width: 100%; }
}
</style>