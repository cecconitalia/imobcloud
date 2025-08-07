<template>
  <div class="form-container">
    <header class="view-header">
      <h1>{{ isEditing ? `Editar Imóvel #${imovel.codigo_referencia}` : 'Adicionar Novo Imóvel' }}</h1>
      <router-link to="/imoveis" class="btn-secondary">Voltar à Lista</router-link>
    </header>

    <div v-if="isLoadingData" class="loading-message">
      A carregar dados do imóvel...
    </div>

    <form v-else @submit.prevent="handleSaveAndExit" class="imovel-form">
      <div class="tabs">
        <button type="button" @click="activeTab = 'geral'" :class="{ active: activeTab === 'geral' }">Geral</button>
        <button type="button" @click="activeTab = 'valores'" :class="{ active: activeTab === 'valores' }">Valores e Medidas</button>
        <button type="button" @click="activeTab = 'caracteristicas'" :class="{ active: activeTab === 'caracteristicas' }">Características</button>
        <button type="button" @click="activeTab = 'condominio'" :class="{ active: activeTab === 'condominio' }">Condomínio</button>
        <button type="button" @click="activeTab = 'autorizacao'" :class="{ active: activeTab === 'autorizacao' }">Autorização</button>
      </div>

      <div class="tab-content">
        <div v-show="activeTab === 'geral'" class="form-grid">
          <div class="form-group full-width">
            <label for="titulo_anuncio">Título do Anúncio</label>
            <input type="text" id="titulo_anuncio" v-model="imovel.titulo_anuncio" required />
          </div>
          <div class="form-group">
            <label for="tipo">Tipo de Imóvel</label>
            <select id="tipo" v-model="imovel.tipo" required>
              <option value="CASA">Casa</option>
              <option value="APARTAMENTO">Apartamento</option>
              <option value="TERRENO">Terreno</option>
              <option value="SALA_COMERCIAL">Sala Comercial</option>
              <option value="GALPAO">Galpão</option>
              <option value="RURAL">Rural</option>
              <option value="OUTRO">Outro</option>
            </select>
          </div>
          <div class="form-group">
            <label for="finalidade">Finalidade</label>
            <select id="finalidade" v-model="imovel.finalidade" required>
                <option value="RESIDENCIAL">Residencial</option>
                <option value="COMERCIAL">Comercial</option>
                <option value="INDUSTRIAL">Industrial</option>
                <option value="RURAL">Rural</option>
            </select>
          </div>
          <div class="form-group">
            <label for="status">Status</label>
            <select id="status" v-model="imovel.status" required>
              <option value="A_VENDA">À Venda</option>
              <option value="PARA_ALUGAR">Para Alugar</option>
              <option value="VENDIDO">Vendido</option>
              <option value="ALUGADO">Alugado</option>
              <option value="EM_CONSTRUCAO">Em Construção</option>
              <option value="DESATIVADO">Desativado</option>
            </select>
          </div>
          <div class="form-group">
            <label for="situacao">Situação do Imóvel</label>
            <select id="situacao" v-model="imovel.situacao">
                <option :value="null">Não informado</option>
                <option value="NOVO">Novo</option>
                <option value="USADO">Usado</option>
                <option value="NA_PLANTA">Na Planta</option>
            </select>
          </div>
          <div class="form-group full-width">
            <label for="endereco">Endereço Completo</label>
            <input type="text" id="endereco" v-model="imovel.endereco" required />
          </div>
          <div class="form-group">
            <label for="bairro">Bairro</label>
            <input type="text" id="bairro" v-model="imovel.bairro" required />
          </div>
          <div class="form-group">
            <label for="cidade">Cidade</label>
            <input type="text" id="cidade" v-model="imovel.cidade" required />
          </div>
          <div class="form-group">
            <label for="estado">Estado (UF)</label>
            <input type="text" id="estado" maxlength="2" v-model="imovel.estado" required />
          </div>
          <div class="form-group">
            <label for="cep">CEP</label>
            <input type="text" id="cep" v-model="imovel.cep" />
          </div>
        </div>

        <div v-show="activeTab === 'valores'" class="form-grid">
            <div class="form-group">
                <label for="valor_venda">Valor de Venda (R$)</label>
                <input type="number" step="0.01" id="valor_venda" v-model.number="imovel.valor_venda" />
            </div>
            <div class="form-group">
                <label for="valor_aluguel">Valor de Aluguel (R$)</label>
                <input type="number" step="0.01" id="valor_aluguel" v-model.number="imovel.valor_aluguel" />
            </div>
            <div class="form-group">
                <label for="valor_condominio">Valor do Condomínio (R$)</label>
                <input type="number" step="0.01" id="valor_condominio" v-model.number="imovel.valor_condominio" />
            </div>
            <div class="form-group">
                <label for="valor_iptu">Valor do IPTU (Anual, R$)</label>
                <input type="number" step="0.01" id="valor_iptu" v-model.number="imovel.valor_iptu" />
            </div>
            <div class="form-group">
                <label for="area_total">Área Total (m²)</label>
                <input type="number" step="0.01" id="area_total" v-model.number="imovel.area_total" />
            </div>
            <div class="form-group">
                <label for="area_util">Área Útil (m²)</label>
                <input type="number" step="0.01" id="area_util" v-model.number="imovel.area_util" />
            </div>
            <div class="form-group">
                <label for="quartos">Quartos</label>
                <input type="number" id="quartos" v-model.number="imovel.quartos" />
            </div>
            <div class="form-group">
                <label for="suites">Suítes</label>
                <input type="number" id="suites" v-model.number="imovel.suites" />
            </div>
            <div class="form-group">
                <label for="banheiros">Banheiros</label>
                <input type="number" id="banheiros" v-model.number="imovel.banheiros" />
            </div>
            <div class="form-group">
                <label for="vagas_garagem">Vagas de Garagem</label>
                <input type="number" id="vagas_garagem" v-model.number="imovel.vagas_garagem" />
            </div>
        </div>
        
        <div v-show="activeTab === 'caracteristicas'" class="form-grid checkbox-grid">
            <div class="checkbox-group">
                <input type="checkbox" id="lavabo" v-model="imovel.lavabo">
                <label for="lavabo">Lavabo</label>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="escritorio" v-model="imovel.escritorio">
                <label for="escritorio">Escritório</label>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="varanda" v-model="imovel.varanda">
                <label for="varanda">Varanda / Sacada</label>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="mobiliado" v-model="imovel.mobiliado">
                <label for="mobiliado">Mobiliado</label>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="ar_condicionado" v-model="imovel.ar_condicionado">
                <label for="ar_condicionado">Ar Condicionado</label>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="moveis_planejados" v-model="imovel.moveis_planejados">
                <label for="moveis_planejados">Móveis Planejados</label>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="piscina_privativa" v-model="imovel.piscina_privativa">
                <label for="piscina_privativa">Piscina Privativa</label>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="churrasqueira_privativa" v-model="imovel.churrasqueira_privativa">
                <label for="churrasqueira_privativa">Churrasqueira Privativa</label>
            </div>
        </div>

        <div v-show="activeTab === 'condominio'" class="form-grid checkbox-grid">
            <div class="checkbox-group">
                <input type="checkbox" id="portaria_24h" v-model="imovel.portaria_24h">
                <label for="portaria_24h">Portaria 24h</label>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="elevador" v-model="imovel.elevador">
                <label for="elevador">Elevador</label>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="piscina_condominio" v-model="imovel.piscina_condominio">
                <label for="piscina_condominio">Piscina no Condomínio</label>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="academia" v-model="imovel.academia">
                <label for="academia">Academia</label>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="salao_festas" v-model="imovel.salao_festas">
                <label for="salao_festas">Salão de Festas</label>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="playground" v-model="imovel.playground">
                <label for="playground">Playground</label>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="quadra_esportiva" v-model="imovel.quadra_esportiva">
                <label for="quadra_esportiva">Quadra Esportiva</label>
            </div>
             <div class="checkbox-group">
                <input type="checkbox" id="espaco_pet" v-model="imovel.espaco_pet">
                <label for="espaco_pet">Espaço Pet</label>
            </div>
        </div>

        <div v-show="activeTab === 'autorizacao'" class="form-grid">
            <div class="form-group">
                <label for="proprietario">Proprietário (Cliente)</label>
                <select id="proprietario" v-model="imovel.proprietario">
                    <option :value="null">-- Selecione um Cliente --</option>
                    <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">
                        {{ cliente.nome_completo }}
                    </option>
                </select>
            </div>
            <div class="form-group">
                <label for="numero_matricula">Número da Matrícula</label>
                <input type="text" id="numero_matricula" v-model="imovel.numero_matricula" />
            </div>
            <div class="form-group">
                <label for="data_captacao">Data de Captação</label>
                <input type="date" id="data_captacao" v-model="imovel.data_captacao" />
            </div>
            <div class="form-group">
                <label for="data_fim_autorizacao">Data de Fim da Autorização</label>
                <input type="date" id="data_fim_autorizacao" v-model="imovel.data_fim_autorizacao" />
            </div>
            <div class="form-group">
                <label for="comissao_percentual">Comissão (%)</label>
                <input type="number" step="0.01" id="comissao_percentual" v-model.number="imovel.comissao_percentual" />
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="possui_exclusividade" v-model="imovel.possui_exclusividade">
                <label for="possui_exclusividade">Possui Contrato de Exclusividade?</label>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="publicado_no_site" v-model="imovel.publicado_no_site">
                <label for="publicado_no_site">Publicar no site? (Ativar anúncio)</label>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="financiavel" v-model="imovel.financiavel">
                <label for="financiavel">Aceita Financiamento</label>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="quitado" v-model="imovel.quitado">
                <label for="quitado">Imóvel Quitado</label>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="documentacao_ok" v-model="imovel.documentacao_ok">
                <label for="documentacao_ok">Documentação OK</label>
            </div>
            <div class="form-group full-width">
                <label for="informacoes_adicionais_autorizacao">Informações Adicionais (para o contrato)</label>
                <textarea id="informacoes_adicionais_autorizacao" v-model="imovel.informacoes_adicionais_autorizacao" rows="4"></textarea>
            </div>
            
            <div class="form-group full-width" v-if="isEditing">
                <button type="button" @click="gerarContratoPDF" class="btn-info">
                    Gerar Contrato de Autorização (PDF)
                </button>
            </div>
        </div>

      </div>

      <div class="form-actions full-width">
        <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
        <button type="button" @click="handleSaveAndContinue" class="btn-info-outline" :disabled="isSubmitting">
          {{ isSubmitting ? 'A guardar...' : 'Salvar e Continuar' }}
        </button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'A guardar...' : 'Salvar e Sair' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';

