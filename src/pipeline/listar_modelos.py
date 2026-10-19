import os
from dotenv import load_dotenv
import anthropic

load_dotenv()
API_KEY = os.environ.get("ANTHROPIC_API_KEY")

if not API_KEY:
    print("ERRO: Configure sua ANTHROPIC_API_KEY válida no arquivo .env")
    exit(1)

client = anthropic.Anthropic(api_key=API_KEY)

print("Tentando buscar os modelos pela API...")
try:
    # Nas versões recentes do SDK, isso lista os modelos
    modelos = client.models.list()
    print("\n=== MODELOS DISPONÍVEIS NA SUA CHAVE ===")
    for m in modelos.data:
        print(f" - {m.id}")
    print("=========================================\n")
    print("Por favor, cole um dos nomes acima no chat para continuarmos!")
except Exception as e:
    print(f"\nErro ao usar client.models.list(): {e}")
    print("\nParece que o seu SDK da Anthropic está numa versão onde models.list() não existe ou o método de autenticação da chave é muito antigo.")
    print("Neste caso, a Anthropic exige que você use a string genérica do último modelo lançado.")