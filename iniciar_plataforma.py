import os
import sys
import time
import webbrowser
import uvicorn
from pathlib import Path

def main():
    print("=" * 65)
    print("INICIANDO PAPIRO REVERSO - PLATAFORMA DE ESTUDOS")
    print("Player YouTube + Progresso de Aulas + Mapa Mental + Questoes")
    print("=" * 65)
    
    url_local = "http://localhost:8000"
    print(f"\n[Servidor] Ativo em: {url_local}")
    print("[Navegador] Abrindo plataforma automaticamente...")
    
    # Abre o navegador automaticamente em 1.5s
    def abrir_navegador():
        time.sleep(1.5)
        webbrowser.open(url_local)

    import threading
    threading.Thread(target=abrir_navegador, daemon=True).start()

    # Executa o servidor FastAPI com uvicorn
    import server
    uvicorn.run(server.app, host="127.0.0.1", port=8000, reload=False, log_level="info")

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    main()
