@echo off
chcp 65001 > nul
title Instalando Dependências do Papiro Reverso
cls
echo ====================================================================
echo   INSTALAÇÃO DE TODAS AS DEPENDÊNCIAS (PAPIRO REVERSO)
echo   Inclui: Whisper, PyTorch, FastAPI, yt-dlp, FPDF2, GenAnki, etc.
echo ====================================================================
echo.
echo [1/2] Atualizando o instalador pip...
python -m pip install --upgrade pip

echo.
echo [2/2] Baixando e instalando bibliotecas do requirements.txt...
python -m pip install -r requirements.txt

echo.
echo ====================================================================
echo   ✅ TODAS AS DEPENDÊNCIAS FORAM INSTALADAS COM SUCESSO!
echo   Para abrir o programa, dê dois cliques em:
echo   👉 Iniciar_Plataforma.bat
echo ====================================================================
echo.
pause
