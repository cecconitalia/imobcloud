<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Comercial</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <router-link :to="{ name: 'funil-vendas' }">Funil</router-link>
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">{{ isEditing ? 'Editar Oportunidade' : 'Nova Oportunidade' }}</span>
           </nav>
           
           <h1>{{ isEditing ? 'Editar Negócio' : 'Criar Novo Negócio' }}</h1>
        </div>
        
        <div class="actions-area">
            <button @click="$router.back()" class="btn-secondary-thin">
                <i class="fas fa-arrow-left"></i> Voltar
            </button>
            <button @click="handleSubmit" class="btn-primary-thin" :disabled="isLoading">
                <i class="fas fa-save" :class="{ 'fa-spin': isLoading }"></i>
                {{ isLoading ? 'Salvando...' : 'Salvar Negócio' }}
            </button>
        </div>
      </div>
    </header>

    <div v-if="isLoadingData" class="loading-state">
        <div class="spinner"></div>
    </div>

    <main v-else class="form-wrapper">
      <form @submit.prevent="handleSubmit">
        
        <div class="form-column main-col">
            
            <section class="card">
                <div class="card-header">
                    <h3><i class="fas fa-info-circle"></i> Informações do Negócio</h3>
                </div>
                <div class="card-body">
                    
                    <div class="form-group">
                        <label>Título da Oportunidade <span class="req">*</span></label>
                        <input type="text" v-model="form.titulo" required class="form-control" placeholder="Ex: Venda Apartamento Centro">
                    </div>

                    <div class="form-grid-2 mt-4">
                        <div class="form-group">
                            <label>Cliente / Lead <span class="req">*</span></label>
                            <v-select 
                                v-model="form.cliente" 
                                :options="clientesList" 
                                :reduce="(option: any) => option.id" 
                                label="nome_display"
                                placeholder="Buscar cliente..."
                                class="style-chooser"
                            >
                                <template #no-options>Digite para buscar...</template>
                                <template #option="option">
                                    <div class="select-option">
                                        <span>{{ option.nome }}</span>
                                        <small v-if="option.razao_social" class="text-muted">{{ option.razao_social }}</small>
                                    </div>
                                </template>
                            </v-select>
                        </div>

                        <div class="form-group">
                            <label>Imóvel de Interesse</label>
                            <v-select 
                                v-model="form.imovel" 
                                :options="imoveisList" 
                                :reduce="(option: any) => option.id" 
                                label="titulo_formatado"
                                placeholder="Buscar imóvel..."
                                class="style-chooser"
                            >
                                <template #option="option">
                                    <div class="select-option">
                                        <span>{{ option.codigo_referencia }} - {{ option.titulo_anuncio }}</span>
                                        <small class="text-muted">{{ option.bairro || 'Bairro não inf.' }} - {{ option.cidade }}</small>
                                    </div>
                                </template>
                            </v-select>
                        </div>
                    </div>

                    <div class="form-grid-2 mt-4">
                        <div class="form-group">
                            <label>Valor Estimado (R$)</label>
                            <input 
                                type="number" 
                                step="0.01" 
                                v-model="form.valor_estimado" 
                                class="form-control" 
                                placeholder="0,00"
                            >
                        </div>
                        <div class="form-group">
                            <label>Probabilidade de Fechamento (%)</label>
                            <input 
                                type="number" 
                                min="0" max="100" 
                                v-model="form.probabilidade" 
                                class="form-control" 
                                placeholder="Ex: 50"
                            >
                        </div>
                    </div>

                    <div class="form-group mt-4">
                        <label>Descrição / Observações</label>
                        <textarea v-model="form.descricao" rows="4" class="form-control" placeholder="Detalhes sobre a negociação..."></textarea>
                    </div>

                </div>
            </section>

        </div>

        <div class="form-column side-col">
            
            <section class="card mb-4">
                <div class="card-header">
                    <h3><i class="fas fa-tasks"></i> Andamento</h3>
                </div>
                <div class="card-body">
                    <div class="form-group">
                        <label>Etapa do Funil <span class="req">*</span></label>
                        <div class="status-steps">
                            <div 
                                v-for="fase in fasesList" 
                                :key="fase.id"
                                class="step-item"
                                :class="{ active: form.fase === fase.id }"
                                @click="form.fase = fase.id"
                            >
                                <div class="step-circle"></div>
                                <span class="step-label">{{ fase.titulo }}</span>
                            </div>
                        </div>
                    </div>

                    <div class="form-group mt-4">
                        <label>Previsão de Fechamento <span class="req">*</span></label>
                        <input type="date" v-model="form.data_fechamento_prevista" required class="form-control">
                        <small class="help-text">Data estimada para conclusão do negócio.</small>
                    </div>
                </div>
            </section>

            <section v-if="isAdmin" class="card highlight-border">
                <div class="card-header bg-orange-light">
                    <h3 class="text-orange"><i class="fas fa-user-tie"></i> Responsável</h3>
                </div>
                <div class="card-body">
                    <div class="form-group">
                        <label class="text-orange-dark font-bold">Corretor Responsável</label>
                        <v-select 
                            v-model="form.responsavel" 
                            :options="usersList" 
                            :reduce="(option: any) => option.id" 
                            :get-option-label="(option: any) => `${option.first_name} ${option.last_name || ''} (${option.username})`"
                            placeholder="Selecione o corretor..."
                            class="style-chooser"
                        >
                        </v-select>
                        <small class="help-text mt-2">
                            <i class="fas fa-info-circle"></i> Ao alterar, o novo corretor será notificado e a oportunidade aparecerá no funil dele.
                        </small>
                    </div>
                </div>
            </section>

            <section class="card mt-4">
                <div class="card-header">
                    <h3><i class="fas fa-bullhorn"></i> Origem</h3>
                </div>
                <div class="card-body">
                    <div class="form-group">
                        <label>Fonte do Lead</label>
                        <select v-model="form.fonte" class="form-control">
                            <option value="">Selecione...</option>
                            <option value="SITE">Site da Imobiliária</option>
                            <option value="PORTAL">Portal Imobiliário</option>
                            <option value="INDICACAO">Indicação</option>
                            <option value="REDES_SOCIAIS">Redes Sociais</option>
                            <option value="TELEFONE">Telefone Ativo</option>
                            <option value="OUTRO">Outro</option>
                        </select>
                    </div>
                </div>
            </section>

        </div>

      </form>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '@/services/api';
