<template>
  <div class="min-h-screen bg-white font-sans text-gray-600 overflow-x-hidden selection:bg-blue-100 selection:text-blue-900">
    
    <nav class="fixed top-0 left-0 right-0 z-50 transition-all duration-500 border-b border-transparent" 
         :class="{'bg-white/90 backdrop-blur-md py-2 shadow-sm border-gray-100': scrolled, 'bg-transparent py-5': !scrolled}">
      <div class="container mx-auto px-6 flex justify-between items-center">
        
        <div class="text-xl font-bold tracking-tighter flex items-center gap-2 cursor-pointer group" @click="scrollToTop">
          <div class="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:scale-110 transition-transform duration-300">
            <i class="fas fa-home text-white text-xs"></i>
          </div>
          <span :class="scrolled ? 'text-gray-800' : 'text-white'" class="transition-colors font-extrabold tracking-tight">ImobHome</span>
        </div>

        <div class="hidden md:flex items-center p-1 rounded-full border backdrop-blur-md transition-all duration-300"
             :class="scrolled 
                ? 'bg-gray-50/80 border-gray-200 shadow-inner' 
                : 'bg-white/10 border-white/20 shadow-lg'">
          
          <button @click="setFiltroEBuscar('')" 
                  class="px-4 py-1.5 rounded-full text-xs font-bold transition-all duration-300 border-none outline-none cursor-pointer"
                  :class="filtros.status === '' 
                    ? 'bg-white text-blue-600 shadow-sm transform scale-105' 
                    : (scrolled ? 'text-gray-500 hover:text-blue-600 bg-transparent' : 'text-white/90 hover:text-white hover:bg-white/10 bg-transparent')">
            Todos
          </button>

          <button @click="setFiltroEBuscar('A_VENDA')" 
                  class="px-4 py-1.5 rounded-full text-xs font-bold transition-all duration-300 border-none outline-none cursor-pointer"
                  :class="filtros.status === 'A_VENDA' 
                    ? 'bg-white text-blue-600 shadow-sm transform scale-105' 
                    : (scrolled ? 'text-gray-500 hover:text-blue-600 bg-transparent' : 'text-white/90 hover:text-white hover:bg-white/10 bg-transparent')">
            Comprar
          </button>
          
          <button @click="setFiltroEBuscar('PARA_ALUGAR')" 
                  class="px-4 py-1.5 rounded-full text-xs font-bold transition-all duration-300 border-none outline-none cursor-pointer"
                  :class="filtros.status === 'PARA_ALUGAR' 
                    ? 'bg-white text-blue-600 shadow-sm transform scale-105' 
                    : (scrolled ? 'text-gray-500 hover:text-blue-600 bg-transparent' : 'text-white/90 hover:text-white hover:bg-white/10 bg-transparent')">
            Alugar
          </button>

          <div class="w-px h-3 mx-2" :class="scrolled ? 'bg-gray-300' : 'bg-white/20'"></div>

          <button @click="goToCadastro" 
                  class="px-4 py-1.5 rounded-full text-xs font-bold transition-all duration-300 border-none outline-none cursor-pointer whitespace-nowrap"
                  :class="scrolled ? 'text-blue-600 hover:bg-blue-50 bg-transparent' : 'text-blue-200 hover:text-white hover:bg-white/10 bg-transparent'">
            Anunciar
          </button>
        </div>

        <div class="flex items-center gap-3">
           <button 
            @click="$router.push('/login')" 
            class="hidden md:block px-4 py-2 text-xs font-bold rounded-full transition-all duration-300 border-none outline-none cursor-pointer bg-transparent"
            :class="scrolled ? 'text-gray-600 hover:bg-gray-100' : 'text-white hover:bg-white/10 border border-white/20'"
          >
            Entrar
          </button>
          <button 
            @click="goToCadastro" 
            class="group relative px-5 py-2 rounded-full text-xs font-bold transition-all duration-300 shadow-lg border-none outline-none cursor-pointer flex items-center gap-2 overflow-hidden"
            :class="scrolled 
              ? 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-blue-600/40' 
              : 'bg-white text-blue-900 hover:bg-blue-50 hover:shadow-white/20'"
          >
            <span class="relative z-10 flex items-center gap-2">Cadastrar <i class="fas fa-arrow-right text-[10px] group-hover:translate-x-1 transition-transform"></i></span>
          </button>
        </div>
      </div>
    </nav>

    <header class="relative min-h-[650px] flex items-center justify-center overflow-hidden bg-gray-900">
      <div class="absolute inset-0 z-0">
        <img 
          src="https://images.unsplash.com/photo-1600596542815-e32c215962bb?q=80&w=2600&auto=format&fit=crop" 
          alt="Luxury Home" 
          class="w-full h-full object-cover opacity-60 animate-slow-zoom"
        />
        <div class="absolute inset-0 bg-gradient-to-r from-gray-900 via-gray-900/80 to-transparent"></div>
        <div class="absolute inset-0 bg-gradient-to-t from-gray-900 via-transparent to-transparent"></div>
      </div>

      <div class="container mx-auto px-6 relative z-10 pt-16 grid lg:grid-cols-2 gap-12 items-center">
        
        <div class="max-w-xl">
          <div class="animate-slide-up-fade" style="animation-delay: 0.1s;">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 border border-blue-400/30 text-blue-200 text-[10px] font-bold uppercase tracking-widest mb-6 backdrop-blur-md shadow-lg shadow-blue-900/20">
              <span class="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"></span>
              Plataforma Inteligente
            </div>
          </div>
          
          <h1 class="animate-slide-up-fade text-4xl lg:text-6xl font-bold text-white mb-4 leading-[1.1] tracking-tight drop-shadow-xl" style="animation-delay: 0.2s;">
            Seu novo lar <br/>
            está <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300">esperando.</span>
          </h1>
          
          <p class="animate-slide-up-fade text-base text-gray-300 mb-8 leading-relaxed font-light max-w-lg drop-shadow-md" style="animation-delay: 0.3s;">
            Navegue por milhares de imóveis exclusivos em Chapecó e região. Compra, venda e aluguel com segurança jurídica.
          </p>

          <div class="animate-slide-up-fade flex flex-col sm:flex-row gap-3" style="animation-delay: 0.4s;">
             <button @click="scrollTo('search-box')" class="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white px-6 py-3 rounded-xl font-bold shadow-xl shadow-blue-600/30 transition-all hover:-translate-y-0.5 flex items-center justify-center gap-2 border-none outline-none cursor-pointer text-sm">
              <i class="fas fa-search"></i> Buscar Agora
            </button>
            <button @click="goToCadastro" class="bg-white/5 hover:bg-white/10 backdrop-blur-md border border-white/20 text-white px-6 py-3 rounded-xl font-bold transition-all flex items-center justify-center gap-2 outline-none cursor-pointer hover:shadow-lg hover:shadow-white/5 text-sm hover:-translate-y-0.5">
              Sou Proprietário
            </button>
          </div>

          <div class="animate-slide-up-fade mt-10 flex items-center gap-3 text-xs text-gray-400 font-medium" style="animation-delay: 0.5s;">
             <div class="flex -space-x-2">
                <img class="w-8 h-8 rounded-full border-2 border-gray-900 object-cover" src="https://i.pravatar.cc/100?img=1" alt="User">
                <img class="w-8 h-8 rounded-full border-2 border-gray-900 object-cover" src="https://i.pravatar.cc/100?img=5" alt="User">
                <img class="w-8 h-8 rounded-full border-2 border-gray-900 object-cover" src="https://i.pravatar.cc/100?img=8" alt="User">
                <div class="w-8 h-8 rounded-full border-2 border-gray-900 bg-gray-800 text-white flex items-center justify-center text-[10px] font-bold shadow-inner">+2k</div>
             </div>
             <p>Clientes felizes em Santa Catarina.</p>
          </div>
        </div>

        <div id="search-box" class="animate-slide-left-fade hidden lg:block bg-white p-6 rounded-[2rem] shadow-2xl shadow-black/50 relative backdrop-blur-xl bg-white/95 border border-white/50" style="animation-delay: 0.4s;">
          
          <div class="flex p-1 bg-gray-100 rounded-xl mb-6 shadow-inner border border-gray-200">
            <button @click="filtros.status = ''" class="flex-1 py-2 text-xs font-extrabold rounded-lg transition-all border-none cursor-pointer" :class="filtros.status === '' ? 'bg-white text-blue-600 shadow-sm transform scale-[1.02]' : 'bg-transparent text-gray-500 hover:text-gray-700'">Todos</button>
            <button @click="filtros.status = 'A_VENDA'" class="flex-1 py-2 text-xs font-extrabold rounded-lg transition-all border-none cursor-pointer" :class="filtros.status === 'A_VENDA' ? 'bg-white text-blue-600 shadow-sm transform scale-[1.02]' : 'bg-transparent text-gray-500 hover:text-gray-700'">Comprar</button>
            <button @click="filtros.status = 'PARA_ALUGAR'" class="flex-1 py-2 text-xs font-extrabold rounded-lg transition-all border-none cursor-pointer" :class="filtros.status === 'PARA_ALUGAR' ? 'bg-white text-blue-600 shadow-sm transform scale-[1.02]' : 'bg-transparent text-gray-500 hover:text-gray-700'">Alugar</button>
          </div>

          <div class="space-y-4">
            <div class="group">
              <label class="text-[10px] font-extrabold text-gray-400 uppercase tracking-widest mb-2 block ml-1">Localização</label>
              <div class="relative flex items-center">
                <div class="absolute left-3 w-8 h-8 bg-blue-50/50 rounded-lg flex items-center justify-center text-blue-600 text-sm transition-colors group-focus-within:bg-blue-600 group-focus-within:text-white"><i class="fas fa-map-marker-alt"></i></div>
                <input v-model="filtros.cidade" type="text" placeholder="Cidade ou Bairro..." class="w-full bg-gray-50 border border-gray-200 text-gray-800 font-bold text-sm pl-14 pr-4 py-3 rounded-xl focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all h-[52px]" @keyup.enter="buscarImoveis(true)"/>
              </div>
            </div>

            <div class="grid grid-cols-5 gap-3">
              <div class="group col-span-3">
                <label class="text-[10px] font-extrabold text-gray-400 uppercase tracking-widest mb-2 block ml-1">Tipo</label>
                <div class="relative flex items-center">
                  <div class="absolute left-3 w-8 h-8 bg-blue-50/50 rounded-lg flex items-center justify-center text-blue-600 text-sm pointer-events-none z-10 transition-colors group-focus-within:bg-blue-600 group-focus-within:text-white"><i class="fas fa-home"></i></div>
                   <select v-model="filtros.tipo" class="w-full bg-gray-50 border border-gray-200 text-gray-800 font-bold text-sm pl-14 pr-8 py-3 rounded-xl focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none appearance-none cursor-pointer h-[52px] transition-all">
                    <option value="" class="text-gray-400">Todos</option>
                    <option value="CASA">Casa</option>
                    <option value="APARTAMENTO">Apartamento</option>
                    <option value="TERRENO">Terreno</option>
                    <option value="SALA_COMERCIAL">Comercial</option>
                  </select>
                  <i class="fas fa-chevron-down absolute right-4 text-gray-400 pointer-events-none text-xs"></i>
                </div>
              </div>

              <div class="col-span-2">
                <label class="text-[10px] font-bold text-transparent uppercase tracking-wider mb-2 block select-none">Action</label>
                <button @click="buscarImoveis(true)" class="group w-full h-[52px] bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-sm font-bold rounded-xl hover:shadow-lg hover:shadow-blue-600/30 transition-all active:scale-95 flex items-center justify-center gap-2 border-none outline-none cursor-pointer">
                  <span v-if="loading"><i class="fas fa-spinner fa-spin"></i></span>
                  <span v-else class="flex items-center gap-1">Buscar <i class="fas fa-arrow-right text-xs ml-1 group-hover:translate-x-1 transition-transform"></i></span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <div class="bg-white border-b border-gray-100 py-10">
        <div class="container mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-6 text-center divide-x divide-gray-100">
            <div class="group cursor-default">
                <div class="text-2xl font-black text-gray-900 mb-1 group-hover:text-blue-600 transition-colors transform group-hover:scale-110 duration-300">1.2k+</div>
                <div class="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Imóveis</div>
            </div>
             <div class="group cursor-default">
                <div class="text-2xl font-black text-gray-900 mb-1 group-hover:text-blue-600 transition-colors transform group-hover:scale-110 duration-300">450M</div>
                <div class="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Vendas</div>
            </div>
             <div class="group cursor-default">
                <div class="text-2xl font-black text-gray-900 mb-1 group-hover:text-blue-600 transition-colors transform group-hover:scale-110 duration-300">98%</div>
                <div class="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Satisfação</div>
            </div>
             <div class="group cursor-default">
                <div class="text-2xl font-black text-gray-900 mb-1 group-hover:text-blue-600 transition-colors transform group-hover:scale-110 duration-300">24h</div>
                <div class="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Suporte</div>
            </div>
        </div>
    </div>

    <section class="py-16 bg-gray-50" id="imoveis-section">
      <div class="container mx-auto px-6">
        <div class="flex flex-col md:flex-row justify-between items-end mb-10 gap-6">
          <div class="max-w-xl">
            <span class="text-blue-600 font-bold uppercase tracking-widest text-[10px] mb-2 block">Destaques Exclusivos</span>
            <h2 class="text-3xl font-extrabold text-gray-900 leading-tight">Encontre o lugar que você <br/>sempre sonhou.</h2>
          </div>
          
          <div class="flex gap-2">
             <button class="w-10 h-10 rounded-full bg-white border border-gray-200 flex items-center justify-center hover:bg-gray-50 hover:shadow-md transition text-gray-600 border-none outline-none cursor-pointer"><i class="fas fa-chevron-left text-sm"></i></button>
             <button class="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center hover:bg-blue-700 shadow-lg shadow-blue-500/30 transition border-none outline-none cursor-pointer"><i class="fas fa-chevron-right text-sm"></i></button>
          </div>
        </div>

        <div class="md:hidden mb-6">
           <input v-model="filtros.cidade" @input="buscarImoveis(false)" type="text" placeholder="Filtrar por cidade..." class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 shadow-sm text-sm">
        </div>

        <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div v-for="i in 4" :key="i" class="bg-white rounded-[1.5rem] overflow-hidden shadow-sm border border-gray-100 h-[380px] animate-pulse">
            <div class="h-52 bg-gray-200"></div>
            <div class="p-5 space-y-3">
               <div class="h-3 bg-gray-200 rounded-full w-3/4"></div>
               <div class="h-3 bg-gray-200 rounded-full w-1/2"></div>
            </div>
          </div>
        </div>

        <div v-else-if="imoveis.length === 0" class="text-center py-20">
          <div class="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4">
            <i class="fas fa-home text-blue-300 text-2xl"></i>
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-2">Nenhum imóvel encontrado</h3>
          <button @click="limparFiltros" class="text-blue-600 text-sm font-bold hover:underline border-none bg-transparent cursor-pointer">Limpar busca</button>
        </div>

        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <article 
            v-for="imovel in imoveis" 
            :key="imovel.id" 
            class="group bg-white rounded-[1.5rem] overflow-hidden shadow-sm hover:shadow-2xl hover:shadow-blue-900/10 border border-gray-100 transition-all duration-500 cursor-pointer flex flex-col h-full transform hover:-translate-y-2"
            @click="abrirImovel(imovel)"
          >
            <div class="relative h-[220px] overflow-hidden">
              <img 
                :src="getImovelImage(imovel)" 
                class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                alt="Imóvel"
              >
              <div class="absolute inset-x-0 bottom-0 h-3/4 bg-gradient-to-t from-gray-900/80 via-transparent to-transparent"></div>
              
              <div class="absolute top-3 left-3 flex gap-1.5">
                <span 
                  class="text-[9px] font-bold px-2 py-1 rounded-md uppercase tracking-wider shadow-sm text-white backdrop-blur-md border border-white/20"
                  :class="imovel.status === 'A_VENDA' ? 'bg-green-500/90' : 'bg-blue-500/90'"
                >
                  {{ formatStatus(imovel.status) }}
                </span>
                <span v-if="imovel.nome_imobiliaria" class="text-[9px] font-bold px-2 py-1 rounded-md uppercase tracking-wider shadow-sm text-gray-800 bg-white/95 backdrop-blur-md border border-white/20 flex items-center gap-1">
                    {{ imovel.nome_imobiliaria }}
                </span>
              </div>

              <div class="absolute bottom-3 left-4 text-white">
                <p class="text-[10px] font-bold text-gray-300 mb-0.5 uppercase tracking-wide flex items-center gap-1">
                    <i class="fas fa-tag text-[8px]"></i> {{ imovel.tipo }}
                </p>
                <p class="text-lg font-black tracking-tight shadow-black drop-shadow-md">{{ formatCurrency(getValor(imovel)) }}</p>
              </div>
            </div>

            <div class="p-5 flex-1 flex flex-col">
              <h3 class="text-base font-bold text-gray-800 mb-1 leading-snug line-clamp-2 group-hover:text-blue-600 transition-colors">
                {{ imovel.titulo_anuncio }}
              </h3>
              
              <div class="flex items-center text-gray-500 text-xs mb-4 font-medium">
                 <i class="fas fa-map-marker-alt text-gray-300 mr-1.5"></i>
                 <span class="truncate">{{ imovel.cidade }}<span v-if="imovel.bairro">, {{ imovel.bairro }}</span></span>
              </div>

              <div class="grid grid-cols-3 gap-2 mt-auto border-t border-gray-50 pt-3">
                <div class="flex flex-col items-center justify-center p-1.5 rounded-lg bg-gray-50 group-hover:bg-blue-50 transition-colors">
                  <i class="fas fa-bed text-gray-400 group-hover:text-blue-500 mb-1 text-[10px]"></i>
                  <span class="text-xs font-bold text-gray-700">{{ imovel.quartos }}</span>
                </div>
                <div class="flex flex-col items-center justify-center p-1.5 rounded-lg bg-gray-50 group-hover:bg-blue-50 transition-colors">
                  <i class="fas fa-bath text-gray-400 group-hover:text-blue-500 mb-1 text-[10px]"></i>
                  <span class="text-xs font-bold text-gray-700">{{ imovel.banheiros || 1 }}</span>
                </div>
                <div class="flex flex-col items-center justify-center p-1.5 rounded-lg bg-gray-50 group-hover:bg-blue-50 transition-colors">
                  <i class="fas fa-ruler text-gray-400 group-hover:text-blue-500 mb-1 text-[10px]"></i>
                  <span class="text-xs font-bold text-gray-700">{{ imovel.area_util }}m²</span>
                </div>
              </div>
            </div>
          </article>
        </div>

        <div v-if="imoveis.length > 0" class="mt-12 text-center">
             <button class="bg-white border border-gray-200 text-gray-600 hover:border-blue-500 hover:text-blue-600 font-bold py-3 px-8 rounded-full transition-all shadow-sm hover:shadow-md border-none cursor-pointer text-sm">
                Ver mais imóveis
             </button>
        </div>
      </div>
    </section>

    <section class="relative py-20 bg-gray-900 overflow-hidden">
        <div class="absolute top-0 right-0 w-[600px] h-[600px] bg-blue-600/20 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/2 animate-pulse"></div>
        <div class="absolute bottom-0 left-0 w-[400px] h-[400px] bg-purple-600/20 rounded-full blur-[80px] translate-y-1/2 -translate-x-1/2"></div>

        <div class="container mx-auto px-6 relative z-10">
            <div class="bg-gradient-to-br from-gray-800/80 to-gray-900/80 backdrop-blur-xl border border-white/10 rounded-[3rem] p-10 md:p-14 flex flex-col md:flex-row items-center justify-between gap-10 shadow-2xl relative overflow-hidden group">
                <div class="md:max-w-lg relative z-10">
                    <span class="inline-block px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 font-bold uppercase tracking-widest text-[10px] mb-4">Área do Proprietário</span>
                    <h2 class="text-3xl md:text-5xl font-black text-white mb-4 leading-tight">Quer vender ou alugar <br/>com <span class="text-blue-500">rapidez?</span></h2>
                    <p class="text-gray-300 text-base mb-8 leading-relaxed font-light">
                        Cadastre seu imóvel em nossa plataforma em menos de 5 minutos. Fotos profissionais e gestão automatizada.
                    </p>
                    <div class="flex flex-col sm:flex-row gap-3 justify-center md:justify-start">
                        <button @click="goToCadastro" class="bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-8 rounded-xl shadow-xl shadow-blue-600/30 transition-all hover:-translate-y-1 flex items-center justify-center gap-2 border-none outline-none cursor-pointer text-sm">
                           <i class="fas fa-file-signature"></i> Cadastrar Imóvel
                        </button>
                        <button class="text-white font-bold hover:text-blue-300 px-6 py-3 transition flex items-center justify-center gap-2 border border-white/10 rounded-xl hover:bg-white/5 cursor-pointer text-sm">
                           <i class="fas fa-play-circle"></i> Como funciona
                        </button>
                    </div>
                </div>
                
                <div class="relative w-full md:w-auto z-10">
                    <div class="bg-white p-6 rounded-[1.5rem] shadow-2xl transform rotate-2 hover:rotate-0 transition-all duration-500 md:w-[320px]">
                        <div class="flex items-center gap-4 mb-4">
                            <div class="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center text-green-600 text-lg shadow-sm"><i class="fas fa-check"></i></div>
                            <div>
                                <div class="font-bold text-gray-800 text-base">Imóvel Publicado!</div>
                                <div class="text-xs text-gray-500 font-medium">Visível para todos.</div>
                            </div>
                        </div>
                        <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
                            <div class="h-full bg-gradient-to-r from-green-400 to-green-500 w-full animate-[progress_1.5s_ease-out]"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <footer class="bg-white border-t border-gray-100 pt-12 pb-8 text-gray-500 text-xs">
      <div class="container mx-auto px-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          <div class="col-span-1 md:col-span-1">
            <div class="text-xl font-black text-gray-900 flex items-center gap-2 mb-4">
              <i class="fas fa-home text-blue-600"></i> ImobHome
            </div>
            <p class="mb-6 leading-relaxed">Conectando pessoas aos seus sonhos com simplicidade e segurança.</p>
            <div class="flex gap-3">
               <a href="#" class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-400 hover:bg-blue-600 hover:text-white transition-all"><i class="fab fa-instagram text-xs"></i></a>
               <a href="#" class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-400 hover:bg-blue-600 hover:text-white transition-all"><i class="fab fa-facebook-f text-xs"></i></a>
               <a href="#" class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-400 hover:bg-blue-600 hover:text-white transition-all"><i class="fab fa-linkedin-in text-xs"></i></a>
            </div>
          </div>
          
          <div>
             <h4 class="font-bold text-gray-900 mb-4 uppercase text-[10px] tracking-wider">Navegação</h4>
             <ul class="space-y-2">
                <li><button @click="scrollToTop" class="hover:text-blue-600 transition border-none bg-transparent cursor-pointer p-0">Início</button></li>
                <li><button @click="setFiltroEBuscar('A_VENDA')" class="hover:text-blue-600 transition border-none bg-transparent cursor-pointer p-0">Comprar</button></li>
                <li><button @click="setFiltroEBuscar('PARA_ALUGAR')" class="hover:text-blue-600 transition border-none bg-transparent cursor-pointer p-0">Alugar</button></li>
                <li><button @click="goToCadastro" class="hover:text-blue-600 transition text-blue-600 font-bold border-none bg-transparent cursor-pointer p-0">Anunciar</button></li>
             </ul>
          </div>

           <div>
             <h4 class="font-bold text-gray-900 mb-4 uppercase text-[10px] tracking-wider">Institucional</h4>
             <ul class="space-y-2">
                <li><a href="#" class="hover:text-blue-600 transition">Sobre Nós</a></li>
                <li><a href="#" class="hover:text-blue-600 transition">Privacidade</a></li>
                <li><a href="#" class="hover:text-blue-600 transition">Termos</a></li>
                <li><a href="#" class="hover:text-blue-600 transition">Carreiras</a></li>
             </ul>
          </div>

           <div>
             <h4 class="font-bold text-gray-900 mb-4 uppercase text-[10px] tracking-wider">Contato</h4>
             <ul class="space-y-3">
                <li class="flex items-center gap-2">
                    <i class="fas fa-phone text-blue-500 text-[10px]"></i> 
                    <span class="font-medium text-gray-700">(49) 3190-0603</span>
                </li>
                <li class="flex items-center gap-2">
                    <i class="fas fa-envelope text-blue-500 text-[10px]"></i> 
                    <span class="font-medium text-gray-700">imobhomesolutions@gmail.com</span>
                </li>
                <li class="flex items-start gap-2">
                    <i class="fas fa-map-marker-alt text-blue-500 text-[10px] mt-0.5"></i> 
                    <span class="font-medium text-gray-700">Av. Nereu Ramos, 247, Chapecó - SC</span>
                </li>
             </ul>
          </div>
        </div>
        
        <div class="border-t border-gray-100 pt-6 flex flex-col md:flex-row justify-between items-center gap-4">
           <div>&copy; 2026 ImobHome Tecnologia. Todos os direitos reservados.</div>
           <div class="flex items-center gap-2 text-[10px] font-medium">
              <span>Feito com <i class="fas fa-heart text-red-500 mx-0.5"></i> e Inteligência</span>
           </div>
        </div>
      </div>
    </footer>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import publicApiClient from '@/services/publicApiClient';

