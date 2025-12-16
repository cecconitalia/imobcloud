<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-content">
        <button class="btn-back" @click="goBack" title="Voltar para lista">
          <i class="fas fa-arrow-left"></i>
        </button>
        <div class="header-text">
          <h1>{{ isEdit ? 'Editar Vistoria' : 'Nova Vistoria' }}</h1>
          <p class="subtitle">Preencha as informações básicas para iniciar o processo de vistoria.</p>
        </div>
      </div>
    </header>

    <main class="main-content">
      <form @submit.prevent="saveVistoria" class="form-layout">
        
        <div class="form-card">
          <div class="card-header-custom">
            <i class="fas fa-file-contract icon-header"></i>
            <div>
              <h3>Vínculo Contratual</h3>
              <p>Pesquise e selecione o contrato para esta vistoria.</p>
            </div>
          </div>
          
          <div class="card-body-custom">
            <div class="row">
              <div class="col-12 position-relative">
                <label class="input-label">Contrato <span class="required">*</span></label>
                
                <div class="search-wrapper" v-click-outside="closeDropdown">
                  <div class="input-group-custom">
                    <i class="fas fa-search input-icon"></i>
                    <input 
                      type="text" 
                      class="form-control custom-input with-chevron" 
                      placeholder="Busque por endereço, ID ou nome do inquilino..."
                      v-model="searchQuery"
                      @focus="showDropdown = true"
                      @input="showDropdown = true"
                      :disabled="isEdit"
                      :class="{ 'disabled-input': isEdit }"
                    >
                    <i class="fas fa-chevron-down input-chevron" :class="{ 'rotate': showDropdown }"></i>
                  </div>

                  <div v-if="showDropdown && !isEdit" class="dropdown-list shadow-sm">
                    <ul class="list-unstyled mb-0">
                      <li 
                        v-for="c in filteredContratos" 
                        :key="c.id" 
                        @click="selectContrato(c)"
                        class="dropdown-item-custom"
                      >
                        <div class="d-flex justify-content-between align-items-center">
                          <span class="fw-bold text-dark">Contrato #{{ c.id }}</span>
                          <span class="badge bg-light text-dark border">{{ c.tipo_contrato || 'Aluguel' }}</span>
                        </div>
                        <div class="text-primary mt-1"><i class="fas fa-map-marker-alt me-1"></i> {{ c.imovel_display }}</div>
                        <div class="text-muted small mt-1"><i class="fas fa-user me-1"></i> {{ c.inquilino_nome || 'Sem Inquilino' }}</div>
                      </li>
                      
                      <li v-if="filteredContratos.length === 0" class="p-3 text-center text-muted">
                        <i class="fas fa-search mb-2 d-block"></i>
                        Nenhum contrato encontrado para "{{ searchQuery }}".
                      </li>
                    </ul>
                  </div>
                </div>
                <div v-if="contratos.length === 0 && !loading" class="empty-state-warning mt-2">
                  <i class="fas fa-exclamation-circle"></i> 
                  Não foram encontrados contratos ativos no sistema.
                </div>
                <small v-if="isEdit" class="helper-text">O contrato não pode ser alterado após a criação.</small>
              </div>
            </div>
          </div>
        </div>

        <div class="form-card">
          <div class="card-header-custom">
            <i class="fas fa-clipboard-check icon-header"></i>
            <div>
              <h3>Detalhes da Execução</h3>
              <p>Defina o tipo e a data de realização.</p>
            </div>
          </div>

          <div class="card-body-custom">
            <div class="row g-4">
              <div class="col-md-6">
                <label class="input-label">Tipo de Vistoria <span class="required">*</span></label>
                <div class="select-option-grid">
                  
                  <label class="radio-card" :class="{ active: form.tipo === 'ENTRADA' }">
                    <input type="radio" v-model="form.tipo" value="ENTRADA" class="d-none">
                    <div class="radio-content">
                      <span class="icon-box success"><i class="fas fa-sign-in-alt"></i></span>
                      <span class="radio-title">Entrada</span>
                    </div>
                  </label>

                  <label class="radio-card" :class="{ active: form.tipo === 'SAIDA' }">
                    <input type="radio" v-model="form.tipo" value="SAIDA" class="d-none">
                    <div class="radio-content">
                      <span class="icon-box danger"><i class="fas fa-sign-out-alt"></i></span>
                      <span class="radio-title">Saída</span>
                    </div>
                  </label>

                  <label class="radio-card" :class="{ active: form.tipo === 'PERIODICA' }">
                    <input type="radio" v-model="form.tipo" value="PERIODICA" class="d-none">
                    <div class="radio-content">
                      <span class="icon-box info"><i class="fas fa-sync-alt"></i></span>
                      <span class="radio-title">Periódica</span>
                    </div>
                  </label>

                </div>
              </div>

              <div class="col-md-6">
                <label class="input-label">Data da Realização <span class="required">*</span></label>
                <div class="input-group-custom">
                  <i class="far fa-calendar-alt input-icon"></i>
                  <input type="date" class="form-control custom-input" v-model="form.data_vistoria" required>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="form-card">
          <div class="card-header-custom">
            <i class="fas fa-align-left icon-header"></i>
            <div>
              <h3>Observações Gerais</h3>
              <p>Informações adicionais sobre o estado geral do imóvel.</p>
            </div>
          </div>

          <div class="card-body-custom">
            <div class="col-12">
              <textarea 
                class="form-control custom-textarea" 
                rows="5" 
                v-model="form.observacoes" 
                placeholder="Descreva aqui observações gerais, estado de conservação das chaves, medidores, etc..."
              ></textarea>
            </div>
          </div>
        </div>

        <div class="form-actions-bar">
          <button type="button" class="btn-cancel" @click="goBack">
            Cancelar
          </button>
          <button type="submit" class="btn-save" :disabled="saving">
            <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="fas fa-check me-2"></i>
            {{ isEdit ? 'Salvar Alterações' : 'Salvar e Iniciar Checklist' }}
          </button>
        </div>

      </form>
    </main>

  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '@/services/api';

