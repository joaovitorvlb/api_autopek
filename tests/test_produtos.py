#!/usr/bin/env python3
"""
Testes de Produtos
Testa: criar, listar, buscar, atualizar, deletar produtos
"""

import sys
sys.path.append('.')

from tests.config import *
from tests.utils import *


# Variável para armazenar ID do produto criado nos testes
PRODUTO_ID = None


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


def test_listar_produtos():
    """Testa listagem de produtos (rota pública)"""
    print_separador("1. LISTAR PRODUTOS")
    
    contador = TestResultCounter()
    
    print_info("Testando GET /api/produtos/")
    
    sucesso, response, erro = fazer_request('GET', f"{ENDPOINTS['produtos']['base']}/")
    
    if not sucesso:
        contador.registrar_falha("Listar produtos", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        produtos = data.get('produtos', [])
        contador.registrar_sucesso(f"Listar produtos ({len(produtos)} encontrados)")
        
        if produtos:
            print_json(produtos[0], "Exemplo de Produto")
    else:
        contador.registrar_falha("Listar produtos", mensagem)
    
    return contador


def test_criar_produto():
    """Testa criação de produto"""
    global PRODUTO_ID
    
    print_separador("2. CRIAR PRODUTO (SEM IMAGEM)")
    
    contador = TestResultCounter()
    
    if not get_token():
        contador.registrar_falha("Criar produto", "Token não disponível")
        return contador
    
    print_info("Testando POST /api/produtos/ (JSON)")
    
    produto_data = {
        "nome": "Filtro de Óleo Teste Automatizado",
        "descricao": "Produto criado via teste automatizado",
        "preco": 49.90,
        "estoque": 50
    }
    
    print_json(produto_data, "Dados do Produto")
    
    sucesso, response, erro = fazer_request(
        'POST',
        f"{ENDPOINTS['produtos']['base']}/",
        json=produto_data,
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Criar produto", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 201)
    
    if valido and data.get('success'):
        produto = data.get('produto')
        PRODUTO_ID = produto.get('id_produto')
        contador.registrar_sucesso(f"Criar produto (ID: {PRODUTO_ID})")
        print_json(produto, "Produto Criado")
    else:
        contador.registrar_falha("Criar produto", mensagem)
    
    # Teste: Criar produto sem nome
    print_info("\nTestando criação sem nome (deve falhar)")
    
    sucesso, response, erro = fazer_request(
        'POST',
        f"{ENDPOINTS['produtos']['base']}/",
        json={"preco": 10, "estoque": 5},
        headers=get_headers()
    )
    
    if sucesso and response.status_code == 400:
        contador.registrar_sucesso("Validação: produto sem nome rejeitado")
    else:
        contador.registrar_falha("Validação: produto sem nome", "Deveria retornar 400")
    
    return contador


def test_criar_produto_com_imagem():
    """Testa criação de produto COM imagem"""
    global PRODUTO_ID
    
    print_separador("2B. CRIAR PRODUTO COM IMAGEM")
    
    contador = TestResultCounter()
    
    if not get_token():
        contador.registrar_falha("Criar produto com imagem", "Token não disponível")
        return contador
    
    print_info("Testando POST /api/produtos/ (multipart/form-data)")
    
    # Buscar uma imagem de teste na pasta docs/
    from pathlib import Path
    docs_dir = Path('docs')
    imagens = list(docs_dir.glob('*.png'))
    
    if not imagens:
        print_info("⚠️  Nenhuma imagem encontrada em docs/ - pulando teste")
        return contador
    
    imagem_path = imagens[0]
    print_info(f"Usando imagem: {imagem_path.name}")
    
    # Preparar dados
    produto_data = {
        'nome': 'Produto com Imagem Teste',
        'descricao': 'Produto criado via teste com upload de imagem',
        'preco': '199.90',
        'estoque': '25'
    }
    
    print_json(produto_data, "Dados do Produto")
    print_info(f"Arquivo: {imagem_path.name} ({imagem_path.stat().st_size / 1024:.2f} KB)")
    
    # Fazer upload
    try:
        with open(imagem_path, 'rb') as img_file:
            files = {
                'imagem': (imagem_path.name, img_file, 'image/png')
            }
            
            response = requests.post(
                f"{ENDPOINTS['produtos']['base']}/",
                data=produto_data,
                files=files,
                headers={"Authorization": f"Bearer {get_token()}"}
            )
        
        valido, mensagem, data = validar_response_success(response, 201)
        
        if valido and data.get('success'):
            produto = data.get('produto')
            PRODUTO_ID = produto.get('id_produto')
            
            contador.registrar_sucesso(f"Criar produto com imagem (ID: {PRODUTO_ID})")
            
            # Mostrar estrutura do JSON de retorno
            print("\n" + "="*70)
            print("📋 ESTRUTURA DO JSON DE RETORNO:")
            print("="*70)
            print_json(data, "Response Completo")
            
            print("\n" + "="*70)
            print("📸 IMAGENS GERADAS:")
            print("="*70)
            imagens = produto.get('imagens', {})
            if imagens:
                print(f"✅ Thumbnail (150x150): {imagens.get('thumbnail')}")
                print(f"✅ Medium (400x400):   {imagens.get('medium')}")
                print(f"✅ Large (800x800):    {imagens.get('large')}")
                print(f"\n📝 Nome base armazenado: {produto.get('nome_imagem')}")
            
            print("\n" + "="*70)
            print("📝 EXPLICAÇÃO DA REQUISIÇÃO:")
            print("="*70)
            print("""
A requisição utiliza multipart/form-data para enviar arquivo + dados:

MÉTODO: POST /api/produtos/
HEADERS:
  - Authorization: Bearer {token}
  - Content-Type: multipart/form-data (automático)

BODY (form-data):
  - nome: string (obrigatório)
  - descricao: string (opcional)
  - preco: string (obrigatório) - enviado como string!
  - estoque: string (obrigatório) - enviado como string!
  - imagem: file (opcional) - PNG, JPG ou JPEG

PROCESSAMENTO:
1. API recebe arquivo e dados
2. Cria produto no banco (gera ID)
3. Processa imagem em 3 resoluções:
   - Thumbnail: 150x150px
   - Medium: 400x400px
   - Large: 800x800px
4. Salva em: static/images/produtos/Produto_{id}_{uuid}_{resolução}.png
5. Atualiza campo 'nome_imagem' no banco
6. Retorna produto com URLs das imagens

PADRÃO DE NOME: Produto_{id}_{uuid}_{resolução}.png
Exemplo: Produto_1_5b65ee75_thumbnail.png
            """)
            
        else:
            contador.registrar_falha("Criar produto com imagem", mensagem)
            
    except Exception as e:
        contador.registrar_falha("Criar produto com imagem", str(e))
    
    return contador


def test_buscar_produto_por_id():
    """Testa busca de produto por ID"""
    print_separador("3. BUSCAR PRODUTO POR ID")
    
    contador = TestResultCounter()
    
    if not PRODUTO_ID:
        contador.registrar_falha("Buscar produto por ID", "ID do produto não disponível")
        return contador
    
    print_info(f"Testando GET /api/produtos/{PRODUTO_ID}")
    
    sucesso, response, erro = fazer_request(
        'GET',
        f"{ENDPOINTS['produtos']['base']}/{PRODUTO_ID}"
    )
    
    if not sucesso:
        contador.registrar_falha("Buscar produto por ID", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        contador.registrar_sucesso("Buscar produto por ID")
        print_json(data.get('produto'), "Produto Encontrado")
    else:
        contador.registrar_falha("Buscar produto por ID", mensagem)
    
    # Teste: Buscar produto inexistente
    print_info("\nTestando busca de produto inexistente")
    
    sucesso, response, erro = fazer_request(
        'GET',
        f"{ENDPOINTS['produtos']['base']}/99999"
    )
    
    if sucesso and response.status_code == 404:
        contador.registrar_sucesso("Produto inexistente retorna 404")
    else:
        contador.registrar_falha("Produto inexistente", "Deveria retornar 404")
    
    return contador


def test_buscar_produtos_por_nome():
    """Testa busca de produtos por nome"""
    print_separador("4. BUSCAR PRODUTOS POR NOME")
    
    contador = TestResultCounter()
    
    print_info("Testando GET /api/produtos/buscar?nome=Filtro")
    
    sucesso, response, erro = fazer_request(
        'GET',
        ENDPOINTS['produtos']['buscar'],
        params={'nome': 'Filtro'}
    )
    
    if not sucesso:
        contador.registrar_falha("Buscar por nome", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        produtos = data.get('produtos', [])
        contador.registrar_sucesso(f"Buscar por nome ({len(produtos)} encontrados)")
        
        if produtos:
            print_json(produtos, "Produtos Encontrados")
    else:
        contador.registrar_falha("Buscar por nome", mensagem)
    
    return contador


def test_atualizar_produto():
    """Testa atualização de produto"""
    print_separador("5. ATUALIZAR PRODUTO")
    
    contador = TestResultCounter()
    
    if not PRODUTO_ID:
        contador.registrar_falha("Atualizar produto", "ID do produto não disponível")
        return contador
    
    if not get_token():
        contador.registrar_falha("Atualizar produto", "Token não disponível")
        return contador
    
    print_info(f"Testando PUT /api/produtos/{PRODUTO_ID}")
    
    update_data = {
        "nome": "Filtro de Óleo ATUALIZADO",
        "preco": 59.90
    }
    
    print_json(update_data, "Dados para Atualização")
    
    sucesso, response, erro = fazer_request(
        'PUT',
        f"{ENDPOINTS['produtos']['base']}/{PRODUTO_ID}",
        json=update_data,
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Atualizar produto", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        contador.registrar_sucesso("Atualizar produto")
        print_json(data.get('produto'), "Produto Atualizado")
    else:
        contador.registrar_falha("Atualizar produto", mensagem)
    
    return contador


def test_deletar_produto():
    """Testa exclusão de produto"""
    print_separador("6. DELETAR PRODUTO")
    
    contador = TestResultCounter()
    
    if not PRODUTO_ID:
        contador.registrar_falha("Deletar produto", "ID do produto não disponível")
        return contador
    
    if not get_token():
        contador.registrar_falha("Deletar produto", "Token não disponível")
        return contador
    
    print_info(f"Testando DELETE /api/produtos/{PRODUTO_ID}")
    
    sucesso, response, erro = fazer_request(
        'DELETE',
        f"{ENDPOINTS['produtos']['base']}/{PRODUTO_ID}",
        headers=get_headers()
    )
    
    if not sucesso:
        contador.registrar_falha("Deletar produto", erro)
        return contador
    
    valido, mensagem, data = validar_response_success(response, 200)
    
    if valido and data.get('success'):
        contador.registrar_sucesso("Deletar produto")
        
        # Verificar se foi deletado
        print_info("\nVerificando se produto foi realmente deletado")
        
        sucesso, response, erro = fazer_request(
            'GET',
            f"{ENDPOINTS['produtos']['base']}/{PRODUTO_ID}"
        )
        
        if sucesso and response.status_code == 404:
            contador.registrar_sucesso("Produto deletado com sucesso")
        else:
            contador.registrar_falha("Verificar deleção", "Produto ainda existe")
    else:
        contador.registrar_falha("Deletar produto", mensagem)
    
    return contador


def run_all_produto_tests():
    """Executa todos os testes de produtos"""
    print("\n" + "📦"*35)
    print("   TESTES DE PRODUTOS - API AutoPek")
    print("📦"*35 + "\n")
    
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
    contador_listar = test_listar_produtos()
    contador_criar = test_criar_produto()
    contador_criar_imagem = test_criar_produto_com_imagem()
    contador_buscar_id = test_buscar_produto_por_id()
    contador_buscar_nome = test_buscar_produtos_por_nome()
    contador_atualizar = test_atualizar_produto()
    contador_deletar = test_deletar_produto()
    
    # Consolidar resultados
    resultado_geral = TestResultCounter()
    
    for contador in [contador_listar, contador_criar, contador_criar_imagem,
                     contador_buscar_id, contador_buscar_nome, 
                     contador_atualizar, contador_deletar]:
        if isinstance(contador, TestResultCounter):
            resultado_geral.total += contador.total
            resultado_geral.sucessos += contador.sucessos
            resultado_geral.falhas += contador.falhas
            resultado_geral.erros.extend(contador.erros)
    
    # Imprimir resumo geral
    sucesso = resultado_geral.imprimir_resumo()
    
    return sucesso


if __name__ == '__main__':
    sucesso = run_all_produto_tests()
    sys.exit(0 if sucesso else 1)
