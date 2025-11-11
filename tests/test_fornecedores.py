#!/usr/bin/env python3
"""
Testes de Fornecedores
Testa: criar, listar, buscar, atualizar, deletar, estatísticas
"""

import sys
sys.path.append('.')

from tests.config import *
from tests.utils import *


# Variável para armazenar ID do fornecedor criado nos testes
FORNECEDOR_ID = None


def setup():
    """Preparação: fazer login para obter token"""
    print_info("Fazendo login para obter token de autenticação...")
    
    sucesso, response, erro = fazer_request(
        'POST',
        ENDPOINTS['auth']['login'],
        json={'email': ADMIN_EMAIL, 'senha': ADMIN_SENHA}
    )
    
    if sucesso and response.status_code == 200:
        data = response.json()
        set_token(data['token'])
        print_sucesso("Login realizado com sucesso\n")
        return True
    else:
        print_erro(f"Falha no login: {erro}")
        return False


def test_criar_fornecedor():
    """Testa criação de fornecedor"""
    global FORNECEDOR_ID
    
    print_separador("1. CRIAR FORNECEDOR")
    
    contador = TestResultCounter()
    
    if not get_token():
        contador.registrar_falha("Criar fornecedor", "Token não disponível")
        return contador
    
    print_info("Testando POST /api/fornecedores/")
    
    fornecedor_data = {
        "razao_social": "Fornecedor Teste Automatizado LTDA",
        "nome_fantasia": "Fornecedor Teste Automatizado",
        "cnpj": "34028316000103",  # CNPJ válido diferente
        "email": "fornecedor@teste.com",
        "telefone": "(11) 98765-4321",
        "endereco": "Rua Teste, 123 - São Paulo, SP"
    }
    
    print_json(fornecedor_data, "Dados do Fornecedor")
    
    sucesso, response, erro = fazer_request(
        'POST',
        f"{ENDPOINTS['fornecedores']['base']}/",
        json=fornecedor_data,
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Criar fornecedor", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 201)
    
    if valido and data.get('success'):
        fornecedor = data.get('fornecedor')
        FORNECEDOR_ID = fornecedor.get('id_fornecedor')
        contador.registrar_sucesso(f"Criar fornecedor (ID: {FORNECEDOR_ID})")
        print_json(fornecedor, "Fornecedor Criado")
    else:
        contador.registrar_falha("Criar fornecedor", mensagem)
    
    # Teste: Criar com CNPJ inválido
    print_info("\nTestando criação com CNPJ inválido")
    
    sucesso, response, erro = fazer_request(
        'POST',
        f"{ENDPOINTS['fornecedores']['base']}/",
        json={"cnpj": "12345678000000", "razao_social": "Teste", "nome_fantasia": "Teste"},
        headers=get_headers()
    )
    
    if sucesso and response.status_code == 400:
        contador.registrar_sucesso("Validação: CNPJ inválido rejeitado")
    else:
        contador.registrar_falha("Validação: CNPJ inválido", "Deveria retornar 400")
    
    return contador


def test_listar_fornecedores():
    """Testa listagem de fornecedores"""
    print_separador("2. LISTAR FORNECEDORES")
    
    contador = TestResultCounter()
    
    if not get_token():
        contador.registrar_falha("Listar fornecedores", "Token não disponível")
        return contador
    
    print_info("Testando GET /api/fornecedores/")
    
    sucesso, response, erro = fazer_request(
        'GET',
        f"{ENDPOINTS['fornecedores']['base']}/",
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Listar fornecedores", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        fornecedores = data.get('fornecedores', [])
        contador.registrar_sucesso(f"Listar fornecedores ({len(fornecedores)} encontrados)")
        
        if fornecedores:
            print_json(fornecedores[0], "Exemplo de Fornecedor")
    else:
        contador.registrar_falha("Listar fornecedores", mensagem)
    
    return contador


def test_buscar_fornecedor_por_id():
    """Testa busca de fornecedor por ID"""
    print_separador("3. BUSCAR FORNECEDOR POR ID")
    
    contador = TestResultCounter()
    
    if not FORNECEDOR_ID:
        contador.registrar_falha("Buscar fornecedor por ID", "ID não disponível")
        return contador
    
    if not get_token():
        contador.registrar_falha("Buscar fornecedor por ID", "Token não disponível")
        return contador
    
    print_info(f"Testando GET /api/fornecedores/{FORNECEDOR_ID}")
    
    sucesso, response, erro = fazer_request(
        'GET',
        f"{ENDPOINTS['fornecedores']['base']}/{FORNECEDOR_ID}",
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Buscar fornecedor por ID", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        contador.registrar_sucesso("Buscar fornecedor por ID")
        print_json(data.get('fornecedor'), "Fornecedor Encontrado")
    else:
        contador.registrar_falha("Buscar fornecedor por ID", mensagem)
    
    return contador


def test_buscar_fornecedores_por_nome():
    """Testa busca de fornecedores por nome"""
    print_separador("4. BUSCAR FORNECEDORES POR NOME")
    
    contador = TestResultCounter()
    
    if not get_token():
        contador.registrar_falha("Buscar por nome", "Token não disponível")
        return contador
    
    print_info("Testando GET /api/fornecedores/buscar?nome=Teste")
    
    sucesso, response, erro = fazer_request(
        'GET',
        ENDPOINTS['fornecedores']['buscar'],
        params={'nome': 'Teste'},
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Buscar por nome", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        fornecedores = data.get('fornecedores', [])
        contador.registrar_sucesso(f"Buscar por nome ({len(fornecedores)} encontrados)")
        
        if fornecedores:
            print_json(fornecedores, "Fornecedores Encontrados")
    else:
        contador.registrar_falha("Buscar por nome", mensagem)
    
    return contador


def test_atualizar_fornecedor():
    """Testa atualização de fornecedor"""
    print_separador("5. ATUALIZAR FORNECEDOR")
    
    contador = TestResultCounter()
    
    if not FORNECEDOR_ID:
        contador.registrar_falha("Atualizar fornecedor", "ID não disponível")
        return contador
    
    if not get_token():
        contador.registrar_falha("Atualizar fornecedor", "Token não disponível")
        return contador
    
    print_info(f"Testando PUT /api/fornecedores/{FORNECEDOR_ID}")
    
    update_data = {
        "nome_fantasia": "Fornecedor Teste ATUALIZADO",
        "email": "novoemail@teste.com",
        "telefone": "(11) 91234-5678"
    }
    
    print_json(update_data, "Dados para Atualização")
    
    sucesso, response, erro = fazer_request(
        'PUT',
        f"{ENDPOINTS['fornecedores']['base']}/{FORNECEDOR_ID}",
        json=update_data,
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Atualizar fornecedor", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        contador.registrar_sucesso("Atualizar fornecedor")
        print_json(data.get('fornecedor'), "Fornecedor Atualizado")
    else:
        contador.registrar_falha("Atualizar fornecedor", mensagem)
    
    return contador


def test_estatisticas_fornecedores():
    """Testa estatísticas de fornecedores"""
    print_separador("6. ESTATÍSTICAS DE FORNECEDORES")
    
    contador = TestResultCounter()
    
    if not get_token():
        contador.registrar_falha("Estatísticas", "Token não disponível")
        return contador
    
    print_info("Testando GET /api/fornecedores/estatisticas")
    
    sucesso, response, erro = fazer_request(
        'GET',
        ENDPOINTS['fornecedores']['estatisticas'],
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Estatísticas", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        contador.registrar_sucesso("Estatísticas")
        print_json(data.get('estatisticas'), "Estatísticas")
    else:
        contador.registrar_falha("Estatísticas", mensagem)
    
    return contador


def test_deletar_fornecedor():
    """Testa exclusão de fornecedor"""
    print_separador("7. DELETAR FORNECEDOR")
    
    contador = TestResultCounter()
    
    if not FORNECEDOR_ID:
        contador.registrar_falha("Deletar fornecedor", "ID não disponível")
        return contador
    
    if not get_token():
        contador.registrar_falha("Deletar fornecedor", "Token não disponível")
        return contador
    
    print_info(f"Testando DELETE /api/fornecedores/{FORNECEDOR_ID}")
    
    sucesso, response, erro = fazer_request(
        'DELETE',
        f"{ENDPOINTS['fornecedores']['base']}/{FORNECEDOR_ID}",
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Deletar fornecedor", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        contador.registrar_sucesso("Deletar fornecedor")
        
        # Verificar se foi deletado
        print_info("\nVerificando se fornecedor foi realmente deletado")
        
        sucesso, response, erro = fazer_request(
            'GET',
            f"{ENDPOINTS['fornecedores']['base']}/{FORNECEDOR_ID}",
            headers=get_headers()
        )
        
        if sucesso and response.status_code == 404:
            contador.registrar_sucesso("Fornecedor deletado com sucesso")
        else:
            contador.registrar_falha("Verificar deleção", "Fornecedor ainda existe")
    else:
        contador.registrar_falha("Deletar fornecedor", mensagem)
    
    return contador


def run_all_fornecedor_tests():
    """Executa todos os testes de fornecedores"""
    print("\n" + "🏭"*35)
    print("   TESTES DE FORNECEDORES - API AutoPek")
    print("🏭"*35 + "\n")
    
    # Verificar se API está online
    if not verificar_api_online(API_BASE_URL):
        print_erro(f"API não está online em {API_BASE_URL}")
        print_info("Certifique-se de executar: python app.py")
        return False
    
    print_sucesso(f"API está online em {API_BASE_URL}\n")
    
    # Setup: fazer login
    if not setup():
        return False
    
    # Executar testes na ordem
    contador_criar = test_criar_fornecedor()
    contador_listar = test_listar_fornecedores()
    contador_buscar_id = test_buscar_fornecedor_por_id()
    contador_buscar_nome = test_buscar_fornecedores_por_nome()
    contador_atualizar = test_atualizar_fornecedor()
    contador_estatisticas = test_estatisticas_fornecedores()
    contador_deletar = test_deletar_fornecedor()
    
    # Consolidar resultados
    resultado_geral = TestResultCounter()
    
    for contador in [contador_criar, contador_listar, contador_buscar_id,
                     contador_buscar_nome, contador_atualizar, 
                     contador_estatisticas, contador_deletar]:
        if isinstance(contador, TestResultCounter):
            resultado_geral.total += contador.total
            resultado_geral.sucessos += contador.sucessos
            resultado_geral.falhas += contador.falhas
            resultado_geral.erros.extend(contador.erros)
    
    # Imprimir resumo geral
    sucesso = resultado_geral.imprimir_resumo()
    
    return sucesso


if __name__ == '__main__':
    sucesso = run_all_fornecedor_tests()
    sys.exit(0 if sucesso else 1)
