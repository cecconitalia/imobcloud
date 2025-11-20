<template>
  <div class="page-container">
    <div class="content-wrapper">
      
      <div class="view-header">
        <div class="header-left">
          <h1>{{ isEditing ? 'Editar Utilizador' : 'Novo Utilizador' }}</h1>
          <p class="subtitle">Preencha os dados para {{ isEditing ? 'atualizar' : 'cadastrar' }} um membro da equipa.</p>
        </div>
        <button @click="handleCancel" class="btn-back">
          <i class="fas fa-arrow-left"></i> Voltar à Lista
        </button>
      </div>

      <div v-if="isLoadingData" class="loading-state card">
         <div class="spinner"></div>
         <p>A carregar dados...</p>
      </div>

      <div v-else class="card form-card">
        <form @submit.prevent="handleSubmit">
          
          <div class="form-section">
             <h3 class="section-title"><i class="fas fa-user-shield"></i> Dados de Acesso & Pessoais</h3>
             <div class="form-grid">
                <div class="form-group">
                  <label for="username">Nome de Utilizador <span class="required">*</span></label>
                  <div class="input-wrapper">
                    <i class="fas fa-at input-icon"></i>
                    <input type="text" id="username" v-model="user.username" required class="form-input has-icon" placeholder="Ex: joao.silva" />
                  </div>
                </div>

                <div class="form-group">
                  <label for="email">Email Corporativo <span class="required">*</span></label>
                  <div class="input-wrapper">
                    <i class="fas fa-envelope input-icon"></i>
                    <input type="email" id="email" v-model="user.email" required class="form-input has-icon" placeholder="joao@imobiliaria.com" />
                  </div>
                </div>

                <div class="form-group">
                   <label for="password">Palavra-passe</label>
                   <div class="input-wrapper">
                     <i class="fas fa-lock input-icon"></i>
                     <input 
                        type="password" 
                        id="password" 
                        v-model="user.password" 
                        class="form-input has-icon" 
                        :placeholder="isEditing ? 'Deixe vazio para manter a atual' : 'Senha inicial'" 
                        :required="!isEditing" 
                     />
                   </div>
                </div>

                <div class="form-group full-width">
                  <label>Cargos / Permissões <span class="required">*</span></label>
                  <div class="roles-container">
                      <label class="role-checkbox">
                          <input type="checkbox" v-model="user.perfil.is_admin" />
                          <span class="role-label">
                              <i class="fas fa-user-shield"></i> Administrador
                              <small>Acesso total às configurações</small>
                          </span>
                      </label>
                      <label class="role-checkbox">
                          <input type="checkbox" v-model="user.perfil.is_corretor" />
                          <span class="role-label">
                              <i class="fas fa-user-tie"></i> Corretor
                              <small>Pode receber leads e gerir imóveis</small>
                          </span>
                      </label>
                  </div>
                </div>

                <div class="form-group">
                  <label for="first_name">Nome Próprio <span class="required">*</span></label>
                  <input type="text" id="first_name" v-model="user.first_name" required class="form-input" />
                </div>

                <div class="form-group">
                  <label for="last_name">Apelido <span class="required">*</span></label>
                  <input type="text" id="last_name" v-model="user.last_name" required class="form-input" />
                </div>
                
                <div class="form-group">
                  <label for="telefone">Telefone / WhatsApp</label>
                  <input type="tel" id="telefone" v-model="user.perfil.telefone" class="form-input" placeholder="(00) 00000-0000" />
                </div>

                <div class="form-group">
                  <label for="creci">CRECI</label>
                  <input type="text" id="creci" v-model="user.perfil.creci" class="form-input" placeholder="Nº do registo" />
                </div>
             </div>
          </div>

          <div class="section-divider"></div>

          <div class="form-section">
             <h3 class="section-title"><i class="fas fa-map-marker-alt"></i> Endereço Residencial</h3>
             <div class="form-grid">
                <div class="form-group">
                  <label for="cep">CEP</label>
                  <input type="text" id="cep" v-model="user.perfil.endereco_cep" class="form-input" placeholder="00000-000" />
                </div>
                
                <div class="form-group span-2">
                  <label for="logradouro">Logradouro</label>
                  <input type="text" id="logradouro" v-model="user.perfil.endereco_logradouro" class="form-input" />
                </div>

                <div class="form-group">
                  <label for="numero">Número</label>
                  <input type="text" id="numero" v-model="user.perfil.endereco_numero" class="form-input" />
                </div>

                <div class="form-group">
                  <label for="bairro">Bairro</label>
                  <input type="text" id="bairro" v-model="user.perfil.endereco_bairro" class="form-input" />
                </div>

                <div class="form-group">
                  <label for="cidade">Cidade</label>
                  <input type="text" id="cidade" v-model="user.perfil.endereco_cidade" class="form-input" />
                </div>

                <div class="form-group">
                  <label for="estado">Estado (UF)</label>
                  <input type="text" id="estado" maxlength="2" v-model="user.perfil.endereco_estado" class="form-input" style="text-transform: uppercase;" />
                </div>
             </div>
          </div>

          <div class="section-divider"></div>

          <div class="form-section">
             <h3 class="section-title"><i class="fas fa-file-signature"></i> Assinatura Digital</h3>
             <div class="integration-card">
                <div class="integration-body">
                    <p class="help-text">Esta assinatura será utilizada automaticamente em documentos gerados pelo sistema (ex: Termos de Visita).</p>
                    
                    <div class="signature-preview" v-if="previewAssinatura">
                        <img :src="previewAssinatura" alt="Pré-visualização da Assinatura" />
                        <button type="button" class="btn-remove-sig" @click="removeAssinatura">
                            <i class="fas fa-trash"></i> Remover
                        </button>
                    </div>

                    <div class="file-upload-area" v-else>
                        <label for="assinatura_file" class="custom-file-upload">
                            <i class="fas fa-pen-nib"></i>
                            <span>Carregar Imagem da Assinatura (PNG/JPG)</span>
                        </label>
                        <input type="file" id="assinatura_file" @change="handleAssinaturaUpload" accept="image/*" />
                    </div>
                    <small class="help-text" style="margin-top: 0.5rem; display: block;">Recomendado: Imagem com fundo transparente (PNG), proporção horizontal.</small>
                </div>
             </div>
          </div>
          
           <div class="section-divider"></div>

           <div class="form-section">
             <h3 class="section-title"><i class="fas fa-plug"></i> Integrações & Observações</h3>
             
             <div class="form-group full-width">
                <label for="observacoes">Observações Internas</label>
                <textarea id="observacoes" v-model="user.perfil.observacoes" rows="3" class="form-textarea" placeholder="Informações adicionais sobre este utilizador..."></textarea>
             </div>

             <div class="integration-card">
                <div class="integration-header">
                    <i class="fab fa-google"></i>
                    <h4>Google Calendar</h4>
                </div>
                <div class="integration-body">
                    <p class="help-text">Conecte a conta para sincronizar automaticamente tarefas e visitas.</p>
                    
                    <div class="file-upload-area">
                        <label for="google_json_file" class="custom-file-upload">
                            <i class="fas fa-cloud-upload-alt"></i>
                            <span v-if="!user.perfil.google_json_file">Carregar JSON de Credenciais</span>
                            <span v-else>Arquivo selecionado: {{ typeof user.perfil.google_json_file === 'string' ? 'Já enviado' : user.perfil.google_json_file.name }}</span>
                        </label>
                        <input type="file" id="google_json_file" @change="handleFileUpload" accept=".json" />
                    </div>

                    <div v-if="isEditing && user.perfil.google_json_file" class="auth-actions">
                        <div v-if="user.perfil.google_calendar_token" class="status-connected">
                            <i class="fas fa-check-circle"></i> Conectado com sucesso
                        </div>
                        <button v-else type="button" @click="handleGoogleAuth" class="btn-google">
                            Autorizar Acesso Google
                        </button>
                    </div>
                </div>
             </div>
          </div>

          <div v-if="successMessage" class="alert alert-success">
            <i class="fas fa-check-circle"></i> {{ successMessage }}
          </div>
          <div v-if="errorMessage" class="alert alert-error">
            <i class="fas fa-exclamation-triangle"></i> {{ errorMessage }}
          </div>

          <div class="form-actions-footer">
            <button type="button" @click="handleCancel" class="btn-secondary">
                Cancelar
            </button>
            <button type="submit" class="btn-primary" :disabled="isSubmitting">
              <i v-if="isSubmitting" class="fas fa-spinner fa-spin"></i>
              <span v-else>
                  <i class="fas fa-save"></i> {{ isEditing ? 'Salvar Alterações' : 'Registar Utilizador' }}
              </span>
            </button>
          </div>
        </form>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';

