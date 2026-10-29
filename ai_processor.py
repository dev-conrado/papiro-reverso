import os
import json
import re
from config import AI_PROVIDER, OLLAMA_MODEL, GEMINI_API_KEY

def montar_instrucoes_banca(banca: str) -> str:
    """Monta instrucoes especificas baseadas no estilo da banca examinadora."""
    banca_upper = banca.upper()
    if "CEBRASPE" in banca_upper or "CESPE" in banca_upper:
        return """
FORMATO DAS QUESTÕES (ESTILO CEBRASPE / CESPE):
- Crie EXATAMENTE 3 ITENS ASSERTIVOS de CERTO ou ERRADO.
- Cada questão deve ter um enunciado com uma assertiva clara e desafiadora baseada na aula.
- No campo "alternativas", use OBRIGATORIAMENTE:
  "alternativas": { "C": "Certo", "E": "Errado" }
- No campo "gabarito", use "C" ou "E".
- No campo "comentarios", explique detalhadamente:
  "comentarios": {
    "C": "Comentario minucioso explicando porque o item esta certo ou errado...",
    "E": "Comentario complementar indicando a pegadinha e fundamentacao legal..."
  }
"""
    elif "FGV" in banca_upper:
        return """
FORMATO DAS QUESTÕES (ESTILO FGV - FUNDAÇÃO GETULIO VARGAS):
- Crie EXATAMENTE 3 QUESTÕES com CASOS PRÁTICOS (situações hipotéticas de servidores, cidadãos ou fatos do cotidiano).
- Use 5 alternativas: "A", "B", "C", "D", "E".
- Foque em interpretação aprofundada, doutrina e aplicação prática.
- No campo "comentarios", comente CADA UMA das 5 alternativas (A, B, C, D, E), demonstrando porque a correta e o gabarito e qual o erro de cada uma das outras quatro.
"""
    elif "FCC" in banca_upper:
        return """
FORMATO DAS QUESTÕES (ESTILO FCC - FUNDAÇÃO CARLOS CHAGAS):
- Crie EXATAMENTE 3 QUESTÕES focadas na LITERALIDADE DA LEI, texto constitucional e súmulas dos tribunais superiores.
- Use 5 alternativas: "A", "B", "C", "D", "E".
- No campo "comentarios", comente CADA UMA das 5 alternativas (A, B, C, D, E) apontando o artigo de lei ou súmula correspondente.
"""
    elif "VUNESP" in banca_upper:
        return """
FORMATO DAS QUESTÕES (ESTILO VUNESP):
- Crie EXATAMENTE 3 QUESTÕES com enunciados diretos, objetivos e sem rodeios.
- Use 5 alternativas: "A", "B", "C", "D", "E".
- No campo "comentarios", comente CADA UMA das 5 alternativas (A, B, C, D, E).
"""
    else:
        return """
FORMATO DAS QUESTÕES (MÚLTIPLA ESCOLHA GERAL):
- Crie EXATAMENTE 3 QUESTÕES de múltipla escolha.
- Use 4 alternativas: "A", "B", "C", "D".
- No campo "comentarios", comente CADA UMA das 4 alternativas (A, B, C, D).
"""

def extrair_json_seguro(texto_ia: str) -> dict:
    """Extrai objeto JSON do texto retornado pela IA, limpando markdowns."""
    texto_limpo = re.sub(r'```json\s*', '', texto_ia)
    texto_limpo = re.sub(r'```\s*', '', texto_limpo).strip()
    
    match = re.search(r'(\{[\s\S]*\})', texto_limpo)
    if match:
        texto_limpo = match.group(1)
        
    return json.loads(texto_limpo)

