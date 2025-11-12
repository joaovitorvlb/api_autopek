#!/usr/bin/env python3
"""
Testes de Pedidos de Venda
Testa: criar, listar, adicionar itens, confirmar, calcular lucro, cancelar, relatórios
"""

import sys
sys.path.append('.')

from tests.config import *
from tests.utils import *


# Variáveis para armazenar IDs criados nos testes
CLIENTE_ID = None
PRODUTO_ID = None
PEDIDO_VENDA_ID = None


def setup():
    """Preparação: fazer login, criar cliente e produto de teste"""
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
    
    # Buscar ou criar cliente de teste
    global CLIENTE_ID
    print_info("Buscando/criando cliente de teste...")
    
    # Tentar buscar clientes existentes
    sucesso, response, erro = fazer_request(
        'GET',
        f"{ENDPOINTS['clientes']['base']}/",
        headers=get_headers()
    )
    
    if sucesso and response.status_code == 200:
        data = response.json()
        clientes = data.get('clientes', [])
        if clientes and len(clientes) > 0:
            # Usar o primeiro cliente disponível
            CLIENTE_ID = clientes[0]['id_cliente']
            print_sucesso(f"Usando cliente existente (ID: {CLIENTE_ID})")
        else:
            # Criar novo cliente
            sucesso, response, erro = fazer_request(
                'POST',
                ENDPOINTS['clientes']['register'],
                json={
                    "nome": "Cliente Teste Pedido Venda",
                    "email": "cliente_teste_venda@teste.com",
                    "senha": "senha123",
                    "cpf": "52998224725",  # CPF válido
                    "endereco": "Rua Teste, 123",
                    "telefone": "(11) 98765-4321"
                }
            )
            
            if sucesso and response.status_code == 201:
                CLIENTE_ID = response.json()['id_cliente']
                print_sucesso(f"Cliente criado (ID: {CLIENTE_ID})")
            else:
                print_erro("Falha ao criar cliente de teste")
                return False
    else:
        print_erro("Falha ao buscar clientes")
        return False
    
    # Criar produto de teste com estoque
    global PRODUTO_ID
    print_info("Criando produto de teste com estoque...")
    
    sucesso, response, erro = fazer_request(
        'POST',
        f"{ENDPOINTS['produtos']['base']}/",
        json={
            "nome": "Produto Teste Pedido Venda",
            "descricao": "Produto para teste de pedido de venda",
            "preco": 100.00,
            "estoque": 50  # Estoque suficiente para os testes
        },
        headers=get_headers()
    )
    
    if sucesso and response.status_code == 201:
        PRODUTO_ID = response.json()['produto']['id_produto']
        print_sucesso(f"Produto criado (ID: {PRODUTO_ID}) com estoque de 50 unidades")
    else:
        print_erro("Falha ao criar produto de teste")
        return False
    
    print()
    return True


