# --- CONFIGURACOES ---
$ServerIp = "155.138.233.124"
$ServerUser = "root"
$RemotePath = "/var/www/imobhome"
$LocalPath = "C:\wamp64\www\ImobHome"
$SshKey = "C:\Users\Cristiano Ceccon\.ssh\id_rsa"
$TempFile = "deploy_package.tar.gz"

# 1. Validacao do Diretorio Local
if (!(Test-Path $LocalPath)) {
    Write-Error "ERRO: Diretorio do projeto nao encontrado: $LocalPath"
    exit
}
Set-Location $LocalPath

Write-Host "--- INICIANDO DEPLOY COMPLETO (ImobHome + Digital) ---" -ForegroundColor Cyan

# 2. Compilar Frontend (ImobHome)
Write-Host "[1/6] Compilando Frontend ImobHome..." -ForegroundColor Yellow
if (Test-Path "$LocalPath\frontend") {
    Push-Location "$LocalPath\frontend"
    if (Get-Command "npm" -ErrorAction SilentlyContinue) {
        npm run build
    } else {
        Write-Warning "AVISO: NPM nao encontrado. Pulando build."
    }
    Pop-Location
}

# 3. Compactar Backend
Write-Host "[2/6] Compactando arquivos..." -ForegroundColor Yellow

if (Test-Path $TempFile) { Remove-Item $TempFile }

if (!(Get-Command "tar" -ErrorAction SilentlyContinue)) {
    Write-Error "ERRO: Comando 'tar' nao encontrado no Windows."
    exit
}

# Cria o arquivo tar.gz
tar -czf $TempFile `
    --exclude="venv" `
    --exclude="node_modules" `
    --exclude=".git" `
    --exclude=".idea" `
    --exclude=".vscode" `
    --exclude=".env" `
    --exclude="db.sqlite3" `
    --exclude="media" `
    --exclude="staticfiles" `
    --exclude="__pycache__" `
    --exclude="*.pyc" `
    --exclude="deploy.sh" `
    --exclude="deploy.ps1" `
    .

if (!(Test-Path $TempFile)) {
    Write-Error "ERRO: Falha ao criar o arquivo compactado."
    exit
}

# 4. Enviar Pacotes via SCP
Write-Host "[3/6] Enviando arquivos para o servidor..." -ForegroundColor Yellow
# Envia o Backend
scp -i $SshKey $TempFile "$($ServerUser)@$($ServerIp):/tmp/$TempFile"

# Envia o Frontend
if (Test-Path "$LocalPath\frontend\dist") {
    scp -i $SshKey -r "$LocalPath\frontend\dist" "$($ServerUser)@$($ServerIp):$RemotePath/frontend/"
}

# 5. Executar Comandos Remotos
Write-Host "[4/6] Executando manutencao no servidor..." -ForegroundColor Cyan

# ATENCAO: O "@" de fechamento deve estar na extrema esquerda
$RemoteScript = @"
    cd $RemotePath
    
    echo '--- [ImobHome] Extraindo arquivos ---'
    tar -xzf /tmp/$TempFile -C $RemotePath
    rm /tmp/$TempFile

    echo '--- [ImobHome] Reiniciando Containers ---'
    docker compose restart web celery celery-beat

    echo '--- [ImobHome] Aguardando inicializacao ---'
    sleep 5

    echo '--- [ImobHome] Rodando Migracoes ---'
    docker exec imobhome-web-1 python manage.py migrate

    echo '--- [ImobHome] Coletando Arquivos Estaticos ---'
    docker exec imobhome-web-1 python manage.py collectstatic --noinput

    echo '--- [Digital] Reiniciando servico Digital ---'
    systemctl restart digital
    
    echo '--- [Geral] Reiniciando Nginx ---'
    systemctl restart nginx

    echo ''
    echo '=== STATUS FINAL ==='
    echo 'IMOBHOME (Docker):'
    # Aspas simples aqui resolvem o erro visual
    docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep imobhome-web
    
    echo ''
    echo 'DIGITAL (Systemd):'
    systemctl status digital --no-pager | grep "Active:"
    echo ''
    echo '=== CONCLUIDO ==='
"@

# Remove caracteres de quebra de linha do Windows
$RemoteScript = $RemoteScript -replace "`r", ""

# Executa via SSH
ssh -i $SshKey "$($ServerUser)@$($ServerIp)" $RemoteScript

# 6. Limpeza Local
if (Test-Path $TempFile) { Remove-Item $TempFile }
Write-Host "--- SUCESSO! DEPLOY FINALIZADO ---" -ForegroundColor Green