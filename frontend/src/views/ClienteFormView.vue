<template>
  <div class="form-container">
    <div v-if="isLoadingData" class="loading-message">
      A carregar dados do cliente...
    </div>

    <form v-else @submit.prevent="handleSubmit" class="cliente-form">
      <div class="form-card">
        <div class="tipo-pessoa-selector">
          <label class="tipo-pessoa-label">Tipo de Pessoa</label>
          <div class="tipo-pessoa-options">
            <label class="radio-option">
              <input type="radio" value="FISICA" :checked="cliente.tipo_pessoa === 'FISICA'" @change="onTipoPessoaChange">
              <span>Pessoa Física</span>
            </label>
            <label class="radio-option">
              <input type="radio" value="JURIDICA" :checked="cliente.tipo_pessoa === 'JURIDICA'" @change="onTipoPessoaChange">
              <span>Pessoa Jurídica</span>
            </label>
          </div>
        </div>
      </div>

      <div class="main-form-grid">

        <div class="form-card grid-col-span-2"> <h3 class="card-title">
            {{ cliente.tipo_pessoa === 'FISICA' ? 'Dados Pessoais' : 'Dados Empresariais' }}
          </h3>
          <div class="card-content-grid">
            <div class="profile-pic-area">
              <div class="profile-pic-preview">
                <img v-if="profilePicPreview" :src="profilePicPreview" alt="Pré-visualização da Foto de Perfil" class="profile-img"/>
                <i v-else class="fas fa-user-circle profile-icon"></i>
              </div>
              <label for="foto_perfil_input" class="btn-action upload-btn">
                <i class="fas fa-upload"></i> Carregar Foto
              </label>
              <input type="file" id="foto_perfil_input" @change="handleProfilePicChange" accept="image/*" />
              <button type="button" v-if="profilePicPreview" @click="removeProfilePic" class="btn-action remove-btn">
                <i class="fas fa-trash-alt"></i> Remover Foto
              </button>
            </div>

            <div class="fields-area">
              <template v-if="cliente.tipo_pessoa === 'FISICA'">
                <div class="form-group">
                  <label for="nome_completo">Nome Completo</label>
                  <input type="text" id="nome_completo" v-model="cliente.nome_completo" required />
                </div>
                <div class="form-group">
                  <label for="documento_pf">CPF</label>
                  <input type="text" id="documento_pf" v-model="cliente.documento" />
                </div>
                <div class="form-group">
                  <label for="data_nascimento">Data de Nascimento</label>
                  <input type="date" id="data_nascimento" v-model="cliente.data_nascimento" />
                </div>
              </template>

              <template v-else>
                <div class="form-group">
                  <label for="razao_social">Razão Social</label>
                  <input type="text" id="razao_social" v-model="cliente.razao_social" required />
                </div>
                <div class="form-group">
                    <label for="nome_fantasia">Nome Fantasia</label>
                    <input type="text" id="nome_fantasia" v-model="cliente.nome_fantasia" />
                </div>
                <div class="form-group">
                  <label for="documento_pj">CNPJ</label>
                  <input type="text" id="documento_pj" v-model="cliente.documento" />
                </div>
              </template>

              <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" v-model="cliente.email" />
              </div>
              <div class="form-group">
                <label for="telefone">Telefone Principal</label>
                <input type="text" id="telefone" v-model="cliente.telefone" />
              </div>
              <div class="form-group">
                <label for="telefone_alternativo">Telefone Alternativo</label>
                <input type="text" id="telefone_alternativo" v-model="cliente.telefone_alternativo" />
              </div>
            </div>
          </div>
        </div>

        <div class="form-card">
          <h3 class="card-title">Endereço</h3>
          <div class="card-content">
             <div class="form-group">
              <label for="cep">CEP</label>
              <input type="text" id="cep" v-model="cliente.cep" @blur="fetchAddressFromCEP" />
            </div>
            <div class="form-group">
              <label for="logradouro">Logradouro</label>
              <input type="text" id="logradouro" v-model="cliente.logradouro" />
            </div>
            <div class="form-group">
              <label for="numero">Número</label>
              <input type="text" id="numero" v-model="cliente.numero" />
            </div>
             <div class="form-group">
              <label for="complemento">Complemento</label>
              <input type="text" id="complemento" v-model="cliente.complemento" />
            </div>
            <div class="form-group">
              <label for="bairro">Bairro</label>
              <input type="text" id="bairro" v-model="cliente.bairro" />
            </div>
            <div class="form-group">
              <label for="cidade">Cidade</label>
              <input type="text" id="cidade" v-model="cliente.cidade" />
            </div>
            <div class="form-group">
              <label for="estado">Estado (UF)</label>
              <input type="text" id="estado" v-model="cliente.estado" maxlength="2" />
            </div>
          </div>
        </div>

        <div class="form-card">
          <h3 class="card-title">Outras Informações</h3>
          <div class="card-content">
            <div class="form-group">
              <label for="tipo">Tipo de Cliente</label>
              <select id="tipo" v-model="cliente.tipo">
                <option value="PROPRIETARIO">Proprietário</option>
                <option value="INTERESSADO">Interessado</option>
                <option value="AMBOS">Ambos</option>
              </select>
            </div>
            <div class="form-group">
              <label for="observacoes">Observações</label>
              <textarea id="observacoes" v-model="cliente.observacoes" rows="4"></textarea>
            </div>
             <div class="checkbox-group">
                 <input type="checkbox" id="ativo" v-model="cliente.ativo">
                 <label for="ativo">Cliente Ativo</label>
             </div>
          </div>
        </div>
      </div> <div class="form-actions">
        <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'A guardar...' : (isEditing ? 'Atualizar Cliente' : 'Guardar Cliente') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';

