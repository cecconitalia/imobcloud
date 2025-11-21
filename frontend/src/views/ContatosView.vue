<template>
  <div class="page-container">
    
    <div class="header-bar">
        <h2 class="page-subtitle">Contatos de Leads Recebidos pelo Site</h2>
    </div>

    <div class="search-and-filter-bar">
      <input 
        type="text" 
        v-model="filtro" 
        placeholder="Buscar por nome, email ou imóvel..." 
        class="search-input"
      />
      
      <div class="filter-group">
        <label for="status">Status:</label>
        <select id="status" disabled>
          <option value="">Abertos (Padrão)</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="tipo">Tipo:</label>
        <select id="tipo" disabled>
          <option value="">Leads (Padrão)</option>
        </select>
      </div>

      <div class="btn-add">
        <i class="fas fa-inbox"></i> <span class="mobile-hide">{{ contatos.length }} Pendentes</span>
      </div>
    </div>

    <div v-if="isLoading" class="loading-message card">
      <div class="spinner"></div>
      A carregar contatos...
    </div>
    <div v-else-if="error" class="error-message card">{{ error }}</div>
    
    <div v-else-if="contatos.length > 0" class="contatos-grid">
      <div 
        v-for="contato in filteredContatos" 
        :key="contato.id" 
        class="contato-card status-rascunho"
      >
        <div class="card-top-bar">
           <div class="badges-left">
               <span class="contrato-id">#{{ contato.id }}</span>
               <span class="tipo-badge tipo-lead">
                  Lead (Site)
               </span>
           </div>
           <div class="badges-right">
               <span class="status-pill status-rascunho">
                  <i class="fas fa-star"></i> NOVO
               </span>
           </div>
        </div>
        
        <div class="card-body">
          <div class="imovel-section">
             <h4 class="imovel-title" :title="contato.nome">
                <i class="fas fa-user-circle"></i> {{ contato.nome }}
             </h4>
             <p class="imovel-address">
                <i class="fas fa-at text-muted"></i> {{ contato.email }}
                <span v-if="contato.telefone" class="ml-10"> 
                    <i class="fas fa-phone text-muted"></i> {{ contato.telefone }}
                </span>
             </p>
             <p class="imovel-address mt-5">
                <i class="fas fa-building text-muted"></i> 
                <router-link v-if="contato.imovel_obj?.id" :to="`/imoveis/editar/${contato.imovel_obj.id}`" class="link-imovel">
                  Imóvel Ref: {{ contato.imovel_obj?.codigo_referencia || 'N/A' }} 
                  ({{ contato.imovel_obj?.tipo || 'N/A' }})
                </router-link>
                <span v-else>Imóvel não encontrado.</span>
             </p>
          </div>

          <div class="mensagem-container">
             <div class="data-col">
                <span class="data-label">Mensagem do Cliente:</span>
                <div class="data-value mensagem-text">
                    "{{ contato.mensagem }}"
                </div>
             </div>
          </div>
        </div>
        
        <div class="valor-footer">
           <span class="valor-label">Data do Contato</span>
           <span class="valor-amount">{{ formatarData(contato.data_contato) }}</span>
        </div>

        <div class="card-actions">
          <div class="actions-left">
            <button 
                @click="handleGerarOportunidade(contato)"
                class="btn-pill btn-ativar"
            >
                <i class="fas fa-funnel-dollar"></i> Gerar Lead
            </button>
          </div>

          <div class="actions-right">
              <button class="btn-mini btn-info" @click="handleResponder(contato)" title="Responder por Email">
                <i class="fas fa-reply"></i>
              </button>
              <button @click="handleArquivar(contato)" class="btn-mini btn-delete-mini" title="Arquivar">
                <i class="fas fa-archive"></i>
              </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="empty-state card">
      <div class="empty-icon"><i class="fas fa-inbox"></i></div>
      <p>Parabéns! Não há contatos de leads pendentes no momento.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';