import { useAuthStore } from '@/stores/auth';
import { useToast } from 'vue-toast-notification';
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();

const isEditing = ref(false);
const isLoading = ref(false);
const isLoadingData = ref(true);

// Listas para Dropdowns
const clientesList = ref<any[]>([]);
const imoveisList = ref<any[]>([]);
const fasesList = ref<any[]>([]);
const usersList = ref<any[]>([]);

// Modelo do Formulário
const form = ref({
    titulo: '',
    cliente: null as number | null,
    imovel: null as number | null,
    fase: null as number | null,
    valor_estimado: null as number | null,
    probabilidade: 50,
    descricao: '',
    fonte: '',
    data_fechamento_prevista: '',
    responsavel: null as number | null 
});

// Permissão de Admin
const isAdmin = computed(() => {
    const user = authStore.user;
    return user?.is_superuser || user?.is_admin;
});

// --- FUNÇÃO AUXILIAR: CALCULAR DATA PADRÃO (+3 MESES) ---
const getThreeMonthsAheadDate = () => {
    const date = new Date();
    date.setMonth(date.getMonth() + 3);
    // Formato YYYY-MM-DD
    return date.toISOString().split('T')[0];
};

// --- CARREGAMENTO DE DADOS ---
onMounted(async () => {
    try {
        await Promise.all([
            fetchClientes(),
            fetchImoveis(),
            fetchFases(),
            isAdmin.value ? fetchUsers() : Promise.resolve()
        ]);

        if (route.params.id) {
            isEditing.value = true;
            await loadOportunidade(Number(route.params.id));
        } else {
            // == CONFIGURAÇÃO INICIAL PARA NOVA OPORTUNIDADE ==
            
            // 1. Define responsável como eu mesmo por padrão
            if (authStore.user) {
                form.value.responsavel = authStore.user.id;
            }
            // 2. Define primeira fase como padrão
            if (fasesList.value.length > 0) {
                form.value.fase = fasesList.value[0].id;
            }
            // 3. Define data de fechamento para +3 meses
            form.value.data_fechamento_prevista = getThreeMonthsAheadDate();
        }
    } catch (e) {
        console.error("Erro ao inicializar formulário", e);
        toast.error("Erro ao carregar dados iniciais.");
    } finally {
        isLoadingData.value = false;
    }
});

