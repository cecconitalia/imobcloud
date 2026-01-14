<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Cadastros</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Clientes</span>
           </nav>
           
           <h1>Gerenciar Clientes</h1>
        </div>
        
        <div class="actions-area">
            <button class="btn-icon-thin" @click="fetchClientes" title="Atualizar Lista">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            </button>
            
            <button class="btn-primary-thin" @click="goToCreateCliente">
              <i class="fas fa-plus"></i> Novo Cliente
            </button>
        </div>
      </div>
    </header>

    <div class="kpi-grid">
      <div class="kpi-card blue" :class="{ active: filters.perfil === '' }" @click="setQuickFilter('')">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.total }}</span>
          <span class="kpi-label">Total Clientes</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-users"></i></div>
      </div>
      
      <div class="kpi-card green" :class="{ active: filters.perfil === 'PROPRIETARIO' }" @click="setQuickFilter('PROPRIETARIO')">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.proprietarios }}</span>
          <span class="kpi-label">Proprietários</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-key"></i></div>
      </div>
      
      <div class="kpi-card orange" :class="{ active: filters.perfil === 'INTERESSADO' }" @click="setQuickFilter('INTERESSADO')">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.interessados }}</span>
          <span class="kpi-label">Leads / Interessados</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-bullhorn"></i></div>
      </div>
      
      <div class="kpi-card red" :class="{ active: filters.status === 'INATIVO' }" @click="setQuickFilter('INATIVO')">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.inativos }}</span>
          <span class="kpi-label">Inativos</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-user-slash"></i></div>
      </div>
    </div>

    <div class="toolbar-row">
        <div class="filter-group search-group">
          <label>Buscar</label>
          <div class="input-with-icon">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="filters.search" 
              placeholder="Nome, doc, email..." 
              class="form-control"
              @input="filterList"
            >
          </div>
        </div>

        <div class="filter-group">
          <label>Perfil</label>
          <select v-model="filters.perfil" @change="filterList" class="form-control">
            <option value="">Todos</option>
            <option value="PROPRIETARIO">Proprietário</option>
            <option value="INTERESSADO">Interessado</option>
            <option value="LEAD">Lead</option>
            <option value="COMPRADOR">Comprador</option>
            <option value="INQUILINO">Inquilino</option>
          </select>
        </div>

        <div class="filter-group">
           <label>Status</label>
           <select v-model="filters.status" @change="filterList" class="form-control">
            <option value="">Todos</option>
            <option value="ATIVO">Ativos</option>
            <option value="INATIVO">Inativos</option>
          </select>
        </div>

        <div class="filter-group small-btn">
            <label>&nbsp;</label>
            <button @click="clearFilters" class="btn-clear" title="Limpar Filtros">
                <i class="fas fa-eraser"></i>
            </button>
        </div>
    </div>

    <main class="report-main-wrapper">
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Atualizando base de dados...</p>
      </div>

      <div v-else-if="filteredList.length === 0" class="empty-state">
        <i class="fas fa-filter"></i>
        <p>Nenhum registro encontrado.</p>
      </div>

      <div v-else class="report-scroll-viewport">
        <table class="report-table">
          <thead>
            <tr>
              <th width="35%">Cliente</th>
              <th width="25%">Contatos</th>
              <th width="20%">Classificação</th>
              <th width="10%">Cadastro</th>
              <th width="10%" class="text-right">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cliente in filteredList" :key="cliente.id">
              <td>
                <div class="cell-imovel">
                  <span class="cliente-name">{{ cliente.nome }}</span>
                  <span class="cliente-doc" v-if="cliente.documento">
                    <i class="far fa-id-card"></i> {{ cliente.documento }}
                  </span>
                </div>
              </td>
              <td>
                <div class="contact-info">
                    <div v-if="cliente.email" class="contact-row">
                        <i class="far fa-envelope"></i> {{ cliente.email }}
                    </div>
                    <div v-if="cliente.telefone" class="contact-row">
                        <i class="fab fa-whatsapp"></i> {{ cliente.telefone }}
                    </div>
                </div>
              </td>
              <td>
                <div class="badges-container">
                    <span v-for="(badge, index) in getUniqueBadges(cliente.perfil_cliente)" 
                          :key="index" 
                          class="badge-type" 
                          :class="badge.class">
                        {{ badge.label }}
                    </span>
                </div>
              </td>
              <td class="text-muted">
                  {{ formatDate(cliente.data_criacao) }}
              </td>
              <td class="text-right">
                <div class="actions-flex">
                    <button class="btn-action edit" @click="editCliente(cliente.id)" title="Editar Dados">
                        <i class="fas fa-pen"></i>
                    </button>
                    <button class="btn-action delete" @click="confirmDelete(cliente)" title="Inativar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api';