export default defineComponent({
  name: 'VistoriaFormView',
  directives: {
    clickOutside: {
      mounted(el, binding) {
        el.clickOutsideEvent = function(event: any) {
          if (!(el === event.target || el.contains(event.target))) {
            binding.value(event, el);
          }
        };
        document.body.addEventListener('click', el.clickOutsideEvent);
      },
      unmounted(el) {
        document.body.removeEventListener('click', el.clickOutsideEvent);
      },
    },
  },
  setup() {
    const router = useRouter();
    const route = useRoute();
    
    const saving = ref(false);
    const loading = ref(true);
    const contratos = ref<any[]>([]);
    
    // Controle da Pesquisa
    const searchQuery = ref('');
    const showDropdown = ref(false);
    
    const vistoriaId = route.params.id ? Number(route.params.id) : null;
    const isEdit = computed(() => !!vistoriaId);

    const today = new Date().toISOString().split('T')[0];
    const form = ref({
      contrato: null as number | null,
      tipo: 'ENTRADA',
      data_vistoria: today,
      observacoes: ''
    });

    const filteredContratos = computed(() => {
      if (!searchQuery.value) return contratos.value.slice(0, 5);
      
      const term = searchQuery.value.toLowerCase();
      return contratos.value.filter(c => 
        c.imovel_display.toLowerCase().includes(term) ||
        (c.inquilino_nome && c.inquilino_nome.toLowerCase().includes(term)) ||
        String(c.id).includes(term)
      ).slice(0, 10);
    });

    const selectContrato = (contrato: any) => {
      form.value.contrato = contrato.id;
      searchQuery.value = `Contrato #${contrato.id} - ${contrato.imovel_display}`;
      showDropdown.value = false;
    };

    const closeDropdown = () => {
      showDropdown.value = false;
    };

    const fetchContratos = async () => {
      loading.value = true;
      try {
        const response = await api.get('/v1/contratos/');
        const rawData = response.data.results ? response.data.results : response.data;
        
        contratos.value = rawData.map((c: any) => {
            let display = `Imóvel ID ${c.imovel}`;
            let inquilino = c.inquilino_detalhes?.nome_display || '';
            
            if (c.imovel_detalhes) {
                 if (c.imovel_detalhes.endereco_completo) display = c.imovel_detalhes.endereco_completo;
                 else if (c.imovel_detalhes.logradouro) display = c.imovel_detalhes.logradouro;
            }
            
            return { 
                id: c.id, 
                imovel_display: display,
                inquilino_nome: inquilino,
                tipo_contrato: c.tipo_contrato
            };
        });
      } catch (error) { 
        console.error('Erro contratos:', error); 
      } finally {
        loading.value = false;
      }
    };

    const syncSearchText = () => {
        if (form.value.contrato && contratos.value.length > 0) {
            const selected = contratos.value.find(c => c.id === form.value.contrato);
            if (selected) {
                searchQuery.value = `Contrato #${selected.id} - ${selected.imovel_display}`;
            }
        }
    };

    const fetchVistoria = async () => {
      if (!vistoriaId) return;
      try {
        const response = await api.get(`/v1/vistorias/vistorias/${vistoriaId}/`);
        form.value = {
            ...response.data,
            data_vistoria: response.data.data_vistoria ? response.data.data_vistoria.split('T')[0] : today
        };
        syncSearchText();
      } catch (error) {
        alert("Erro ao carregar dados.");
        router.push('/vistorias');
      }
    };

    const saveVistoria = async () => {
      if (!form.value.contrato) {
        alert("Por favor, pesquise e selecione um contrato.");
        return;
      }
      saving.value = true;
      try {
        let idParaRedirecionar = vistoriaId;

        if (isEdit.value) {
          await api.patch(`/v1/vistorias/vistorias/${vistoriaId}/`, form.value);
        } else {
          const response = await api.post('/v1/vistorias/vistorias/', form.value);
          idParaRedirecionar = response.data.id;
        }
        
        // Redireciona para a tela de Checklist/Ambientes
        router.push({ name: 'vistoria-checklist', params: { id: idParaRedirecionar } });

      } catch (error: any) {
        const msg = error.response?.data?.detail || "Erro ao salvar vistoria.";
        alert(msg);
      } finally {
        saving.value = false;
      }
    };

    const goBack = () => {
      router.push('/vistorias');
    };

    onMounted(async () => {
      await fetchContratos();
      if (isEdit.value) {
          await fetchVistoria();
      }
    });

    watch(contratos, () => {
        if (isEdit.value) syncSearchText();
    });

    return { 
        form, contratos, filteredContratos, saving, isEdit, loading,
        searchQuery, showDropdown, 
        selectContrato, closeDropdown,
        saveVistoria, goBack 
    };
  }
});
</script>

