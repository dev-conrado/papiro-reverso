@echo off
title Papiro Reverso - Plataforma de Estudos para Concursos
chcp 65001 > nul
cls
echo ====================================================================
echo   INICIANDO PAPIRO REVERSO - PLATAFORMA DE ESTUDOS PARA CONCURSOS
echo ====================================================================
echo.
echo [1/2] Iniciando Servidor Local em http://localhost:8000 ...
echo [2/2] Abrindo seu navegador automaticamente...
echo.
python iniciar_plataforma.py
pause