const route = useRoute();
const router = useRouter();

const clienteId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!clienteId.value);
const isLoadingData = ref(false);
const isSubmitting = ref(false);

const profilePicFile = ref<File | null>(null);
const profilePicPreview = ref<string | null>(null);

const createEmptyCliente = () => ({
  id: null,
  tipo_pessoa: 'FISICA', // Valor inicial default
  nome_completo: '',
  razao_social: '',
  nome_fantasia: '',
  documento: '', // CPF ou CNPJ
  data_nascimento: null,
  email: '',
  telefone: '',
  telefone_alternativo: '',
  foto_perfil: null,
  tipo: 'INTERESSADO',
  observacoes: '',
  cep: '',
  logradouro: '',
  numero: '',
  complemento: '',
  bairro: '',
  cidade: '',
  estado: '',
  ativo: true,
});

const cliente = ref(createEmptyCliente());

function onTipoPessoaChange(event: Event) {
    const target = event.target as HTMLInputElement;
    cliente.value.tipo_pessoa = target.value === 'FISICA' ? 'FISICA' : 'JURIDICA';
    // Limpar campos específicos do outro tipo ao trocar
    if (cliente.value.tipo_pessoa === 'FISICA') {
        cliente.value.razao_social = '';
        cliente.value.nome_fantasia = '';
    } else {
        cliente.value.nome_completo = '';
        cliente.value.data_nascimento = null;
    }
    cliente.value.documento = ''; // Limpar documento ao trocar
}


watch(clienteId, (newId) => {
  if (newId) {
    fetchClienteData(newId);
  } else {
    // Resetar formulário se navegou para a rota de criação
    cliente.value = createEmptyCliente();
    profilePicFile.value = null;
    profilePicPreview.value = null;
  }
}, { immediate: true }); // Executa imediatamente ao montar

