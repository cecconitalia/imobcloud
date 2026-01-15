<template>
  <div class="min-h-screen bg-gray-50 p-4 md:p-8 font-sans text-slate-700">
    
    <header class="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
      <div class="flex flex-col gap-2">
        <nav class="flex items-center gap-2 text-xs font-medium text-slate-400 uppercase tracking-wide">
          <router-link to="/" class="hover:text-primary-600 transition-colors decoration-none">Início</router-link>
          <div class="i-fas-chevron-right text-[10px]" />
          <router-link to="/imoveis" class="hover:text-primary-600 transition-colors decoration-none">Imóveis</router-link>
          <div class="i-fas-chevron-right text-[10px]" />
          <span class="text-primary-600 font-bold">{{ isEditing ? 'Editar' : 'Novo' }}</span>
        </nav>
        <h1 class="text-2xl md:text-3xl font-light text-slate-800 tracking-tight m-0">
          {{ isEditing ? 'Editar Imóvel' : 'Cadastrar Novo Imóvel' }}
        </h1>
      </div>
    </header>

    <div v-if="isLoadingData" class="flex flex-col items-center justify-center py-16 text-slate-400">
         <div class="w-10 h-10 border-3 border-slate-200 border-t-primary-500 rounded-full animate-spin mb-4" />
         <p class="text-sm font-medium">A carregar dados do imóvel...</p>
    </div>

    <form v-else @submit.prevent="handleSaveAndExit" class="grid grid-cols-1 lg:grid-cols-[1fr_350px] gap-6 items-start">
      
      <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col min-h-[600px]">
            
            <div class="flex flex-wrap bg-slate-50 border-b border-slate-200">
                <button 
                    v-for="tab in tabs" 
                    :key="tab.id"
                    type="button" 
                    @click="activeTab = tab.id" 
                    :disabled="tab.disabled"
                    class="flex-1 min-w-[110px] py-4 px-2 text-sm font-medium text-slate-500 hover:text-slate-700 hover:bg-slate-100 transition-colors border-b-2 border-transparent flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                    :class="{ '!text-primary-600 !border-primary-600 !bg-white font-bold': activeTab === tab.id }"
                >
                    <div :class="tab.icon"></div> {{ tab.label }}
                </button>
            </div>

            <div class="p-6 md:p-8 flex-1">
                
                <div v-show="activeTab === 'geral'" class="animate-fade-in flex flex-col gap-8">
                    <div class="flex flex-col gap-5">
                        <div class="flex flex-col gap-1.5">
                            <label class="text-sm font-bold text-slate-600">Título do Anúncio <span class="text-red-500">*</span></label>
                            <div class="relative">
                                <div class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 i-fas-heading text-sm pointer-events-none" />
                                <input 
                                    type="text" 
                                    v-model="imovel.titulo_anuncio" 
                                    required 
                                    class="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white"
                                    placeholder="Ex: Apartamento Vista Mar no Centro" 
                                />
                            </div>
                        </div>

                        <div>
                            <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 pb-2 border-b border-dashed border-slate-200">Localização</h3>
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
                                <div class="flex flex-col gap-1.5">
                                    <label class="text-sm font-bold text-slate-600">CEP</label>
                                    <div class="relative">
                                        <div class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 i-fas-map-marker-alt text-sm pointer-events-none z-10" />
                                        <CepInput 
                                            v-model="imovel.cep" 
                                            class="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" 
                                        />
                                    </div>
                                </div>
                                <div class="flex flex-col gap-1.5 md:col-span-2">
                                    <label class="text-sm font-bold text-slate-600">Logradouro <span class="text-red-500">*</span></label>
                                    <input type="text" v-model="imovel.logradouro" required class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" />
                                </div>
                                <div class="flex flex-col gap-1.5">
                                    <label class="text-sm font-bold text-slate-600">Número</label>
                                    <input type="text" v-model="imovel.numero" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" />
                                </div>
                                <div class="flex flex-col gap-1.5 md:col-span-2">
                                    <label class="text-sm font-bold text-slate-600">Complemento</label>
                                    <input type="text" v-model="imovel.complemento" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" />
                                </div>
                                <div class="flex flex-col gap-1.5">
                                    <label class="text-sm font-bold text-slate-600">Bairro <span class="text-red-500">*</span></label>
                                    <input type="text" v-model="imovel.bairro" required class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" />
                                </div>
                                <div class="flex flex-col gap-1.5">
                                    <label class="text-sm font-bold text-slate-600">Cidade <span class="text-red-500">*</span></label>
                                    <input type="text" v-model="imovel.cidade" required class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" />
                                </div>
                                <div class="flex flex-col gap-1.5">
                                    <label class="text-sm font-bold text-slate-600">Estado (UF) <span class="text-red-500">*</span></label>
                                    <input type="text" v-model="imovel.estado" maxlength="2" required class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white uppercase" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div v-show="activeTab === 'valores'" class="animate-fade-in flex flex-col gap-8">
                    <div>
                        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 pb-2 border-b border-dashed border-slate-200">Financeiro</h3>
                        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-5">
                            <div class="flex flex-col gap-1.5">
                                <label class="text-sm font-bold text-slate-600">Valor de Venda</label>
                                <MoneyInput v-model="imovel.valor_venda" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" :prefix="'R$ '" />
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <label class="text-sm font-bold text-slate-600">Valor de Aluguel</label>
                                <MoneyInput v-model="imovel.valor_aluguel" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" :prefix="'R$ '" />
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <label class="text-sm font-bold text-slate-600">Condomínio</label>
                                <MoneyInput v-model="imovel.valor_condominio" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" :prefix="'R$ '" />
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <label class="text-sm font-bold text-slate-600">IPTU (Anual)</label>
                                <MoneyInput v-model="imovel.valor_iptu" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" :prefix="'R$ '" />
                            </div>
                        </div>
                    </div>

                    <div>
                        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 pb-2 border-b border-dashed border-slate-200">Medidas e Divisões</h3>
                        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-5">
                            <div class="flex flex-col gap-1.5">
                                <label class="text-sm font-bold text-slate-600">Área Total</label>
                                <input type="number" step="0.01" v-model.number="imovel.area_total" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" placeholder="m²" />
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <label class="text-sm font-bold text-slate-600">Área Útil</label>
                                <input type="number" step="0.01" v-model.number="imovel.area_util" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" placeholder="m²" />
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <label class="text-sm font-bold text-slate-600">Quartos</label>
                                <input type="number" v-model.number="imovel.quartos" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" />
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <label class="text-sm font-bold text-slate-600">Suítes</label>
                                <input type="number" v-model.number="imovel.suites" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" />
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <label class="text-sm font-bold text-slate-600">Banheiros</label>
                                <input type="number" v-model.number="imovel.banheiros" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" />
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <label class="text-sm font-bold text-slate-600">Vagas</label>
                                <input type="number" v-model.number="imovel.vagas_garagem" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" />
                            </div>
                        </div>
                    </div>
                </div>

                <div v-show="activeTab === 'caracteristicas'" class="animate-fade-in flex flex-col gap-8">
                    <div>
                        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 pb-2 border-b border-dashed border-slate-200">Comodidades do Imóvel</h3>
                        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.lavabo" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Lavabo</span></label>
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.escritorio" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Escritório</span></label>
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.varanda" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Varanda / Sacada</span></label>
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.mobiliado" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Mobiliado</span></label>
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.ar_condicionado" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Ar Condicionado</span></label>
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.moveis_planejados" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Móveis Planejados</span></label>
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.piscina_privativa" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Piscina Privativa</span></label>
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.churrasqueira_privativa" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Churrasqueira</span></label>
                        </div>
                    </div>

                    <div>
                        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 pb-2 border-b border-dashed border-slate-200">Infraestrutura do Condomínio</h3>
                        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.portaria_24h" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Portaria 24h</span></label>
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.elevador" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Elevador</span></label>
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.piscina_condominio" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Piscina</span></label>
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.academia" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Academia</span></label>
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.salao_festas" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Salão de Festas</span></label>
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.playground" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Playground</span></label>
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.quadra_esportiva" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Quadra Esportiva</span></label>
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.espaco_pet" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Espaço Pet</span></label>
                        </div>
                    </div>

                    <div>
                        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 pb-2 border-b border-dashed border-slate-200">Descrição e Observações</h3>
                        <div class="flex flex-col gap-4">
                            <div class="flex flex-col gap-1.5">
                                <div class="flex justify-between items-center mb-1">
                                    <label class="text-sm font-bold text-slate-600">Descrição Completa (Site)</label>
                                    <button type="button" @click.prevent="handleGerarDescricaoIA" 
                                            :disabled="isGerandoDescricao || !isEditing" 
                                            class="text-xs font-bold text-primary-600 hover:text-primary-700 flex items-center gap-1.5 transition-colors cursor-pointer disabled:opacity-50">
                                        <div :class="isGerandoDescricao ? 'i-fas-spinner animate-spin' : 'i-fas-magic'"></div>
                                        {{ isGerandoDescricao ? 'Gerando...' : 'Gerar com IA' }}
                                    </button>
                                </div>
                                <textarea v-model="imovel.descricao_completa" rows="6" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white resize-y min-h-[100px]"></textarea>
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <label class="text-sm font-bold text-slate-600">Outras Características</label>
                                <textarea v-model="imovel.outras_caracteristicas" rows="3" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white resize-y min-h-[80px]"></textarea>
                            </div>
                        </div>
                    </div>
                </div>

                <div v-show="activeTab === 'imagens'" class="animate-fade-in">
                    <div v-if="isEditing && imovel.id">
                        <ImovelImagensView :imovel-id="Number(imovel.id)" />
                    </div>
                    <div v-else class="flex flex-col items-center justify-center py-16 text-slate-400 bg-slate-50 rounded-lg border border-dashed border-slate-200">
                        <div class="i-fas-save text-3xl mb-3 opacity-50" />
                        <h3 class="text-base font-bold text-slate-600 mb-1">Salve o imóvel primeiro</h3>
                        <p class="text-sm">Você precisa salvar os dados básicos antes de fazer upload das imagens.</p>
                    </div>
                </div>

                <div v-show="activeTab === 'autorizacao'" class="animate-fade-in flex flex-col gap-8">
                    <div>
                        <div class="flex flex-col gap-1.5 mb-6">
                            <label class="text-sm font-bold text-slate-600">Proprietário <span class="text-red-500">*</span></label>
                            <div class="relative">
                                <input 
                                    type="text" 
                                    v-model="searchQuery" 
                                    @input="debouncedSearch($event.target.value)"
                                    placeholder="Buscar proprietário por nome, email ou CPF..."
                                    class="w-full pl-3 pr-10 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white"
                                    autocomplete="off"
                                    :disabled="isLoadingData || isSearchingProprietario"
                                />
                                <div class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">
                                    <div v-if="isSearchingProprietario" class="i-fas-spinner animate-spin" />
                                    <div v-else class="i-fas-search" />
                                </div>
                                
                                <ul v-if="searchQuery && proprietarioSearchResults.length" class="absolute top-full left-0 right-0 bg-white border border-slate-200 rounded-lg mt-1 shadow-lg z-20 max-h-60 overflow-y-auto list-none p-0 m-0">
                                    <li v-for="cliente in proprietarioSearchResults" 
                                        :key="cliente.id"
                                        @click="selectProprietario(cliente)"
                                        class="px-4 py-3 hover:bg-slate-50 cursor-pointer border-b border-slate-50 last:border-none transition-colors"
                                    >
                                        <div class="text-sm font-bold text-slate-800">{{ cliente.nome || cliente.razao_social }}</div>
                                        <div class="text-xs text-slate-500">{{ cliente.documento }} - {{ cliente.email }}</div>
                                    </li>
                                </ul>
                            </div>
                            
                            <div v-if="proprietarioNomeSelecionado" class="mt-2 flex items-center justify-between bg-primary-50 border border-primary-200 text-primary-700 px-3 py-2 rounded-lg text-sm">
                                <div class="flex items-center gap-2">
                                    <div class="i-fas-user-check" />
                                    <span class="font-medium">{{ proprietarioNomeSelecionado }}</span>
                                </div>
                                <button type="button" @click="clearProprietarioSelection" class="text-primary-400 hover:text-primary-700 cursor-pointer bg-transparent border-none flex items-center" title="Remover">
                                    <div class="i-fas-times" />
                                </button>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-5">
                            <div class="flex flex-col gap-1.5">
                                <label class="text-sm font-bold text-slate-600">Matrícula</label>
                                <input type="text" v-model="imovel.numero_matricula" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" />
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <label class="text-sm font-bold text-slate-600">Comissão (%)</label>
                                <MoneyInput v-model="imovel.comissao_percentual" :suffix="'%'" :precision="2" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" />
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <label class="text-sm font-bold text-slate-600">Data Captação</label>
                                <input type="date" v-model="imovel.data_captacao" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" />
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <label class="text-sm font-bold text-slate-600">Fim Autorização</label>
                                <input type="date" v-model="imovel.data_fim_autorizacao" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" />
                            </div>
                        </div>
                    </div>

                    <div>
                        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 pb-2 border-b border-dashed border-slate-200">Status da Documentação</h3>
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.possui_exclusividade" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Contrato de Exclusividade</span></label>
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.financiavel" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Aceita Financiamento</span></label>
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.quitado" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Quitado</span></label>
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-50 transition-colors text-sm text-slate-600"><input type="checkbox" v-model="imovel.documentacao_ok" class="w-4 h-4 accent-primary-600 cursor-pointer"><span>Documentação OK</span></label>
                        </div>

                        <div class="flex flex-col gap-1.5 mt-6">
                            <label class="text-sm font-bold text-slate-600">Obs. Contratuais</label>
                            <textarea v-model="imovel.informacoes_adicionais_autorizacao" rows="3" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white" placeholder="Informações internas sobre a autorização..."></textarea>
                        </div>
                        
                        <div class="mt-6" v-if="isEditing && imovel.id">
                            <button type="button" @click="gerarContratoPDF" class="w-full px-4 py-2.5 rounded-lg text-sm font-medium text-slate-600 bg-white border border-slate-300 hover:bg-slate-50 transition-colors cursor-pointer flex items-center justify-center gap-2">
                                <div class="i-fas-file-pdf text-red-500" /> Gerar Contrato de Autorização
                            </button>
                        </div>
                    </div>
                </div>

                <div v-show="activeTab === 'publico'" class="animate-fade-in">
                    <div class="bg-amber-50 border border-amber-200 text-amber-800 p-3 rounded-lg flex items-start gap-3 mb-6">
                        <div class="i-fas-info-circle text-lg mt-0.5" />
                        <p class="text-sm m-0">Controle quais campos aparecem publicamente no site da imobiliária.</p>
                    </div>
                    
                    <div v-for="(campos, categoria) in camposVisiveis" :key="categoria" class="mb-6 pb-6 border-b border-slate-100 last:border-none last:mb-0 last:pb-0">
                        <h4 class="text-sm font-bold text-slate-700 mb-3">{{ categoria }}</h4>
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                            <label v-for="(label, key) in campos" :key="key" class="flex items-center gap-2 cursor-pointer text-sm text-slate-600">
                                <input type="checkbox" :id="key" v-model="imovel.configuracao_publica[key]" class="w-4 h-4 accent-primary-600 cursor-pointer">
                                <span>{{ label }}</span>
                            </label>
                        </div>
                    </div>
                </div>

            </div>

            <div class="bg-slate-50 border-t border-slate-200 p-4 md:px-8 flex justify-between items-center">
                <button 
                    type="button" 
                    @click="handleCancel" 
                    class="px-4 py-2 rounded-md text-sm font-medium text-slate-600 bg-white border border-slate-300 hover:bg-slate-50 transition-all cursor-pointer shadow-sm"
                >
                    Cancelar
                </button>
                
                <div class="flex gap-3">
                    <button 
                        type="button" 
                        @click="handleSaveAndContinue" 
                        class="px-4 py-2 rounded-md text-sm font-medium text-primary-600 bg-white border border-primary-600 hover:bg-primary-50 transition-all flex items-center gap-2 cursor-pointer shadow-sm" 
                        :disabled="isSubmitting"
                    >
                        <div class="i-fas-save" /> Salvar e Continuar
                    </button>
                    
                    <button 
                        type="submit" 
                        class="flex items-center justify-center gap-2 px-6 py-2 rounded-md text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 shadow-sm hover:shadow transition-all disabled:opacity-70 disabled:cursor-not-allowed border-none cursor-pointer" 
                        :disabled="isSubmitting"
                    >
                        <div v-if="isSubmitting" class="i-fas-spinner animate-spin" />
                        <span v-else>Salvar e Sair</span>
                    </button>
                </div>
            </div>
      </div> 
      
      <div class="flex flex-col gap-6">
            
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5 border-l-4 border-l-primary-500">
                 <div class="mb-4 pb-2 border-b border-slate-100">
                     <h3 class="text-sm font-bold text-slate-700 m-0 flex items-center gap-2">
                        <div class="i-fas-cog text-primary-600" /> Configurações
                     </h3>
                 </div>
                 
                 <div class="flex flex-col gap-4">
                     <div class="flex flex-col gap-1.5">
                        <label class="text-xs font-bold text-slate-500 uppercase">Tipo de Imóvel</label>
                        <select v-model="imovel.tipo" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white">
                            <option value="CASA">Casa</option>
                            <option value="APARTAMENTO">Apartamento</option>
                            <option value="TERRENO">Terreno</option>
                            <option value="SALA_COMERCIAL">Sala Comercial</option>
                            <option value="GALPAO">Galpão</option>
                            <option value="RURAL">Rural</option>
                            <option value="OUTRO">Outro</option>
                        </select>
                     </div>

                     <div class="flex flex-col gap-1.5">
                        <label class="text-xs font-bold text-slate-500 uppercase">Finalidade</label>
                        <select v-model="imovel.finalidade" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white">
                            <option value="RESIDENCIAL">Residencial</option>
                            <option value="COMERCIAL">Comercial</option>
                            <option value="INDUSTRIAL">Industrial</option>
                            <option value="RURAL">Rural</option>
                        </select>
                     </div>

                     <div class="flex flex-col gap-1.5">
                        <label class="text-xs font-bold text-slate-500 uppercase">Situação</label>
                        <select v-model="imovel.situacao" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white">
                            <option :value="null">Não informado</option>
                            <option value="NOVO">Novo</option>
                            <option value="USADO">Usado</option>
                            <option value="NA_PLANTA">Na Planta</option>
                        </select>
                     </div>

                     <div class="flex flex-col gap-1.5">
                        <label class="text-xs font-bold text-slate-500 uppercase">Status Atual</label>
                        <select v-model="imovel.status" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-slate-700 bg-white font-medium" :class="{'text-emerald-600': imovel.status === 'A_VENDA', 'text-amber-600': imovel.status === 'EM_CONSTRUCAO'}">
                            <option value="A_VENDA">À Venda</option>
                            <option value="PARA_ALUGAR">Para Alugar</option>
                            <option value="VENDIDO">Vendido</option>
                            <option value="ALUGADO">Alugado</option>
                            <option value="EM_CONSTRUCAO">Em Construção</option>
                            <option value="DESATIVADO">Desativado</option>
                        </select>
                     </div>
                 </div>
            </div>

            <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5 border-l-4 border-l-emerald-500">
                 <div class="mb-4 pb-2 border-b border-slate-100">
                     <h3 class="text-sm font-bold text-slate-700 m-0 flex items-center gap-2">
                        <div class="i-fas-globe text-emerald-500" /> Visibilidade
                     </h3>
                 </div>
                 
                 <div class="flex items-center gap-3">
                    <label class="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" v-model="imovel.publicado_no_site" class="sr-only peer">
                        <div class="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-100 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"></div>
                    </label>
                    <span class="text-sm font-bold" :class="imovel.publicado_no_site ? 'text-emerald-600' : 'text-slate-400'">
                        {{ imovel.publicado_no_site ? 'Publicado' : 'Oculto' }}
                    </span>
                 </div>
                 <p class="text-xs text-slate-400 mt-3 italic">Se desativado, o imóvel não aparecerá no site, independente das outras configurações.</p>
            </div>

      </div> 

    </form>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api'; 