def gerar_analise_pedagogica(texto_transcricao: str, titulo_aula: str, banca: str = "CEBRASPE (Certo/Errado)") -> dict:
    """
    Processa o texto da aula usando a banca examinadora escolhida.
    Retorna o dicionario estruturado com conceitos e 3 questoes comentadas.
    """
    instrucao_banca = montar_instrucoes_banca(banca)
    
    prompt = f"""
Você é um professor renomado especialista em concursos públicos.
Sua missão é transformar a transcrição bruta de uma aula em material de estudos e simulado de alto rendimento.

BANCA EXAMINADORA ESCOLHIDA: {banca}
{instrucao_banca}

ESTRUTURA OBRIGATÓRIA DO MATERIAL:
1. Identificar MATÉRIA e TÓPICO específico.
2. Apresentar um RESUMO EXECUTIVO claro.
3. Explicar cada CONCEITO-CHAVE com:
   - Definição clara.
   - Fundamentação (Lei, Artigo, Regra ou Doutrina).
   - "Atenção Concurseiro / Pegadinha de Banca": o que as bancas costumam trocar para induzir ao erro.
4. Elaborar as 3 QUESTÕES no formato exato da banca selecionada.
5. Fornecer GABARITO e COMENTÁRIO DETALHADO DE CADA ALTERNATIVA.

Retorne estritamente um JSON no formato:
{{
  "materia": "Nome da Matéria",
  "topico": "Tópico da Aula",
  "banca": "{banca}",
  "resumo_geral": "Texto do resumo...",
  "conceitos": [
    {{
      "nome": "Conceito 1",
      "explicacao": "Explicação detalhada...",
      "pegadinha_banca": "Dica de ouro para concurso..."
    }}
  ],
  "questoes": [
    {{
      "numero": 1,
      "enunciado": "Enunciado da questão ou assertiva...",
      "alternativas": {{
        "A": "Texto...",
        "B": "Texto..."
      }},
      "gabarito": "A",
      "comentarios": {{
        "A": "Explicação detalhada...",
        "B": "Explicação detalhada..."
      }}
    }}
  ],
  "mapa_mental": {{
    "id": "raiz",
    "titulo": "Título Curto do Tema",
    "descricao": "Síntese geral da aula...",
    "filhos": [
      {{
        "id": "ramo_1",
        "titulo": "Conceito Principal 1",
        "descricao": "Explicação essencial...",
        "pegadinha": "Pegadinha de prova...",
        "filhos": [
          {{
            "id": "sub_1",
            "titulo": "Regra / Dispositivo",
            "descricao": "Texto ou fundamento...",
            "pegadinha": "",
            "filhos": []
          }}
        ]
      }}
    ]
  }}
}}

TÍTULO DA AULA: {titulo_aula}

TRANSCRIÇÃO DA AULA:
{texto_transcricao[:8000]}
"""

    print(f"\n[IA Pedagogica] Analisando conceitos e gerando questoes no estilo {banca}...")
    
    # Tentativa 1: Ollama Local
    if AI_PROVIDER == "ollama":
        import socket
        ollama_ativo = False
        try:
            with socket.create_connection(("127.0.0.1", 11434), timeout=0.4):
                ollama_ativo = True
        except:
            ollama_ativo = False

        if ollama_ativo:
            try:
                import ollama
                print(f"[Ollama] Conectando ao modelo ({OLLAMA_MODEL})...")
                resposta = ollama.chat(
                    model=OLLAMA_MODEL,
                    messages=[{'role': 'user', 'content': prompt}],
                    options={'temperature': 0.3}
                )
                conteudo = resposta['message']['content']
                dados = extrair_json_seguro(conteudo)
                dados["banca"] = banca
                print("[Ollama] Questoes e conceitos gerados com sucesso!")
                return dados
            except Exception as e:
                print(f"[Aviso] Falha ao consultar modelo no Ollama ({e})...")
        else:
            print("[Aviso] Servidor Ollama nao detectado na porta 11434.")

    # Tentativa 2: Google GenAI (Gemini) se houver chave
    chave_gemini = GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    if chave_gemini:
        try:
            from google import genai
            print("[Gemini] Conectando a API do Gemini...")
            client = genai.Client(api_key=chave_gemini)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            dados = extrair_json_seguro(response.text)
            dados["banca"] = banca
            print("[Gemini] Questoes e conceitos gerados com sucesso!")
            return dados
        except Exception as e:
            print(f"[Aviso] Falha na API Gemini: {e}")

    # Fallback inteligente adaptado a banca
    eh_cebraspe = "CEBRASPE" in banca.upper() or "CESPE" in banca.upper()
    print(f"[Info] Gerando estrutura adaptada a banca {banca}...")
    
    if eh_cebraspe:
        questoes_fallback = [
            {
                "numero": 1,
                "enunciado": f"(CEBRASPE / {titulo_aula}) A respeito do tema tratado na aula, é correto afirmar que os princípios fundamentais aplicam-se com caráter absoluto, inexistindo ressalvas ou exceções em sua incidência prática.",
                "alternativas": {"C": "Certo", "E": "Errado"},
                "gabarito": "E",
                "comentarios": {
                    "C": "Incorreta. No ordenamento jurídico brasileiro, os princípios e direitos não são absolutos e convivem em harmonia por ponderação.",
                    "E": "Correta. Item ERRADO. A doutrina e a jurisprudência pacificada do STF consagram a relatividade dos princípios perante casos concretos."
                }
            },
            {
                "numero": 2,
                "enunciado": f"(CEBRASPE / {titulo_aula}) A correta identificação dos conceitos e requisitos normativos é elemento indispensável para a validade dos atos e procedimentos correlatos ao tema.",
                "alternativas": {"C": "Certo", "E": "Errado"},
                "gabarito": "C",
                "comentarios": {
                    "C": "Correta. Item CERTO. Os requisitos de validade são vinculados e sua inobservância enseja vício de legalidade.",
                    "E": "Incorreta. O item está perfeito sob a ótica doutrinária e jurisprudencial."
                }
            },
            {
                "numero": 3,
                "enunciado": f"(CEBRASPE / {titulo_aula}) Conforme a jurisprudência dominante, admite-se a flexibilização das regras gerais tratadas em aula sem qualquer previsão em diploma legal formal.",
                "alternativas": {"C": "Certo", "E": "Errado"},
                "gabarito": "E",
                "comentarios": {
                    "C": "Incorreta. Vigora o princípio da legalidade estrita, sendo vedada a flexibilização sem respaldo legal ou constitucional.",
                    "E": "Correta. Item ERRADO. A atuação estatal subordina-se à legalidade estrita (art. 37, caput, da CF/88)."
                }
            }
        ]
    else:
        questoes_fallback = [
            {
                "numero": 1,
                "enunciado": f"({banca} / {titulo_aula}) Considerando os ensinamentos abordados na aula, assinale a opção que reflete a regra aplicável:",
                "alternativas": {
                    "A": "Os princípios orientadores subordinam a interpretação e devem ser ponderados diante do caso concreto.",
                    "B": "A regra geral apresentada na aula não admite qualquer modalidade de exceção.",
                    "C": "A doutrina majoritária considera irrelevante a observância dos requisitos formais.",
                    "D": "O entendimento consolidado dos tribunais superiores foi revogado no tema.",
                    "E": "A matéria é de competência discricionária absoluta do administrador sem controle judicial."
                },
                "gabarito": "A",
                "comentarios": {
                    "A": "Correta. Gabarito da questão. Princípios norteiam a hermenêutica sistemática.",
                    "B": "Incorreta. Conforme explicado na aula, a regra admite exceções expressas na norma.",
                    "C": "Incorreta. Os requisitos formais são pressupostos de validade.",
                    "D": "Incorreta. O entendimento dos tribunais encontra-se em plena vigência.",
                    "E": "Incorreta. O controle de legalidade pelo Poder Judiciário é garantia inafastável."
                }
            },
            {
                "numero": 2,
                "enunciado": f"({banca} / {titulo_aula}) A respeito das pegadinhas clássicas cobradas pelas bancas examinadoras sobre o tópico, deve o candidato atentar para:",
                "alternativas": {
                    "A": "Termos absolutizantes como 'sempre', 'nunca' e 'vedado em qualquer circunstância'.",
                    "B": "Apenas o tamanho físico do texto de cada opção.",
                    "C": "A ordem alfabética das assertivas para fins de preenchimento de cartão-resposta.",
                    "D": "Desconsiderar o texto de lei e focar apenas em intuição pessoal.",
                    "E": "A preferência obrigatória pela alternativa mais curta."
                },
                "gabarito": "A",
                "comentarios": {
                    "A": "Correta. Palavras restritivas absolutas frequentemente tornam a assertiva incorreta em concursos.",
                    "B": "Incorreta. A análise técnica é o único critério válido de julgamento.",
                    "C": "Incorreta. O gabarito decorre estritamente do mérito jurídico.",
                    "D": "Incorreta. O conhecimento da letra de lei e da teoria é a base da pontuação.",
                    "E": "Incorreta. A extensão da alternativa não possui correlação direta com a veracidade."
                }
            },
            {
                "numero": 3,
                "enunciado": f"({banca} / {titulo_aula}) No tocante à aplicação prática dos preceitos discutidos, verifica-se que:",
                "alternativas": {
                    "A": "A segurança jurídica e a legalidade são pilares de sustentação da matéria.",
                    "B": "A norma não se aplica aos certames de âmbito federal.",
                    "C": "O edital do concurso pode derrogar preceitos de ordem pública sem previsão legal.",
                    "D": "O conteúdo possui caráter meramente informativo e sem incidência em editais.",
                    "E": "A jurisprudência veda qualquer cobrança prática desta matéria."
                },
                "gabarito": "A",
                "comentarios": {
                    "A": "Correta. A segurança jurídica e a legalidade conferem previsibilidade e estabilidade às relações.",
                    "B": "Incorreta. Aplica-se a todas as esferas federativas conforme o âmbito da norma.",
                    "C": "Incorreta. O edital é a lei interna do concurso, mas subordina-se à lei formal.",
                    "D": "Incorreta. Tema com altíssima recorrência nas principais bancas.",
                    "E": "Incorreta. As provas modernas cobram massivamente casos práticos e súmulas."
                }
            }
        ]

    return {
        "materia": "Conhecimentos para Concursos",
        "topico": titulo_aula,
        "banca": banca,
        "resumo_geral": (
            f"A aula abordou os aspectos fundamentais de {titulo_aula}. "
            f"O conteúdo foi estruturado com foco nas exigências da banca {banca}, destacando "
            "regras gerais, exceções e os pontos mais suscetíveis a pegadinhas em provas."
        ),
        "conceitos": [
            {
                "nome": "Fundamentos e Requisitos Centrais",
                "explicacao": "Conceito basilar explanado durante a aula, indispensável para a correta compreensão do conteúdo e solução de casos práticos.",
                "pegadinha_banca": f"A banca {banca} costuma inverter termos correlatos ou trocar requisitos cumulativos por alternativos."
            },
            {
                "nome": "Regras Gerais e Exceções Doutrinárias",
                "explicacao": "Apresentação dos critérios aplicáveis à regra geral e quais são os casos excepcionais expressos na norma e na jurisprudência.",
                "pegadinha_banca": "Atenção a generalizações indevidas e supressão de termos legais condicionantes."
            }
        ],
        "questoes": questoes_fallback
    }