const router = useRouter();

// --- Estado ---
const imoveis = ref<any[]>([]);
const loading = ref(true);
const scrolled = ref(false);

const filtros = reactive({
  status: '', // Padrão: Vazio (Mostra todos)
  tipo: '',
  cidade: ''
});

// --- Scroll Navbar Effect ---
const handleScroll = () => {
  scrolled.value = window.scrollY > 20;
};

// --- Navegação ---
const scrollTo = (id: string) => {
  const element = document.getElementById(id);
  if (element) {
    const offset = 80;
    const bodyRect = document.body.getBoundingClientRect().top;
    const elementRect = element.getBoundingClientRect().top;
    const elementPosition = elementRect - bodyRect;
    const offsetPosition = elementPosition - offset;

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    });
  }
};

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

// ============================================
// REDIRECIONAMENTO PARA CADASTRO (Novo Link)
// ============================================
const goToCadastro = () => {
  router.push('/cadastro');
};

const setFiltroEBuscar = (status: string) => {
  filtros.status = status;
  scrollTo('search-box');
  buscarImoveis();
};

// ============================================
// ABRIR IMÓVEL (COM REDIRECIONAMENTO DE SUBDOMÍNIO)
// ============================================
const abrirImovel = (imovel: any) => {
  // Verifica se temos o subdomínio (vindo da atualização do serializer)
  if (!imovel.subdominio) {
    // Se não tiver subdomínio, abre internamente (fallback)
    router.push(`/imovel/${imovel.id}`);
    return;
  }

  // Verifica se estamos rodando localmente (localhost ou IP)
  const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  
  if (isLocal) {
    // Em localhost, não conseguimos abrir "subdominio.localhost" facilmente sem configurar hosts.
    // Vamos abrir uma nova aba simulando o endereço de produção para fins de teste.
    const urlProducao = `https://${imovel.subdominio}.imobhome.com.br/imovel/${imovel.id}`;
    
    // Tenta abrir a URL de produção (se o DNS existir, vai funcionar)
    window.open(urlProducao, '_blank');
    
  } else {
    // === EM PRODUÇÃO (imobhome.com.br) ===
    // Monta a URL: https://CLIENTE.imobhome.com.br/imovel/123
    const targetUrl = `https://${imovel.subdominio}.imobhome.com.br/imovel/${imovel.id}`;
    
    // Abre em nova aba para não tirar o usuário do portal principal
    window.open(targetUrl, '_blank');
  }
};