import ImovelImagensView from './ImovelImagensView.vue';
import { debounce } from 'lodash'; 
import '@fortawesome/fontawesome-free/css/all.css';
import MoneyInput from '@/components/MoneyInput.vue';
import CepInput from '@/components/CepInput.vue';

const route = useRoute();
const router = useRouter();

const imovelId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!imovelId.value);
const activeTab = ref('geral');

const tabs = [
    { id: 'geral', label: 'Dados Básicos', icon: 'i-fas-info-circle' },
    { id: 'valores', label: 'Valores', icon: 'i-fas-dollar-sign' },
    { id: 'caracteristicas', label: 'Detalhes', icon: 'i-fas-list' },
    { id: 'imagens', label: 'Imagens', icon: 'i-fas-camera', disabled: !isEditing.value },
    { id: 'autorizacao', label: 'Autorização', icon: 'i-fas-file-signature' },
    { id: 'publico', label: 'Site', icon: 'i-fas-globe' },
];

const isLoadingData = ref(false);
const isSubmitting = ref(false);
const isGerandoDescricao = ref(false); 

const proprietarioSearchResults = ref<any[]>([]);
const searchQuery = ref('');
const isSearchingProprietario = ref(false);

const proprietarioNomeSelecionado = computed(() => {
    if (imovel.value && imovel.value.proprietario_detalhes) {
        return imovel.value.proprietario_detalhes.nome || imovel.value.proprietario_detalhes.razao_social;
    }
    return null;
});

