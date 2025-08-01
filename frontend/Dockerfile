# Use a imagem oficial do Node.js 18 como base
FROM node:18-alpine

# Define o diretório de trabalho no contêiner
WORKDIR /app

# Copia os arquivos de configuração do frontend para o contêiner
COPY package.json .
COPY yarn.lock .

# Instala todas as dependências do package.json
# Isso garante que bibliotecas como 'lucide-react' e 'axios' sejam instaladas
RUN yarn install --frozen-lockfile --network-timeout 100000

# Copia o restante do código da aplicação
COPY . .

# Expõe a porta 5173, onde o servidor de desenvolvimento do Vite será executado
EXPOSE 5173

# Comando para iniciar o servidor de desenvolvimento do Vite
CMD ["yarn", "dev", "--host", "0.0.0.0"]