const fetchClientes = async () => {
    const { data } = await api.get('/v1/clientes/lista-simples/');
    clientesList.value = data;
};

const fetchImoveis = async () => {
    try {
        const { data } = await api.get('/v1/imoveis/lista-simples/');
        imoveisList.value = data.map((i: any) => ({
            ...i,
            titulo_formatado: `${i.codigo_referencia || 'S/REF'} - ${i.titulo_anuncio || 'Sem Título'}`
        }));
    } catch (e) {
        console.error("Erro ao buscar imóveis", e);
    }
};

const fetchFases = async () => {
    const { data } = await api.get('/v1/fases-funil/');
    fasesList.value = data.results || data;
};

const fetchUsers = async () => {
    const { data } = await api.get('/v1/core/usuarios/?page_size=100&is_active=true');
    usersList.value = data.results || data;
};

const loadOportunidade = async (id: number) => {
    try {
        const { data } = await api.get(`/v1/oportunidades/${id}/`);
        form.value = {
            titulo: data.titulo,
            cliente: data.cliente?.id || data.cliente,
            imovel: data.imovel?.id || data.imovel,
            fase: data.fase?.id || data.fase,
            valor_estimado: data.valor_estimado,
            probabilidade: data.probabilidade,
            descricao: data.descricao || '',
            fonte: data.fonte || '',
            data_fechamento_prevista: data.data_fechamento_prevista || '',
            responsavel: (typeof data.responsavel === 'object' && data.responsavel) ? data.responsavel.id : data.responsavel
        };
    } catch (e) {
        toast.error("Erro ao carregar oportunidade.");
        router.push({ name: 'funil-vendas' });
    }
};

// --- SUBMIT ---
const handleSubmit = async () => {
    // Validação de campos obrigatórios
    if (!form.value.titulo || !form.value.cliente || !form.value.fase) {
        return toast.warning("Preencha os campos obrigatórios (Título, Cliente, Etapa).");
    }
    
    // Validação da Data de Fechamento (Agora Obrigatória)
    if (!form.value.data_fechamento_prevista) {
        return toast.warning("A Previsão de Fechamento é obrigatória.");
    }

    isLoading.value = true;
    try {
        const payload = { ...form.value };

        if (isEditing.value) {
            await api.patch(`/v1/oportunidades/${route.params.id}/`, payload);
            toast.success("Oportunidade atualizada!");
        } else {
            await api.post('/v1/oportunidades/', payload);
            toast.success("Oportunidade criada!");
        }
        router.push({ name: 'funil-vendas' });
    } catch (e: any) {
        console.error(e);
        toast.error("Erro ao salvar oportunidade.");
    } finally {
        isLoading.value = false;
    }
};
</script>

<style scoped>
/* GERAL */
.page-container {
  min-height: 100vh;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
}

/* HEADER */
.page-header { margin-bottom: 2rem; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }
.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.actions-area { display: flex; gap: 0.75rem; }

