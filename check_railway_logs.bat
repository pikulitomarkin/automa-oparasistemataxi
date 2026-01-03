@echo off
echo ====================================
echo   RAILWAY LOGS CHECKER
echo ====================================
echo.
echo Verificando se Railway CLI esta instalado...
where railway >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Railway CLI nao encontrado!
    echo.
    echo Para instalar:
    echo   npm install -g @railway/cli
    echo.
    echo Ou acesse diretamente:
    echo   https://railway.app/dashboard
    pause
    exit /b 1
)

echo Railway CLI encontrado!
echo.
echo Conectando ao projeto...
railway logs --tail 100

pause