<style scoped>
/* =========================================
   ESTILOS PRINCIPAIS
   ========================================= */
.page-container {
  min-height: 100vh;
  background-color: #f3f4f6;
  padding-bottom: 80px;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
}

/* Header */
.page-header {
  background-color: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 20px 32px;
  margin-bottom: 32px;
}
.header-content {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 20px;
}
.btn-back {
  width: 40px; height: 40px;
  border-radius: 50%; border: 1px solid #e5e7eb; background: white; color: #6b7280;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.2s;
}
.btn-back:hover { background: #f9fafb; color: #111827; border-color: #d1d5db; }
.header-text h1 { font-size: 24px; font-weight: 700; color: #111827; margin: 0; }
.subtitle { color: #6b7280; font-size: 14px; margin: 4px 0 0 0; }

/* Main Content */
.main-content { max-width: 1100px; margin: 0 auto; padding: 0 20px; }
.form-layout { display: flex; flex-direction: column; gap: 24px; }

/* Cards */
.form-card {
  background: white; border-radius: 12px; border: 1px solid #e5e7eb;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05); overflow: visible; 
}
.card-header-custom {
  padding: 24px; border-bottom: 1px solid #f3f4f6; display: flex; align-items: flex-start; gap: 16px;
  background-color: #fcfcfc; border-radius: 12px 12px 0 0;
}
.icon-header {
  font-size: 20px; color: #3b82f6; background: #eff6ff; padding: 10px; border-radius: 8px;
}
.card-header-custom h3 { font-size: 16px; font-weight: 600; color: #1f2937; margin: 0 0 2px 0; }
.card-header-custom p { font-size: 13px; color: #6b7280; margin: 0; }
.card-body-custom { padding: 32px; }

/* --- INPUTS GERAIS --- */
.input-label { display: block; font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.02em; }
.required { color: #ef4444; }
.input-group-custom { position: relative; }
.input-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: #9ca3af; pointer-events: none; z-index: 5; }

.custom-input, .custom-textarea {
  width: 100%; padding: 12px 12px 12px 40px; border: 1px solid #d1d5db;
  border-radius: 8px; font-size: 14px; color: #111827; transition: all 0.2s; background-color: #fff;
}
.custom-input:focus, .custom-textarea:focus { border-color: #3b82f6; outline: none; box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1); }
.custom-textarea { padding: 12px; resize: vertical; }
.disabled-input { background-color: #f9fafb; cursor: not-allowed; color: #6b7280; }

/* --- DROPDOWN PESQUISA --- */
.search-wrapper { position: relative; }
.with-chevron { padding-right: 40px; }
.input-chevron { position: absolute; right: 14px; top: 50%; transform: translateY(-50%); color: #9ca3af; pointer-events: none; transition: transform 0.2s; }
.input-chevron.rotate { transform: translateY(-50%) rotate(180deg); }

.dropdown-list {
  position: absolute; top: 100%; left: 0; width: 100%;
  background: white; border: 1px solid #e5e7eb; border-radius: 8px;
  margin-top: 6px; z-index: 50; max-height: 280px; overflow-y: auto;
}
.dropdown-item-custom {
  padding: 12px 16px; border-bottom: 1px solid #f3f4f6; cursor: pointer; transition: background 0.1s;
}
.dropdown-item-custom:hover { background-color: #eff6ff; }
.dropdown-item-custom:last-child { border-bottom: none; }

/* --- RADIO CARDS --- */
.select-option-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.radio-card { border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s; background: white; }
.radio-card:hover { border-color: #3b82f6; background: #eff6ff; }
.radio-card.active { border-color: #3b82f6; background-color: #eff6ff; box-shadow: 0 0 0 2px #3b82f6; }
.radio-content { display: flex; flex-direction: column; align-items: center; gap: 8px; text-align: center; }
.icon-box { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border-radius: 6px; font-size: 14px; }
.icon-box.success { background: #dcfce7; color: #166534; }
.icon-box.danger { background: #fee2e2; color: #991b1b; }
.icon-box.info { background: #e0f2fe; color: #075985; }
.radio-title { font-size: 13px; font-weight: 600; color: #374151; }

/* --- FOOTER --- */
.form-actions-bar { display: flex; justify-content: flex-end; gap: 16px; margin-top: 24px; }
.btn-cancel { padding: 12px 24px; background: white; border: 1px solid #d1d5db; border-radius: 8px; font-weight: 600; color: #374151; cursor: pointer; transition: all 0.2s; }
.btn-cancel:hover { background: #f9fafb; border-color: #9ca3af; }
.btn-save { padding: 12px 32px; background: #3b82f6; border: none; border-radius: 8px; font-weight: 600; color: white; cursor: pointer; transition: all 0.2s; box-shadow: 0 2px 5px rgba(59, 130, 246, 0.3); }
.btn-save:hover { background: #2563eb; transform: translateY(-1px); }
.btn-save:disabled { background: #93c5fd; cursor: wait; }

/* Responsividade */
@media (max-width: 768px) {
  .select-option-grid { grid-template-columns: 1fr; }
  .header-content { flex-direction: column; align-items: flex-start; }
  .form-actions-bar { flex-direction: column-reverse; }
  .btn-save, .btn-cancel { width: 100%; }
}
</style>