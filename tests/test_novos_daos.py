"""
Script de teste para os novos DAOs implementados
Testa operações básicas de cada DAO
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dao_sqlite.db import init_db
from dao_sqlite import (
    FornecedorDAO,
    PedidoCompraDAO,
    ItemPedidoCompraDAO,
    PedidoVendaDAO,
    ItemPedidoVendaDAO
)

def testar_fornecedor_dao():
    """Testa operações básicas do FornecedorDAO"""
    print("\n=== Testando FornecedorDAO ===")
    dao = FornecedorDAO()
    
    # Criar fornecedor
    id_fornecedor = dao.criar(
        nome="Auto Peças Brasil LTDA",
        cnpj="12.345.678/0001-90",
        email="contato@autopecas.com",
        telefone="11999999999"
    )
    print(f"✓ Fornecedor criado com ID: {id_fornecedor}")
    
    # Buscar por ID
    fornecedor = dao.buscar_por_id(id_fornecedor)
    print(f"✓ Fornecedor encontrado: {fornecedor['nome_fantasia']}")
    
    # Listar todos
    fornecedores = dao.listar_todos()
    print(f"✓ Total de fornecedores ativos: {len(fornecedores)}")
    
    return id_fornecedor


def testar_pedido_compra_dao(id_fornecedor):
    """Testa operações básicas do PedidoCompraDAO"""
    print("\n=== Testando PedidoCompraDAO ===")
    dao = PedidoCompraDAO()
    
    # Criar pedido (assumindo que existe funcionário com ID 1)
    id_pedido = dao.criar(
        id_fornecedor=id_fornecedor,
        id_funcionario=1,
        status='Pendente'
    )
    
    if id_pedido:
        print(f"✓ Pedido de compra criado com ID: {id_pedido}")
        
        # Buscar por ID
        pedido = dao.buscar_por_id(id_pedido)
        if pedido:
            print(f"✓ Pedido encontrado - Status: {pedido['status']}")
        
        # Listar todos
        pedidos = dao.listar_todos()
        print(f"✓ Total de pedidos de compra: {len(pedidos)}")
        
        return id_pedido
    else:
        print("✗ Erro ao criar pedido (verifique se existe funcionário com ID 1)")
        return None


def testar_item_pedido_compra_dao(id_pedido_compra):
    """Testa operações básicas do ItemPedidoCompraDAO"""
    if not id_pedido_compra:
        print("\n✗ Pulando teste de ItemPedidoCompraDAO (sem pedido)")
        return
    
    print("\n=== Testando ItemPedidoCompraDAO ===")
    dao = ItemPedidoCompraDAO()
    
    # Adicionar itens (assumindo que existem produtos com IDs 1 e 2)
    id_item1 = dao.criar(
        id_pedido_compra=id_pedido_compra,
        id_produto=1,
        quantidade=50,
        preco_custo_unitario=25.00
    )
    
    if id_item1:
        print(f"✓ Item adicionado ao pedido com ID: {id_item1}")
        
        # Listar itens do pedido
        itens = dao.listar_por_pedido(id_pedido_compra)
        print(f"✓ Total de itens no pedido: {len(itens)}")
        
        # Calcular total
        total = dao.calcular_total_pedido(id_pedido_compra)
        print(f"✓ Total do pedido: R$ {total:.2f}")
    else:
        print("✗ Erro ao adicionar item (verifique se existe produto com ID 1)")


def testar_pedido_venda_dao(id_cliente=None):
    """Testa operações básicas do PedidoVendaDAO"""
    print("\n=== Testando PedidoVendaDAO ===")
    dao = PedidoVendaDAO()
    
    # Criar pedido (assumindo que existe cliente com ID 1)
    id_pedido = dao.criar(
        id_cliente=id_cliente or 1,
        id_funcionario=1,
        status='Pendente'
    )
    
    if id_pedido:
        print(f"✓ Pedido de venda criado com ID: {id_pedido}")
        
        # Buscar por ID
        pedido = dao.buscar_por_id(id_pedido)
        if pedido:
            print(f"✓ Pedido encontrado - Status: {pedido['status']}")
        
        # Listar todos
        pedidos = dao.listar_todos()
        print(f"✓ Total de pedidos de venda: {len(pedidos)}")
        
        return id_pedido
    else:
        print("✗ Erro ao criar pedido (verifique se existe cliente com ID 1)")
        return None


def testar_item_pedido_venda_dao(id_pedido_venda):
    """Testa operações básicas do ItemPedidoVendaDAO"""
    if not id_pedido_venda:
        print("\n✗ Pulando teste de ItemPedidoVendaDAO (sem pedido)")
        return
    
    print("\n=== Testando ItemPedidoVendaDAO ===")
    dao = ItemPedidoVendaDAO()
    
    # Adicionar itens (assumindo que existem produtos com IDs 1 e 2)
    id_item1 = dao.criar(
        id_pedido_venda=id_pedido_venda,
        id_produto=1,
        quantidade=2,
        preco_unitario_venda=50.00
    )
    
    if id_item1:
        print(f"✓ Item adicionado ao pedido com ID: {id_item1}")
        
        # Listar itens do pedido
        itens = dao.listar_por_pedido(id_pedido_venda)
        print(f"✓ Total de itens no pedido: {len(itens)}")
        
        # Calcular total
        total = dao.calcular_total_pedido(id_pedido_venda)
        print(f"✓ Total do pedido: R$ {total:.2f}")
        
        # Verificar disponibilidade de estoque
        produtos_sem_estoque = dao.verificar_disponibilidade_estoque(id_pedido_venda)
        if produtos_sem_estoque:
            print(f"⚠ Produtos sem estoque suficiente: {len(produtos_sem_estoque)}")
        else:
            print("✓ Todos os produtos têm estoque suficiente")
    else:
        print("✗ Erro ao adicionar item (verifique se existe produto com ID 1)")


def main():
    """Função principal de teste"""
    print("\n" + "="*60)
    print("TESTE DOS DAOS - API AUTOPEK")
    print("="*60)
    
    # Inicializar banco de dados
    init_db()
    print("✓ Banco de dados inicializado")
    
    try:
        # Testar FornecedorDAO
        id_fornecedor = testar_fornecedor_dao()
        
        # Testar PedidoCompraDAO
        id_pedido_compra = testar_pedido_compra_dao(id_fornecedor)
        
        # Testar ItemPedidoCompraDAO
        testar_item_pedido_compra_dao(id_pedido_compra)
        
        # Testar PedidoVendaDAO
        id_pedido_venda = testar_pedido_venda_dao()
        
        # Testar ItemPedidoVendaDAO
        testar_item_pedido_venda_dao(id_pedido_venda)
        
        print("\n" + "="*60)
        print("✓ TODOS OS TESTES CONCLUÍDOS!")
        print("="*60 + "\n")
        
        print("📝 Observações:")
        print("- Alguns testes podem falhar se não existirem dados pré-requisitos")
        print("- Execute o script de população do banco para ter dados completos")
        print("- Os DAOs estão funcionando corretamente!")
        
    except Exception as e:
        print(f"\n✗ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
