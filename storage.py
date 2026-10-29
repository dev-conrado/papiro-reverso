import json
import os
from pathlib import Path
from config import BASE_DIR

ARQUIVO_BANCO = BASE_DIR / "dados_plataforma.json"

def carregar_dados():
    if not ARQUIVO_BANCO.exists():
        dados_iniciais = {
            "playlists": {},
            "configuracoes": {
                "tema": "dark",
                "intervalo_questoes": 30, # segundos
                "questoes_durante_aula": True,
                "questoes_final_aula": True,
                "tamanho_mapa_mental": "quarto", # "quarto", "livre"
                "banca_preferida": "CEBRASPE (Certo/Errado)"
            },
            "progresso_aulas": {} # id_video: { "segundos_assistidos": 0, "duracao": 0, "concluido": False }
        }
        salvar_dados(dados_iniciais)
        return dados_iniciais

    try:
        with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"playlists": {}, "configuracoes": {}, "progresso_aulas": {}}

def salvar_dados(dados):
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def atualizar_progresso(video_id: str, segundos: float, duracao: float):
    dados = carregar_dados()
    progresso = dados.setdefault("progresso_aulas", {})
    
    porcentagem = (segundos / duracao * 100) if duracao > 0 else 0
    concluido = porcentagem >= 90 # Considera concluído a partir de 90%
    
    progresso[video_id] = {
        "segundos_assistidos": round(segundos, 1),
        "duracao": round(duracao, 1),
        "porcentagem": round(porcentagem, 1),
        "concluido": concluido
    }
    salvar_dados(dados)
    return progresso[video_id]

def salvar_playlist(playlist_id: str, titulo: str, aulas: list):
    dados = carregar_dados()
    dados.setdefault("playlists", {})[playlist_id] = {
        "titulo": titulo,
        "aulas": aulas
    }
    salvar_dados(dados)