const route = useRoute();
const router = useRouter();

const imovelId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!imovelId.value);
const activeTab = ref('geral');
const clientes = ref<any[]>([]);

const imovel = ref({
  titulo_anuncio: '',
  codigo_referencia: '',
  tipo: 'CASA',
  finalidade: 'RESIDENCIAL',
  status: 'A_VENDA',
  situacao: null,
  disponibilidade: null,
  publicado_no_site: true,
  valor_venda: null,
  valor_aluguel: null,
  valor_condominio: null,
  valor_iptu: null,
  endereco: '',
  bairro: '',
  cidade: '',
  estado: '',
  cep: '',
  posicao_solar: null,
  andar: null,
  vista: '',
  ponto_referencia: '',
  localizacao_condominio: '',
  area_construida: null,
  area_util: null,
  area_total: null,
  area_terreno: null,
  dimensao_frente: null,
  dimensao_fundos: null,
  dimensao_direita: null,
  dimensao_esquerda: null,
  ano_construcao: null,
  numero_pavimentos: 1,
  unidades_por_andar: null,
  tipo_construcao: null,
  pe_direito: null,
  quartos: 0,
  suites: 0,
  banheiros: 0,
  vagas_garagem: 0,
  lavabo: false,
  sala_estar: false,
  sala_jantar: false,
  sala_tv: false,
  cozinha: false,
  copa: false,
  escritorio: false,
  area_servico: false,
  despensa: false,
  closet: false,
  varanda: false,
  vaga_coberta: false,
  vaga_privativa: false,
  portao_eletronico: false,
  ar_condicionado: false,
  aquecimento: '',
  gas_central: false,
  hidrometro_individual: false,
  piso: '',
  moveis_planejados: false,
  churrasqueira_privativa: false,
  piscina_privativa: false,
  piscina_condominio: false,
  churrasqueira_condominio: false,
  espaco_gourmet: false,
  playground: false,
  salao_festas: false,
  academia: false,
  quadra_esportiva: false,
  sauna: false,
  espaco_pet: false,
  portaria_24h: false,
  elevador: false,
  vagas_visitantes: false,
  bicicletario: false,
  financiavel: false,
  aceita_permuta: false,
  quitado: false,
  documentacao_ok: false,
  descricao_completa: '',
  aceita_pet: false,
  mobiliado: false,
  proprietario: null,
  numero_matricula: '',
  data_captacao: null,
  data_fim_autorizacao: null,
  possui_exclusividade: false,
  comissao_percentual: null,
  // NOVO CAMPO
  informacoes_adicionais_autorizacao: '',
});

