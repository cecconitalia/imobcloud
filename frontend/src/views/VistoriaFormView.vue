<template>
  <div class="app-layout">
    <nav class="nav-header">
      <div class="nav-inner">
        <div class="nav-left">
          <button class="btn-circle-back" @click="goBack">
            <i class="fas fa-arrow-left"></i>
          </button>
          <div class="nav-title-group">
            <span class="nav-category">Vistorias</span>
            <h1 class="nav-title">{{ isEdit ? 'Edição Técnica' : 'Nova Inspeção' }}</h1>
          </div>
        </div>
        <div class="nav-right">
          <button class="btn-cancel" @click="goBack">Cancelar</button>
          <button class="btn-save-main" @click="saveVistoria" :disabled="saving">
            <template v-if="saving">
              <i class="fas fa-spinner fa-spin me-2"></i> Processando...
            </template>
            <template v-else>
              {{ isEdit ? 'Atualizar Vistoria' : 'Criar e Continuar' }}
              <i class="fas fa-chevron-right ms-2"></i>
            </template>
          </button>
        </div>
      </div>
    </nav>

    <main class="page-content">
      <div class="content-grid">
        
        <div class="main-form-col">
          
          <div class="glass-card mb-4" :class="{ 'step-completed': form.contrato }">
            <div class="card-header-main">
              <div class="step-indicator">1</div>
              <div class="header-info">
                <h2>Vínculo do Imóvel</h2>
                <p>Busque o contrato de aluguel para associar esta vistoria.</p>
              </div>
            </div>

            <div class="card-body-main">
              <div class="search-engine-wrapper" v-click-outside="closeDropdown">
                
                <div v-if="form.contrato && !showDropdown" class="selected-contract-pill fade-in">
                  <div class="pill-icon"><i class="fas fa-file-contract"></i></div>
                  <div class="pill-text">
                    <span class="pill-label">Contrato Selecionado (#{{ form.contrato }})</span>
                    <span class="pill-value text-truncate">{{ currentContratoDisplay.imovel }}</span>
                    <span class="pill-sub mt-1" v-if="currentContratoDisplay.inquilino">
                        <i class="far fa-user me-1 text-primary"></i> {{ currentContratoDisplay.inquilino }}
                    </span>
                  </div>
                  <button v-if="!isEdit" class="btn-change" @click="clearSelection">Alterar</button>
                </div>

                <div v-else class="search-input-container">
                  <i class="fas fa-search search-main-icon"></i>
                  <input 
                    type="text" 
                    v-model="searchQuery" 
                    placeholder="Busque por endereço, inquilino ou ID..."
                    class="main-search-input"
                    @focus="openDropdown"
                    @input="handleInput"
                    :disabled="isEdit || loadingContratos"
                  />
                  <div v-if="loadingContratos" class="input-loader spinner-border spinner-border-sm text-primary"></div>
                </div>

                <transition name="dropdown-anim">
                  <div v-if="showDropdown && !isEdit" class="search-results-panel">
                    
                    <div v-if="filteredContratos.length > 0">
                      <div 
                        v-for="c in filteredContratos" 
                        :key="c.id" 
                        class="result-row"
                        @click="selectContrato(c)"
                      >
                        <div class="result-avatar"><i class="fas fa-map-marker-alt"></i></div>
                        <div class="result-data">
                          <span class="result-title">{{ c.imovel_display }}</span>
                          <span class="result-sub">
                             Contrato #{{ c.id }} 
                             <span v-if="c.inquilino_nome"> • <i class="far fa-user mx-1"></i> {{ c.inquilino_nome }}</span>
                          </span>
                        </div>
                        <div class="result-tags">
                            <span class="badge-status">{{ c.status }}</span>
                        </div>
                      </div>
                    </div>

                    <div v-else class="no-results p-4 text-center">
                      <div v-if="loadingContratos" class="text-muted">
                          <i class="fas fa-circle-notch fa-spin mb-2"></i>
                          <p class="small mb-0">Carregando lista de contratos...</p>
                      </div>
                      <div v-else>
                          <i class="fas fa-folder-open mb-3 fs-4 text-muted opacity-50"></i>
                          <p class="fw-bold text-dark mb-1">Nenhum contrato encontrado.</p>
                          <p class="small text-muted mb-0" v-if="form.tipo === 'ENTRADA'">
                              Listando apenas contratos <b>ATIVOS</b> sem vistoria de entrada.
                          </p>
                          <p class="small text-muted mb-0" v-else-if="form.tipo === 'SAIDA'">
                              Listando apenas contratos <b>ATIVOS</b> sem vistoria de saída.
                          </p>
                      </div>
                    </div>

                  </div>
                </transition>
              </div>
            </div>
          </div>

          <div class="glass-card mb-4">
            <div class="card-header-main">
              <div class="step-indicator">2</div>
              <div class="header-info">
                <h2>Configuração da Inspeção</h2>
                <p>Dados de controle, data e tipo de movimentação.</p>
              </div>
            </div>

            <div class="card-body-main">
              <div class="row g-4">
                <div class="col-12">
                  <label class="form-section-label">Propósito da Vistoria</label>
                  <div class="type-cards-group">
                    <label class="t-card" :class="{ 'active success': form.tipo === 'ENTRADA' }">
                      <input type="radio" v-model="form.tipo" value="ENTRADA" :disabled="isEdit" @change="fetchContratosAptos">
                      <i class="fas fa-key"></i>
                      <span>Entrada</span>
                    </label>
                    <label class="t-card" :class="{ 'active danger': form.tipo === 'SAIDA' }">
                      <input type="radio" v-model="form.tipo" value="SAIDA" :disabled="isEdit" @change="fetchContratosAptos">
                      <i class="fas fa-door-open"></i>
                      <span>Saída</span>
                    </label>
                    <label class="t-card" :class="{ 'active info': form.tipo === 'PERIODICA' }">
                      <input type="radio" v-model="form.tipo" value="PERIODICA" :disabled="isEdit" @change="fetchContratosAptos">
                      <i class="fas fa-history"></i>
                      <span>Periódica</span>
                    </label>
                  </div>
                </div>

                <div class="col-md-6">
                  <label class="field-label-pro">Data de Realização</label>
                  <div class="input-pro-wrapper">
                    <i class="far fa-calendar-check"></i>
                    <input type="date" v-model="form.data_vistoria" class="input-pro">
                  </div>
                </div>

                <div class="col-md-6">
                  <label class="field-label-pro">Vistoriador</label>
                  <div class="input-pro-wrapper">
                    <i class="far fa-id-badge"></i>
                    <input type="text" v-model="form.realizado_por_nome" class="input-pro" placeholder="Nome do perito">
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <aside class="side-options-col">
          <div class="sticky-wrapper">
            
            <div class="glass-card side-card-padding mb-4">
              <h3 class="side-title">Configurações de Laudo</h3>
              
              <div class="switch-block">
                <div class="switch-content">
                  <strong>Assinatura Proprietário</strong>
                  <p>Inclui campo para o dono do imóvel.</p>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="form.exige_assinatura_proprietario">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>

            <div class="glass-card side-card-padding">
              <h3 class="side-title">Observações Técnicas</h3>
              <textarea 
                v-model="form.observacoes" 
                class="textarea-pro" 
                placeholder="Ex: Entrega de 3 chaves tetra, vistoria de gás realizada..."
                rows="6"
              ></textarea>
              <div class="textarea-footer">
                <i class="fas fa-info-circle me-1"></i> Estas notas aparecerão no laudo.
              </div>
            </div>

            <div class="help-box mt-4">
               <h4>Dica de Uso</h4>
               <p>Certifique-se de que a data informada corresponde ao dia em que você esteve fisicamente no imóvel.</p>
            </div>

          </div>
        </aside>
      </div>
    </main>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '@/services/api';

export default defineComponent({
  name: 'VistoriaFormView',
  directives: {
    clickOutside: {
      mounted(el, binding) {
        el.clickOutsideEvent = (event: any) => {
          if (!(el === event.target || el.contains(event.target))) binding.value();
        };
        document.body.addEventListener('click', el.clickOutsideEvent);
      },
      unmounted(el) { document.body.removeEventListener('click', el.clickOutsideEvent); },
    },
  },
  setup() {
    const router = useRouter();
    const route = useRoute();
    
    const saving = ref(false);
    const loadingContratos = ref(false);
    const contratos = ref<any[]>([]); // Lista que vem da API
    const searchQuery = ref('');
    const showDropdown = ref(false);
    
    const vistoriaId = route.params.id ? Number(route.params.id) : null;
    const isEdit = computed(() => !!vistoriaId);

    const form = ref({
      contrato: null as number | null,
      tipo: 'ENTRADA',
      data_vistoria: new Date().toISOString().split('T')[0],
      observacoes: '',
      exige_assinatura_proprietario: false,
      realizado_por_nome: ''
    });

    // Display do contrato selecionado
    const currentContratoDisplay = computed(() => {
        const selected = contratos.value.find(c => c.id === form.value.contrato);
        if (selected) {
            return {
                imovel: selected.imovel_display,
                inquilino: selected.inquilino_nome
            };
        }
        return {
            imovel: searchQuery.value || 'Contrato Selecionado',
            inquilino: '' 
        };
    });

    // Filtro local da pesquisa
    const filteredContratos = computed(() => {
      const term = searchQuery.value.toLowerCase();
      // Mostra até 10 resultados para facilitar
      if(!term) return contratos.value.slice(0, 10);
      
      return contratos.value.filter(c => 
        (c.imovel_display || '').toLowerCase().includes(term) ||
        (c.inquilino_nome || '').toLowerCase().includes(term) ||
        String(c.id).includes(term)
      ).slice(0, 10);
    });

    const openDropdown = () => { if (!isEdit.value) showDropdown.value = true; };
    
    const handleInput = () => { 
        showDropdown.value = true; 
        if (form.value.contrato) form.value.contrato = null; 
    };
    
    const closeDropdown = () => { showDropdown.value = false; };
    
    const clearSelection = () => { 
        searchQuery.value = ''; 
        form.value.contrato = null; 
        showDropdown.value = true; 
        fetchContratosAptos(); // Recarrega para mostrar a lista completa
    };

    const selectContrato = (c: any) => {
      form.value.contrato = c.id;
      searchQuery.value = c.imovel_display;
      showDropdown.value = false;
    };

    // --- BUSCA DINÂMICA (Back-end Filter) ---
    const fetchContratosAptos = async () => {
      if (isEdit.value) return;

      loadingContratos.value = true;
      contratos.value = [];
      form.value.contrato = null;
      searchQuery.value = '';

      try {
        const tipo = form.value.tipo;
        // Chama a rota corrigida
        const response = await api.get('/v1/contratos/pendentes_vistoria/', { 
            params: { tipo: tipo } 
        });
        
        const data = response.data.results || response.data;
        console.log(`API retornou ${data.length} contratos para ${tipo}`); // DEBUG

        // Mapeia para o formato correto
        contratos.value = data.map((c: any) => {
            // Lógica para nome do inquilino (Fallback)
            let inqNome = 'Locatário';
            if (c.inquilino_detalhes?.nome_display) inqNome = c.inquilino_detalhes.nome_display;
            else if (c.inquilino_detalhes?.nome) inqNome = c.inquilino_detalhes.nome;
            else if (c.inquilino_nome) inqNome = c.inquilino_nome;
            else if (typeof c.inquilino === 'object' && c.inquilino?.nome) inqNome = c.inquilino.nome;

            // Lógica para imóvel
            let imovDisp = `Contrato #${c.id}`;
            if (c.imovel_display) imovDisp = c.imovel_display;
            else if (c.imovel_detalhes?.endereco_completo) imovDisp = c.imovel_detalhes.endereco_completo;
            else if (c.imovel_detalhes?.logradouro) imovDisp = c.imovel_detalhes.logradouro;

            return {
                id: c.id,
                imovel_display: imovDisp,
                inquilino_nome: inqNome,
                tipo_contrato: c.tipo_contrato || 'ALUGUEL',
                status: c.status_contrato || 'ATIVO'
            };
        });

      } catch (error) {
        console.error("Erro ao buscar contratos:", error);
      } finally {
        loadingContratos.value = false;
      }
    };

    const saveVistoria = async () => {
      if (!form.value.contrato) return alert("Selecione um contrato antes de continuar.");
      saving.value = true;
      try {
        let targetId = vistoriaId;
        if (isEdit.value) {
            await api.patch(`/v1/vistorias/vistorias/${vistoriaId}/`, form.value);
        } else {
            const res = await api.post('/v1/vistorias/vistorias/', form.value);
            targetId = res.data.id;
        }
        
        // --- CORREÇÃO DE ROTA AQUI ---
        // Usa o NAME da rota para garantir o match correto
        router.push({ name: 'vistoria-checklist', params: { id: targetId } });
        
      } catch (error: any) {
        let msg = "Erro técnico ao salvar.";
        if (error.response?.data) {
           const data = error.response.data;
           msg = data.detail || Object.values(data).flat()[0] as string;
        }
        alert(msg);
      } finally { saving.value = false; }
    };

    const goBack = () => router.push('/vistorias');

    onMounted(async () => {
      if (isEdit.value) {
        // Carrega dados da edição
        try {
          const res = await api.get(`/v1/vistorias/vistorias/${vistoriaId}/`);
          Object.assign(form.value, res.data);
          
          if (res.data.data_vistoria) form.value.data_vistoria = res.data.data_vistoria.split('T')[0];
          
          // Carrega o contrato específico
          if (form.value.contrato) {
              const cRes = await api.get(`/v1/contratos/${form.value.contrato}/`);
              const cData = cRes.data;
              const display = cData.imovel_display || cData.imovel_detalhes?.logradouro || `Contrato #${cData.id}`;
              const inq = cData.inquilino_detalhes?.nome_display || cData.inquilino_nome || 'Inquilino';
              
              searchQuery.value = display;
              contratos.value = [{ 
                  id: cData.id, 
                  imovel_display: display, 
                  inquilino_nome: inq,
                  status: cData.status_contrato 
              }];
          }
        } catch (e) { router.push('/vistorias'); }
      } else {
        // Carrega lista inicial
        await fetchContratosAptos();
      }
    });

    return { 
        form, filteredContratos, saving, isEdit, loadingContratos, searchQuery, showDropdown, 
        currentContratoDisplay, openDropdown, handleInput, selectContrato, clearSelection, 
        saveVistoria, goBack, closeDropdown, fetchContratosAptos
    };
  }
});
</script>

<style scoped>
/* APP LAYOUT */
.app-layout {
  background-color: #fcfdfe;
  min-height: 100vh;
  color: #121417;
  font-family: 'Inter', -apple-system, sans-serif;
  padding-top: 80px;
}

/* NAV HEADER FIXA */
.nav-header {
  position: fixed; top: 0; left: 0; right: 0;
  height: 80px; background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #edf2f7;
  z-index: 1000;
}
.nav-inner {
  max-width: 1280px; margin: 0 auto; height: 100%;
  display: flex; align-items: center; justify-content: space-between; padding: 0 32px;
}
.nav-left { display: flex; align-items: center; gap: 20px; }
.btn-circle-back {
  width: 44px; height: 44px; border-radius: 50%; border: 1px solid #e2e8f0;
  background: white; color: #64748b; cursor: pointer; transition: 0.2s;
}
.btn-circle-back:hover { background: #000; color: white; border-color: #000; }
.nav-title-group { display: flex; flex-direction: column; }
.nav-category { font-size: 11px; font-weight: 700; color: #3b82f6; text-transform: uppercase; letter-spacing: 0.05em; }
.nav-title { font-size: 20px; font-weight: 800; margin: 0; letter-spacing: -0.02em; }

.nav-right { display: flex; gap: 12px; }
.btn-cancel { background: transparent; border: none; font-weight: 600; color: #64748b; padding: 12px 20px; cursor: pointer; border-radius: 8px; }
.btn-cancel:hover { color: #1e293b; background: #f1f5f9; }
.btn-save-main { background: #121417; color: white; border: none; padding: 12px 28px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.3s; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.btn-save-main:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.15); }

/* GRID LAYOUT */
.page-content { max-width: 1280px; margin: 0 auto; padding: 32px; }
.content-grid { display: grid; grid-template-columns: 1fr 400px; gap: 40px; align-items: start; }

/* GLASS CARD DESIGN */
.glass-card {
  background: white; border: 1px solid #edf2f7; border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02); overflow: visible;
  transition: border-color 0.3s;
}
.glass-card.step-completed { border-color: #22c55e; }

.card-header-main { padding: 32px; display: flex; gap: 20px; border-bottom: 1px solid #f8fafc; }
.step-indicator {
  width: 36px; height: 36px; background: #000; color: white; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; font-weight: 800;
}
.header-info h2 { font-size: 18px; font-weight: 700; margin: 0; }
.header-info p { font-size: 14px; color: #64748b; margin: 4px 0 0 0; }
.card-body-main { padding: 32px; }

/* SMART SEARCH & RESULTS */
.search-engine-wrapper { position: relative; }
.selected-contract-pill {
  background: #f0fdf4; border: 1px solid #22c55e; border-radius: 12px;
  padding: 16px; display: flex; align-items: center; gap: 16px;
}
.pill-icon { width: 40px; height: 40px; background: white; color: #22c55e; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
.pill-text { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.pill-label { font-size: 11px; font-weight: 700; color: #166534; text-transform: uppercase; }
.pill-value { font-weight: 600; font-size: 15px; color: #14532d; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.pill-sub { font-size: 13px; color: #15803d; }

.btn-change { background: white; border: 1px solid #22c55e; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 700; color: #22c55e; cursor: pointer; }

.search-input-container {
  display: flex; align-items: center; border: 2px solid #e2e8f0; border-radius: 12px;
  padding: 0 20px; height: 60px; transition: 0.3s;
}
.search-input-container:focus-within { border-color: #3b82f6; box-shadow: 0 0 0 4px rgba(59,130,246,0.1); }
.search-main-icon { color: #94a3b8; font-size: 1.2rem; margin-right: 16px; }
.main-search-input { flex: 1; border: none; background: transparent; outline: none; font-size: 16px; font-weight: 500; }

.search-results-panel {
  position: absolute; top: calc(100% + 12px); left: 0; right: 0;
  background: white; border-radius: 16px; border: 1px solid #e2e8f0;
  z-index: 1000; box-shadow: 0 20px 40px rgba(0,0,0,0.12); overflow: hidden;
}
.result-row {
  display: flex; align-items: center; padding: 16px 20px; cursor: pointer; transition: 0.1s; justify-content: space-between;
}
.result-row:hover { background: #f8fafc; }
.result-avatar { width: 40px; height: 40px; background: #eff6ff; color: #3b82f6; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 16px; flex-shrink: 0; }
.result-data { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.result-title { font-weight: 600; font-size: 14px; color: #1e293b; }
.result-sub { font-size: 12px; color: #64748b; }
.result-tags { display: flex; align-items: center; gap: 8px; margin-left: 12px; }
.badge-status { font-size: 10px; font-weight: 700; background: #dcfce7; color: #15803d; padding: 4px 8px; border-radius: 6px; text-transform: uppercase; }

/* TYPE CARDS */
.type-cards-group { display: flex; gap: 16px; margin-top: 12px; }
.t-card {
  flex: 1; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;
  display: flex; flex-direction: column; align-items: center; gap: 10px;
  cursor: pointer; transition: 0.2s; background: #fff;
}
.t-card i { font-size: 1.5rem; color: #94a3b8; }
.t-card span { font-size: 13px; font-weight: 700; color: #64748b; }
.t-card.active { transform: scale(1.02); }
.t-card.active.success { border-color: #22c55e; background: #f0fdf4; color: #166534; }
.t-card.active.success i, .t-card.active.success span { color: #166534; }
.t-card.active.danger { border-color: #ef4444; background: #fef2f2; color: #991b1b; }
.t-card.active.danger i, .t-card.active.danger span { color: #991b1b; }
.t-card.active.info { border-color: #3b82f6; background: #eff6ff; color: #1e40af; }
.t-card.active.info i, .t-card.active.info span { color: #1e40af; }
.t-card input { display: none; }

/* INPUTS PRO */
.form-section-label { display: block; font-size: 12px; font-weight: 800; color: #1e293b; text-transform: uppercase; margin-bottom: 12px; }
.field-label-pro { font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 8px; display: block; }
.input-pro-wrapper {
  position: relative; display: flex; align-items: center; background: #f8fafc;
  border: 1px solid #e2e8f0; border-radius: 10px; padding: 0 14px; height: 48px;
}
.input-pro-wrapper i { color: #94a3b8; margin-right: 12px; }
.input-pro { flex: 1; border: none; background: transparent; outline: none; font-size: 14px; color: #1e293b; font-weight: 500; }

/* ASIDE */
.side-card-padding { padding: 24px; }
.side-title { font-size: 15px; font-weight: 700; margin-bottom: 20px; }
.switch-block { display: flex; justify-content: space-between; align-items: center; gap: 16px; }
.switch-content strong { font-size: 13px; display: block; }
.switch-content p { font-size: 12px; color: #64748b; margin: 2px 0 0 0; line-height: 1.4; }

.toggle-switch { position: relative; width: 44px; height: 24px; flex-shrink: 0; }
.toggle-switch input { display: none; }
.toggle-slider { position: absolute; inset: 0; background: #e2e8f0; border-radius: 20px; cursor: pointer; transition: 0.3s; }
.toggle-slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background: white; border-radius: 50%; transition: 0.3s; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
input:checked + .toggle-slider { background: #000; }
input:checked + .toggle-slider:before { transform: translateX(20px); }

.textarea-pro {
  width: 100%; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px;
  padding: 16px; font-size: 14px; outline: none; resize: none; transition: 0.3s;
}
.textarea-pro:focus { border-color: #3b82f6; background: white; }
.textarea-footer { font-size: 11px; color: #94a3b8; margin-top: 8px; }

.help-box { background: #fffbeb; border: 1px solid #fef3c7; border-radius: 12px; padding: 20px; }
.help-box h4 { font-size: 13px; font-weight: 700; color: #92400e; margin-bottom: 6px; }
.help-box p { font-size: 12px; color: #b45309; margin: 0; line-height: 1.5; }

/* UTILS */
.mb-4 { margin-bottom: 24px; }
.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.dropdown-anim-enter-active, .dropdown-anim-leave-active { transition: all 0.3s ease; }
.dropdown-anim-enter-from, .dropdown-anim-leave-to { opacity: 0; transform: translateY(-10px); }

@media (max-width: 1024px) {
  .content-grid { grid-template-columns: 1fr; }
  .side-options-col { order: -1; }
}
</style>