async function fetchClienteData(id: string) {
  isLoadingData.value = true;
  try {
    const { data } = await apiClient.get(`/v1/clientes/${id}/`);
    // Ajuste para garantir que tipo_pessoa seja 'FISICA' ou 'JURIDICA'
    const tipoPessoaCorrigido = data.tipo_pessoa === 'PF' ? 'FISICA' : (data.tipo_pessoa === 'PJ' ? 'JURIDICA' : 'FISICA');

    cliente.value = { ...createEmptyCliente(), ...data, tipo_pessoa: tipoPessoaCorrigido }; // Mescla com o objeto vazio para garantir todos os campos
    profilePicPreview.value = cliente.value.foto_perfil || null; // Define a pré-visualização da foto existente
  } catch (error) {
    console.error('Erro ao carregar dados do cliente:', error);
    alert('Não foi possível carregar os dados do cliente.');
    router.push('/clientes'); // Redireciona em caso de erro
  } finally {
    isLoadingData.value = false;
  }
}

async function fetchAddressFromCEP() {
    const cep = cliente.value.cep?.replace(/\D/g, ''); // Remove não-dígitos
    if (cep && cep.length === 8) {
        try {
            const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
            if (!response.ok) throw new Error('CEP não encontrado');
            const data = await response.json();
            if (data.erro) throw new Error('CEP inválido');

            cliente.value.logradouro = data.logradouro;
            cliente.value.bairro = data.bairro;
            cliente.value.cidade = data.localidade;
            cliente.value.estado = data.uf;
            // Opcional: focar no campo número
            // document.getElementById('numero')?.focus();
        } catch (error) {
            console.warn("Erro ao buscar CEP:", error);
            // Poderia adicionar um feedback visual para o usuário aqui
        }
    }
}


function handleProfilePicChange(event: Event) {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    profilePicFile.value = input.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      profilePicPreview.value = e.target?.result as string;
    };
    reader.readAsDataURL(profilePicFile.value);
  }
}

function removeProfilePic() {
  profilePicFile.value = null;
  profilePicPreview.value = null;
  cliente.value.foto_perfil = null; // Garante que a foto existente seja removida no backend se salvar
}

