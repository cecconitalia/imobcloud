<template>
  <router-view />
</template>

<script setup lang="ts">
// Nenhum script adicional é necessário aqui.
</script>

<style>
/* --- ESTILOS GLOBAIS (RESET & TEMA) --- */

/* 1. A REGRA DE OURO: Forçar o motor do navegador para o Modo Claro */
:root {
  color-scheme: light; /* Isso corrige checkboxes pretos, datepickers e selects nativos */
}

/* 2. Garantia de Fundo e Texto */
body, html, #app {
  background-color: #f8fafc !important; /* Fundo Cinza Claro Profissional */
  color: #1e293b !important; /* Texto Cinza Escuro (quase preto) */
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  font-family: 'Inter', sans-serif; /* Garante a fonte padrão */
}

/* 3. PADRONIZAÇÃO DE FORMULÁRIOS (Inputs, Selects, Checkboxes) */

/* Inputs de Texto e Selects */
input:not([type="checkbox"]):not([type="radio"]), 
select, 
textarea, 
.form-control {
  background-color: #ffffff !important;
  color: #1e293b !important;
  border-color: #cbd5e1;
}

/* Checkboxes e Radio Buttons (Correção Específica) */
input[type="checkbox"], 
input[type="radio"] {
  accent-color: #2563eb; /* Cor Azul do Sistema quando marcado */
  cursor: pointer;
}

/* Correção para as OPÇÕES do Select (Dropdown) */
select option {
  background-color: #ffffff !important;
  color: #1e293b !important;
}

/* Remove o fundo azul/amarelo do autocomplete do Chrome */
input:-webkit-autofill,
input:-webkit-autofill:hover, 
input:-webkit-autofill:focus, 
input:-webkit-autofill:active {
  -webkit-box-shadow: 0 0 0 30px white inset !important;
  -webkit-text-fill-color: #1e293b !important;
}

/* 4. SCROLLBAR (Barra de Rolagem) ELEGANTE */

/* Chrome, Edge, Safari */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 4px;
  border: 2px solid transparent;
  background-clip: content-box;
}

::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}

/* Firefox */
* {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}
</style>