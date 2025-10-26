<template>
  <div class="contatos-container">
    <div v-if="isLoading" class="loading-message">Carregando contatos...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <table v-if="contatos.length > 0" class="contatos-table">
      <thead>
        <tr>
          <th>Imóvel</th>
          <th>Nome</th>
          <th>Email</th>
          <th>Telefone</th>
          <th>Mensagem</th>
          <th>Data</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="contato in contatos" :key="contato.id">
          <td>
            <router-link v-if="contato.imovel_obj?.id" :to="`/imoveis/editar/${contato.imovel_obj.id}`">
              {{ contato.imovel_obj?.codigo_referencia || 'Link' }}
            </router-link>
            <span v-else>N/A</span>
             ({{ contato.imovel_obj?.tipo || 'N/A' }})
          </td>
          <td>{{ contato.nome }}</td>
          <td>{{ contato.email }}</td>
          <td>{{ contato.telefone || 'Não informado' }}</td>
          <td class="mensagem-cell">{{ contato.mensagem }}</td>
          <td>{{ formatarData(contato.data_contato) }}</td>
          <td class="actions-cell">
            <button class="btn-sm btn-info" @click="handleResponder(contato)">Responder</button>
            <button class="btn-sm btn-secondary" @click="handleArquivar(contato)">Arquivar</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="!isLoading && contatos.length === 0 && !error" class="no-data-message">
      <p>Nenhum contato encontrado.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api'; // Certifique-se que o caminho está correto

interface ImovelResumo {
  id: number;
  codigo_referencia?: string;
  tipo?: string;
  endereco?: string; // Mantido caso a API envie
}

interface Contato {
  id: number;
  imovel: number;
  imovel_obj?: ImovelResumo; // Detalhes do imóvel (opcional, dependendo da API)
  nome: string;
  email: string;
  telefone?: string;
  mensagem: string;
  data_contato: string;
  arquivado: boolean;
}

const contatos = ref<Contato[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

async function fetchContatos() {
  isLoading.value = true;
  error.value = null;
  try {
    // A URL assume que a listagem de contatos não arquivados está neste endpoint
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

function formatarData(data: string | null): string {
  if (!data) return 'N/A';
  const options: Intl.DateTimeFormatOptions = {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  };
  try {
      return new Date(data).toLocaleString('pt-BR', options);
  } catch {
      return 'Data inválida';
  }
}


function handleResponder(contato: Contato) {
    // Abrir cliente de email padrão com informações preenchidas
    const subject = `Contato sobre imóvel ${contato.imovel_obj?.codigo_referencia || contato.imovel}`;
    const body = `Olá ${contato.nome},\n\nEm resposta à sua mensagem:\n"${contato.mensagem}"\n\n`;
    window.location.href = `mailto:${contato.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}


async function handleArquivar(contato: Contato) {
  if (!window.confirm(`Tem a certeza de que deseja arquivar o contato de ${contato.nome}?`)) {
    return;
  }
  try {
    // Endpoint para arquivar o contato
    await apiClient.post(`/v1/contatos/${contato.id}/arquivar/`);
    // Remove o contato da lista local após arquivar com sucesso
    contatos.value = contatos.value.filter(c => c.id !== contato.id);
    alert(`Contato de ${contato.nome} arquivado com sucesso.`);
  } catch(err) {
      console.error("Erro ao arquivar contato:", err);
      alert(`Ocorreu um erro ao arquivar o contato de ${contato.nome}.`);
  }
}
</script>

<style scoped>
.contatos-container {
  padding: 0; /* Espaçamento removido */
}

/* Regra .view-header removida */

.loading-message, .error-message, .no-data-message {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: #6c757d;
}
.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.contatos-table { /* Adicionado para aplicar estilos específicos à tabela */
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem; /* Margem para separar da borda superior */
  background-color: #fff; /* Fundo branco para a tabela */
  box-shadow: 0 2px 4px rgba(0,0,0,0.05); /* Sombra suave */
  border-radius: 8px; /* Bordas arredondadas */
  overflow: hidden; /* Garante que o border-radius funcione */
}

th, td {
  border-bottom: 1px solid #dee2e6; /* Linha divisória mais suave */
  padding: 12px 15px;
  text-align: left;
  vertical-align: middle;
}

th {
  background-color: #f8f9fa; /* Fundo do cabeçalho */
  font-weight: 600; /* Peso da fonte do cabeçalho */
  color: #495057;
}

tr:hover {
  background-color: #f1f3f5; /* Cor de fundo ao passar o mouse */
}

td a { /* Estilo para links dentro da tabela */
    color: #007bff;
    text-decoration: none;
    font-weight: 500;
}
td a:hover {
    text-decoration: underline;
}

.mensagem-cell {
    max-width: 300px; /* Limita largura da mensagem */
    white-space: normal; /* Permite quebra de linha */
    word-wrap: break-word; /* Quebra palavras longas */
}

.actions-cell {
  white-space: nowrap; /* Impede que os botões quebrem linha */
  text-align: right; /* Alinha botões à direita */
}

.btn-sm { /* Estilo base para botões pequenos */
  padding: 5px 10px;
  font-size: 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  border: none;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
  font-weight: 500;
  margin-left: 0.5rem; /* Espaço entre botões */
  transition: background-color 0.2s;
}

.btn-info { /* Azul claro */
  background-color: #17a2b8;
  color: white;
}
.btn-info:hover {
  background-color: #138496;
}

.btn-secondary { /* Cinza */
  background-color: #6c757d;
  color: white;
}
.btn-secondary:hover {
  background-color: #5a6268;
}

.no-data-message {
  margin-top: 1rem;
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
</style>