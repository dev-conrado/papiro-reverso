import os
import json
import re
from pathlib import Path
from config import DIR_MAPAS

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa Mental Interativo - {TITULO_AULA}</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            user-select: none;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%);
            color: #f8fafc;
            overflow: hidden;
            height: 100vh;
            width: 100vw;
        }

        /* Top Bar */
        #topbar {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 55px;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(8px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            z-index: 50;
        }
        .header-title {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .badge-materia {
            background: #3b82f6;
            color: #ffffff;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 4px;
            text-transform: uppercase;
        }
        .aula-nome {
            font-size: 15px;
            font-weight: 600;
            color: #f1f5f9;
        }

        /* Controls Floating Panel */
        #controls {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(30, 41, 59, 0.9);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 8px 16px;
            border-radius: 40px;
            display: flex;
            align-items: center;
            gap: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.4);
            z-index: 50;
        }
        .btn-ctrl {
            background: #334155;
            color: #f8fafc;
            border: none;
            padding: 8px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .btn-ctrl:hover {
            background: #2563eb;
            transform: translateY(-1px);
        }
        .btn-ctrl:active {
            transform: translateY(0);
        }
        .step-counter {
            font-size: 13px;
            font-weight: 600;
            color: #94a3b8;
            min-width: 130px;
            text-align: center;
        }

        /* SVG Canvas */
        #viewport {
            width: 100vw;
            height: 100vh;
            cursor: grab;
        }
        #viewport:active {
            cursor: grabbing;
        }

        /* Mind Map Elements */
        .link {
            fill: none;
            stroke-width: 2.2px;
            transition: stroke-dashoffset 0.5s ease, opacity 0.4s ease;
        }
        .node-group {
            cursor: pointer;
            transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.4s ease;
        }
        .node-group:hover rect {
            filter: drop-shadow(0 0 10px rgba(59, 130, 246, 0.6));
        }
        .node-rect {
            rx: 8px;
            ry: 8px;
            stroke-width: 1.5px;
            transition: all 0.3s;
        }
        .node-text {
            font-size: 13px;
            font-weight: 600;
            fill: #ffffff;
            dominant-baseline: central;
            text-anchor: middle;
            pointer-events: none;
        }
        .badge-count {
            fill: #94a3b8;
            font-size: 10px;
            font-weight: bold;
        }

        /* Detail Sidebar Card */
        #detail-card {
            position: absolute;
            top: 75px;
            right: 20px;
            width: 320px;
            background: rgba(30, 41, 59, 0.95);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 15px 30px rgba(0,0,0,0.5);
            z-index: 45;
            transition: all 0.3s;
            display: none;
        }
        #detail-card h3 {
            font-size: 15px;
            color: #60a5fa;
            margin-bottom: 8px;
        }
        #detail-card p {
            font-size: 13px;
            color: #cbd5e1;
            line-height: 1.5;
            margin-bottom: 12px;
        }
        .pegadinha-box {
            background: rgba(217, 131, 36, 0.15);
            border-left: 3px solid #f59e0b;
            padding: 8px 10px;
            border-radius: 4px;
            font-size: 12px;
            color: #fbbf24;
        }
        .pegadinha-box strong {
            display: block;
            margin-bottom: 3px;
            color: #fef3c7;
        }

        /* Keyboard Hints */
        .keyboard-hint {
            position: absolute;
            bottom: 22px;
            right: 20px;
            font-size: 11px;
            color: #64748b;
            background: rgba(15, 23, 42, 0.6);
            padding: 6px 12px;
            border-radius: 6px;
            border: 1px solid rgba(255,255,255,0.05);
            pointer-events: none;
        }
        .kbd {
            background: #334155;
            color: #e2e8f0;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: monospace;
            font-size: 10px;
        }
    </style>