const isLoadingData = ref(false);
const isSubmitting = ref(false);

async function fetchClientes() {
    try {
        const response = await apiClient.get('/v1/clientes/clientes/');
        clientes.value = response.data;
    } catch (error) {
        console.error("Erro ao buscar clientes:", error);
        alert("Não foi possível carregar a lista de proprietários.");
    }
}

async function fetchImovelData() {
  if (isEditing.value) {
    isLoadingData.value = true;
    try {
      const response = await apiClient.get(`/v1/imoveis/imoveis/${imovelId.value}/`);
      imovel.value = response.data;
    } catch (error) {
      console.error("Erro ao buscar dados do imóvel:", error);
      alert("Não foi possível carregar os dados do imóvel para edição.");
      router.push({ name: 'imoveis' });
    } finally {
      isLoadingData.value = false;
    }
  }
}

async function gerarContratoPDF() {
    if (!imovelId.value) return;
    if (!imovel.value.proprietario || !imovel.value.data_captacao || !imovel.value.data_fim_autorizacao) {
        alert("Para gerar o contrato, por favor, preencha os campos: Proprietário, Data de Captação e Data de Fim da Autorização.");
        return;
    }
    try {
        const response = await apiClient.get(`/v1/imoveis/imoveis/${imovelId.value}/gerar-autorizacao-pdf/`, {
            responseType: 'blob',
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        const contentDisposition = response.headers['content-disposition'];
        let fileName = `autorizacao_imovel_${imovel.value.codigo_referencia}.pdf`;
        if (contentDisposition) {
            const fileNameMatch = contentDisposition.match(/filename="(.+)"/);
            if (fileNameMatch && fileNameMatch.length === 2)
                fileName = fileNameMatch[1];
        }
        link.setAttribute('download', fileName);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
    } catch (error: any) {
        console.error("Erro ao gerar PDF:", error);
        if (error.response && error.response.data) {
            const reader = new FileReader();
            reader.onload = () => {
                alert(`Erro ao gerar PDF: ${reader.result}`);
            };
            reader.readAsText(error.response.data);
        } else {
            alert("Ocorreu um erro desconhecido ao gerar o PDF.");
        }
    }
}


onMounted(() => {
  fetchImovelData();
  fetchClientes();
});

async function saveImovel() {
  isSubmitting.value = true;
  const payload = { ...imovel.value };
  for (const key in payload) {
    if (payload[key as keyof typeof payload] === null) {
      delete payload[key as keyof typeof payload];
    }
  }
  try {
    if (isEditing.value) {
      return await apiClient.put(`/v1/imoveis/imoveis/${imovelId.value}/`, payload);
    } else {
      return await apiClient.post('/v1/imoveis/imoveis/', payload);
    }
  } catch (error: any) {
    console.error("Erro ao guardar o imóvel:", error.response?.data || error);
    alert('Ocorreu um erro ao guardar o imóvel. Verifique os dados.');
    return null;
  } finally {
    isSubmitting.value = false;
  }
}

async function handleSaveAndExit() {
  const response = await saveImovel();
  if (response) {
    router.push({ name: 'imoveis' });
  }
}

async function handleSaveAndContinue() {
  const response = await saveImovel();
  if (response) {
    if (!isEditing.value) {
      const newId = response.data.id;
      router.push({ name: 'imovel-editar', params: { id: newId } });
    } else {
      alert('Imóvel guardado com sucesso!');
      fetchImovelData();
    }
  }
}

function handleCancel() {
  router.push({ name: 'imoveis' });
}
</script>

<style scoped>
.form-container { padding: 2rem; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }

.tabs {
  display: flex;
  flex-wrap: wrap;
  border-bottom: 2px solid #ccc;
  margin-bottom: 1.5rem;
  width: 100%;
}
.tabs button {
  padding: 10px 20px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  color: #6c757d;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
}
.tabs button.active {
  color: #007bff;
  border-bottom-color: #007bff;
  font-weight: bold;
}
.tab-content {
    width: 100%;
}

.imovel-form { display: flex; flex-wrap: wrap; gap: 1.5rem; }
.form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    width: 100%;
}
.form-group { display: flex; flex-direction: column; }
.form-group.full-width { grid-column: 1 / -1; }
label { margin-bottom: 0.5rem; font-weight: bold; }
input, select, textarea { padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; }

.checkbox-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
}
.checkbox-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.checkbox-group input[type="checkbox"] {
    width: auto;
}
.checkbox-group label {
    margin-bottom: 0;
    font-weight: normal;
}

.form-actions { display: flex; justify-content: flex-end; gap: 1rem; width: 100%; margin-top: 1rem; }
.btn-primary, .btn-secondary, .btn-info, .btn-info-outline { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; font-weight: bold; }
.btn-primary { background-color: #007bff; color: white; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-info { background-color: #17a2b8; color: white; width: 100%; }
.btn-info-outline {
  background-color: white;
  color: #17a2b8;
  border: 1px solid #17a2b8;
}
.loading-message { text-align: center; padding: 2rem; }
</style>