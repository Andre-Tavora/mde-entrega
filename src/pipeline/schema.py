# src/schema.py â€” NÃƒO RENOMEAR (auditoria depende destes nomes)
# Entrada: claude_results.jsonl
K_ID          = "id"
K_VALIDO      = "valido"
K_STATUS      = "status"
K_PRED        = "predicao_llm"
K_RACIOCINIO  = "raciocinio_juridico"
K_ESCOPO      = "pertence_ao_escopo"
K_TEMA        = "id_tema_escolhido"
K_EXTRAS      = "ids_extras"
K_CONF        = "confianca_modelo"

# SaÃ­da: publicacao.csv (colunas exigidas no edital)
COLS_PUBLICACAO = ["id", "decisao", "tema_central", "extras", "confianca"]
DECISOES = {"publicar", "revisar", "fora"}
PATH_PUBLICACAO = r"mde-entrega/output/publicacao.csv"
CONF_MIN = 5   # ponto de partida; serÃ¡ recalibrado na auditoria (Fase 4)

# --- Taxonomia (temas.csv) e caminhos ---
from pathlib import Path
ROOT            = Path(__file__).resolve().parents[2]
PATH_TEMAS      = ROOT / "data" / "raw" / "temas.csv"
PATH_PRED       = ROOT / "data" / "raw_predictions" / "claude_results.jsonl"
PATH_PUBLICACAO = ROOT / "output" / "publicacao.csv"
CSV_ENCODING    = "utf-8"
T_ID     = "tema_id"
T_STATUS = "status"
T_NIVEL  = "nivel"
T_ATIVO  = "active"

K_ID = 'id_questao'