import { format, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';

const router = useRouter();

interface Cliente {
  id: number;
  nome: string;
  documento: string;
  email: string;
  telefone: string;
  perfil_cliente: string[]; 
  ativo: boolean;
  data_criacao: string;
}

const rawList = ref<Cliente[]>([]);
const filteredList = ref<Cliente[]>([]);
const isLoading = ref(true);

const filters = ref({ search: '', perfil: '', status: '' });

const kpis = computed(() => {
  const total = rawList.value.length;
  let proprietarios = 0;
  let interessados = 0; 
  let inativos = 0;

  rawList.value.forEach(c => {
    if (!c.ativo) inativos++;
    if (c.perfil_cliente) {
        const perfis = c.perfil_cliente.join(' ').toUpperCase();
        if (perfis.includes('PROPRIETARIO')) proprietarios++;
        if (perfis.includes('INTERESSADO') || perfis.includes('LEAD')) interessados++;
    }
  });
  return { total, proprietarios, interessados, inativos };
});

const fetchClientes = async () => {
  isLoading.value = true;
  try {
    const response = await api.get('/v1/clientes/'); 
    const dataApi = Array.isArray(response.data) ? response.data : (response.data.results || []);
    
    rawList.value = dataApi.map((item: any) => ({
        id: item.id,
        nome: item.nome,
        documento: item.documento || item.cpf_cnpj || '',
        email: item.email,
        telefone: item.telefone || item.celular || '',
        perfil_cliente: item.perfil_cliente || [],
        ativo: item.ativo,
        data_criacao: item.data_cadastro || item.data_criacao || item.created_at || item.date_joined || item.criado_em || null
    }));
    filterList();
  } catch (error) {
    console.error("Erro ao buscar clientes:", error);
  } finally {
    isLoading.value = false;
  }
};

const goToCreateCliente = () => { router.push({ name: 'cliente-novo' }); };

// Função corrigida para garantir que o ID seja passado corretamente na rota
const editCliente = (id: number) => { 
    if (id) {
        router.push({ name: 'cliente-editar', params: { id: id.toString() } }); 
    }
};

const confirmDelete = async (cliente: Cliente) => {
    if(confirm(`Deseja inativar ${cliente.nome}?`)) {
        try {
            await api.delete(`/v1/clientes/${cliente.id}/`);
            fetchClientes();
        } catch { alert('Erro ao inativar.'); }
    }
}

const getUniqueBadges = (perfis: string[]) => {
    if (!perfis || perfis.length === 0) return [];
    const map = new Map<string, { label: string, class: string }>();

    perfis.forEach(raw => {
        const p = raw.toUpperCase();
        let label = '', cssClass = 'bg-gray';

        if (p.includes('PROPRIETARIO')) { label = 'Proprietário'; cssClass = 'bg-purple'; } 
        else if (p.includes('INTERESSADO')) { label = 'Interessado'; cssClass = 'bg-orange'; } 
        else if (p.includes('LEAD')) { label = 'Lead'; cssClass = 'bg-yellow'; } 
        else if (p.includes('COMPRADOR')) { label = 'Comprador'; cssClass = 'bg-blue'; } 
        else if (p.includes('INQUILINO')) { label = 'Inquilino'; cssClass = 'bg-teal'; } 
        else { label = raw.charAt(0).toUpperCase() + raw.slice(1).toLowerCase(); }

        if (!map.has(label)) map.set(label, { label, class: cssClass });
    });
    return Array.from(map.values());
};

const setQuickFilter = (tipo: string) => {
    if (tipo === 'INATIVO') {
        filters.value.status = filters.value.status === 'INATIVO' ? '' : 'INATIVO';
        filters.value.perfil = '';
    } else {
        filters.value.perfil = filters.value.perfil === tipo ? '' : tipo;
        filters.value.status = '';
    }
    filterList();
};

const clearFilters = () => { filters.value = { search: '', perfil: '', status: '' }; filterList(); };

const filterList = () => {
  let temp = rawList.value;
  const searchLower = filters.value.search.toLowerCase();

  if (filters.value.search) {
    temp = temp.filter(c => 
      (c.nome && c.nome.toLowerCase().includes(searchLower)) ||
      (c.email && c.email.toLowerCase().includes(searchLower)) ||
      (c.documento && c.documento.includes(searchLower))
    );
  }
  if (filters.value.perfil) {
    temp = temp.filter(c => c.perfil_cliente.some(p => p.toUpperCase().includes(filters.value.perfil)));
  }
  if (filters.value.status) {
      if (filters.value.status === 'ATIVO') temp = temp.filter(c => c.ativo);
      if (filters.value.status === 'INATIVO') temp = temp.filter(c => !c.ativo);
  }
  filteredList.value = temp;
};

const formatDate = (dateString: string | null) => {
  if (!dateString) return '-';
  try { return format(parseISO(dateString), 'dd/MM/yy', { locale: ptBR }); } catch { return '-'; }
};

onMounted(fetchClientes);
</script>

<style scoped>
/* CONFIGURAÇÃO GERAL */
.page-container {
  min-height: 100vh;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
}

/* HEADER DA PÁGINA (Breadcrumb e Título) */
.page-header {
  margin-bottom: 2rem;
}

.title-area { display: flex; flex-direction: column; gap: 6px; }
.title-area h1 {
  font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em;
}

.breadcrumb {
  display: flex; align-items: center; gap: 6px;
  font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;
}
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }

.header-main {
  display: flex; justify-content: space-between; align-items: flex-end;
}

.actions-area { display: flex; gap: 0.75rem; }

/* Botões Estilo Fino */
.btn-primary-thin {
  background: #2563eb; color: white; border: none; padding: 0.5rem 1.2rem;
  border-radius: 6px; font-weight: 400; font-size: 0.85rem; cursor: pointer;
  display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(37, 99, 235, 0.15);
}
.btn-primary-thin:hover { background: #1d4ed8; transform: translateY(-1px); }

.btn-icon-thin {
  background: white; border: 1px solid #e2e8f0; color: #64748b; width: 34px; height: 34px;
  border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; font-size: 0.8rem;
}
.btn-icon-thin:hover { border-color: #cbd5e1; color: #2563eb; background: #f8fafc; }

/* KPIS */
.kpi-grid { 
    display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
    gap: 1.25rem; margin-bottom: 2rem; 
}

.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); cursor: pointer; transition: all 0.2s;
  position: relative; overflow: hidden;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.04); }
.kpi-card.active { border: 1px solid; }

.kpi-content { display: flex; flex-direction: column; }
.kpi-value { font-size: 1.6rem; font-weight: 300; line-height: 1.1; color: #111; }
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; letter-spacing: 0.05em; }
.kpi-icon { 
    font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; 
}