const camposVisiveis = {
    'Geral': {
        'titulo_anuncio': 'Título', 'tipo': 'Tipo', 'finalidade': 'Finalidade', 'status': 'Status',
    },
    'Financeiro': {
        'valor_venda': 'Valor Venda', 'valor_aluguel': 'Valor Aluguel', 'valor_condominio': 'Condomínio', 'valor_iptu': 'IPTU',
    },
    'Localização': {
        'logradouro': 'Logradouro', 'numero': 'Número', 'bairro': 'Bairro', 'cidade': 'Cidade',
    },
    'Dimensões': {
        'area_util': 'Área Útil', 'area_total': 'Área Total', 'quartos': 'Quartos', 'suites': 'Suítes', 'vagas_garagem': 'Vagas',
    },
    'Detalhes': {
        'descricao_completa': 'Descrição', 'piscina_privativa': 'Piscina', 'churrasqueira_privativa': 'Churrasqueira', 'portaria_24h': 'Portaria 24h', 'elevador': 'Elevador', 'aceita_pet': 'Aceita Pet'
    },
};

const createEmptyImovel = () => {
    const allPublicKeys = Object.values(camposVisiveis).flatMap(obj => Object.keys(obj));
    const defaultConfig = allPublicKeys.reduce((acc, key) => { acc[key] = true; return acc; }, {} as { [key: string]: boolean });

    return {
        id: null,
        titulo_anuncio: '',
        codigo_referencia: '',
        tipo: 'CASA',
        finalidade: 'RESIDENCIAL',
        status: 'A_VENDA',
        situacao: null,
        publicado_no_site: true,
        valor_venda: null as number | null,
        valor_aluguel: null as number | null,
        valor_condominio: null as number | null,
        valor_iptu: null as number | null,
        logradouro: '', numero: '', complemento: '', bairro: '', cidade: '', estado: '', cep: '',
        quartos: 0, suites: 0, banheiros: 0, vagas_garagem: 0, area_total: 0, area_util: 0,
        lavabo: false, escritorio: false, varanda: false, mobiliado: false, ar_condicionado: false,
        moveis_planejados: false, piscina_privativa: false, churrasqueira_privativa: false,
        portaria_24h: false, elevador: false, piscina_condominio: false, academia: false,
        salao_festas: false, playground: false, quadra_esportiva: false, espaco_pet: false,
        financiavel: false, quitado: false, documentacao_ok: false, aceita_pet: false,
        proprietario: null,
        numero_matricula: '', data_captacao: null, data_fim_autorizacao: null, possui_exclusividade: false,
        comissao_percentual: null as number | null,
        informacoes_adicionais_autorizacao: '',
        outras_caracteristicas: '', descricao_completa: '', 
        configuracao_publica: defaultConfig,
        proprietario_detalhes: null as any 
    };
};

