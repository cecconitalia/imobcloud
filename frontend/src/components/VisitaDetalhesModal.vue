<template>
  <div v-if="show" class="modal-backdrop" @click="close">
    <div class="modal-container" @click.stop>
      
      <div class="modal-header">
        <div class="header-content">
          <h2>Detalhes da Visita #{{ visita.id }}</h2>
          <span :class="['status-badge', visita.realizada ? 'realizada' : 'pendente']">
            {{ visita.realizada ? 'Realizada' : 'Agendada' }}
          </span>
        </div>
        <button class="close-btn" @click="close"><i class="fas fa-times"></i></button>
      </div>

      <div class="modal-body">
        
        <div class="detail-section">
            <div class="info-grid">
                <div class="info-item">
                    <label>Data e Hora</label>
                    <p class="highlight"><i class="far fa-calendar-alt"></i> {{ formatarData(visita.data_visita) }}</p>
                </div>
                <div class="info-item full-width">
                    <label>Observações</label>
                    <p>{{ visita.observacoes || 'Nenhuma observação registrada.' }}</p>
                </div>
            </div>
        </div>

        <div class="divider"></div>

        <div class="columns-grid">
            <div class="column-card">
                <h3>
                    <i class="fas fa-home"></i> 
                    Imóveis do Roteiro
                    <span class="counter-badge" v-if="imoveisSelecionados.length > 0">{{ imoveisSelecionados.length }}</span>
                </h3>
                <p class="help-text" v-if="!todosAssinaram">
                    <i class="fas fa-info-circle"></i> Selecione os imóveis efetivamente visitados.
                </p>

                <div class="imoveis-list-container">
                    <div v-if="visita.imoveis_obj && visita.imoveis_obj.length > 0">
                        <div 
                            v-for="imovel in visita.imoveis_obj" 
                            :key="imovel.id" 
                            class="imovel-item-wrapper"
                            :class="{ 'disabled': todosAssinaram }"
                        >
                            <label class="imovel-checkbox-row">
                                <div class="checkbox-container">
                                    <input type="checkbox" :value="imovel.id" v-model="imoveisSelecionados" :disabled="todosAssinaram">
                                    <span class="checkmark"></span>
                                </div>
                                <div class="imovel-content">
                                    <h4>{{ imovel.titulo_anuncio || 'Imóvel sem título' }}</h4>
                                    <p class="sub-text">Cód: {{ imovel.codigo_referencia || imovel.id }}</p>
                                    <p class="address">{{ imovel.logradouro }}, {{ imovel.numero }} - {{ imovel.bairro }}</p>
                                </div>
                            </label>
                        </div>
                    </div>
                    <div v-else class="empty-imoveis">Nenhum imóvel vinculado.</div>
                </div>
            </div>

            <div class="column-card">
                <h3><i class="fas fa-user"></i> Cliente</h3>
                <div v-if="visita.cliente_obj" class="card-content">
                    <h4>{{ visita.cliente_obj.nome || visita.cliente_obj.razao_social }}</h4>
                    <p v-if="visita.cliente_obj.telefone"><i class="fas fa-phone"></i> {{ visita.cliente_obj.telefone }}</p>
                    <p v-if="visita.cliente_obj.email"><i class="fas fa-envelope"></i> {{ visita.cliente_obj.email }}</p>
                </div>
            </div>
        </div>

        <div class="signatures-section">
            <h3><i class="fas fa-file-contract"></i> Assinaturas Digitais</h3>
            
            <div class="proof-grid">
                <div class="proof-item signature-box">
                    <label>Corretor</label>
                    <div v-if="visita.assinatura_corretor" class="img-wrapper signed">
                        <img :src="visita.assinatura_corretor" alt="Assinatura Corretor" />
                        <div class="timestamp"><i class="fas fa-check"></i> Assinado</div>
                    </div>
                    <div v-else class="placeholder-box">
                        <p>Pendente</p>
                        <button class="btn-sign-action" @click="iniciarAssinatura('CORRETOR')">
                            <i class="fas fa-pen"></i> Assinar
                        </button>
                    </div>
                </div>

                <div class="proof-item signature-box">
                    <label>Cliente</label>
                    <div v-if="visita.assinatura_cliente" class="img-wrapper signed">
                        <img :src="visita.assinatura_cliente" alt="Assinatura Cliente" />
                        <div class="timestamp"><i class="fas fa-check"></i> Assinado</div>
                    </div>
                    <div v-else class="placeholder-box">
                        <p>Pendente</p>
                        <button 
                            class="btn-sign-action" 
                            @click="iniciarAssinatura('CLIENTE')"
                            :disabled="!visita.assinatura_corretor" 
                            title="O corretor deve assinar primeiro"
                        >
                            <i class="fas fa-pen"></i> Assinar
                        </button>
                    </div>
                </div>
            </div>
        </div>

      </div>

      <div class="modal-footer">
        <button class="btn-secondary" @click="close">Fechar</button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { format, parseISO } from 'date-fns';

