// Em um componente Vue (ex: DetalhesImovel.vue)
import axios from 'axios';

export default {
  // ...
  methods: {
    async gerarTextoParaRedeSocial() {
      try {
        const response = await axios.post('/api/publicacoes/gerar-texto/', {
          imovel_id: this.imovel.id
        });
        this.texto_sugerido = response.data.texto_sugerido;
        // Agora, exiba 'this.texto_sugerido' em um modal ou textarea
      } catch (error) {
        console.error("Erro ao gerar texto:", error);
        // Exiba uma mensagem de erro para o usuário
      }
    },
    async publicarPost() {
      // Lógica para enviar o texto final e as plataformas para o backend
    }
  }
}