const limparFiltros = () => {
    filtros.status = '';
    filtros.tipo = '';
    filtros.cidade = '';
    buscarImoveis();
}

// --- Helpers ---
const formatCurrency = (value: number) => {
  if (!value) return 'Sob Consulta';
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
};

const formatStatus = (status: string) => {
  const map: Record<string, string> = {
    'A_VENDA': 'Venda',
    'PARA_ALUGAR': 'Aluguel',
    'VENDIDO': 'Vendido',
    'ALUGADO': 'Alugado'
  };
  return map[status] || status;
};

const getValor = (imovel: any) => {
  if (imovel.status === 'PARA_ALUGAR' || imovel.status === 'ALUGADO') {
    return imovel.valor_aluguel;
  }
  return imovel.valor_venda;
};

const getImovelImage = (imovel: any) => {
  if (imovel.imagem_principal) return imovel.imagem_principal;
  if (imovel.imagens && imovel.imagens.length > 0) return imovel.imagens[0].imagem;
  // Imagem placeholder mais elegante
  return 'https://images.unsplash.com/photo-1613490493576-7fde63acd811?q=80&w=2071&auto=format&fit=crop'; 
};

// --- API ---
const buscarImoveis = async (scroll = false) => {
  loading.value = true;
  try {
    const params: any = {};
    if (filtros.status) params.status = filtros.status;
    if (filtros.tipo) params.tipo = filtros.tipo;
    if (filtros.cidade) params.cidade = filtros.cidade;

    const response = await publicApiClient.getImoveis(params);
    imoveis.value = Array.isArray(response) ? response : (response.results || []);
    
    if (scroll) {
        setTimeout(() => scrollTo('imoveis-section'), 100);
    }

  } catch (error) {
    console.error('Erro ao buscar imóveis:', error);
  } finally {
    loading.value = false;
  }
};

// --- Lifecycle ---
onMounted(() => {
  window.addEventListener('scroll', handleScroll);
  buscarImoveis();
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
/* Animações Customizadas */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideLeft {
  from { opacity: 0; transform: translateX(-30px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes slowZoom {
  0% { transform: scale(1); }
  100% { transform: scale(1.1); }
}

.animate-slide-up-fade {
  opacity: 0;
  animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.animate-slide-left-fade {
  opacity: 0;
  animation: slideLeft 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.animate-slow-zoom {
  animation: slowZoom 25s linear infinite alternate;
}
</style>