<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Gestão</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <router-link :to="{ name: 'corretores' }">Utilizadores</router-link>
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">{{ isEditing ? 'Editar' : 'Novo' }}</span>
           </nav>
           
           <h1>{{ isEditing ? 'Editar Colaborador' : 'Cadastrar Novo Colaborador' }}</h1>
        </div>
        
        <div class="actions-area">
            <button @click="$router.push({ name: 'corretores' })" class="btn-secondary-thin">
                <i class="fas fa-arrow-left"></i> Voltar
            </button>
            <button @click="handleSubmit" class="btn-primary-thin" :disabled="isLoading">
                <i class="fas fa-save" :class="{ 'fa-spin': isLoading }"></i>
                {{ isLoading ? 'Salvando...' : 'Salvar Dados' }}
            </button>
        </div>
      </div>
    </header>

    <main class="form-wrapper">
      <form @submit.prevent="handleSubmit">
        
        <div class="form-column left-col">
            
            <section class="form-section">
                <h3 class="section-title"><i class="far fa-id-card"></i> Dados Pessoais</h3>
                
                <div class="form-grid-2">
                    <div class="form-group">
                        <label>Nome <span class="req">*</span></label>
                        <div class="input-with-icon">
                            <i class="fas fa-user"></i>
                            <input type="text" v-model="form.first_name" required class="form-control" placeholder="Ex: Ana">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Sobrenome <span class="req">*</span></label>
                        <input type="text" v-model="form.last_name" required class="form-control" placeholder="Ex: Silva">
                    </div>
                </div>

                <div class="form-group mt-3">
                    <label>Email Corporativo <span class="req">*</span></label>
                    <div class="input-with-icon">
                        <i class="far fa-envelope"></i>
                        <input type="email" v-model="form.email" required class="form-control" placeholder="ana@imobiliaria.com">
                    </div>
                </div>
            </section>

            <section class="form-section mt-6">
                <h3 class="section-title"><i class="fas fa-key"></i> Credenciais</h3>
                
                <div class="form-grid-2">
                    <div class="form-group">
                        <label>Usuário (Login) <span class="req">*</span></label>
                        <div class="input-with-icon">
                            <i class="fas fa-at"></i>
                            <input type="text" v-model="form.username" required class="form-control" placeholder="ana.silva">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            {{ isEditing ? 'Nova Senha' : 'Senha Inicial' }} 
                            <span v-if="!isEditing" class="req">*</span>
                        </label>
                        <div class="input-with-icon">
                            <i class="fas fa-lock"></i>
                            <input 
                                type="password" 
                                v-model="form.password" 
                                :required="!isEditing" 
                                class="form-control" 
                                placeholder="******"
                                autocomplete="new-password"
                            >
                        </div>
                    </div>
                </div>
                
                <div class="form-group mt-4">
                    <label class="toggle-label">
                        <div class="toggle-switch">
                            <input type="checkbox" v-model="form.is_active">
                            <span class="slider"></span>
                        </div>
                        <div class="toggle-text">
                            <span class="main">Acesso Ativo</span>
                            <span class="sub">Permite que o usuário faça login no sistema.</span>
                        </div>
                    </label>
                </div>
            </section>
        </div>

        <div class="form-column permissions-column">
            <section class="permissions-card">
                <div class="card-header">
                    <h3><i class="fas fa-user-shield"></i> Permissões de Acesso</h3>
                    <p>Defina exatamente o que este usuário pode ver ou fazer.</p>
                </div>

                <div class="profile-tabs">
                    <button type="button" class="profile-tab" :class="{ active: currentProfile === 'corretor' }" @click="applyProfile('corretor')">
                        <i class="fas fa-id-badge"></i> Padrão Corretor
                    </button>
                    <button type="button" class="profile-tab" :class="{ active: currentProfile === 'admin' }" @click="applyProfile('admin')">
                        <i class="fas fa-crown"></i> Admin Total
                    </button>
                    <button type="button" class="profile-tab" :class="{ active: currentProfile === 'custom' }" @click="currentProfile = 'custom'">
                        <i class="fas fa-sliders-h"></i> Personalizado
                    </button>
                </div>

                <div class="permissions-scroll">
                    
                    <div v-for="(group, gIndex) in allPermissionGroups" :key="gIndex" class="perm-group">
                        <div class="perm-group-header">
                            <h4 class="perm-group-title">{{ group.name }}</h4>
                            <button type="button" class="btn-text-small" @click="toggleGroup(group)">
                                {{ isGroupFull(group) ? 'Desmarcar Todos' : 'Marcar Todos' }}
                            </button>
                        </div>
                        
                        <div class="perm-grid">
                            <label v-for="perm in group.permissions" :key="perm.code" class="checkbox-wrapper">
                                <input type="checkbox" v-model="form.permissions" :value="perm.code">
                                <span class="checkmark"></span>
                                <span class="label-text">{{ perm.label }}</span>
                            </label>
                        </div>
                    </div>

                </div>
            </section>
        </div>

      </form>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '@/services/api';
