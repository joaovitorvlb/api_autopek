#!/usr/bin/env python3
"""
Testes de Pedidos de Compra
Testa: criar, listar, adicionar itens, receber, cancelar, relatório
"""

import sys
sys.path.append('.')

from tests.config import *
from tests.utils import *


# Variáveis para armazenar IDs criados nos testes
FORNECEDOR_ID = None
PRODUTO_ID = None
PEDIDO_COMPRA_ID = None


def setup():
    """Preparação: fazer login, criar fornecedor e produto de teste"""
    print_info("Fazendo login para obter token de autenticação...")
    
    sucesso, response, erro = fazer_request(
        'POST',
        ENDPOINTS['auth']['login'],
        json={'email': ADMIN_EMAIL, 'senha': ADMIN_SENHA}
    )
    
    if not sucesso or response.status_code != 200:
        print_erro(f"Falha no login: {erro}")
        return False
    
    data = response.json()
    set_token(data['token'])
    print_sucesso("Login realizado com sucesso")
    
    # Buscar ou criar fornecedor de teste
    global FORNECEDOR_ID
    print_info("Buscando/criando fornecedor de teste...")
    
    # Tentar buscar fornecedores existentes
    sucesso, response, erro = fazer_request(
        'GET',
        f"{ENDPOINTS['fornecedores']['base']}/",
        headers=get_headers()
    )
    
    if sucesso and response.status_code == 200:
        data = response.json()
        fornecedores = data.get('fornecedores', [])
        if fornecedores and len(fornecedores) > 0:
            # Usar o primeiro fornecedor disponível
            FORNECEDOR_ID = fornecedores[0]['id_fornecedor']
            print_sucesso(f"Usando fornecedor existente (ID: {FORNECEDOR_ID})")
        else:
            # Criar novo fornecedor
            sucesso, response, erro = fazer_request(
                'POST',
                f"{ENDPOINTS['fornecedores']['base']}/",
                json={
                    "razao_social": "Fornecedor Teste Pedidos LTDA",
                    "nome_fantasia": "Fornecedor Teste Pedidos",
                    "cnpj": "27865757000102",  # CNPJ válido
                    "email": "teste@fornecedor.com",
                    "telefone": "(11) 98765-4321"
                },
                headers=get_headers()
            )
            
            if sucesso and response.status_code == 201:
                FORNECEDOR_ID = response.json()['fornecedor']['id_fornecedor']
                print_sucesso(f"Fornecedor criado (ID: {FORNECEDOR_ID})")
            else:
                print_erro(f"Falha ao criar fornecedor de teste")
                return False
    else:
        print_erro("Falha ao buscar fornecedores")
        return False
    
    # Criar produto de teste
    global PRODUTO_ID
    print_info("Criando produto de teste...")
    
    sucesso, response, erro = fazer_request(
        'POST',
        f"{ENDPOINTS['produtos']['base']}/",
        json={
            "nome": "Produto Teste Pedido Compra",
            "descricao": "Produto para teste de pedido de compra",
            "preco": 50.00,
            "estoque": 10
        },
        headers=get_headers()
    )
    
    if sucesso and response.status_code == 201:
        PRODUTO_ID = response.json()['produto']['id_produto']
        print_sucesso(f"Produto criado (ID: {PRODUTO_ID})")
    else:
        print_erro("Falha ao criar produto de teste")
        return False
    
    print()
    return True


