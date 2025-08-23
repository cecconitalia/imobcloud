<template>
  <div class="public-layout">
    <header class="public-header">
      <div class="container header-container">
        <div class="brand-social">
          <router-link to="/site" class="header-link">
            <h1>{{ imobiliariaNome || 'Portal Imobiliário' }}</h1>
          </router-link>
          <div class="social-icons">
            <a href="#" class="social-icon"><i class="fab fa-facebook-f"></i></a>
            <a href="#" class="social-icon"><i class="fab fa-instagram"></i></a>
          </div>
        </div>
        <nav class="public-nav">
          <router-link to="/site" class="nav-link">Início</router-link>
          <a href="#" class="nav-link">Sobre Nós</a>
          <a href="#" class="nav-link">Contato</a>
        </nav>
      </div>
    </header>
    <main class="main-content">
      <router-view />
    </main>
    <footer class="public-footer">
      <div class="container footer-container">
        <p>&copy; {{ new Date().getFullYear() }} {{ imobiliariaNome }}. Todos os direitos reservados.</p>
        <p>Telefone: (xx) xxxx-xxxx | Email: contato@{{ imobiliariaNome }}.com</p>
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
    imobiliariaNome.value = parts[0].charAt(0).toUpperCase() + parts[0].slice(1);
  }
});
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

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
.brand-social {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}
.header-link {
    text-decoration: none;
    color: inherit;
}
h1 {
    font-size: 1.8rem;
    margin: 0;
}
.social-icons {
    display: flex;
    gap: 1rem;
}
.social-icon {
    color: white;
    font-size: 1.2rem;
    transition: color 0.2s;
}
.social-icon:hover {
    color: #3498db;
}
.public-nav {
    display: flex;
    gap: 1.5rem;
}
.nav-link {
    color: white;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s;
}
.nav-link:hover {
    color: #3498db;
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
.footer-container p {
    margin: 0.25rem 0;
    font-size: 0.9rem;
}
</style>