/* BOTÕES */
.btn-primary-thin, .btn-secondary-thin {
  padding: 0.5rem 1.2rem; border-radius: 6px; font-weight: 500; font-size: 0.85rem; cursor: pointer;
  display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s; border: none; text-decoration: none;
}
.btn-primary-thin { background: #2563eb; color: white; box-shadow: 0 1px 2px rgba(37, 99, 235, 0.15); }
.btn-primary-thin:hover { background: #1d4ed8; transform: translateY(-1px); }
.btn-secondary-thin { background: white; border: 1px solid #e2e8f0; color: #64748b; }
.btn-secondary-thin:hover { background: #f8fafc; border-color: #cbd5e1; color: #334155; }
.btn-primary-thin:disabled { opacity: 0.7; cursor: not-allowed; }

/* LAYOUT FORMULÁRIO */
.form-wrapper form {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 1.5rem;
    align-items: start;
    max-width: 1200px;
}

/* CARDS */
.card {
    background: white; border-radius: 8px; border: 1px solid #e5e7eb;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02); overflow: hidden;
}
.card-header { padding: 1rem 1.5rem; border-bottom: 1px solid #f1f5f9; background: #fff; }
.card-header h3 { font-size: 0.95rem; font-weight: 600; color: #1e293b; margin: 0; display: flex; align-items: center; gap: 0.5rem; }
.card-header i { color: #2563eb; }
.card-body { padding: 1.5rem; }

/* INPUTS */
.form-group { margin-bottom: 1rem; display: flex; flex-direction: column; gap: 0.4rem; }
.form-group label { font-size: 0.75rem; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.02em; }
.req { color: #ef4444; margin-left: 2px; }

.form-control {
  width: 100%; padding: 0.6rem 0.8rem; font-size: 0.9rem;
  border: 1px solid #cbd5e1; border-radius: 6px; background-color: #fff; color: #334155;
  outline: none; height: 40px; box-sizing: border-box; transition: all 0.2s;
}
textarea.form-control { height: auto; font-family: inherit; }
.form-control:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1); }

.form-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.mt-4 { margin-top: 1.5rem; }
.mb-4 { margin-bottom: 1.5rem; }

/* ESTILOS CUSTOMIZADOS PARA TRANSFERÊNCIA */
.highlight-border { border: 1px solid #fed7aa; }
.bg-orange-light { background-color: #fff7ed; }
.text-orange { color: #ea580c !important; }
.text-orange-dark { color: #9a3412 !important; }
.help-text { font-size: 0.75rem; color: #64748b; display: block; line-height: 1.4; }

/* STEPS DE FASE */
.status-steps {
    display: flex; flex-direction: column; gap: 0; border-left: 2px solid #e2e8f0; margin-left: 8px; padding: 10px 0;
}
.step-item {
    position: relative; padding-left: 20px; cursor: pointer; padding-bottom: 15px;
    display: flex; align-items: center; transition: all 0.2s;
}
.step-item:last-child { padding-bottom: 0; }
.step-circle {
    width: 12px; height: 12px; border-radius: 50%; background: white; border: 2px solid #cbd5e1;
    position: absolute; left: -7px; transition: all 0.2s;
}
.step-label { font-size: 0.85rem; color: #64748b; font-weight: 500; }

.step-item:hover .step-label { color: #2563eb; }
.step-item.active .step-circle { background: #2563eb; border-color: #2563eb; transform: scale(1.2); }
.step-item.active .step-label { color: #1e293b; font-weight: 700; }

/* VUE SELECT CUSTOM */
:deep(.style-chooser .vs__dropdown-toggle) {
    border-color: #cbd5e1; border-radius: 6px; padding: 4px 0;
}
:deep(.style-chooser .vs__search::placeholder) { color: #94a3b8; }

.select-option { display: flex; flex-direction: column; line-height: 1.2; }
.select-option small { font-size: 0.7rem; }

.loading-state { text-align: center; padding: 4rem; }
.spinner {
  border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%;
  width: 32px; height: 32px; animation: spin 0.8s linear infinite; margin: 0 auto;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

@media (max-width: 1024px) {
    .page-container { padding: 1rem; }
    .form-wrapper form { grid-template-columns: 1fr; }
    .side-col { order: -1; }
}
</style>