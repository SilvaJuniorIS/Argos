@echo off
setlocal EnableExtensions
chcp 65001 >nul 2>&1
cd /d "%~dp0"

title ARGOS - Iniciando

echo.
echo  ========================================
echo   ARGOS - Inicializacao automatica
echo  ========================================
echo.

where docker >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Docker nao encontrado. Instale o Docker Desktop e tente novamente.
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Docker Desktop nao esta em execucao. Abra o Docker Desktop e tente novamente.
    pause
    exit /b 1
)

if not exist ".env" (
    if exist ".env.example" (
        copy /Y ".env.example" ".env" >nul
        echo [OK] Arquivo .env criado a partir de .env.example
    ) else (
        echo [AVISO] .env.example nao encontrado; usando padroes do Docker Compose.
    )
)

if not exist "frontend\argos-web\.env" (
    if exist "frontend\argos-web\.env.example" (
        copy /Y "frontend\argos-web\.env.example" "frontend\argos-web\.env" >nul
        echo [OK] frontend\argos-web\.env criado
    )
)

echo.
echo [1/5] Subindo containers (Postgres, Redis, API, Worker, Beat)...
docker compose up --build -d
if errorlevel 1 (
    echo [ERRO] Falha ao iniciar containers.
    pause
    exit /b 1
)

echo.
echo [2/5] Aguardando API ficar pronta...
set /a TENTATIVAS=0
:aguardar_api
set /a TENTATIVAS+=1
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://localhost:8002/health' -UseBasicParsing -TimeoutSec 3).StatusCode | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel%==0 goto api_pronta
if %TENTATIVAS% GEQ 45 (
    echo [ERRO] API nao respondeu em tempo habil. Execute: docker compose logs api
    pause
    exit /b 1
)
timeout /t 2 /nobreak >nul
goto aguardar_api
:api_pronta
echo [OK] API respondendo em http://localhost:8002

echo.
echo [3/5] Aplicando migracoes do banco...
docker compose exec -T api alembic upgrade head
if errorlevel 1 (
    echo [AVISO] Migracao falhou; verifique os logs da API.
)

echo.
echo [4/5] Criando somente usuario admin, sem dados de demonstracao...
docker compose exec -T api python scripts/create_admin.py
if errorlevel 1 (
    echo [AVISO] Criacao do admin falhou; verifique os logs da API.
)

echo.
echo [5/5] Iniciando frontend React...
if not exist "frontend\argos-web\node_modules" (
    echo       Instalando dependencias npm (primeira vez)...
    pushd frontend\argos-web
    call npm install
    if errorlevel 1 (
        popd
        echo [ERRO] npm install falhou no frontend.
        pause
        exit /b 1
    )
    popd
)

start "ARGOS - Frontend" cmd /k "cd /d "%~dp0frontend\argos-web" && title ARGOS Frontend && npm run dev"

echo       Aguardando frontend...
timeout /t 6 /nobreak >nul

start "" "http://localhost:5175"
start "" "http://localhost:8002/docs"

echo.
echo  ========================================
echo   ARGOS em execucao!
echo  ========================================
echo.
echo   Frontend:  http://localhost:5175
echo   API Docs:  http://localhost:8002/docs
echo   Health:    http://localhost:8002/health
echo.
echo   Login admin:
echo     E-mail: admin@argos.gov.br
echo     Senha:  argos123
echo.
echo   Para encerrar tudo, execute: parar-argos.bat
echo.
pause
endlocal
