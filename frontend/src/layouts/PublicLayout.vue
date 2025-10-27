<template>
  <div class="public-layout">
    <header :class="['public-header', { 'scrolled': isScrolled }]">
      <div class="container header-container">
        <a href="/site" class="header-brand">
          <h1>{{ imobiliariaNome || 'Portal Imobiliário' }}</h1>
        </a>
        <div class="right-section">
          <nav class="public-nav">
            <a href="http://localhost:5173/login" class="nav-link">Login</a>
          </nav>
          <div class="social-links">
          </div>
        </div>
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
import publicApiClient from '@/services/publicApiClient';

const imobiliariaNome = ref('');
const isScrolled = ref(false);

function handleScroll() {
  isScrolled.value = window.scrollY > 0;
}

// Funções para manipular a cor (mantidas)
function hexToRgb(hex: string) {
  const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
  hex = hex.replace(shorthandRegex, function(m, r, g, b) {
    return r + r + g + g + b + b;
  });
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
}

function lightenColor(hex: string, percent: number) {
  let rgb = hexToRgb(hex);
  if (!rgb) return hex;
  
  let r = rgb.r + percent;
  let g = rgb.g + percent;
  let b = rgb.b + percent;
  
  r = Math.min(255, Math.max(0, r));
  g = Math.min(255, Math.max(0, g));
  b = Math.min(255, Math.max(0, b));
  
  return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
}

function darkenColor(hex: string, amount: number) {
  let usePound = false;
  if (hex[0] === "#") {
    hex = hex.slice(1);
    usePound = true;
  }
  let num = parseInt(hex, 16);
  let r = (num >> 16) + amount;
  if (r > 255) r = 255;
  else if (r < 0) r = 0;
  let b = ((num >> 8) & 0x00FF) + amount;
  if (b > 255) b = 255;
  else if (b < 0) b = 0;
  let g = (num & 0x0000FF) + amount;
  if (g > 255) g = 255;
  else if (g < 0) g = 0;
  return (usePound ? "#" : "") + (g | (b << 8) | (r << 16)).toString(16).padStart(6, '0');
}

// FUNÇÃO PARA BUSCAR O NOME E A COR DA IMOBILIÁRIA VIA API
async function fetchImobiliariaData(subdomain: string) {
  try {
    // CORREÇÃO: A chamada usa o caminho que está mapeado na raiz do Django (sem prefixo /api/v1/)
    const response = await publicApiClient.get(`/public/imobiliaria/${subdomain}/`);
    imobiliariaNome.value = response.data.nome;
    const primaryColor = response.data.cor_primaria || '#007bff';
    const footerColor = darkenColor(primaryColor, -20);
    const bodyBgColor = lightenColor(primaryColor, 230);
    document.documentElement.style.setProperty('--primary-color', primaryColor);
    document.documentElement.style.setProperty('--footer-color', footerColor);
    document.documentElement.style.setProperty('--body-bg-color', bodyBgColor);
  } catch (err) {
    console.error("Erro ao buscar dados da imobiliária:", err);
    imobiliariaNome.value = subdomain.charAt(0).toUpperCase() + subdomain.slice(1);
    document.documentElement.style.setProperty('--primary-color', '#007bff');
    document.documentElement.style.setProperty('--footer-color', '#34495e');
    document.documentElement.style.setProperty('--body-bg-color', '#f4f7f6');
  }
}

onMounted(() => {
  const hostname = window.location.hostname;
  const parts = hostname.split('.');
  
  if (parts.length > 1 && parts[0] !== 'www' && parts[0] !== 'localhost') {
    const subdomain = parts[0];
    fetchImobiliariaData(subdomain);
  } else {
    document.documentElement.style.setProperty('--primary-color', '#007bff');
    document.documentElement.style.setProperty('--footer-color', '#34495e');
    document.documentElement.style.setProperty('--body-bg-color', '#f4f7f6');
  }

  window.addEventListener('scroll', handleScroll);
});
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

.public-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--body-bg-color);
}

/* HEADER */
.public-header {
  background-color: var(--primary-color);
  backdrop-filter: blur(10px);
  color: #fff;
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
  transition: all 0.3s ease;
}

.public-header.scrolled {
  background-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.header-brand {
  text-decoration: none;
  color: #fff;
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  transition: all 0.2s ease-in-out;
}

.header-brand h1 {
  margin: 0;
  font-size: 1.3em;
}

.right-section {
    display: flex;
    align-items: center;
    gap: 2rem;
}

.public-nav {
  display: flex;
  gap: 1.5rem;
}

.social-links {
  display: flex;
  gap: 1rem;
}

.nav-link {
  color: #fff;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease, transform 0.2s ease;
  position: relative;
}

.nav-link::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -5px;
  width: 0;
  height: 2px;
  background-color: #fff;
  transition: width 0.3s ease;
}

.nav-link:hover::after {
  width: 100%;
}

.social-icon {
  color: #fff;
  font-size: 1.2rem;
  transition: color 0.2s ease, transform 0.2s ease;
}

.social-icon:hover {
  color: #f0f0f0;
  transform: scale(1.1);
}

/* MAIN CONTENT */
.main-content {
  flex-grow: 1;
}

/* FOOTER */
.public-footer {
  background-color: var(--footer-color);
  color: #ecf0f1;
  text-align: center;
  padding: 1.5rem 0;
  margin-top: 2rem;
}

.footer-container p {
  margin: 0.25rem 0;
  font-size: 0.9rem;
}

/* MEDIA QUERIES */
@media (max-width: 768px) {
  .header-container {
    flex-wrap: nowrap;
    justify-content: space-between;
    gap: 1rem;
  }
  .public-nav, .social-links, .header-brand {
    width: auto;
    text-align: left;
  }
  .right-section {
    flex-direction: row;
    gap: 1rem;
    width: auto;
  }
}
</style>