.kpi-card.blue.active { background-color: #f8fbff; border-color: #3b82f6; }
.kpi-card.blue .kpi-value { color: #2563eb; }
.kpi-card.green.active { background-color: #f3fdf8; border-color: #10b981; }
.kpi-card.green .kpi-value { color: #059669; }
.kpi-card.orange.active { background-color: #fffdf5; border-color: #f59e0b; }
.kpi-card.orange .kpi-value { color: #d97706; }
.kpi-card.red.active { background-color: #fff5f5; border-color: #ef4444; }
.kpi-card.red .kpi-value { color: #dc2626; }

/* TOOLBAR */
.toolbar-row {
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  padding: 1rem;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
  display: flex; flex-wrap: wrap; gap: 1rem; align-items: flex-end;
  margin-bottom: 1.5rem;
}

.filter-group { flex: 1; display: flex; flex-direction: column; gap: 0.3rem; min-width: 160px; }
.search-group { flex: 2; min-width: 260px; }
.small-btn { flex: 0 0 auto; min-width: auto; }

.filter-group label { font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; }

.input-with-icon { position: relative; width: 100%; }
.input-with-icon i { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 0.9rem; }

.form-control {
  width: 100%; padding: 0.5rem 0.8rem; font-size: 0.85rem;
  border: 1px solid #cbd5e1; border-radius: 6px; background-color: #fff; color: #334155;
  outline: none; height: 38px; box-sizing: border-box; transition: all 0.2s;
}
.input-with-icon .form-control { padding-left: 2.2rem; }
.form-control:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1); }

.btn-clear {
    width: 38px; height: 38px; border: 1px solid #cbd5e1; background: #f8fafc;
    border-radius: 6px; color: #64748b; cursor: pointer;
    display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.btn-clear:hover { background: #fee2e2; color: #ef4444; border-color: #fca5a5; }

/* TABELA */
.report-main-wrapper {
  background: white; border-radius: 8px; border: 1px solid #e5e7eb;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
  display: flex; flex-direction: column; overflow: hidden;
}
.report-scroll-viewport { width: 100%; overflow-x: auto; }

.report-table { width: 100%; border-collapse: collapse; min-width: 900px; }
.report-table th {
  background: #f8fafc; padding: 0.8rem 1.2rem; text-align: left;
  font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em;
  border-bottom: 1px solid #e2e8f0;
}
.report-table td {
  padding: 0.8rem 1.2rem; border-bottom: 1px solid #f1f5f9;
  font-size: 0.85rem; color: #334155; vertical-align: middle;
}
.report-table tr:hover { background-color: #fcfcfc; }

.cliente-name { font-weight: 600; color: #1e293b; font-size: 0.9rem; display: block; }
.cliente-doc { font-size: 0.75rem; color: #64748b; margin-top: 2px; display: inline-flex; align-items: center; gap: 5px; }

.contact-info { display: flex; flex-direction: column; gap: 4px; font-size: 0.8rem; }
.contact-row { display: flex; align-items: center; gap: 8px; color: #475569; }
.contact-row i { color: #94a3b8; width: 14px; text-align: center; }

.badges-container { display: flex; gap: 4px; flex-wrap: wrap; }
.badge-type {
  font-size: 0.65rem; font-weight: 600; padding: 3px 8px; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.02em;
}
.bg-purple { background: #f3e8ff; color: #7e22ce; }
.bg-orange { background: #ffedd5; color: #c2410c; }
.bg-yellow { background: #fef9c3; color: #854d0e; }
.bg-blue { background: #e0f2fe; color: #0369a1; }
.bg-teal { background: #ccfbf1; color: #0f766e; }
.bg-gray { background: #f3f4f6; color: #475569; }

.actions-flex { display: flex; gap: 0.5rem; justify-content: flex-end; }
.btn-action {
  width: 32px; height: 32px; border: none; border-radius: 6px; cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.btn-action.edit { background-color: #eff6ff; color: #2563eb; }
.btn-action.edit:hover { background-color: #2563eb; color: #fff; }
.btn-action.delete { background-color: #fff1f2; color: #e11d48; }
.btn-action.delete:hover { background-color: #e11d48; color: #fff; }

@media (max-width: 1024px) {
  .page-container { padding: 1rem; }
  .header-main { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .actions-area { width: 100%; justify-content: flex-start; }
  .toolbar-row { flex-direction: column; align-items: stretch; }
  .filter-group, .search-group { width: 100%; }
}
</style>