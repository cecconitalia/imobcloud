<template>
  <div class="public-layout">
    <header class="main-header">
      <div class="container">
        <h1 class="logo">Imobiliária</h1>
        <nav class="main-nav">
          <router-link to="/site">Início</router-link>
          </nav>
      </div>
    </header>

    <main class="main-content">
      <router-view />
    </main>

    <footer class="main-footer">
      <div class="container">
        <p>&copy; 2025 ImobCloud. Todos os direitos reservados.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.public-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  font-family: sans-serif;
}
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}
.main-header {
  background-color: #fff;
  border-bottom: 1px solid #e0e0e0;
  padding: 1rem 0;
}
.main-header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.logo {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
}
.main-nav a {
  margin-left: 1.5rem;
  text-decoration: none;
  color: #333;
  font-weight: 500;
}
.main-nav a.router-link-exact-active {
  color: #007bff;
}
.main-content {
  flex-grow: 1;
  padding: 2rem 0;
  background-color: #f8f9fa;
}
.main-footer {
  background-color: #343a40;
  color: white;
  padding: 1.5rem 0;
  text-align: center;
  margin-top: auto;
}
</style>