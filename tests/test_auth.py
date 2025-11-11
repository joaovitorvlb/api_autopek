#!/usr/bin/env python3
"""
Testes de Autenticação
Testa: login, logout, verificação de token, dados do usuário
"""

import sys
sys.path.append('.')

from tests.config import *
from tests.utils import *


def test_login():
    """Testa login do administrador"""
    print_separador("1. LOGIN DE ADMINISTRADOR")
    
    contador = TestResultCounter()
    
    # Teste: Login com credenciais válidas
    print_info(f"Testando login com {ADMIN_EMAIL}")
    
    sucesso, response, erro = fazer_request(
        'POST',
        ENDPOINTS['auth']['login'],
        json={'email': ADMIN_EMAIL, 'senha': ADMIN_SENHA}
    )
    
    if not sucesso:
        contador.registrar_falha("Login com credenciais válidas", erro)
        return False
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if not valido:
        contador.registrar_falha("Login com credenciais válidas", mensagem)
        return False
    
    if not data.get('success') or not data.get('token'):
        contador.registrar_falha("Login com credenciais válidas", "Token não retornado")
        return False
    
    # Salvar token para outros testes
    set_token(data['token'])
    
    contador.registrar_sucesso("Login com credenciais válidas")
    print_json(data.get('usuario'), "Dados do Usuário")
    
    # Teste: Login com senha incorreta
    print_info("\nTestando login com senha incorreta")
    
    sucesso, response, erro = fazer_request(
        'POST',
        ENDPOINTS['auth']['login'],
        json={'email': ADMIN_EMAIL, 'senha': 'senha_errada'}
    )
    
    if sucesso and response.status_code == 401:
        contador.registrar_sucesso("Login rejeitado com senha incorreta")
    else:
        contador.registrar_falha("Login rejeitado com senha incorreta", "Deveria retornar 401")
    
    # Teste: Login sem email
    print_info("\nTestando login sem email")
    
    sucesso, response, erro = fazer_request(
        'POST',
        ENDPOINTS['auth']['login'],
        json={'senha': ADMIN_SENHA}
    )
    
    if sucesso and response.status_code == 400:
        contador.registrar_sucesso("Login rejeitado sem email")
    else:
        contador.registrar_falha("Login rejeitado sem email", "Deveria retornar 400")
    
    return contador


def test_verify_token():
    """Testa verificação de token"""
    print_separador("2. VERIFICAÇÃO DE TOKEN")
    
    contador = TestResultCounter()
    
    if not get_token():
        contador.registrar_falha("Verificar token válido", "Token não disponível (execute test_login primeiro)")
        return contador
    
    # Teste: Token válido
    print_info("Testando token válido")
    
    sucesso, response, erro = fazer_request(
        'GET',
        ENDPOINTS['auth']['verify'],
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Token válido", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        contador.registrar_sucesso("Token válido")
        print_json(data.get('usuario'), "Dados do Token")
    else:
        contador.registrar_falha("Token válido", mensagem)
    
    # Teste: Token inválido
    print_info("\nTestando token inválido")
    
    sucesso, response, erro = fazer_request(
        'GET',
        ENDPOINTS['auth']['verify'],
        headers={"Authorization": "Bearer token_invalido"}
    )
    
    if sucesso and response.status_code == 401:
        contador.registrar_sucesso("Token inválido rejeitado")
    else:
        contador.registrar_falha("Token inválido rejeitado", "Deveria retornar 401")
    
    # Teste: Sem token
    print_info("\nTestando requisição sem token")
    
    sucesso, response, erro = fazer_request(
        'GET',
        ENDPOINTS['auth']['verify']
    )
    
    if sucesso and response.status_code == 401:
        contador.registrar_sucesso("Requisição sem token rejeitada")
    else:
        contador.registrar_falha("Requisição sem token rejeitada", "Deveria retornar 401")
    
    return contador


def test_get_user_data():
    """Testa obtenção de dados do usuário autenticado"""
    print_separador("3. DADOS DO USUÁRIO AUTENTICADO")
    
    contador = TestResultCounter()
    
    if not get_token():
        contador.registrar_falha("Obter dados do usuário", "Token não disponível")
        return contador
    
    print_info("Testando GET /api/auth/me")
    
    sucesso, response, erro = fazer_request(
        'GET',
        ENDPOINTS['auth']['me'],
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Obter dados do usuário", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        contador.registrar_sucesso("Obter dados do usuário")
        print_json(data.get('usuario'), "Perfil Completo")
    else:
        contador.registrar_falha("Obter dados do usuário", mensagem)
    
    return contador


def test_logout():
    """Testa logout (invalidação de token)"""
    print_separador("4. LOGOUT")
    
    contador = TestResultCounter()
    
    if not get_token():
        contador.registrar_falha("Logout", "Token não disponível")
        return contador
    
    print_info("Testando POST /api/auth/logout")
    
    sucesso, response, erro = fazer_request(
        'POST',
        ENDPOINTS['auth']['logout'],
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Logout", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        contador.registrar_sucesso("Logout realizado")
        
        # Teste: Token invalidado
        print_info("\nTestando se token foi invalidado")
        
        sucesso, response, erro = fazer_request(
            'GET',
            ENDPOINTS['auth']['verify'],
            headers=get_headers()
        )
        
        if sucesso and response.status_code == 401:
            contador.registrar_sucesso("Token invalidado após logout")
        else:
            contador.registrar_falha("Token invalidado após logout", "Token ainda está válido")
    else:
        contador.registrar_falha("Logout", mensagem)
    
    return contador


def run_all_auth_tests():
    """Executa todos os testes de autenticação"""
    print("\n" + "🔐"*35)
    print("   TESTES DE AUTENTICAÇÃO - API AutoPek")
    print("🔐"*35 + "\n")
    
    # Verificar se API está online
    if not verificar_api_online(API_BASE_URL):
        print_erro(f"API não está online em {API_BASE_URL}")
        print_info("Certifique-se de executar: python app.py")
        return False
    
    print_sucesso(f"API está online em {API_BASE_URL}\n")
    
    # Executar testes na ordem
    contador_login = test_login()
    contador_verify = test_verify_token()
    contador_user_data = test_get_user_data()
    contador_logout = test_logout()
    
    # Consolidar resultados
    resultado_geral = TestResultCounter()
    
    for contador in [contador_login, contador_verify, contador_user_data, contador_logout]:
        if isinstance(contador, TestResultCounter):
            resultado_geral.total += contador.total
            resultado_geral.sucessos += contador.sucessos
            resultado_geral.falhas += contador.falhas
            resultado_geral.erros.extend(contador.erros)
        else:
            # Se retornou False, conta como falha
            resultado_geral.total += 1
            resultado_geral.falhas += 1
    
    # Imprimir resumo geral
    sucesso = resultado_geral.imprimir_resumo()
    
    return sucesso


if __name__ == '__main__':
    sucesso = run_all_auth_tests()
    sys.exit(0 if sucesso else 1)
