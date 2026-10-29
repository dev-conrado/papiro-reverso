# 🎓 Papiro Reverso - Plataforma Completa de Estudos para Concursos

Plataforma integrada de videoaulas, simulados adaptativos, mapas mentais interativos e geração de apostilas para concursos públicos.

---

## 🌟 O que a Plataforma oferece:

1. **Player Híbrido (Online ou Uso Local)**:
   - **Online**: Assista diretamente a videoaulas e playlists do YouTube via player IFrame integrado.
   - **Opções de Download Personalizado**:
     - **Vídeo (com áudio integrado)** em 3 resoluções: **1080p (Full HD)**, **720p (HD Padrão)** e **480p (Econômico)**.
     - **Áudio MP3** em 2 tamanhos: **192 kbps (Alta Fidelidade)** e **64 kbps (Super Leve)**.
   - **Player Local Offline**: Execute arquivos de áudio/vídeo baixados diretamente pelo navegador.

2. **Barra Lateral com Progresso em Tempo Real**:
   - Lista todas as aulas da playlist com identificação do canal e duração.
   - Barrinha de progresso azul individual para cada aula com percentual e tempo assistido.
   - Botão para recolher/expandir a barra lateral para modo cinema / tela cheia.

3. **Mapa Mental Interativo & HUD Dinâmico**:
   - **3 Modos de Visualização**:
     1. **⏳ Em Tempo Real**: Os nós nascem e expandem sincronizados com a fala do professor no vídeo.
     2. **🌐 Ver Completo**: Exibe a árvore inteira renderizada para visão panorâmica do assunto.
     3. **👁️ Ocultar Mapa**: Minimiza o HUD para quem prefere foco total apenas no vídeo.
   - **Navegação com Mouse & Teclado**:
     - **Scroll do mouse**: Zoom in / Zoom out suave.
     - **Arrastar do mouse (Pan)**: Navegação livre por qualquer área do mapa.
     - **Setinhas do Teclado (← / →)** ou botões do HUD: Avanço e recuo passo a passo pelos conceitos.
     - **Nós Clicáveis**: Clique em qualquer nó para o vídeo saltar direto para o minuto exato da explicação.

4. **Motor de Questões Pop-Up (Estilo Tablet)**:
   - Pausa automática do vídeo durante a aula nos intervalos configuráveis (20s, 30s, 60s) ou ao término.
   - **Seleção de Banca**: CEBRASPE (Certo/Errado), FGV, FCC, VUNESP e Geral (Múltipla Escolha).
   - Feedback imediato (verde/vermelho) com justificativa pedagógica e **comentário alternativa por alternativa**.
   - Botão "Continuar Aula ▶" para retomar o estudo sem perder o ritmo.

5. **Importador do TEC CONCURSOS**:
   - Cole o código HTML ou importe arquivos `.html`/`.txt` do caderno de questões do TEC Concursos.
   - Gera automaticamente o PDF oficial diagramado: `Apostila_[Nome da Aula]_TEC_CONCURSO.pdf`.

6. **Apostilas Editoriais em PDF & Flashcards Anki**:
   - Geração imediata de apostilas em PDF com layout profissional, quadros "CUIDADO CONCURSEIRO" e tabelas comparativas.
   - Exportação automática de baralhos Anki (`.apkg`) para memorização por repetição espaçada.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos:
- Python 3.10 ou superior
- (Opcional) FFmpeg instalado no PATH do Windows para mesclagem de vídeo/áudio

### Instalação das dependências:
```bash
pip install -r requirements.txt
```

### Iniciar a Plataforma:
- **No Windows**: Duplo clique em `Iniciar_Plataforma.bat`
- **Ou pelo terminal**:
```bash
python iniciar_plataforma.py
```
A plataforma abrirá automaticamente no seu navegador padrão em: `http://localhost:8000`.