const imovel = ref(createEmptyImovel());

const parseToNumber = (value: any): number | null => {
    if (value === null || value === undefined || value === '') return null;
    const num = Number(value);
    return isNaN(num) ? null : num;
};

async function fetchImovelData(id: string) {
  if (!id) return; 
  isLoadingData.value = true;
  try {
    const { data } = await apiClient.get(`/v1/imoveis/${id}/`);
    const emptyImovel = createEmptyImovel();
    
    imovel.value = { 
      ...emptyImovel,
      ...data,
      valor_venda: parseToNumber(data.valor_venda),
      valor_aluguel: parseToNumber(data.valor_aluguel),
      valor_condominio: parseToNumber(data.valor_condominio),
      valor_iptu: parseToNumber(data.valor_iptu),
      comissao_percentual: parseToNumber(data.comissao_percentual),
      proprietario: data.proprietario_detalhes?.id || null, 
      proprietario_detalhes: data.proprietario_detalhes || null, 
      configuracao_publica: { ...emptyImovel.configuracao_publica, ...data.configuracao_publica }
    };
  } catch (error) { console.error(error); } finally { isLoadingData.value = false; }
}

const searchProprietarios = async (query: string) => {
    if (!query || query.length < 3) { proprietarioSearchResults.value = []; return; }
    isSearchingProprietario.value = true;
    try {
        const response = await apiClient.get('/v1/clientes/', { params: { search: query, status: 'ativo' } });
        proprietarioSearchResults.value = response.data;
    } catch (error) { console.error(error); } finally { isSearchingProprietario.value = false; }
};
const debouncedSearch = debounce(searchProprietarios, 300); 

