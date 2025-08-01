# Use uma imagem base Python oficial (Debian slim - Python 3.8)
FROM python:3.8-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instale dependências do sistema necessárias para o PostgreSQL client (usando apt-get para Debian)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copie o arquivo de requisitos para o diretório de trabalho
COPY requirements.txt .

# Limpa o cache do pip e depois o atualiza
RUN pip cache purge \
    && pip install --no-cache-dir --upgrade pip

# Instale as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código da aplicação para o contêiner
COPY . .

# Expõe a porta 8000 para o servidor Django
EXPOSE 8000

# Comando padrão para iniciar o servidor Django (pode ser sobrescrito pelo docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]