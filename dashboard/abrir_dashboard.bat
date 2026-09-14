@echo off
title Jogo do Bicho 2024 - Dashboard
cd /d "D:\Jogo do bicho"
call .venv\Scripts\activate.bat

echo.
echo ============================================================
echo   INICIANDO DASHBOARD JOGO DO BICHO 2024
echo ============================================================
echo.
echo O navegador vai abrir automaticamente em 5 segundos...
echo Para FECHAR o dashboard, feche esta janela preta.
echo.

start "" http://localhost:8501

streamlit run dashboard_streamlit.py

pause