import { format, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface ImovelResumo {
  id: number;
  codigo_referencia?: string;
  tipo?: string;
  endereco?: string;
}

interface Contato {
  id: number;
  imovel: number;
  imovel_obj?: ImovelResumo;
  nome: string;
  email: string;
  telefone?: string;
  mensagem: string;
  data_contato: string;
  arquivado: boolean;
}

const router = useRouter();
const contatos = ref<Contato[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const filtro = ref('');

async function fetchContatos() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get<Contato[]>('/v1/contatos/');
    contatos.value = response.data;
  } catch (err: any) {
    console.error("Erro ao buscar contatos:", err);
    error.value = err.response?.data?.detail || 'Não foi possível carregar os contatos.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(fetchContatos);

const filteredContatos = computed(() => {
  return contatos.value.filter(contato => {
    const searchLower = filtro.value.toLowerCase().trim();
    return !searchLower ||
      (contato.nome.toLowerCase()).includes(searchLower) ||
      (contato.email.toLowerCase()).includes(searchLower) ||
      (contato.telefone?.toLowerCase() || '').includes(searchLower) ||
      (contato.imovel_obj?.codigo_referencia?.toLowerCase() || '').includes(searchLower) ||
      (contato.mensagem.toLowerCase()).includes(searchLower);
  });
});

function formatarData(data: string | null): string {
  if (!data) return '—';
  try {
      return format(parseISO(data), 'dd/MM/yy HH:mm', { locale: ptBR });
  } catch {
      return 'Inválida';
  }
}

function handleResponder(contato: Contato) {
    const subject = `Contato sobre imóvel ${contato.imovel_obj?.codigo_referencia || contato.imovel}`;
    const body = `Olá ${contato.nome},\n\nEm resposta à sua mensagem:\n"${contato.mensagem}"\n\n`;
    window.location.href = `mailto:${contato.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}

async function handleArquivar(contato: Contato) {
  if (!window.confirm(`Tem a certeza de que deseja arquivar o contato de ${contato.nome}?`)) {
    return;
  }
  try {
    await apiClient.post(`/v1/contatos/${contato.id}/arquivar/`);
    contatos.value = contatos.value.filter(c => c.id !== contato.id);
  } catch(err) {
      console.error("Erro ao arquivar contato:", err);
      alert(`Ocorreu um erro ao arquivar o contato de ${contato.nome}.`);
  }
}

function handleGerarOportunidade(contato: Contato) {
    router.push({
        name: 'oportunidade-nova',
        query: {
            imovel_id: contato.imovel,
            contato_nome: contato.nome,
            contato_email: contato.email,
            contato_telefone: contato.telefone,
            mensagem: contato.mensagem,
            contato_id: contato.id
        }
    });
}
</script>

<style scoped>
/* ================================================== */
/* 1. Layout Geral (Padrão ContratosView) */
/* ================================================== */
.page-container { padding: 0; }
.header-bar {
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e9ecef;
}
.page-subtitle {
    font-size: 1.1rem;
    font-weight: 600;
    color: #495057;
    margin: 0;
}
.main-card, .loading-message.card, .error-message.card, .empty-state.card {
  background-color: #fff; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); 
  padding: 1.5rem; border: 1px solid #eaedf0;
}

/* ================================================== */
/* 2. Search & Filter Bar (Padrão ContratosView) */
/* ================================================== */
.search-and-filter-bar {
  display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem;
  align-items: center; background-color: transparent; padding: 0; box-shadow: none;
}
.search-input {
  padding: 10px; border: 1px solid #ccc; border-radius: 5px; width: 100%; max-width: 350px; box-sizing: border-box; font-family: system-ui, sans-serif;
}
.filter-group { display: flex; align-items: center; gap: 0.5rem; }
.filter-group label { font-weight: 500; color: #555; white-space: nowrap; }
.filter-group select {
  padding: 8px 12px; border: 1px solid #ccc; border-radius: 5px; font-size: 0.95rem;
  background-color: #f8f9fa; min-width: 120px; font-family: system-ui, sans-serif;
}
.btn-add {
  background-color: #f3f4f6; color: #374151; padding: 10px 15px; border: none; border-radius: 5px;
  font-weight: bold; font-size: 0.95rem; display: flex; align-items: center; gap: 0.5rem; 
  margin-left: auto; width: auto; text-decoration: none; font-family: system-ui, sans-serif;
  border: 1px solid #e5e7eb;
}
.mobile-hide { display: inline; }
@media (max-width: 768px) {
  .search-and-filter-bar { flex-direction: column; align-items: stretch; }
  .search-input { max-width: 100%; }
  .filter-group { flex-direction: column; align-items: stretch; }
  .btn-add { margin-left: 0; justify-content: center; }
}

/* ================================================== */
/* 3. Grid de Contatos (NOVA ESTRUTURA) */
/* ================================================== */
.contatos-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.5rem; padding-bottom: 2rem;
}

.contato-card {
  background-color: #fff; border-radius: 12px; border: 1px solid rgba(0,0,0,0.06);
  box-shadow: 0 4px 12px rgba(0,0,0,0.03); display: flex; flex-direction: column;
  transition: all 0.3s ease; position: relative; overflow: hidden;
}
.contato-card:hover { transform: translateY(-3px); box-shadow: 0 8px 18px rgba(0,0,0,0.06); }


/* Header (Status/Type) */
.card-top-bar {
    padding: 0.85rem 1.25rem; display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid #f0f2f5; background: #fff;
}
.badges-left, .badges-right { display: flex; align-items: center; gap: 8px; }

.contrato-id {
    font-size: 0.75rem; font-weight: 800; color: #9333ea;
    background: #f3e8ff; padding: 3px 8px; border-radius: 6px;
}
.tipo-badge {
    font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
    padding: 3px 8px; border-radius: 6px; color: #0284c7; background-color: #e0f2fe;
}
.status-pill {
    padding: 0.35em 0.85em; border-radius: 50px; font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; display: flex; align-items: center; gap: 5px;
}
.status-rascunho { background-color: #fef3c7; color: #92400e; } /* Amarelo para Novo Lead */


/* Body - Informações do Cliente/Imóvel */
.card-body { padding: 0; flex-grow: 1; display: flex; flex-direction: column; }
.imovel-section { padding: 1.25rem 1.25rem 0.75rem; }
.imovel-title {
    font-size: 1.05rem; font-weight: 700; color: #111827; margin: 0 0 0.5rem 0;
    line-height: 1.4; display: flex; align-items: center; gap: 8px;
}
.imovel-address {
    font-size: 0.8rem; color: #6b7280; margin: 0;
    display: flex; align-items: center; gap: 6px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.mt-5 { margin-top: 5px; }
.ml-10 { margin-left: 10px; }

/* Mensagem (o destaque do Lead) */
.mensagem-container {
    display: flex; flex-direction: column; 
    padding: 1rem 1.25rem; background-color: #f8fafc; border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9;
    flex-grow: 1;
}
.data-col { display: flex; flex-direction: column; gap: 2px; }
.data-label { font-size: 0.7rem; color: #9ca3af; font-weight: 600; text-transform: uppercase; margin-bottom: 5px;}
.data-value { font-size: 0.85rem; font-weight: 500; color: #374151; }
.mensagem-text {
    line-height: 1.5;
    white-space: normal;
    word-wrap: break-word;
    font-style: italic;
    color: #1f2937;
}

/* Footer Values */
.valor-footer {
    margin-top: auto; padding: 0.85rem 1.25rem;
    display: flex; justify-content: space-between; align-items: center;
    background-color: #f9fafb; color: #111827; 
}
.valor-label { font-size: 0.75rem; color: #9ca3af; font-weight: 500; text-transform: uppercase; }
.valor-amount { font-size: 1.0rem; font-weight: 700; color: #374151; }

/* Actions */
.card-actions {
    padding: 0.85rem 1.25rem; background-color: #fff;
    display: flex; justify-content: space-between; align-items: center; gap: 1rem;
}
.actions-left { display: flex; gap: 0.5rem; }
.actions-right { display: flex; gap: 0.25rem; }

/* Action Buttons */
.btn-pill {
    border: none; border-radius: 6px; padding: 0.4rem 0.85rem; font-size: 0.8rem; font-weight: 600;
    cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s;
}
.btn-ativar { background-color: #d1fae5; color: #065f46; } /* Verde para Gerar Lead */
.btn-ativar:hover { background-color: #a7f3d0; }

.btn-mini {
    width: 32px; height: 32px; border-radius: 6px; border: 1px solid transparent; background: transparent;
    color: #9ca3af; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s;
}
.btn-mini:hover { background-color: #f3f4f6; color: #374151; }

.btn-info { color: #17a2b8; } /* Azul para Responder */
.btn-info:hover { background-color: #e0faff; }

.btn-delete-mini:hover { background-color: #fee2e2; color: #dc2626; } /* Vermelho para Arquivar */

.link-imovel {
    color: #007bff; text-decoration: none; font-weight: 500;
}
.link-imovel:hover { text-decoration: underline; }

/* Mensagens de estado */
.error-message { color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; }
.loading-message { display: flex; flex-direction: column; align-items: center; }
.spinner { border: 3px solid #e9ecef; border-top: 3px solid #007bff; border-radius: 50%; width: 40px; height: 40px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.empty-state { padding: 4rem 2rem; }
.empty-state p { margin-bottom: 0; font-size: 1rem; }
.empty-icon { font-size: 3rem; color: #dee2e6; margin-bottom: 1rem; }
</style>