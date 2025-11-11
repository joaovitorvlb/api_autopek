"""
Utilitários compartilhados para testes
"""

import json
import requests


def print_separador(titulo=""):
    """Imprime um separador visual"""
    print("\n" + "="*70)
    if titulo:
        print(f"  {titulo}")
        print("="*70)


def print_teste_iniciando(nome_teste, numero=None):
    """Imprime cabeçalho ao iniciar um teste"""
    print("\n" + "─"*70)
    if numero:
        print(f"🧪 TESTE {numero}: {nome_teste}")
    else:
        print(f"🧪 {nome_teste}")
    print("─"*70)


def print_sucesso(mensagem):
    """Imprime mensagem de sucesso"""
    print(f"✅ {mensagem}")


def print_erro(mensagem):
    """Imprime mensagem de erro"""
    print(f"❌ {mensagem}")


def print_info(mensagem):
    """Imprime mensagem informativa"""
    print(f"ℹ️  {mensagem}")


def print_json(data, titulo=""):
    """Imprime JSON formatado"""
    if titulo:
        print(f"\n📄 {titulo}:")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def verificar_api_online(base_url):
    """Verifica se a API está online"""
    try:
        response = requests.get(base_url, timeout=5)
        return response.status_code == 200
    except:
        return False


def fazer_request(method, url, **kwargs):
    """
    Wrapper para fazer requests com tratamento de erro padrão
    
    Args:
        method: 'GET', 'POST', 'PUT', 'DELETE'
        url: URL completa
        **kwargs: Argumentos para requests (json, headers, params, etc)
    
    Returns:
        tuple: (success: bool, response: Response ou None, error_message: str)
    """
    try:
        response = requests.request(method, url, **kwargs)
        return True, response, None
    except requests.exceptions.ConnectionError:
        return False, None, "Não foi possível conectar à API. Certifique-se que está rodando."
    except requests.exceptions.Timeout:
        return False, None, "Timeout ao conectar à API."
    except Exception as e:
        return False, None, f"Erro inesperado: {str(e)}"


def validar_response_success(response, codigo_esperado=200):
    """
    Valida se response tem sucesso esperado
    
    Returns:
        tuple: (sucesso: bool, mensagem: str, data: dict ou None)
    """
    if response.status_code != codigo_esperado:
        try:
            error_data = response.json()
            return False, f"Status {response.status_code}: {error_data.get('message', 'Erro desconhecido')}", None
        except:
            return False, f"Status {response.status_code}", None
    
    try:
        data = response.json()
        return True, "OK", data
    except:
        return False, "Resposta não é JSON válido", None


class TestResultCounter:
    """Contador de resultados de testes"""
    
    def __init__(self):
        self.total = 0
        self.sucessos = 0
        self.falhas = 0
        self.erros = []
        self.testes_executados = []
    
    def registrar_sucesso(self, nome_teste):
        """Registra um teste bem-sucedido"""
        self.total += 1
        self.sucessos += 1
        self.testes_executados.append({
            'nome': nome_teste,
            'status': 'SUCESSO',
            'erro': None
        })
        print(f"\n{'─'*70}")
        print(f"✅ TESTE SATISFEITO: {nome_teste}")
        print(f"{'─'*70}")
    
    def registrar_falha(self, nome_teste, mensagem_erro):
        """Registra um teste que falhou"""
        self.total += 1
        self.falhas += 1
        erro_info = {
            'teste': nome_teste,
            'erro': mensagem_erro
        }
        self.erros.append(erro_info)
        self.testes_executados.append({
            'nome': nome_teste,
            'status': 'FALHA',
            'erro': mensagem_erro
        })
        print(f"\n{'─'*70}")
        print(f"❌ TESTE FALHOU: {nome_teste}")
        print(f"   Erro: {mensagem_erro}")
        print(f"{'─'*70}")
    
    def imprimir_resumo(self):
        """Imprime resumo detalhado dos testes"""
        print("\n" + "="*70)
        print("  RESUMO FINAL DOS TESTES")
        print("="*70)
        
        # Lista todos os testes executados
        print("\n� TESTES EXECUTADOS:")
        for i, teste in enumerate(self.testes_executados, 1):
            if teste['status'] == 'SUCESSO':
                print(f"   {i}. ✅ {teste['nome']} - SATISFEITO")
            else:
                print(f"   {i}. ❌ {teste['nome']} - FALHOU")
        
        # Estatísticas
        print(f"\n{'='*70}")
        print("📊 ESTATÍSTICAS:")
        print(f"{'='*70}")
        print(f"   Total de testes executados: {self.total}")
        print(f"   ✅ Testes satisfeitos: {self.sucessos}")
        print(f"   ❌ Testes que falharam: {self.falhas}")
        
        if self.total > 0:
            taxa_sucesso = (self.sucessos / self.total) * 100
            print(f"   📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        # Detalhes das falhas
        if self.falhas > 0:
            print(f"\n{'='*70}")
            print(f"⚠️  DETALHES DAS {self.falhas} FALHA(S):")
            print(f"{'='*70}")
            for i, erro in enumerate(self.erros, 1):
                print(f"\n   {i}. Teste: {erro['teste']}")
                print(f"      Erro: {erro['erro']}")
        else:
            print(f"\n{'='*70}")
            print("🎉 TODOS OS TESTES FORAM SATISFEITOS COM SUCESSO!")
            print(f"{'='*70}")
        
        print("\n" + "="*70 + "\n")
        
        return self.falhas == 0