def test_criar_pedido_compra():
    """Testa criação de pedido de compra"""
    global PEDIDO_COMPRA_ID
    
    print_separador("1. CRIAR PEDIDO DE COMPRA")
    
    contador = TestResultCounter()
    
    if not FORNECEDOR_ID or not PRODUTO_ID:
        contador.registrar_falha("Criar pedido", "Fornecedor ou produto não disponível")
        return contador
    
    print_info("Testando POST /api/pedidos-compra/")
    
    pedido_data = {
        "id_fornecedor": FORNECEDOR_ID,
        "itens": [
            {
                "id_produto": PRODUTO_ID,
                "quantidade": 20,
                "preco_custo_unitario": 45.00
            }
        ]
    }
    
    print_json(pedido_data, "Dados do Pedido")
    
    sucesso, response, erro = fazer_request(
        'POST',
        f"{ENDPOINTS['pedidos_compra']['base']}/",
        json=pedido_data,
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Criar pedido", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 201)
    
    if valido and data.get('success'):
        pedido = data.get('pedido')
        PEDIDO_COMPRA_ID = pedido.get('id_pedido_compra')
        contador.registrar_sucesso(f"Criar pedido (ID: {PEDIDO_COMPRA_ID})")
        print_json(pedido, "Pedido Criado")
    else:
        contador.registrar_falha("Criar pedido", mensagem)
    
    return contador


def test_listar_pedidos_compra():
    """Testa listagem de pedidos de compra"""
    print_separador("2. LISTAR PEDIDOS DE COMPRA")
    
    contador = TestResultCounter()
    
    print_info("Testando GET /api/pedidos-compra/")
    
    sucesso, response, erro = fazer_request(
        'GET',
        f"{ENDPOINTS['pedidos_compra']['base']}/",
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Listar pedidos", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        pedidos = data.get('pedidos', [])
        contador.registrar_sucesso(f"Listar pedidos ({len(pedidos)} encontrados)")
        
        if pedidos:
            print_json(pedidos[0], "Exemplo de Pedido")
    else:
        contador.registrar_falha("Listar pedidos", mensagem)
    
    # Teste: Filtrar por status
    print_info("\nTestando filtro por status: Pendente")
    
    sucesso, response, erro = fazer_request(
        'GET',
        f"{ENDPOINTS['pedidos_compra']['base']}/",
        params={'status': 'Pendente'},
        headers=get_headers()
    )
    
    if sucesso and response.status_code == 200:
        data = response.json()
        contador.registrar_sucesso(f"Filtrar por status ({len(data.get('pedidos', []))} encontrados)")
    else:
        contador.registrar_falha("Filtrar por status", "Erro ao filtrar")
    
    return contador


def test_buscar_pedido_por_id():
    """Testa busca de pedido por ID"""
    print_separador("3. BUSCAR PEDIDO POR ID")
    
    contador = TestResultCounter()
    
    if not PEDIDO_COMPRA_ID:
        contador.registrar_falha("Buscar pedido", "ID não disponível")
        return contador
    
    print_info(f"Testando GET /api/pedidos-compra/{PEDIDO_COMPRA_ID}")
    
    sucesso, response, erro = fazer_request(
        'GET',
        f"{ENDPOINTS['pedidos_compra']['base']}/{PEDIDO_COMPRA_ID}",
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Buscar pedido", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        contador.registrar_sucesso("Buscar pedido por ID")
        print_json(data.get('pedido'), "Pedido Encontrado")
    else:
        contador.registrar_falha("Buscar pedido", mensagem)
    
    return contador


def test_adicionar_item():
    """Testa adição de item ao pedido"""
    print_separador("4. ADICIONAR ITEM AO PEDIDO")
    
    contador = TestResultCounter()
    
    if not PEDIDO_COMPRA_ID or not PRODUTO_ID:
        contador.registrar_falha("Adicionar item", "Pedido ou produto não disponível")
        return contador
    
    print_info(f"Testando POST /api/pedidos-compra/{PEDIDO_COMPRA_ID}/itens")
    
    item_data = {
        "itens": [
            {
                "id_produto": PRODUTO_ID,
                "quantidade": 10,
                "preco_custo_unitario": 47.50
            }
        ]
    }
    
    print_json(item_data, "Dados do Item")
    
    sucesso, response, erro = fazer_request(
        'POST',
        f"{ENDPOINTS['pedidos_compra']['base']}/{PEDIDO_COMPRA_ID}/itens",
        json=item_data,
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Adicionar item", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)  # Status 200, não 201
    
    if valido and data.get('success'):
        contador.registrar_sucesso("Adicionar item")
        print_json(data.get('item'), "Item Adicionado")
    else:
        contador.registrar_falha("Adicionar item", mensagem)
    
    return contador


def test_atualizar_status():
    """Testa atualização de status do pedido"""
    print_separador("5. ATUALIZAR STATUS DO PEDIDO")
    
    contador = TestResultCounter()
    
    if not PEDIDO_COMPRA_ID:
        contador.registrar_falha("Atualizar status", "Pedido não disponível")
        return contador
    
    print_info(f"Testando PUT /api/pedidos-compra/{PEDIDO_COMPRA_ID}/status")
    
    # Mudar para Aprovado
    status_data = {"status": "Aprovado"}
    print_json(status_data, "Novo Status")
    
    sucesso, response, erro = fazer_request(
        'PUT',
        f"{ENDPOINTS['pedidos_compra']['base']}/{PEDIDO_COMPRA_ID}/status",
        json=status_data,
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Atualizar status", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        contador.registrar_sucesso("Atualizar status para Aprovado")
        
        # Mudar para Enviado
        print_info("\nAtualizando para Enviado")
        
        sucesso, response, erro = fazer_request(
            'PUT',
            f"{ENDPOINTS['pedidos_compra']['base']}/{PEDIDO_COMPRA_ID}/status",
            json={"status": "Enviado"},
            headers=get_headers()
        )
        
        if sucesso and response.status_code == 200:
            contador.registrar_sucesso("Atualizar status para Enviado")
        else:
            contador.registrar_falha("Atualizar para Enviado", "Erro ao atualizar")
    else:
        contador.registrar_falha("Atualizar status", mensagem)
    
    return contador


def test_receber_pedido():
    """Testa recebimento do pedido (INCREMENTA ESTOQUE)"""
    print_separador("6. RECEBER PEDIDO (⭐ ENTRADA NO ESTOQUE)")
    
    contador = TestResultCounter()
    
    if not PEDIDO_COMPRA_ID or not PRODUTO_ID:
        contador.registrar_falha("Receber pedido", "Pedido ou produto não disponível")
        return contador
    
    # Consultar estoque antes
    print_info(f"Consultando estoque do produto ANTES do recebimento...")
    
    sucesso, response, erro = fazer_request(
        'GET',
        f"{ENDPOINTS['produtos']['base']}/{PRODUTO_ID}"
    )
    
    estoque_antes = 0
    if sucesso and response.status_code == 200:
        estoque_antes = response.json()['produto']['estoque_atual']
        print_sucesso(f"Estoque atual: {estoque_antes} unidades")
    
    # Receber pedido
    print_info(f"\nTestando POST /api/pedidos-compra/{PEDIDO_COMPRA_ID}/receber")
    
    sucesso, response, erro = fazer_request(
        'POST',
        f"{ENDPOINTS['pedidos_compra']['base']}/{PEDIDO_COMPRA_ID}/receber",
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Receber pedido", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        contador.registrar_sucesso("Receber pedido")
        print_json(data.get('pedido'), "Pedido Recebido")
        
        # Verificar se o estoque foi incrementado
        print_info("\nVerificando se estoque foi incrementado...")
        
        sucesso, response, erro = fazer_request(
            'GET',
            f"{ENDPOINTS['produtos']['base']}/{PRODUTO_ID}"
        )
        
        if sucesso and response.status_code == 200:
            produto = response.json()['produto']
            estoque_depois = produto['estoque_atual']
            
            print(f"\n{'='*70}")
            print(f"📊 RESULTADO DA ENTRADA NO ESTOQUE:")
            print(f"{'='*70}")
            print(f"Estoque ANTES:  {estoque_antes} unidades")
            print(f"Estoque DEPOIS: {estoque_depois} unidades")
            print(f"Incremento:     {estoque_depois - estoque_antes} unidades")
            print(f"Novo custo médio: R$ {produto.get('preco', 0):.2f}")
            print(f"{'='*70}\n")
            
            if estoque_depois > estoque_antes:
                contador.registrar_sucesso("Estoque incrementado corretamente")
            else:
                contador.registrar_falha("Incremento de estoque", "Estoque não foi incrementado")
        else:
            contador.registrar_falha("Verificar estoque", "Erro ao consultar produto")
    else:
        contador.registrar_falha("Receber pedido", mensagem)
    
    return contador


def test_relatorio():
    """Testa geração de relatório"""
    print_separador("7. RELATÓRIO DE PEDIDOS DE COMPRA")
    
    contador = TestResultCounter()
    
    print_info("Testando GET /api/pedidos-compra/relatorio")
    
    sucesso, response, erro = fazer_request(
        'GET',
        ENDPOINTS['pedidos_compra']['relatorio'],
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Relatório", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        contador.registrar_sucesso("Relatório gerado")
        print_json(data.get('relatorio'), "Relatório")
    else:
        contador.registrar_falha("Relatório", mensagem)
    
    return contador


def run_all_pedido_compra_tests():
    """Executa todos os testes de pedidos de compra"""
    print("\n" + "📦"*35)
    print("   TESTES DE PEDIDOS DE COMPRA - API AutoPek")
    print("📦"*35 + "\n")
    
    # Verificar se API está online
    if not verificar_api_online(API_BASE_URL):
        print_erro(f"API não está online em {API_BASE_URL}")
        print_info("Certifique-se de executar: python app.py")
        return False
    
    print_sucesso(f"API está online em {API_BASE_URL}\n")
    
    # Setup: fazer login e criar dados de teste
    if not setup():
        return False
    
    # Executar testes na ordem
    contador_criar = test_criar_pedido_compra()
    contador_listar = test_listar_pedidos_compra()
    contador_buscar = test_buscar_pedido_por_id()
    contador_item = test_adicionar_item()
    contador_status = test_atualizar_status()
    contador_receber = test_receber_pedido()
    contador_relatorio = test_relatorio()
    
    # Consolidar resultados
    resultado_geral = TestResultCounter()
    
    for contador in [contador_criar, contador_listar, contador_buscar,
                     contador_item, contador_status, contador_receber, 
                     contador_relatorio]:
        if isinstance(contador, TestResultCounter):
            resultado_geral.total += contador.total
            resultado_geral.sucessos += contador.sucessos
            resultado_geral.falhas += contador.falhas
            resultado_geral.erros.extend(contador.erros)
    
    # Imprimir resumo geral
    sucesso = resultado_geral.imprimir_resumo()
    
    return sucesso


if __name__ == '__main__':
    sucesso = run_all_pedido_compra_tests()
    sys.exit(0 if sucesso else 1)