function selectProprietario(cliente: any) {
    imovel.value.proprietario = cliente.id; 
    imovel.value.proprietario_detalhes = cliente; 
    proprietarioSearchResults.value = []; searchQuery.value = ''; 
}
function clearProprietarioSelection() { imovel.value.proprietario = null; imovel.value.proprietario_detalhes = null; }

async function gerarContratoPDF() {
    if (!imovel.value.id || !imovel.value.proprietario) {
         alert("Selecione um 'Proprietário' para gerar o contrato."); return;
    }
    try {
        const payload = {
            comissao_percentual: imovel.value.comissao_percentual,
            data_fim_autorizacao: imovel.value.data_fim_autorizacao,
            informacoes_adicionais: imovel.value.informacoes_adicionais_autorizacao,
        };
        const response = await apiClient.post(`/v1/imoveis/${imovel.value.id}/gerar-autorizacao-pdf/`, payload, { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a'); link.href = url;
        link.setAttribute('download', `autorizacao_${imovel.value.codigo_referencia}.pdf`);
        document.body.appendChild(link); link.click(); link.remove(); window.URL.revokeObjectURL(url);
    } catch (error) { console.error(error); alert('Erro ao gerar PDF.'); }
}

async function handleGerarDescricaoIA() {
    if (!isEditing.value || !imovel.value.id) { alert("Salve o imóvel antes."); return; }
    isGerandoDescricao.value = true;
    try {
        const response = await apiClient.post(`/v1/imoveis/${imovel.value.id}/gerar-descricao-ia/`);
        if (response.data?.descricao) { imovel.value.descricao_completa = response.data.descricao; alert("Gerado!"); }
    } catch (error: any) { alert(`Erro: ${error.response?.data?.error || 'Desconhecido'}`); } finally { isGerandoDescricao.value = false; }
}

async function saveImovel() {
  isSubmitting.value = true;
  const payload = { ...imovel.value };
  delete payload.id; delete payload.proprietario_detalhes; 
  Object.keys(payload).forEach(key => { if (key !== 'proprietario' && (payload[key] === null || payload[key] === undefined)) delete payload[key]; });
  
  try {
    if (isEditing.value) return await apiClient.put(`/v1/imoveis/${imovelId.value}/`, payload);
    else return await apiClient.post('/v1/imoveis/', payload);
  } catch (error: any) {
    console.error(error);
    alert('Erro ao salvar. Verifique os campos.');
    return null;
  } finally { isSubmitting.value = false; }
}

async function handleSaveAndExit() {
  const response = await saveImovel();
  if (response?.data) router.push({ name: 'imoveis' });
}

async function handleSaveAndContinue() {
  const response = await saveImovel();
  if (response?.data) {
    const wasCreating = !isEditing.value;
    imovel.value.id = response.data.id;
    fetchImovelData(String(response.data.id));
    if (wasCreating) {
        router.replace({ name: 'imovel-editar', params: { id: response.data.id }, query: { tab: 'imagens' } });
        activeTab.value = 'imagens';
    } else {
        alert('Salvo com sucesso!');
    }
  }
}

function handleCancel() { router.push({ name: 'imoveis' }); }

watch(imovelId, (newId) => { if(newId) fetchImovelData(newId); }, { immediate: true });
watch(() => route.query.tab, (newTab) => { if (newTab) activeTab.value = newTab as string; });
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
</style>