const route = useRoute();
const router = useRouter();

const userId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!userId.value);
const previewAssinatura = ref<string | null>(null);

const user = ref({
  username: '',
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  perfil: {
    is_admin: false,
    is_corretor: true,
    
    creci: '',
    telefone: '',
    endereco_logradouro: '',
    endereco_numero: '',
    endereco_bairro: '',
    endereco_cidade: '',
    endereco_estado: '',
    endereco_cep: '',
    observacoes: '',
    google_json_file: null as File | null | string,
    google_calendar_token: null as string | null,
    assinatura: null as File | null | string // Campo novo
  },
});

const isLoadingData = ref(false);
const isSubmitting = ref(false);
const successMessage = ref('');
const errorMessage = ref('');

async function fetchUserData() {
  if (isEditing.value) {
    isLoadingData.value = true;
    try {
      const response = await apiClient.get(`/v1/core/usuarios/${userId.value}/`);
      const data = response.data;
      
      user.value.username = data.username;
      user.value.first_name = data.first_name;
      user.value.last_name = data.last_name;
      user.value.email = data.email;
      
      const perfilData = data.perfil || {};
      user.value.perfil = { 
          ...user.value.perfil, 
          ...perfilData,
          is_admin: !!perfilData.is_admin,
          is_corretor: !!perfilData.is_corretor 
      };

      // Se já tiver assinatura, mostra o preview
      if (perfilData.assinatura) {
          previewAssinatura.value = perfilData.assinatura;
      }
      
    } catch (error) {
      console.error("Erro ao buscar dados:", error);
      errorMessage.value = "Não foi possível carregar os dados do utilizador.";
      setTimeout(() => router.push({ name: 'corretores' }), 2000);
    } finally {
      isLoadingData.value = false;
    }
  }
}