def test_criar_pedido_venda():
    """Testa criação de pedido de venda"""
    global PEDIDO_VENDA_ID
    
    print_separador("1. CRIAR PEDIDO DE VENDA")
    
    contador = TestResultCounter()
    
    if not CLIENTE_ID or not PRODUTO_ID:
        contador.registrar_falha("Criar pedido", "Cliente ou produto não disponível")
        return contador
    
    print_info("Testando POST /api/pedidos-venda/")
    
    pedido_data = {
        "id_cliente": CLIENTE_ID,
        "itens": [
            {
                "id_produto": PRODUTO_ID,
                "quantidade": 5,
                "preco_venda_unitario": 120.00
            }
        ]
    }
    
    print_json(pedido_data, "Dados do Pedido")
    
    sucesso, response, erro = fazer_request(
        'POST',
        f"{ENDPOINTS['pedidos_venda']['base']}/",
        json=pedido_data,
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Criar pedido", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 201)
    
    if valido and data.get('success'):
        pedido = data.get('pedido')
        PEDIDO_VENDA_ID = pedido.get('id_pedido_venda')
        contador.registrar_sucesso(f"Criar pedido (ID: {PEDIDO_VENDA_ID})")
        print_json(pedido, "Pedido Criado")
    else:
        contador.registrar_falha("Criar pedido", mensagem)
    
    # Teste: Criar pedido sem estoque suficiente
    print_info("\nTestando criação com estoque insuficiente")
    
    sucesso, response, erro = fazer_request(
        'POST',
        f"{ENDPOINTS['pedidos_venda']['base']}/",
        json={
            "id_cliente": CLIENTE_ID,
            "itens": [{"id_produto": PRODUTO_ID, "quantidade": 1000, "preco_venda_unitario": 100.00}]
        },
        headers=get_headers()
    )
    
    if sucesso and response.status_code == 400:
        contador.registrar_sucesso("Validação: estoque insuficiente rejeitado")
    else:
        contador.registrar_falha("Validação: estoque insuficiente", "Deveria retornar 400")
    
    return contador


def test_listar_pedidos_venda():
    """Testa listagem de pedidos de venda"""
    print_separador("2. LISTAR PEDIDOS DE VENDA")
    
    contador = TestResultCounter()
    
    print_info("Testando GET /api/pedidos-venda/")
    
    sucesso, response, erro = fazer_request(
        'GET',
        f"{ENDPOINTS['pedidos_venda']['base']}/",
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
    
    return contador


def test_buscar_pedido_por_id():
    """Testa busca de pedido por ID"""
    print_separador("3. BUSCAR PEDIDO POR ID")
    
    contador = TestResultCounter()
    
    if not PEDIDO_VENDA_ID:
        contador.registrar_falha("Buscar pedido", "ID não disponível")
        return contador
    
    print_info(f"Testando GET /api/pedidos-venda/{PEDIDO_VENDA_ID}")
    
    sucesso, response, erro = fazer_request(
        'GET',
        f"{ENDPOINTS['pedidos_venda']['base']}/{PEDIDO_VENDA_ID}",
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
    
    if not PEDIDO_VENDA_ID or not PRODUTO_ID:
        contador.registrar_falha("Adicionar item", "Pedido ou produto não disponível")
        return contador
    
    print_info(f"Testando POST /api/pedidos-venda/{PEDIDO_VENDA_ID}/itens")
    
    item_data = {
        "itens": [{
            "id_produto": PRODUTO_ID,
            "quantidade": 3,
            "preco_venda_unitario": 125.00
        }]
    }
    
    print_json(item_data, "Dados do Item")
    
    sucesso, response, erro = fazer_request(
        'POST',
        f"{ENDPOINTS['pedidos_venda']['base']}/{PEDIDO_VENDA_ID}/itens",
        json=item_data,
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Adicionar item", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        contador.registrar_sucesso("Adicionar item")
        print_json(data, "Resposta")
    else:
        contador.registrar_falha("Adicionar item", mensagem)
    
    return contador


def test_atualizar_status():
    """Testa atualização de status do pedido"""
    print_separador("5. ATUALIZAR STATUS DO PEDIDO")
    
    contador = TestResultCounter()
    
    if not PEDIDO_VENDA_ID:
        contador.registrar_falha("Atualizar status", "Pedido não disponível")
        return contador
    
    print_info(f"Testando PUT /api/pedidos-venda/{PEDIDO_VENDA_ID}/status")
    
    status_data = {"status": "Preparando"}
    print_json(status_data, "Novo Status")
    
    sucesso, response, erro = fazer_request(
        'PUT',
        f"{ENDPOINTS['pedidos_venda']['base']}/{PEDIDO_VENDA_ID}/status",
        json=status_data,
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Atualizar status", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        contador.registrar_sucesso("Atualizar status para Preparando")
    else:
        contador.registrar_falha("Atualizar status", mensagem)
    
    return contador


def test_confirmar_pedido():
    """Testa confirmação do pedido (DECREMENTA ESTOQUE)"""
    print_separador("6. CONFIRMAR PEDIDO (⭐ SAÍDA DO ESTOQUE)")
    
    contador = TestResultCounter()
    
    if not PEDIDO_VENDA_ID or not PRODUTO_ID:
        contador.registrar_falha("Confirmar pedido", "Pedido ou produto não disponível")
        return contador
    
    # Consultar estoque antes
    print_info(f"Consultando estoque do produto ANTES da confirmação...")
    
    sucesso, response, erro = fazer_request(
        'GET',
        f"{ENDPOINTS['produtos']['base']}/{PRODUTO_ID}"
    )
    
    estoque_antes = 0
    if sucesso and response.status_code == 200:
        estoque_antes = response.json()['produto']['estoque_atual']
        print_sucesso(f"Estoque atual: {estoque_antes} unidades")
    
    # Confirmar pedido
    print_info(f"\nTestando POST /api/pedidos-venda/{PEDIDO_VENDA_ID}/confirmar")
    
    sucesso, response, erro = fazer_request(
        'POST',
        f"{ENDPOINTS['pedidos_venda']['base']}/{PEDIDO_VENDA_ID}/confirmar",
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Confirmar pedido", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        contador.registrar_sucesso("Confirmar pedido")
        print_json(data.get('pedido'), "Pedido Confirmado")
        
        # Verificar se o estoque foi decrementado
        print_info("\nVerificando se estoque foi decrementado...")
        
        sucesso, response, erro = fazer_request(
            'GET',
            f"{ENDPOINTS['produtos']['base']}/{PRODUTO_ID}"
        )
        
        if sucesso and response.status_code == 200:
            estoque_depois = response.json()['produto']['estoque_atual']
            
            print(f"\n{'='*70}")
            print(f"📊 RESULTADO DA SAÍDA DO ESTOQUE:")
            print(f"{'='*70}")
            print(f"Estoque ANTES:  {estoque_antes} unidades")
            print(f"Estoque DEPOIS: {estoque_depois} unidades")
            print(f"Decremento:     {estoque_antes - estoque_depois} unidades")
            print(f"{'='*70}\n")
            
            if estoque_depois < estoque_antes:
                contador.registrar_sucesso("Estoque decrementado corretamente")
            else:
                contador.registrar_falha("Decremento de estoque", "Estoque não foi decrementado")
        else:
            contador.registrar_falha("Verificar estoque", "Erro ao consultar produto")
    else:
        contador.registrar_falha("Confirmar pedido", mensagem)
    
    return contador


def test_calcular_lucro():
    """Testa cálculo de lucro do pedido"""
    print_separador("7. CALCULAR LUCRO DO PEDIDO")
    
    contador = TestResultCounter()
    
    if not PEDIDO_VENDA_ID:
        contador.registrar_falha("Calcular lucro", "Pedido não disponível")
        return contador
    
    print_info(f"Testando GET /api/pedidos-venda/{PEDIDO_VENDA_ID}/lucro")
    
    sucesso, response, erro = fazer_request(
        'GET',
        f"{ENDPOINTS['pedidos_venda']['base']}/{PEDIDO_VENDA_ID}/lucro",
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Calcular lucro", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        lucro = data.get('lucro')
        
        print(f"\n{'='*70}")
        print(f"💰 ANÁLISE DE LUCRO:")
        print(f"{'='*70}")
        print(f"Valor de Venda:   R$ {lucro.get('valor_venda', 0):.2f}")
        print(f"Custo Total:      R$ {lucro.get('custo_total', 0):.2f}")
        print(f"Lucro Bruto:      R$ {lucro.get('lucro_bruto', 0):.2f}")
        print(f"Margem:           {lucro.get('margem_percentual', 0):.2f}%")
        print(f"{'='*70}\n")
        
        contador.registrar_sucesso("Calcular lucro")
    else:
        contador.registrar_falha("Calcular lucro", mensagem)
    
    return contador


def test_relatorio():
    """Testa geração de relatório"""
    print_separador("8. RELATÓRIO DE PEDIDOS DE VENDA")
    
    contador = TestResultCounter()
    
    print_info("Testando GET /api/pedidos-venda/relatorio")
    
    sucesso, response, erro = fazer_request(
        'GET',
        ENDPOINTS['pedidos_venda']['relatorio'],
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


def test_produtos_mais_vendidos():
    """Testa relatório de produtos mais vendidos"""
    print_separador("9. PRODUTOS MAIS VENDIDOS")
    
    contador = TestResultCounter()
    
    print_info("Testando GET /api/pedidos-venda/produtos-mais-vendidos")
    
    sucesso, response, erro = fazer_request(
        'GET',
        ENDPOINTS['pedidos_venda']['produtos_mais_vendidos'],
        params={'limite': 10},
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Produtos mais vendidos", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        produtos = data.get('produtos', [])
        contador.registrar_sucesso(f"Produtos mais vendidos ({len(produtos)} encontrados)")
        
        if produtos:
            print_json(produtos, "Top Produtos")
    else:
        contador.registrar_falha("Produtos mais vendidos", mensagem)
    
    return contador


def run_all_pedido_venda_tests():
    """Executa todos os testes de pedidos de venda"""
    print("\n" + "🛒"*35)
    print("   TESTES DE PEDIDOS DE VENDA - API AutoPek")
    print("🛒"*35 + "\n")
    
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
    contador_criar = test_criar_pedido_venda()
    contador_listar = test_listar_pedidos_venda()
    contador_buscar = test_buscar_pedido_por_id()
    contador_item = test_adicionar_item()
    contador_status = test_atualizar_status()
    contador_confirmar = test_confirmar_pedido()
    contador_lucro = test_calcular_lucro()
    contador_relatorio = test_relatorio()
    contador_mais_vendidos = test_produtos_mais_vendidos()
    
    # Consolidar resultados
    resultado_geral = TestResultCounter()
    
    for contador in [contador_criar, contador_listar, contador_buscar,
                     contador_item, contador_status, contador_confirmar,
                     contador_lucro, contador_relatorio, contador_mais_vendidos]:
        if isinstance(contador, TestResultCounter):
            resultado_geral.total += contador.total
            resultado_geral.sucessos += contador.sucessos
            resultado_geral.falhas += contador.falhas
            resultado_geral.erros.extend(contador.erros)
    
    # Imprimir resumo geral
    sucesso = resultado_geral.imprimir_resumo()
    
    return sucesso


if __name__ == '__main__':
    sucesso = run_all_pedido_venda_tests()
    sys.exit(0 if sucesso else 1)