const props = defineProps<{ show: boolean; visita: any; }>();
const emit = defineEmits(['close', 'iniciar-visita']);

const imoveisSelecionados = ref<number[]>([]);

const todosAssinaram = computed(() => {
    return props.visita.assinatura_cliente && props.visita.assinatura_corretor;
});

watch(() => props.visita, (newVal) => {
    if (newVal && newVal.imoveis_obj) {
        imoveisSelecionados.value = newVal.imoveis_obj.map((i: any) => i.id);
    } else {
        imoveisSelecionados.value = [];
    }
}, { immediate: true });

function close() { emit('close'); }

function iniciarAssinatura(tipo: 'CORRETOR' | 'CLIENTE') {
    emit('iniciar-visita', { 
        visitaId: props.visita.id, 
        imoveisIds: imoveisSelecionados.value,
        tipo: tipo 
    });
}

function formatarData(dataString: string) {
    if (!dataString) return '--';
    return format(parseISO(dataString), 'dd/MM/yyyy HH:mm');
}
function formatarDataCompleta(dataString: string) {
    if (!dataString) return '--';
    return format(parseISO(dataString), "dd/MM/yyyy 'às' HH:mm:ss");
}
function getGoogleMapsLink(coords: string) { return `https://www.google.com/maps/search/?api=1&query=${coords}`; }
</script>

<style scoped>
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(2px); }
.modal-container { background: white; width: 90%; max-width: 700px; max-height: 90vh; border-radius: 12px; display: flex; flex-direction: column; box-shadow: 0 10px 25px rgba(0,0,0,0.1); overflow: hidden; }
.modal-header { padding: 1.5rem; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; background-color: #f8f9fa; }
.header-content h2 { margin: 0; font-size: 1.25rem; color: #2c3e50; }
.status-badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }
.status-badge.pendente { background: #e2e6ea; color: #495057; }
.status-badge.realizada { background: #d4edda; color: #155724; }
.close-btn { background: none; border: none; font-size: 1.2rem; cursor: pointer; color: #adb5bd; }
.modal-body { padding: 1.5rem; overflow-y: auto; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.info-item label { display: block; font-size: 0.75rem; color: #6c757d; font-weight: 600; text-transform: uppercase; }
.info-item p { margin: 0; font-size: 0.95rem; }
.full-width { grid-column: 1 / -1; }
.divider { height: 1px; background: #eee; margin: 1.5rem 0; }
.columns-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem; }
.column-card { background: #f8f9fa; padding: 1rem; border-radius: 8px; border: 1px solid #e9ecef; }
.column-card h3 { margin: 0 0 0.8rem 0; font-size: 0.9rem; color: #6c757d; border-bottom: 1px solid #dee2e6; padding-bottom: 0.5rem; display: flex; justify-content: space-between; }
.counter-badge { background: #007bff; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.7rem; }
.help-text { font-size: 0.8rem; background: #fff3cd; padding: 5px; border-radius: 4px; margin-bottom: 5px; }
.imoveis-list-container { max-height: 200px; overflow-y: auto; }
.imovel-item-wrapper { background: white; border: 1px solid #e9ecef; border-radius: 6px; margin-bottom: 5px; padding: 8px; }
.imovel-checkbox-row { display: flex; align-items: flex-start; gap: 10px; cursor: pointer; }
.signatures-section { margin-top: 1rem; border: 1px solid #d1e7dd; background: #f0fff4; border-radius: 8px; padding: 1rem; }
.signatures-section h3 { color: #0f5132; font-size: 1rem; margin-top: 0; }
.proof-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.signature-box { background: white; padding: 10px; border-radius: 6px; border: 1px solid #c3e6cb; text-align: center; }
.img-wrapper img { max-height: 60px; max-width: 100%; }
.timestamp { font-size: 0.7rem; color: #28a745; margin-top: 5px; }
.placeholder-box { padding: 10px; color: #6c757d; }
.btn-sign-action { background: #007bff; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: 600; margin-top: 5px; }
.btn-sign-action:disabled { background: #ccc; cursor: not-allowed; }
.modal-footer { padding: 1rem; border-top: 1px solid #eee; display: flex; justify-content: flex-end; background: #f8f9fa; }
.btn-secondary { background: #6c757d; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer; }
</style>