import { useToast } from 'vue-toast-notification';

const route = useRoute();
const router = useRouter();
const toast = useToast();

const isEditing = ref(false);
const isLoading = ref(false);
const currentProfile = ref('custom');

// --- ESTRUTURA DE DADOS DAS PERMISSÕES ---
// Aqui definimos TODAS as permissões possíveis no sistema
const allPermissionGroups = [
    {
        name: 'Imóveis',
        permissions: [
            { label: 'Visualizar Lista', code: 'view_imovel' },
            { label: 'Cadastrar Novos', code: 'add_imovel' },
            { label: 'Editar Dados', code: 'change_imovel' },
            { label: 'Excluir Imóveis', code: 'delete_imovel' },
            { label: 'Gerenciar Imagens', code: 'manage_images' },
            { label: 'Autorizações de Venda', code: 'view_autorizacao' }
        ]
    },
    {
        name: 'Clientes & CRM',
        permissions: [
            { label: 'Visualizar Clientes', code: 'view_cliente' },
            { label: 'Cadastrar/Editar', code: 'change_cliente' },
            { label: 'Excluir Clientes', code: 'delete_cliente' },
            { label: 'Acessar Funil', code: 'view_funil' },
            { label: 'Gerenciar Oportunidades', code: 'manage_oportunidade' },
            { label: 'Agendar Visitas', code: 'manage_visita' }
        ]
    },
    {
        name: 'Contratos & Jurídico',
        permissions: [
            { label: 'Visualizar Contratos', code: 'view_contrato' },
            { label: 'Criar Contratos', code: 'add_contrato' },
            { label: 'Editar/Renovar', code: 'change_contrato' },
            { label: 'Gerenciar Vistorias', code: 'manage_vistoria' }
        ]
    },
    {
        name: 'Financeiro',
        permissions: [
            { label: 'Ver Dashboard Fin.', code: 'view_financeiro_dash' },
            { label: 'Contas a Receber', code: 'view_receitas' },
            { label: 'Contas a Pagar', code: 'view_despesas' },
            { label: 'Gerenciar Transações', code: 'manage_transacao' },
            { label: 'Gerenciar Boletos', code: 'manage_boletos' },
            { label: 'Contas Bancárias', code: 'manage_contas_bancarias' }
        ]
    },
    {
        name: 'Marketing & Site',
        permissions: [
            { label: 'Publicar no Site', code: 'publish_site' },
            { label: 'Integração Portais', code: 'manage_portais' },
            { label: 'Redes Sociais', code: 'manage_social' }
        ]
    },
    {
        name: 'Sistema & Admin',
        permissions: [
            { label: 'Gerenciar Usuários', code: 'manage_users' },
            { label: 'Configurações Globais', code: 'manage_settings' },
            { label: 'Ver Relatórios Gerenciais', code: 'view_reports' },
            { label: 'Integrações (API)', code: 'manage_integrations' }
        ]
    }
];

// Perfis pré-definidos (Atalhos)
const presets: any = {
    corretor: [
        'view_imovel', 'add_imovel', 'change_imovel', 'manage_images', 'view_autorizacao',
        'view_cliente', 'change_cliente', 'view_funil', 'manage_oportunidade', 'manage_visita',
        'publish_site'
    ],
    admin: allPermissionGroups.flatMap(g => g.permissions.map(p => p.code)) // Todos
};

// MODELO DO FORM
const form = ref({
  first_name: '',
  last_name: '',
  username: '',
  email: '',
  password: '',
  is_active: true,
  permissions: [] as string[]
});

// --- LÓGICA DE SELEÇÃO ---

const isGroupFull = (group: any) => {
    return group.permissions.every((p: any) => form.value.permissions.includes(p.code));
};

const toggleGroup = (group: any) => {
    if (isGroupFull(group)) {
        // Desmarcar todos do grupo
        form.value.permissions = form.value.permissions.filter(p => !group.permissions.find((gp: any) => gp.code === p));
    } else {
        // Marcar todos do grupo (adiciona os que faltam)
        const groupCodes = group.permissions.map((p: any) => p.code);
        const newPerms = new Set([...form.value.permissions, ...groupCodes]);
        form.value.permissions = Array.from(newPerms);
    }
};

const applyProfile = (profileName: string) => {
    currentProfile.value = profileName;
    if (presets[profileName]) {
        form.value.permissions = [...presets[profileName]];
    }
};