async function handleSubmit() {
  isSubmitting.value = true;
  const formData = new FormData();

  // Mapeia o tipo_pessoa do frontend para o backend
  const tipoPessoaBackend = cliente.value.tipo_pessoa === 'FISICA' ? 'PF' : 'PJ';
  formData.append('tipo_pessoa', tipoPessoaBackend);

  // Adiciona campos baseados no tipo de pessoa
  if (cliente.value.tipo_pessoa === 'FISICA') {
      formData.append('nome_completo', cliente.value.nome_completo);
      if (cliente.value.data_nascimento) {
          formData.append('data_nascimento', cliente.value.data_nascimento);
      }
  } else {
      formData.append('razao_social', cliente.value.razao_social);
      if (cliente.value.nome_fantasia) {
          formData.append('nome_fantasia', cliente.value.nome_fantasia);
      }
  }

  // Adiciona campos comuns, tratando valores nulos ou vazios como strings vazias
  formData.append('documento', cliente.value.documento || '');
  formData.append('email', cliente.value.email || '');
  formData.append('telefone', cliente.value.telefone || '');
  formData.append('telefone_alternativo', cliente.value.telefone_alternativo || '');
  formData.append('tipo', cliente.value.tipo);
  formData.append('observacoes', cliente.value.observacoes || '');
  formData.append('cep', cliente.value.cep || '');
  formData.append('logradouro', cliente.value.logradouro || '');
  formData.append('numero', cliente.value.numero || '');
  formData.append('complemento', cliente.value.complemento || '');
  formData.append('bairro', cliente.value.bairro || '');
  formData.append('cidade', cliente.value.cidade || '');
  formData.append('estado', cliente.value.estado || '');
  formData.append('ativo', cliente.value.ativo ? 'true' : 'false');


  // Adiciona a foto apenas se uma nova foi selecionada
  if (profilePicFile.value) {
    formData.append('foto_perfil', profilePicFile.value);
  } else if (cliente.value.foto_perfil === null && isEditing.value) {
    // Se a foto foi removida (preview é null) e estamos editando,
    // precisamos informar o backend para remover a foto.
    // Isso pode variar dependendo da API (enviar null, string vazia, ou um campo específico).
    // Assumindo que enviar 'foto_perfil' vazio remove a foto:
    formData.append('foto_perfil', '');
  }

  try {
    let response;
    if (isEditing.value && clienteId.value) {
      // Usar PATCH para atualização parcial, PUT para substituição total
      response = await apiClient.patch(`/v1/clientes/${clienteId.value}/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    } else {
      response = await apiClient.post('/v1/clientes/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    }

    if (response.data) {
        alert(`Cliente ${isEditing.value ? 'atualizado' : 'criado'} com sucesso!`);
        router.push('/clientes');
    }

  } catch (error: any) {
    console.error("Erro ao guardar o cliente:", error.response?.data || error);
    // Tenta extrair mensagens de erro específicas da resposta da API
    let errorMessage = `Ocorreu um erro ao ${isEditing.value ? 'atualizar' : 'criar'} o cliente.`;
    if (error.response?.data) {
        // Tenta pegar a primeira mensagem de erro de campo ou erro geral
        const errors = error.response.data;
        const firstErrorKey = Object.keys(errors)[0];
        if (firstErrorKey && Array.isArray(errors[firstErrorKey])) {
            errorMessage += ` Detalhe: ${errors[firstErrorKey][0]}`;
        } else if (typeof errors === 'string') {
            errorMessage += ` Detalhe: ${errors}`;
        }
    }
    alert(errorMessage);
  } finally {
    isSubmitting.value = false;
  }
}


function handleCancel() {
  router.push('/clientes');
}
</script>


<style scoped>
.form-container {
  padding: 0; /* Espaçamento removido */
  max-width: 1200px; /* Limita largura máxima para melhor leitura */
  margin: 0 auto; /* Centraliza */
}

/* Regras .view-header, .header-actions removidas */

.cliente-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem; /* Espaço entre os cards e botões */
}

.main-form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); /* Grid responsivo */
    gap: 1.5rem; /* Espaço entre os cards do grid */
}

.form-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  padding: 1.5rem 2rem; /* Padding interno do card */
}
/* Faz o card de dados pessoais/empresariais ocupar mais espaço se possível */
.grid-col-span-2 {
    grid-column: span 2;
}
@media (max-width: 1100px) { /* Em telas menores, volta a ocupar 1 coluna */
    .grid-col-span-2 {
        grid-column: span 1;
    }
}


.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #343a40;
  margin-top: 0;
  margin-bottom: 1.5rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid #e9ecef;
}

/* Grid interno para alinhar foto e campos */
.card-content-grid {
    display: grid;
    grid-template-columns: auto 1fr; /* Coluna da foto com largura automática, campos ocupam o resto */
    gap: 2rem; /* Espaço entre a área da foto e os campos */
    align-items: flex-start; /* Alinha no topo */
}
@media (max-width: 768px) { /* Em telas menores, empilha a foto e os campos */
    .card-content-grid {
        grid-template-columns: 1fr; /* Uma coluna */
    }
    .profile-pic-area {
        margin-bottom: 1.5rem; /* Adiciona espaço abaixo da foto */
    }
}


.profile-pic-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.8rem; /* Espaço entre preview e botões */
}

.profile-pic-preview {
  width: 130px; /* Tamanho maior */
  height: 130px;
  border-radius: 50%;
  overflow: hidden;
  background-color: #e9ecef;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 3px solid #dee2e6; /* Borda suave */
  margin-bottom: 0.5rem; /* Espaço abaixo do preview */
}
.profile-img { width: 100%; height: 100%; object-fit: cover; }
.profile-icon { font-size: 60px; color: #adb5bd; }

.upload-btn, .remove-btn { width: 100%; }
.remove-btn { background-color: #f8d7da; color: #dc3545; border-color: #f5c6cb; }
.remove-btn:hover { background-color: #f1aeb5; }

/* Área dos campos de texto */
.fields-area {
    display: grid;
    /* Duas colunas de campos, responsivo */
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem 1.5rem; /* Espaço vertical e horizontal entre campos */
}

.form-group { display: flex; flex-direction: column; }
label { margin-bottom: 0.4rem; font-weight: 500; font-size: 0.9rem; color: #495057; }
input[type="text"],
input[type="email"],
input[type="date"],
select,
textarea {
  padding: 0.75rem; /* Padding interno */
  border: 1px solid #ced4da; /* Borda suave */
  border-radius: 6px; /* Bordas arredondadas */
  font-size: 0.95rem; /* Tamanho da fonte */
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
input:focus, select:focus, textarea:focus {
  border-color: #86b7fe;
  outline: 0;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}
textarea { resize: vertical; min-height: 80px; }

.checkbox-group {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-top: 0.5rem; /* Espaço acima */
}
.checkbox-group input[type="checkbox"] {
    width: 1.1em; /* Tamanho do checkbox */
    height: 1.1em;
    cursor: pointer;
}
.checkbox-group label {
    margin-bottom: 0; /* Remove margem padrão */
    font-weight: normal;
    cursor: pointer;
    font-size: 0.95rem;
}


.form-actions {
  display: flex;
  justify-content: flex-end; /* Alinha botões à direita */
  gap: 1rem;
  margin-top: 1rem; /* Espaço acima dos botões */
  padding: 1.5rem 2rem; /* Padding para consistência */
  background-color: #fff; /* Fundo */
  border-radius: 8px; /* Bordas */
  box-shadow: 0 2px 5px rgba(0,0,0,0.1); /* Sombra */
}

/* Estilos gerais de botões */
.btn-primary, .btn-secondary, .btn-action {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.95rem;
    font-weight: 500;
    transition: background-color 0.2s ease, border-color 0.2s ease;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem; /* Espaço entre ícone e texto */
}
.btn-primary { background-color: #0d6efd; color: white; }
.btn-primary:hover { background-color: #0b5ed7; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #5c636a; }
.btn-action { background-color: #f8f9fa; color: #343a40; border: 1px solid #ced4da; }
.btn-action:hover { background-color: #e9ecef; }
.btn-action i { margin-right: 0; } /* Remove margem extra do ícone se usar gap */
.loading-message { text-align: center; padding: 3rem; font-size: 1.2rem; color: #6c757d; }
input[type="file"] { display: none; } /* Esconde input file padrão */

/* Estilos para o seletor de tipo de pessoa */
.tipo-pessoa-selector {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin-bottom: 1.5rem; /* Espaço abaixo */
    padding-bottom: 1rem;
    border-bottom: 1px solid #eee;
}
.tipo-pessoa-label {
    font-size: 1.1rem;
    font-weight: 600;
    color: #495057;
    margin: 0;
}
.tipo-pessoa-options {
    display: flex;
    gap: 1rem;
    align-items: center;
}
.radio-option {
    display: flex;
    align-items: center;
    cursor: pointer;
    font-size: 0.9rem;
    padding: 0.6rem 1rem;
    border: 1px solid #ced4da;
    border-radius: 6px;
    background-color: #fff;
    transition: background-color 0.2s, border-color 0.2s;
}
.radio-option input[type="radio"] {
    margin-right: 0.5rem;
    accent-color: #0d6efd; /* Cor do radio selecionado */
}
.radio-option:hover {
    background-color: #f8f9fa;
}
input[type="radio"]:checked + span {
    font-weight: 600;
    color: #0d6efd;
}
.radio-option input[type="radio"]:checked ~ span { /* Para estilizar o span quando selecionado */
   /* Se precisar de estilo adicional no texto quando selecionado */
}
.radio-option:has(input:checked) { /* Estiliza o container quando selecionado */
    border-color: #0d6efd;
    background-color: #e7f1ff;
}

</style>