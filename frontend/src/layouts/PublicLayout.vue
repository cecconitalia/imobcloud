<template>
  <div class="public-layout">
    <header class="public-header">
      <div class="container header-container">
        <h1>{{ imobiliariaNome || 'Portal Imobiliário' }}</h1>
        <nav>
          </nav>
      </div>
    </header>
    <main class="main-content">
      <router-view />
    </main>
    <footer class="public-footer">
      <div class="container">
        <p>&copy; {{ new Date().getFullYear() }} {{ imobiliariaNome }}. Todos os direitos reservados.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

const imobiliariaNome = ref('');

onMounted(() => {
  const hostname = window.location.hostname;
  const parts = hostname.split('.');
  if (parts.length > 1 && parts[0] !== 'www' && parts[0] !== 'localhost') {
    // Transforma o subdomínio em nome com a primeira letra maiúscula
    imobiliariaNome.value = parts[0].charAt(0).toUpperCase() + parts[0].slice(1);
  }
});
</script>

<style scoped>
.public-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f4f7f6;
}
.public-header {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
/* ATUALIZADO: Usando uma classe container para o alinhamento */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}
.header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.main-content {
  flex-grow: 1;
}
.public-footer {
  background-color: #34495e;
  color: #ecf0f1;
  text-align: center;
  padding: 1.5rem 0;
  margin-top: 2rem;
}
</style>