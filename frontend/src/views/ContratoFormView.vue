<template>
  <div class="page-container">
    <header class="view-header">
      <h1>{{ isEditing ? 'Editar Contrato' : 'Novo Contrato' }}</h1>
      <div class="header-actions">
        <!-- NOVO BOTÃO: Visualizar PDF -->
        <button
          v-if="isEditing"
          @click="visualizarContrato"
          class="btn-info"
          type="button"
        >
          <i class="fas fa-eye"></i> Visualizar
        </button>
        <button
          v-if="isEditing"
          @click="prepararContrato"
          class="btn-info"
          type="button"
        >
          <i class="fas fa-file-pdf"></i> Gerar/Editar Contrato
        </button>
        <router-link to="/contratos" class="btn-secondary">
          <i class="fas fa-arrow-left"></i> Voltar à Lista
        </router-link>
      </div>
    </header>

    <form @submit.prevent="handleSubmit" class="form-layout">
      <div class="form-card">
        <h3 class="card-title">Detalhes do Contrato</h3>
        <div class="form-grid">
          
          <div class="form-group">
            <label for="tipo_contrato">Tipo de Contrato</label>
            <select id="tipo_contrato" v-model="contrato.tipo_contrato" required>
              <option disabled value="">Selecione o tipo</option>
              <option value="Venda">Venda</option>
              <option value="Aluguel">Aluguel</option>
            </select>
          </div>

          <div class="form-group">
            <label for="status_contrato">Status do Contrato</label>
            <select id="status_contrato" v-model="contrato.status_contrato" required>
              <option disabled value="">Selecione o status</option>
              <option value="Pendente">Pendente</option>
              <option value="Ativo">Ativo</option>
              <option value="Concluído">Concluído</option>
              <option value="Rescindido">Rescindido</option>
              <option value="Inativo">Inativo</option>
            </select>
          </div>

          <div class="form-group">
            <label for="valor_total">Valor Total do Contrato (R$)</label>
            <input type="number" id="valor_total" v-model.number="contrato.valor_total" required step="0.01" />
          </div>

          <div v-if="contrato.tipo_contrato === 'Aluguel'" class="form-group">
            <label for="duracao_meses">Duração (meses)</label>
            <input type="number" id="duracao_meses" v-model.number="contrato.duracao_meses" />
          </div>

          <div class="form-group">
            <label for="data_inicio">Data de Início</label>
            <input type="date" id="data_inicio" v-model="contrato.data_inicio" required />
          </div>

          <div class="form-group">
            <label for="data_assinatura">Data de Assinatura</label>
            <input type="date" id="data_assinatura" v-model="contrato.data_assinatura" required />
          </div>
        </div>
      </div>

      <div class="form-card">
        <h3 class="card-title">Partes Envolvidas</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="imovel">Imóvel</label>
            <select id="imovel" v-model="contrato.imovel" required>
              <option disabled :value="null">Selecione um imóvel</option>
              <option v-for="imovel in imoveis" :key="imovel.id" :value="imovel.id">
                {{ imovel.titulo_anuncio || imovel.logradouro }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="proprietario">Proprietário</label>
            <select
              id="proprietario"
              v-model="contrato.proprietario"
              required
              :disabled="isProprietarioDisabled"
            >
              <option disabled :value="null">Selecione o proprietário</option>
              <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">
                {{ cliente.nome_completo }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="inquilino">Inquilino / Comprador</label>
            <select id="inquilino" v-model="contrato.inquilino" required>
              <option disabled :value="null">Selecione o inquilino/comprador</option>
              <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">
                {{ cliente.nome_completo }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <div class="form-card">
        <h3 class="card-title">Informações Adicionais</h3>
        <div class="form-group full-width">
          <label for="informacoes_adicionais">Cláusulas e Observações</label>
          <textarea id="informacoes_adicionais" v-model="contrato.informacoes_adicionais" rows="5"></textarea>
        </div>
      </div>
      
      <div class="form-actions">
        <button type="button" @click="$router.push('/contratos')" class="btn-secondary">Cancelar</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          <span v-if="isSubmitting" class="spinner-border spinner-border-sm"></span>
          {{ isSubmitting ? 'Salvando...' : 'Salvar Contrato' }}
        </button>
      </div>
    </form>
  </div>

  <!-- Modal de Edição de Contrato -->
  <div v-if="showModal" class="modal-overlay">
    <div class="modal">
      <div class="modal-header">
        <h3>Editar Conteúdo do Contrato</h3>
        <button @click="showModal = false" class="close-btn">&times;</button>
      </div>
      <div class="modal-body">
        <div class="info-message">
          <p>Edite o conteúdo do contrato conforme necessário. A formatação será mantida na geração do PDF.</p>
        </div>
        <!-- Container para o editor Quill -->
        <div ref="editorContainer"></div>
      </div>
      <div class="modal-footer">
        <button @click="showModal = false" class="btn-secondary">Cancelar</button>
        <button @click="salvarEGerarPDF" class="btn-primary" :disabled="isGenerating">
            <span v-if="isGenerating" class="spinner-border spinner-border-sm"></span>
            {{ isGenerating ? 'Salvando e Gerando...' : 'Salvar e Gerar PDF' }}
        </button>
      </div>
    </div>
  </div>

  <!-- Modal de Visualização de Contrato -->
  <div v-if="showVisualizarModal" class="modal-overlay">
    <div class="modal-container">
      <div class="modal-header">
        <h3 class="modal-title">Visualização do Contrato (ID: {{ contrato.id }})</h3>
        <button @click="showVisualizarModal = false" class="modal-close-btn">&times;</button>
      </div>
      <div v-if="loadingModal" class="modal-loading-message">
        <div class="spinner"></div>
        Carregando conteúdo do contrato...
      </div>
      <div v-else-if="modalError" class="modal-error-message">
        {{ modalError }}
      </div>
      <div v-else class="modal-body-visualizar" v-html="contratoHtml"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import '@fortawesome/fontawesome-free/css/all.css';
import Quill from 'quill';
import 'quill/dist/quill.snow.css';
import { useToast } from 'vue-toast-notification';

const route = useRoute();
const router = useRouter();
const toast = useToast();

const contrato = ref({
  id: null,
  tipo_contrato: '',
  status_contrato: 'Pendente',
  valor_total: 0,
  duracao_meses: 12,
  data_inicio: '',
  data_assinatura: '',
  imovel: null as number | null,
  proprietario: null as number | null,
  inquilino: null as number | null,
  informacoes_adicionais: '',
});

const clientes = ref<any[]>([]);
const imoveis = ref<any[]>([]);

const isSubmitting = ref(false);
const contratoId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!contratoId.value);
const isProprietarioDisabled = computed(() => !!contrato.value.imovel);

const showModal = ref(false);
const htmlContent = ref('');
const isGenerating = ref(false);

const editorContainer = ref(null);
let quillEditor: Quill | null = null;

// Variáveis para a modal de visualização
const showVisualizarModal = ref(false);
const contratoHtml = ref('');
const loadingModal = ref(false);
const modalError = ref('');


async function fetchData() {
  try {
    const [clientesRes, imoveisRes] = await Promise.all([
      apiClient.get('/v1/clientes/'),
      apiClient.get('/v1/imoveis/')
    ]);
    clientes.value = clientesRes.data;
    imoveis.value = imoveisRes.data;

    if (isEditing.value) {
      const contratoRes = await apiClient.get(`/v1/contratos/${contratoId.value}/`);
      const data = contratoRes.data;

      contrato.value = {
        ...data,
        imovel: data.imovel?.id || null,
        proprietario: data.proprietario?.id || null,
        inquilino: data.inquilino?.id || null,
      };
    }
  } catch (err) {
    console.error("Erro ao buscar dados para o formulário:", err);
    toast.error("Não foi possível carregar os dados necessários.");
  }
}

onMounted(fetchData);

watch(() => contrato.value.imovel, (newImovelId) => {
  const imovelSelecionado = imoveis.value.find(i => i.id === newImovelId);
  if (imovelSelecionado && imovelSelecionado.proprietario_detalhes) {
    contrato.value.proprietario = imovelSelecionado.proprietario_detalhes.id;
  } else {
    contrato.value.proprietario = null;
  }
});

async function prepararContrato() {
    if (!contrato.value.id) {
        toast.error('Por favor, salve o contrato antes de gerar o PDF.');
        return;
    }
    try {
        const response = await apiClient.get(`/v1/contratos/${contrato.value.id}/get-html/`);
        htmlContent.value = response.data;
        showModal.value = true;
        
        await nextTick();
        
        if (editorContainer.value) {
            if (!quillEditor) {
              quillEditor = new Quill(editorContainer.value, {
                  theme: 'snow',
                  modules: {
                    toolbar: [
                      [{ 'header': [1, 2, 3, false] }],
                      ['bold', 'italic', 'underline', 'strike'],
                      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                      [{ 'script': 'sub'}, { 'script': 'super' }],
                      [{ 'indent': '-1'}, { 'indent': '+1' }],
                      [{ 'direction': 'rtl' }],
                      [{ 'align': [] }],
                      ['link'],
                      ['clean']
                    ]
                  }
              });
              quillEditor.on('text-change', () => {
                  if (quillEditor) {
                      htmlContent.value = quillEditor.root.innerHTML;
                  }
              });
            }
            quillEditor.clipboard.dangerouslyPasteHTML(0, htmlContent.value);
        }
    } catch (error) {
        console.error("Erro ao preparar HTML do contrato:", error);
        toast.error('Ocorreu um erro ao preparar o contrato para edição.');
    }
}

async function salvarEGerarPDF() {
    if (!contrato.value.id || !quillEditor) return;
    isGenerating.value = true;
    try {
        const htmlParaSalvar = quillEditor.root.innerHTML;
        // Passo 1: Salvar o conteúdo HTML no banco de dados
        await apiClient.post(
            `/v1/contratos/${contrato.value.id}/salvar-html-editado/`,
            { html_content: htmlParaSalvar }
        );
        
        // Passo 2: Gerar o PDF a partir do conteúdo salvo
        const response = await apiClient.post(
            `/v1/contratos/${contrato.value.id}/gerar-pdf-editado/`,
            { html_content: htmlParaSalvar },
            { responseType: 'blob' }
        );

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `contrato_${contrato.value.id}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        showModal.value = false;
        toast.success('Contrato salvo e PDF gerado com sucesso!');
    } catch (error) {
        console.error("Erro ao salvar ou gerar PDF:", error);
        toast.error('Ocorreu um erro ao salvar o conteúdo ou gerar o PDF.');
    } finally {
        isGenerating.value = false;
    }
}

async function visualizarContrato() {
  if (!contrato.value.id) {
    toast.error('Por favor, salve o contrato antes de visualizá-lo.');
    return;
  }
  showVisualizarModal.value = true;
  loadingModal.value = true;
  modalError.value = '';
  try {
    const response = await apiClient.get(`/v1/contratos/${contrato.value.id}/get-html/`);
    contratoHtml.value = response.data;
  } catch (err) {
    modalError.value = 'Não foi possível carregar o conteúdo do contrato.';
    toast.error(modalError.value);
  } finally {
    loadingModal.value = false;
  }
}

async function handleSubmit() {
  isSubmitting.value = true;
  
  const payload = { ...contrato.value };

  if (payload.tipo_contrato === 'Venda') {
    payload.duracao_meses = 1;
  }

  try {
    if (isEditing.value) {
      await apiClient.put(`/v1/contratos/${contratoId.value}/`, payload);
      toast.success('Contrato atualizado com sucesso!');
    } else {
      const createRes = await apiClient.post('/v1/contratos/', payload);
      toast.success('Contrato criado com sucesso!');
      router.push(`/contratos/editar/${createRes.data.id}`);
    }
    router.push('/contratos');
  } catch (error: any) {
    console.error("Erro ao salvar contrato:", error.response?.data || error);
    const errorMsg = error.response?.data ? JSON.stringify(error.response.data) : 'Verifique os dados e tente novamente.';
    toast.error(`Ocorreu um erro ao salvar o contrato: ${errorMsg}`);
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
/* Estilos padronizados para o formulário */
.page-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}
.header-actions {
  display: flex;
  gap: 1rem;
}
h1 {
  font-size: 2rem;
}
.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #6c757d;
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}
.btn-secondary:hover {
  background-color: #5a6268;
}
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #007bff;
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  border: none;
  cursor: pointer;
}
.btn-info {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #17a2b8;
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  border: none;
  cursor: pointer;
}

.form-layout {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.form-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  padding: 2rem;
}
.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #007bff;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}
.form-group.full-width {
  grid-column: 1 / -1;
}
label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #495057;
}
input, select, textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 1rem;
  box-sizing: border-box;
}
input:focus, select:focus, textarea:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
  outline: none;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

/* ================== ESTILOS DO MODAL ================== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 900px;
  max-height: 90%;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  color: #333;
}

.modal-header .close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  line-height: 1;
  padding: 0;
}

.modal-body {
  flex-grow: 1;
  overflow-y: auto;
  margin-bottom: 1rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

/* Estilos para a nova modal de visualização */
.modal-container {
  background: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 90%;
  max-width: 900px;
  max-height: 90%;
  overflow-y: auto;
  position: relative;
}

.modal-body-visualizar {
  white-space: pre-wrap;
  font-family: 'Inter', sans-serif;
  color: #333;
  line-height: 1.6;
}
</style>
