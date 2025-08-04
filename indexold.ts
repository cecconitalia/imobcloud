router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('authToken');
  const requiresAuth = to.meta.requiresAuth; // Você vai adicionar meta: { requiresAuth: true } nas suas rotas

  if (requiresAuth && !isAuthenticated) {
    next('/login'); // Redireciona para o login se a rota exige auth e o user não está logado
  } else {
    next(); // Permite o acesso
  }
});