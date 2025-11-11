#!/usr/bin/env python3
"""
Script para Popular Produtos com Imagens Reais
Adiciona produtos baseados nas imagens da pasta docs/
"""

import requests
import json
import os
import sys
from pathlib import Path

# Configuração da API
API_BASE_URL = "http://localhost:5000"
API_AUTH_LOGIN = f"{API_BASE_URL}/api/auth/login"
API_PRODUTOS = f"{API_BASE_URL}/api/produtos"

# Credenciais de administrador
ADMIN_EMAIL = "admin@autopeck.com"
ADMIN_SENHA = "admin123"

# Token JWT
TOKEN = None

# Caminho das imagens (relativo ao workspace)
DOCS_DIR = Path(__file__).parent.parent / "docs"


def print_separador(titulo=""):
    """Imprime separador visual"""
    print("\n" + "="*70)
    if titulo:
        print(f"  {titulo}")
        print("="*70)


def print_sucesso(msg):
    print(f"✅ {msg}")


def print_erro(msg):
    print(f"❌ {msg}")


def print_info(msg):
    print(f"ℹ️  {msg}")


def fazer_login():
    """Faz login e obtém token JWT"""
    global TOKEN
    
    print_info("Fazendo login como administrador...")
    
    response = requests.post(
        API_AUTH_LOGIN,
        json={"email": ADMIN_EMAIL, "senha": ADMIN_SENHA}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            TOKEN = data['token']
            print_sucesso(f"Login realizado: {data['usuario']['nome']}")
            return True
    
    print_erro("Falha no login")
    return False


def get_headers():
    """Retorna headers com autenticação"""
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }


def criar_produto_com_imagem(produto_data, imagem_path):
    """
    Cria produto e faz upload da imagem
    
    Args:
        produto_data: Dicionário com dados do produto
        imagem_path: Caminho da imagem (relativo ao docs/)
    """
    print_info(f"Criando produto: {produto_data['nome']}")
    
    # Caminho completo da imagem
    caminho_completo = DOCS_DIR / imagem_path
    
    if not caminho_completo.exists():
        print_erro(f"Imagem não encontrada: {caminho_completo}")
        return None
    
    # Preparar dados do form-data
    files = {
        'imagem': (imagem_path, open(caminho_completo, 'rb'), 'image/png')
    }
    
    data = {
        'nome': produto_data['nome'],
        'descricao': produto_data['descricao'],
        'preco': str(produto_data['preco']),
        'estoque': str(produto_data['estoque'])
    }
    
    # Se tem SKU customizado, adicionar
    if 'sku' in produto_data:
        data['sku'] = produto_data['sku']
    
    try:
        response = requests.post(
            f"{API_PRODUTOS}/",
            data=data,
            files=files,
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        
        # Fechar arquivo
        files['imagem'][1].close()
        
        if response.status_code == 201:
            data_response = response.json()
            if data_response.get('success'):
                produto = data_response['produto']
                print_sucesso(f"Produto criado - ID: {produto['id_produto']} | SKU: {produto['sku']}")
                print_info(f"   Nome: {produto['nome']}")
                print_info(f"   Preço: R$ {produto['preco_venda']:.2f}")
                print_info(f"   Estoque: {produto['estoque_atual']} unidades")
                print_info(f"   Imagem processada: {produto.get('nome_imagem', 'N/A')}")
                
                # Mostrar URLs das imagens geradas
                imagens = produto.get('imagens', {})
                if imagens:
                    print_info(f"   📸 Thumbnail: {imagens.get('thumbnail')}")
                    print_info(f"   📸 Medium: {imagens.get('medium')}")
                    print_info(f"   📸 Large: {imagens.get('large')}")
                    print_info(f"   📸 Original: {imagens.get('original')}")
                
                return produto
        
        try:
            error = response.json()
            print_erro(f"Erro ao criar produto: {error.get('message', 'Desconhecido')}")
        except:
            print_erro(f"Erro HTTP {response.status_code}")
    
    except Exception as e:
        print_erro(f"Erro na requisição: {str(e)}")
    
    return None


def main():
    """Função principal"""
    print_separador("🚗 POPULAR PRODUTOS COM IMAGENS - API AutoPek 🚗")
    
    # Verificar se API está online
    try:
        response = requests.get(API_BASE_URL, timeout=5)
        if response.status_code != 200:
            print_erro("API não está respondendo")
            return False
    except:
        print_erro(f"Não foi possível conectar à API em {API_BASE_URL}")
        print_info("Certifique-se de executar: python app.py")
        return False
    
    print_sucesso(f"API está online: {API_BASE_URL}")
    
    # Fazer login
    if not fazer_login():
        return False
    
    print_separador("ADICIONANDO PRODUTOS")
    
    # Definir produtos baseados nas imagens encontradas
    produtos = [
        {
            "nome": "Carburador Brosol 3E Opala 6cc Gasolina 2º Estágio Vácuo",
            "descricao": """Carburador Brosol modelo 3E para Opala 6 cilindros, 
            ideal para motores a gasolina. Sistema de 2º estágio a vácuo para 
            melhor performance e economia. Compatível com motores 4.1 e 250S.""",
            "preco": 1250.00,
            "estoque": 8,
            "sku": "CARB-BROSOL-3E-OPALA6",
            "imagem": "CarburadorBrosol3eOpala6ccGasolina2ºEstágioVácuo.png"
        },
        {
            "nome": "Injeção Fueltech FT450 + Chicote 3 Metros Motor Dianteiro",
            "descricao": """Módulo de injeção eletrônica programável FuelTech FT450. 
            Inclui chicote de 3 metros para instalação em motor dianteiro. 
            Controle avançado de ignição e injeção. Ideal para preparações 
            turbo e aspiradas de alta performance.""",
            "preco": 4890.00,
            "estoque": 5,
            "sku": "INJ-FUELTECH-FT450-3M",
            "imagem": "InjeçãoFueltechFt450-Chicote3MetrosMotorDianteiro.png"
        },
        {
            "nome": "Coletor de Admissão Opala 6cc Weber IDF 40-44",
            "descricao": """Coletor de admissão para Opala 6 cilindros, preparado 
            para carburadores duplos Weber IDF 40 ou 44. Alumínio fundido de alta 
            qualidade. Aumenta consideravelmente a potência do motor. 
            Excelente para preparações aspiradas.""",
            "preco": 2150.00,
            "estoque": 12,
            "sku": "COL-ADM-OPALA6-WEBER",
            "imagem": "ColetorAdmissãoOpala6ccWeberIdf40-44.png"
        },
        {
            "nome": "Turbina Garrett .70 ZR6064",
            "descricao": """Turbina Garrett modelo ZR6064 com A/R .70. 
            Turbocompressor de alto fluxo para motores de 2.0 a 4.0 litros. 
            Suporta até 650hp. Construção em ferro fundido e eixo balanceado 
            digitalmente. Ideal para preparações street e competição.""",
            "preco": 6200.00,
            "estoque": 3,
            "sku": "TURB-GARRETT-ZR6064-70",
            "imagem": "turbina.70 ZR6064.png"
        }
    ]
    
    produtos_criados = []
    
    for produto in produtos:
        # Extrair imagem do dicionário
        imagem = produto.pop('imagem')
        
        # Criar produto
        produto_criado = criar_produto_com_imagem(produto, imagem)
        
        if produto_criado:
            produtos_criados.append(produto_criado)
        
        print()  # Linha em branco entre produtos
    
    # Resumo
    print_separador("RESUMO")
    
    print(f"\n📊 Estatísticas:")
    print(f"   Produtos tentados: {len(produtos)}")
    print(f"   ✅ Criados com sucesso: {len(produtos_criados)}")
    print(f"   ❌ Falhas: {len(produtos) - len(produtos_criados)}")
    
    if produtos_criados:
        valor_total_estoque = sum(
            p['preco_venda'] * p['estoque_atual'] 
            for p in produtos_criados
        )
        estoque_total = sum(p['estoque_atual'] for p in produtos_criados)
        
        print(f"\n💰 Valores:")
        print(f"   Estoque total: {estoque_total} peças")
        print(f"   Valor em estoque: R$ {valor_total_estoque:,.2f}")
        
        print(f"\n📦 Produtos Adicionados:")
        for p in produtos_criados:
            print(f"   • {p['nome'][:50]}... (ID: {p['id_produto']})")
    
    print("\n" + "="*70)
    
    if len(produtos_criados) == len(produtos):
        print_sucesso("\n🎉 Todos os produtos foram adicionados com sucesso!\n")
        return True
    else:
        print_info(f"\n⚠️  {len(produtos) - len(produtos_criados)} produto(s) não foram adicionados.\n")
        return False


if __name__ == '__main__':
    try:
        sucesso = main()
        sys.exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print_erro(f"\nErro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