// Detecta mudanças manuais para mudar status para "Custom"
watch(() => form.value.permissions, (newPerms) => {
    // Ordena para comparar JSON
    const sortedNew = [...newPerms].sort();
    const sortedCorretor = [...presets.corretor].sort();
    const sortedAdmin = [...presets.admin].sort();

    if (JSON.stringify(sortedNew) === JSON.stringify(sortedCorretor)) currentProfile.value = 'corretor';
    else if (JSON.stringify(sortedNew) === JSON.stringify(sortedAdmin)) currentProfile.value = 'admin';
    else currentProfile.value = 'custom';
}, { deep: true });


// --- API ---

onMounted(async () => {
  // Inicializa limpo ou com padrão corretor? Vamos deixar limpo ou corretor
  applyProfile('corretor');

  if (route.params.id) {
    isEditing.value = true;
    await fetchUser(Number(route.params.id));
  }
});

const fetchUser = async (id: number) => {
  isLoading.value = true;
  try {
    const { data } = await api.get(`/v1/core/usuarios/${id}/`);
    
    form.value.first_name = data.first_name;
    form.value.last_name = data.last_name;
    form.value.username = data.username;
    form.value.email = data.email;
    form.value.is_active = data.is_active;
    
    // IMPORTANTE: Aqui você deve receber as permissões do backend.
    // Se o backend enviar 'user_permissions' ou 'custom_permissions', use aqui.
    // Exemplo: form.value.permissions = data.custom_permissions || [];
    
    // Lógica de compatibilidade se o backend só tiver is_superuser por enquanto:
    if (data.is_superuser || data.is_admin) {
        applyProfile('admin');
    } else {
        // Se tiver campo de permissões reais no futuro, remova essa linha e use o dado real
        // form.value.permissions = data.permissions_list; 
        
        // Fallback: Se não for admin, assume corretor ou tenta ler o que vier
        applyProfile('corretor'); 
    }

  } catch (error) {
    toast.error('Erro ao carregar dados.');
    router.push({ name: 'corretores' });
  } finally {
    isLoading.value = false;
  }
};