function handleFileUpload(event: Event) {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files[0]) {
        user.value.perfil.google_json_file = target.files[0];
    }
}

// Manipula o upload da assinatura e gera preview
function handleAssinaturaUpload(event: Event) {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files[0]) {
        const file = target.files[0];
        user.value.perfil.assinatura = file;
        
        // Cria URL temporária para preview
        previewAssinatura.value = URL.createObjectURL(file);
    }
}

function removeAssinatura() {
    user.value.perfil.assinatura = null; // Será tratado no backend se enviar null/vazio?
    previewAssinatura.value = null;
    // Nota: Para apagar no backend, geralmente precisaríamos de uma flag ou lógica específica, 
    // mas aqui estamos apenas limpando o input para novo upload.
}

function handleGoogleAuth() {
  window.location.href = `${apiClient.defaults.baseURL}/v1/clientes/google-calendar-auth/`;
}

async function handleSubmit() {
  isSubmitting.value = true;
  successMessage.value = '';
  errorMessage.value = '';

  const formData = new FormData();
  formData.append('username', user.value.username);
  formData.append('first_name', user.value.first_name);
  formData.append('last_name', user.value.last_name || '');
  formData.append('email', user.value.email);
  
  if (user.value.password) {
    formData.append('password', user.value.password);
  }

  const p = user.value.perfil;
  formData.append('perfil.is_admin', p.is_admin ? 'true' : 'false');
  formData.append('perfil.is_corretor', p.is_corretor ? 'true' : 'false');
  
  if (p.creci) formData.append('perfil.creci', p.creci);
  if (p.telefone) formData.append('perfil.telefone', p.telefone);
  if (p.endereco_logradouro) formData.append('perfil.endereco_logradouro', p.endereco_logradouro);
  if (p.endereco_numero) formData.append('perfil.endereco_numero', p.endereco_numero);
  if (p.endereco_bairro) formData.append('perfil.endereco_bairro', p.endereco_bairro);
  if (p.endereco_cidade) formData.append('perfil.endereco_cidade', p.endereco_cidade);
  if (p.endereco_estado) formData.append('perfil.endereco_estado', p.endereco_estado);
  if (p.endereco_cep) formData.append('perfil.endereco_cep', p.endereco_cep);
  if (p.observacoes) formData.append('perfil.observacoes', p.observacoes);
  
  // Envia arquivos apenas se forem objetos File (novos uploads)
  if (p.google_json_file instanceof File) {
    formData.append('perfil.google_json_file', p.google_json_file);
  }
  
  if (p.assinatura instanceof File) {
    formData.append('perfil.assinatura', p.assinatura);
  }

  try {
    if (isEditing.value) {
      await apiClient.put(`/v1/core/usuarios/${userId.value}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      successMessage.value = 'Utilizador atualizado com sucesso!';
    } else {
      await apiClient.post('/v1/core/usuarios/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      successMessage.value = 'Utilizador registado com sucesso!';
    }

    setTimeout(() => {
        router.push({ name: 'corretores' });
    }, 1500);

  } catch (err: any) {
    console.error("Erro ao guardar:", err);
    const resp = err.response?.data;
    if (resp) {
        const keys = Object.keys(resp);
        if (keys.length > 0) {
            const firstError = resp[keys[0]];
            errorMessage.value = `${keys[0]}: ${Array.isArray(firstError) ? firstError[0] : firstError}`;
        } else {
             errorMessage.value = "Erro ao processar requisição.";
        }
    } else {
        errorMessage.value = "Ocorreu um erro inesperado.";
    }
  } finally {
    isSubmitting.value = false;
  }
}

function handleCancel() {
  router.push({ name: 'corretores' });
}

onMounted(() => {
  fetchUserData();
});
</script>

<style scoped>
/* Layout Base */
.page-container { 
    padding: 1.5rem; 
    background-color: #f4f7f6; 
    min-height: 100vh; 
    display: flex; 
    justify-content: center; 
}
.content-wrapper { width: 100%; max-width: 900px; }

/* Header */
.view-header {
    display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;
}
.header-left h1 { font-size: 1.5rem; color: #343a40; margin: 0 0 0.3rem 0; font-weight: 700; }
.subtitle { color: #6c757d; font-size: 0.9rem; margin: 0; }

.btn-back {
    background: none; border: 1px solid #dee2e6; padding: 0.5rem 1rem; border-radius: 6px;
    color: #6c757d; cursor: pointer; font-weight: 600; transition: all 0.2s; display: flex; align-items: center; gap: 0.5rem;
}
.btn-back:hover { background-color: #e9ecef; color: #343a40; }

/* Card Form */
.card { background: #fff; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); padding: 2rem; border: 1px solid #eaedf0; }

.form-section { margin-bottom: 2rem; }
.section-title {
    font-size: 1.1rem; color: #2c3e50; margin-bottom: 1.2rem; padding-bottom: 0.5rem;
    border-bottom: 2px solid #f0f2f5; font-weight: 700; display: flex; align-items: center; gap: 0.6rem;
}
.section-divider { height: 1px; background: #f0f2f5; margin: 2rem 0; }

/* Custom Roles Checkboxes */
.roles-container { display: flex; gap: 1rem; flex-wrap: wrap; }
.role-checkbox {
    flex: 1; min-width: 200px; display: flex; align-items: flex-start; gap: 10px;
    border: 1px solid #ced4da; padding: 1rem; border-radius: 8px; cursor: pointer; transition: all 0.2s;
}
.role-checkbox:hover { background-color: #f8f9fa; border-color: #adb5bd; }
.role-checkbox:has(input:checked) { background-color: #e8f0fe; border-color: #3498db; }
.role-label { display: flex; flex-direction: column; font-weight: 600; color: #343a40; }
.role-label small { font-weight: 400; color: #6c757d; margin-top: 2px; font-size: 0.8rem; }
.role-label i { margin-bottom: 5px; color: #3498db; }

/* Grid & Inputs */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; }
@media (max-width: 768px) { .form-grid { grid-template-columns: 1fr; } }

.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.span-2 { grid-column: span 2; }
@media (max-width: 768px) { .span-2 { grid-column: span 1; } }
.full-width { grid-column: 1 / -1; }

label { font-weight: 600; font-size: 0.85rem; color: #495057; }
.required { color: #e74c3c; }

.input-wrapper { position: relative; }
.input-icon {
    position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #adb5bd; font-size: 0.9rem;
}

.form-input, .form-select, .form-textarea {
    width: 100%; padding: 0.6rem 0.8rem; border: 1px solid #ced4da; border-radius: 6px;
    font-size: 0.95rem; transition: border-color 0.2s; background-color: #fff; box-sizing: border-box;
}
.form-input.has-icon { padding-left: 2.2rem; }
.form-input:focus, .form-select:focus, .form-textarea:focus {
    border-color: #3498db; outline: none; box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

/* Integração */
.integration-card {
    background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; overflow: hidden;
}
.integration-header {
    background-color: #fff; padding: 0.8rem 1.2rem; border-bottom: 1px solid #e9ecef;
    display: flex; align-items: center; gap: 0.8rem;
}
.integration-header i { color: #4285F4; font-size: 1.2rem; }
.integration-header h4 { margin: 0; font-size: 0.95rem; font-weight: 700; color: #343a40; }
.integration-body { padding: 1.2rem; }
.help-text { font-size: 0.85rem; color: #6c757d; margin-top: 0; margin-bottom: 1rem; }

/* File Upload Custom */
input[type="file"] { display: none; }
.custom-file-upload {
    display: inline-flex; align-items: center; gap: 0.5rem;
    border: 1px dashed #adb5bd; padding: 0.6rem 1rem; border-radius: 6px;
    cursor: pointer; background-color: #fff; color: #495057; font-size: 0.9rem; transition: all 0.2s; width: 100%; justify-content: center;
}
.custom-file-upload:hover { border-color: #3498db; color: #3498db; background-color: #f1f8ff; }

/* Signature Preview */
.signature-preview {
    display: flex; flex-direction: column; align-items: center; gap: 10px;
    background: #fff; padding: 15px; border: 1px solid #dee2e6; border-radius: 6px;
}
.signature-preview img { max-height: 80px; max-width: 100%; object-fit: contain; }
.btn-remove-sig {
    background: #ffebee; color: #c62828; border: 1px solid #ef9a9a;
    padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; display: flex; align-items: center; gap: 5px;
}
.btn-remove-sig:hover { background: #ffcdd2; }

.auth-actions { margin-top: 1rem; text-align: center; }
.btn-google {
    background-color: #4285F4; color: white; border: none; padding: 0.6rem 1.2rem;
    border-radius: 5px; cursor: pointer; font-weight: 600; display: inline-flex; align-items: center; gap: 0.5rem;
}
.btn-google:hover { background-color: #357ae8; }
.status-connected { color: #27ae60; font-weight: 600; font-size: 0.9rem; display: flex; align-items: center; gap: 0.5rem; justify-content: center; }

/* Footer Actions */
.form-actions-footer {
    display: flex; justify-content: flex-end; gap: 1rem; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #f0f2f5;
}
.btn-primary, .btn-secondary {
    padding: 0.7rem 1.5rem; border-radius: 6px; border: none; font-weight: 600; cursor: pointer; font-size: 0.95rem; display: flex; align-items: center; gap: 0.5rem;
}
.btn-primary { background-color: #007bff; color: white; }
.btn-primary:hover { background-color: #0056b3; transform: translateY(-1px); }
.btn-primary:disabled { background-color: #94aabf; cursor: not-allowed; transform: none; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #5a6268; }

/* Alerts */
.alert { padding: 1rem; border-radius: 6px; margin-top: 1.5rem; font-size: 0.9rem; display: flex; align-items: center; gap: 0.5rem; }
.alert-success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
.alert-error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }

/* Loading */
.loading-state { text-align: center; padding: 4rem; color: #6c757d; }
.spinner {
  border: 3px solid #e9ecef; border-top: 3px solid #007bff; border-radius: 50%;
  width: 40px; height: 40px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>