</head>
<body>

    <div id="topbar">
        <div class="header-title">
            <span class="badge-materia">{MATERIA}</span>
            <span class="aula-nome">{TITULO_AULA}</span>
        </div>
        <div>
            <button class="btn-ctrl" onclick="resetView()">🎯 Centralizar</button>
        </div>
    </div>

    <!-- Canvas SVG Interativo -->
    <svg id="viewport">
        <g id="scene"></g>
    </svg>

    <!-- Painel de Controles e Animação Passo a Passo -->
    <div id="controls">
        <button class="btn-ctrl" onclick="passoAnterior()" title="Seta Esquerda [←]">◀ Voltar</button>
        <span class="step-counter" id="lbl-passo">Passo 1 / 1</span>
        <button class="btn-ctrl" onclick="proximoPasso()" title="Seta Direita [→]">Avançar ▶</button>
        <button class="btn-ctrl" onclick="expandirTudo()" style="margin-left: 6px;">🌐 Expandir Tudo</button>
    </div>

    <!-- Card de Detalhes do Conteúdo -->
    <div id="detail-card">
        <h3 id="card-titulo">Título</h3>
        <p id="card-desc">Descrição do conceito...</p>
        <div class="pegadinha-box" id="card-pegadinha" style="display:none;">
            <strong>⚠️ Atenção Concurseiro:</strong>
            <span id="card-pegadinha-txt"></span>
        </div>
    </div>

    <div class="keyboard-hint">
        Use as setas <span class="kbd">←</span> <span class="kbd">→</span> para animar o mapa passo a passo | <span class="kbd">Scroll</span> zoom | Arraste para navegar
    </div>

    <script>
        const DADOS_ARVORE = {DADOS_JSON};

        // Paleta de cores vibrantes para os ramos principais
        const CORES_RAMOS = [
            "#3b82f6", "#10b981", "#8b5cf6", "#f59e0b", 
            "#ec4899", "#06b6d4", "#f97316", "#14b8a6"
        ];

        let ordemAnimacao = [];
        let passoAtual = 0;
        let scale = 1;
        let panX = 150;
        let panY = window.innerHeight / 2;
        let isDragging = false;
        let startX, startY;

        const scene = document.getElementById("scene");
        const viewport = document.getElementById("viewport");
        const lblPasso = document.getElementById("lbl-passo");

        // Transforma a árvore hierárquica calculando posições (Layout em Árvore Radial/Horizontal)
        function indexarNos(no, nivel = 0, cor = "#3b82f6", parent = null) {
            no.nivel = nivel;
            no.parent = parent;
            no.cor = nivel === 0 ? "#2563eb" : (nivel === 1 ? cor : (parent ? parent.cor : cor));
            no.visivel = false;
            ordemAnimacao.push(no);

            if (no.filhos && no.filhos.length > 0) {
                no.filhos.forEach((filho, idx) => {
                    const corFilho = nivel === 0 ? CORES_RAMOS[idx % CORES_RAMOS.length] : no.cor;
                    indexarNos(filho, nivel + 1, corFilho, no);
                });
            }
        }

        // Layout de posições X, Y
        let curY = 0;
        function calcularPosicoes(no) {
            const ESPACAMENTO_X = 260;
            const ESPACAMENTO_Y = 65;

            if (!no.filhos || no.filhos.length === 0) {
                no.x = no.nivel * ESPACAMENTO_X;
                no.y = curY;
                curY += ESPACAMENTO_Y;
            } else {
                no.filhos.forEach(calcularPosicoes);
                no.x = no.nivel * ESPACAMENTO_X;
                const primeiroY = no.filhos[0].y;
                const ultimoY = no.filhos[no.filhos.length - 1].y;
                no.y = (primeiroY + ultimoY) / 2;
            }
        }

        indexarNos(DADOS_ARVORE);
        curY = 0;
        calcularPosicoes(DADOS_ARVORE);

        // Renderiza elementos SVG
        function renderizarMapa() {
            scene.innerHTML = "";

            // 1. Desenhar Links
            ordemAnimacao.forEach(no => {
                if (no.parent) {
                    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
                    path.setAttribute("id", "link-" + no.id);
                    path.setAttribute("class", "link");
                    path.setAttribute("stroke", no.cor);
                    path.setAttribute("opacity", no.visivel ? "0.6" : "0");

                    // Curva de Bézier suave
                    const startX = no.parent.x + 90;
                    const startY = no.parent.y;
                    const endX = no.x - 90;
                    const endY = no.y;
                    const cX1 = startX + (endX - startX) / 2;
                    const cX2 = startX + (endX - startX) / 2;
                    path.setAttribute("d", `M ${startX} ${startY} C ${cX1} ${startY}, ${cX2} ${endY}, ${endX} ${endY}`);

                    scene.appendChild(path);
                }
            });

            // 2. Desenhar Nós
            ordemAnimacao.forEach(no => {
                const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
                g.setAttribute("id", "node-" + no.id);
                g.setAttribute("class", "node-group");
                g.setAttribute("transform", `translate(${no.x}, ${no.y})`);
                g.setAttribute("opacity", no.visivel ? "1" : "0");
                g.setAttribute("style", no.visivel ? "pointer-events: all;" : "pointer-events: none;");

                const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                const largura = Math.max(160, (no.titulo.length * 8.5) + 30);
                rect.setAttribute("class", "node-rect");
                rect.setAttribute("x", -largura / 2);
                rect.setAttribute("y", -20);
                rect.setAttribute("width", largura);
                rect.setAttribute("height", 40);
                rect.setAttribute("fill", no.nivel === 0 ? "#1d4ed8" : "#1e293b");
                rect.setAttribute("stroke", no.cor);
                rect.setAttribute("stroke-width", no.nivel === 0 ? "2.5" : "1.8");

                const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
                text.setAttribute("class", "node-text");
                text.textContent = no.titulo;

                g.appendChild(rect);
                g.appendChild(text);

                // Interatividade com Mouse: Clique e Hover
                g.onclick = (e) => {
                    e.stopPropagation();
                    mostrarDetalhes(no);
                    toggleNo(no);
                };

                g.onmouseenter = () => mostrarDetalhes(no);

                scene.appendChild(g);
            });

            atualizarTransform();
        }

        function atualizarTransform() {
            scene.setAttribute("transform", `translate(${panX}, ${panY}) scale(${scale})`);
        }

        function mostrarDetalhes(no) {
            const card = document.getElementById("detail-card");
            document.getElementById("card-titulo").textContent = no.titulo;
            document.getElementById("card-desc").textContent = no.descricao || "Conceito estrutural da aula.";
            
            const boxPeg = document.getElementById("card-pegadinha");
            if (no.pegadinha) {
                boxPeg.style.display = "block";
                document.getElementById("card-pegadinha-txt").textContent = no.pegadinha;
            } else {
                boxPeg.style.display = "none";
            }
            card.style.display = "block";
        }

        // Animação Passo a Passo (Setinhas do Teclado)
        function proximoPasso() {
            if (passoAtual < ordemAnimacao.length) {
                const no = ordemAnimacao[passoAtual];
                no.visivel = true;

                // Mostra o nó
                const elNode = document.getElementById("node-" + no.id);
                if (elNode) {
                    elNode.setAttribute("opacity", "1");
                    elNode.setAttribute("style", "pointer-events: all;");
                }
                // Mostra o link
                if (no.parent) {
                    const elLink = document.getElementById("link-" + no.id);
                    if (elLink) elLink.setAttribute("opacity", "0.6");
                }

                mostrarDetalhes(no);

                // Foco suave na câmera
                panX = window.innerWidth / 2 - no.x * scale;
                panY = window.innerHeight / 2 - no.y * scale;
                atualizarTransform();

                passoAtual++;
                atualizarLabelPasso();
            }
        }

        function passoAnterior() {
            if (passoAtual > 1) {
                passoAtual--;
                const no = ordemAnimacao[passoAtual];
                no.visivel = false;

                const elNode = document.getElementById("node-" + no.id);
                if (elNode) {
                    elNode.setAttribute("opacity", "0");
                    elNode.setAttribute("style", "pointer-events: none;");
                }
                if (no.parent) {
                    const elLink = document.getElementById("link-" + no.id);
                    if (elLink) elLink.setAttribute("opacity", "0");
                }

                const noAnterior = ordemAnimacao[passoAtual - 1];
                mostrarDetalhes(noAnterior);
                panX = window.innerWidth / 2 - noAnterior.x * scale;
                panY = window.innerHeight / 2 - noAnterior.y * scale;
                atualizarTransform();

                atualizarLabelPasso();
            }
        }

        function expandirTudo() {
            ordemAnimacao.forEach(no => {
                no.visivel = true;
                const elNode = document.getElementById("node-" + no.id);
                if (elNode) {
                    elNode.setAttribute("opacity", "1");
                    elNode.setAttribute("style", "pointer-events: all;");
                }
                if (no.parent) {
                    const elLink = document.getElementById("link-" + no.id);
                    if (elLink) elLink.setAttribute("opacity", "0.6");
                }
            });
            passoAtual = ordemAnimacao.length;
            atualizarLabelPasso();
            resetView();
        }

        function toggleNo(no) {
            if (no.filhos && no.filhos.length > 0) {
                const algumOculto = no.filhos.some(f => !f.visivel);
                no.filhos.forEach(f => {
                    f.visivel = algumOculto;
                    const elNode = document.getElementById("node-" + f.id);
                    if (elNode) {
                        elNode.setAttribute("opacity", f.visivel ? "1" : "0");
                        elNode.setAttribute("style", f.visivel ? "pointer-events: all;" : "pointer-events: none;");
                    }
                    const elLink = document.getElementById("link-" + f.id);
                    if (elLink) elLink.setAttribute("opacity", f.visivel ? "0.6" : "0");
                });
            }
        }

        function atualizarLabelPasso() {
            lblPasso.textContent = `Passo ${passoAtual} / ${ordemAnimacao.length}`;
        }

        function resetView() {
            scale = 0.9;
            panX = 120;
            panY = window.innerHeight / 2;
            atualizarTransform();
        }

        // Navegação com Teclado
        window.addEventListener("keydown", (e) => {
            if (e.key === "ArrowRight" || e.key === " " || e.key === "PageDown") {
                proximoPasso();
            } else if (e.key === "ArrowLeft" || e.key === "PageUp") {
                passoAnterior();
            } else if (e.key === "Home") {
                passoAtual = 1;
                ordemAnimacao.slice(1).forEach(no => {
                    no.visivel = false;
                    const elNode = document.getElementById("node-" + no.id);
                    if (elNode) elNode.setAttribute("opacity", "0");
                    const elLink = document.getElementById("link-" + no.id);
                    if (elLink) elLink.setAttribute("opacity", "0");
                });
                atualizarLabelPasso();
                resetView();
            }
        });

        // Pan e Zoom com Mouse
        viewport.addEventListener("mousedown", (e) => {
            isDragging = true;
            startX = e.clientX - panX;
            startY = e.clientY - panY;
        });

        window.addEventListener("mousemove", (e) => {
            if (isDragging) {
                panX = e.clientX - startX;
                panY = e.clientY - startY;
                atualizarTransform();
            }
        });

        window.addEventListener("mouseup", () => isDragging = false);

        viewport.addEventListener("wheel", (e) => {
            e.preventDefault();
            const delta = e.deltaY > 0 ? 0.9 : 1.1;
            scale = Math.min(Math.max(0.3, scale * delta), 2.5);
            atualizarTransform();
        }, { passive: false });

        // Inicialização
        renderizarMapa();
        proximoPasso(); // Inicia com a raiz visível
    </script>