const handleSubmit = async () => {
  if (!form.value.first_name || !form.value.username) return toast.warning("Campos obrigatórios faltando.");
  
  isLoading.value = true;
  try {
    // Determina se é admin baseado na permissão crítica 'manage_settings' ou se selecionou tudo
    const isAdminProfile = form.value.permissions.includes('manage_settings') && form.value.permissions.includes('manage_users');
    
    const payload: any = {
        ...form.value,
        is_staff: true, 
        // Mantém compatibilidade com sistema antigo de flags
        is_superuser: isAdminProfile, 
        is_admin: isAdminProfile,
        // Envia a lista granular para o backend (Backend precisa estar preparado para receber isso)
        permissions_list: form.value.permissions 
    };

    if (isEditing.value && !payload.password) delete payload.password;

    if (isEditing.value) {
      await api.patch(`/v1/core/usuarios/${route.params.id}/`, payload);
      toast.success('Usuário atualizado!');
    } else {
      await api.post('/v1/core/usuarios/', payload);
      toast.success('Usuário criado!');
    }
    router.push({ name: 'corretores' });
  } catch (error: any) {
    const msg = error.response?.data?.username ? 'Usuário já existe.' : 'Erro ao salvar.';
    toast.error(msg);
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
  display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s; border: none;
}
.btn-primary-thin { background: #2563eb; color: white; box-shadow: 0 1px 2px rgba(37, 99, 235, 0.15); }
.btn-primary-thin:hover { background: #1d4ed8; transform: translateY(-1px); }
.btn-secondary-thin { background: white; border: 1px solid #e2e8f0; color: #64748b; }
.btn-secondary-thin:hover { background: #f8fafc; border-color: #cbd5e1; color: #334155; }
.btn-primary-thin:disabled { opacity: 0.7; cursor: not-allowed; }
.btn-text-small { background: none; border: none; font-size: 0.7rem; color: #2563eb; cursor: pointer; font-weight: 600; text-transform: uppercase; }
.btn-text-small:hover { text-decoration: underline; }

/* LAYOUT FORMULÁRIO */
.form-wrapper form {
    display: grid;
    grid-template-columns: 1fr 1.2fr; /* Coluna da direita ligeiramente maior */
    gap: 2rem;
    align-items: start;
    max-width: 1400px;
}

/* CARDS */
.form-column {
    background: white; border-radius: 8px; border: 1px solid #e5e7eb;
    padding: 2rem; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}
.left-col { position: sticky; top: 2rem; } /* Coluna esquerda fixa ao rolar */

.section-title {
    font-size: 1rem; color: #1e293b; margin: 0 0 1.5rem 0; font-weight: 600;
    display: flex; align-items: center; gap: 0.6rem; border-bottom: 1px solid #f1f5f9; padding-bottom: 0.8rem;
}
.section-title i { color: #2563eb; font-size: 0.9rem; }

.form-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; }
.mt-3 { margin-top: 1rem; }
.mt-4 { margin-top: 1.5rem; }
.mt-6 { margin-top: 2.5rem; }

.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.form-group label { font-size: 0.75rem; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.02em; }
.req { color: #ef4444; margin-left: 2px; }

.input-with-icon { position: relative; width: 100%; }
.input-with-icon i { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 0.9rem; }

.form-control {
  width: 100%; padding: 0.6rem 0.8rem 0.6rem 2.3rem; font-size: 0.9rem;
  border: 1px solid #cbd5e1; border-radius: 6px; background-color: #fff; color: #334155;
  outline: none; height: 40px; box-sizing: border-box; transition: all 0.2s;
}
.form-control:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1); }

/* TOGGLE */
.toggle-label { display: flex; align-items: center; gap: 1rem; cursor: pointer; }
.toggle-switch { position: relative; width: 44px; height: 24px; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.slider {
  position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
  background-color: #ccc; transition: .4s; border-radius: 34px;
}
.slider:before {
  position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px;
  background-color: white; transition: .4s; border-radius: 50%;
}
input:checked + .slider { background-color: #10b981; }
input:checked + .slider:before { transform: translateX(20px); }
.toggle-text .main { font-weight: 600; font-size: 0.9rem; color: #1e293b; }
.toggle-text .sub { font-size: 0.75rem; color: #64748b; }

/* SEÇÃO DE PERMISSÕES */
.permissions-column { background-color: #fcfcfc; border-color: #e2e8f0; padding: 0; overflow: hidden; display: flex; flex-direction: column; height: auto; }
.permissions-card { display: flex; flex-direction: column; height: 100%; }

.card-header { padding: 1.5rem; border-bottom: 1px solid #f1f5f9; background: white; }
.card-header h3 { font-size: 1rem; font-weight: 600; color: #1e293b; margin: 0 0 0.3rem 0; display: flex; align-items: center; gap: 0.5rem; }
.card-header p { font-size: 0.8rem; color: #64748b; margin: 0; }
.card-header i { color: #2563eb; }

/* TABS DE PERFIL */
.profile-tabs { display: flex; gap: 0.5rem; background: #f1f5f9; padding: 0.5rem 1.5rem; border-bottom: 1px solid #e2e8f0; }
.profile-tab {
    flex: 1; border: none; background: transparent; padding: 0.6rem; border-radius: 6px;
    font-size: 0.75rem; font-weight: 600; color: #64748b; cursor: pointer; transition: all 0.2s;
    display: flex; align-items: center; justify-content: center; gap: 6px; border: 1px solid transparent;
}
.profile-tab:hover { background: rgba(255,255,255,0.5); }
.profile-tab.active { background: white; color: #2563eb; border-color: #e2e8f0; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.profile-tab i { font-size: 0.9rem; }

/* SCROLL AREA */
.permissions-scroll {
    flex: 1; overflow-y: auto; padding: 1.5rem; max-height: 600px;
}

/* GRUPOS */
.perm-group { margin-bottom: 2rem; }
.perm-group-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem; }
.perm-group-title { font-size: 0.8rem; font-weight: 700; color: #334155; text-transform: uppercase; letter-spacing: 0.05em; margin: 0; }

.perm-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; }

.checkbox-wrapper {
    display: flex; align-items: center; position: relative; padding-left: 28px; cursor: pointer;
    font-size: 0.85rem; color: #475569; user-select: none; transition: color 0.2s;
}
.checkbox-wrapper:hover { color: #1e293b; }
.checkbox-wrapper input { position: absolute; opacity: 0; cursor: pointer; height: 0; width: 0; }
.checkmark {
    position: absolute; top: 0; left: 0; height: 18px; width: 18px;
    background-color: #fff; border: 1px solid #cbd5e1; border-radius: 4px; transition: all 0.2s;
}
.checkbox-wrapper:hover input ~ .checkmark { border-color: #94a3b8; }
.checkbox-wrapper input:checked ~ .checkmark { background-color: #2563eb; border-color: #2563eb; }
.checkmark:after {
    content: ""; position: absolute; display: none;
    left: 6px; top: 2px; width: 4px; height: 9px;
    border: solid white; border-width: 0 2px 2px 0; transform: rotate(45deg);
}
.checkbox-wrapper input:checked ~ .checkmark:after { display: block; }

@media (max-width: 1024px) {
    .page-container { padding: 1rem; }
    .form-wrapper form { grid-template-columns: 1fr; }
    .header-main { flex-direction: column; align-items: flex-start; gap: 1rem; }
    .actions-area { width: 100%; justify-content: space-between; }
    .left-col { position: static; }
    .permissions-scroll { max-height: none; }
}
</style>