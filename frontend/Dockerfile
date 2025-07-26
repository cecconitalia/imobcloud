# Caminho: imobcloud/frontend/Dockerfile

FROM node:20

# Define diretório de trabalho
WORKDIR /app

# Copia apenas os arquivos de dependência primeiro
COPY package*.json ./

# Instala dependências
RUN npm install

# Copia todo o restante do projeto
COPY . .

# Expondo a porta padrão do Next.js
EXPOSE 3000

# Comando para rodar em modo desenvolvimento
CMD ["npm", "run", "dev"]