</body>
</html>
"""

def construir_arvore_padrao(titulo: str, conceitos: list) -> dict:
    """Gera uma estrutura hierárquica robusta de nós caso a IA retorne lista de conceitos."""
    filhos_ramos = []
    for idx, c in enumerate(conceitos, 1):
        nome_c = c.get("nome", f"Conceito {idx}")
        explicacao = c.get("explicacao", "")
        pegadinha = c.get("pegadinha_banca", "")

        filhos_ramos.append({
            "id": f"ramo_{idx}",
            "titulo": nome_c[:35],
            "descricao": explicacao,
            "pegadinha": pegadinha,
            "filhos": [
                {
                    "id": f"sub_{idx}_1",
                    "titulo": "Regra & Aplicação",
                    "descricao": explicacao[:200],
                    "pegadinha": "",
                    "filhos": []
                },
                {
                    "id": f"sub_{idx}_2",
                    "titulo": "Pegadinha de Prova",
                    "descricao": pegadinha or "Atenção aos termos restritivos utilizados pela banca examinadora.",
                    "pegadinha": pegadinha,
                    "filhos": []
                }
            ]
        })

    return {
        "id": "raiz",
        "titulo": titulo[:35],
        "descricao": f"Mapa mental estruturado da aula: {titulo}",
        "pegadinha": "",
        "filhos": filhos_ramos
    }

def gerar_mapa_mental_interativo(dados_aula: dict, nome_arquivo_saida: str) -> str:
    """
    Gera o arquivo HTML do mapa mental com animação por setinhas e interação por mouse.
    """
    materia = dados_aula.get("materia", "Concursos")
    topico = dados_aula.get("topico", "Aula")
    arvore = dados_aula.get("mapa_mental")

    if not arvore or not isinstance(arvore, dict) or "filhos" not in arvore:
        arvore = construir_arvore_padrao(topico, dados_aula.get("conceitos", []))

    conteudo_html = HTML_TEMPLATE.replace("{TITULO_AULA}", topico)\
                                 .replace("{MATERIA}", materia)\
                                 .replace("{DADOS_JSON}", json.dumps(arvore, ensure_ascii=False))

    nome_limpo = re.sub(r'[\\/*?:"<>|]', "", nome_arquivo_saida).strip()
    if not nome_limpo.endswith(".html"):
        nome_limpo += ".html"

    caminho_final = DIR_MAPAS / nome_limpo
    with open(caminho_final, "w", encoding="utf-8") as f:
        f.write(conteudo_html)

    print(f"[Mapa Mental] Gerado com animacao interativa em:\n   {caminho_final}")
    return str(caminho_final)
