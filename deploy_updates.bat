@echo off
echo ========================================
echo  DEPLOY - Painel Admin com Reprocessamento
echo ========================================
echo.

echo [1/4] Adicionando arquivos ao Git...
git add app_liquid.py reprocess_failed_orders.py REPROCESS_RAILWAY_CLI.md
if %errorlevel% neq 0 goto :error

echo [2/4] Fazendo commit...
git commit -m "feat: Adiciona painel Admin com reprocessamento de pedidos falhados no dashboard"
if %errorlevel% neq 0 goto :error

echo [3/4] Enviando para GitHub...
git push origin master
if %errorlevel% neq 0 goto :error

echo [4/4] Deploy concluido!
echo.
echo ========================================
echo  SUCESSO! Railway vai fazer deploy automatico
echo ========================================
echo.
echo Acesse: https://railway.app/project/respectful-reverence
echo.
pause
goto :end

:error
echo.
echo ========================================
echo  ERRO no deploy!
echo ========================================
pause

:end
