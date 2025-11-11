from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class ItemPedidoCompra:
    id_item_pedido_compra: int
    id_pedido_compra: int
    id_produto: int
    quantidade: int
    preco_unitario_compra: Decimal
    # Atributos de outras tabelas (quando fazer JOIN)
    produto_nome: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> 'ItemPedidoCompra':
        """
        Cria uma instância de ItemPedidoCompra a partir de um dicionário
        """
        # Converte o preço unitário para Decimal se existir
        if 'preco_unitario_compra' in data and data['preco_unitario_compra'] is not None:
            data['preco_unitario_compra'] = Decimal(str(data['preco_unitario_compra']))

        return ItemPedidoCompra(
            id_item_pedido_compra=data['id_item_pedido_compra'],
            id_pedido_compra=data['id_pedido_compra'],
            id_produto=data['id_produto'],
            quantidade=data['quantidade'],
            preco_unitario_compra=data['preco_unitario_compra'],
            produto_nome=data.get('produto_nome')
        )

    def to_dict(self) -> dict:
        """
        Converte a instância de ItemPedidoCompra para um dicionário
        """
        return {
            'id_item_pedido_compra': self.id_item_pedido_compra,
            'id_pedido_compra': self.id_pedido_compra,
            'id_produto': self.id_produto,
            'quantidade': self.quantidade,
            'preco_unitario_compra': float(self.preco_unitario_compra) if self.preco_unitario_compra is not None else None,
            'produto_nome': self.produto_nome
        }
