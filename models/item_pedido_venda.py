from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class ItemPedidoVenda:
    id_item_pedido_venda: int
    id_pedido_venda: int
    id_produto: int
    quantidade: int
    preco_unitario_venda: Decimal
    # Atributos de outras tabelas (quando fazer JOIN)
    produto_nome: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> 'ItemPedidoVenda':
        """
        Cria uma instância de ItemPedidoVenda a partir de um dicionário
        """
        # Converte o preço unitário para Decimal se existir
        if 'preco_unitario_venda' in data and data['preco_unitario_venda'] is not None:
            data['preco_unitario_venda'] = Decimal(str(data['preco_unitario_venda']))

        return ItemPedidoVenda(
            id_item_pedido_venda=data['id_item_pedido_venda'],
            id_pedido_venda=data['id_pedido_venda'],
            id_produto=data['id_produto'],
            quantidade=data['quantidade'],
            preco_unitario_venda=data['preco_unitario_venda'],
            produto_nome=data.get('produto_nome')
        )

    def to_dict(self) -> dict:
        """
        Converte a instância de ItemPedidoVenda para um dicionário
        """
        return {
            'id_item_pedido_venda': self.id_item_pedido_venda,
            'id_pedido_venda': self.id_pedido_venda,
            'id_produto': self.id_produto,
            'quantidade': self.quantidade,
            'preco_unitario_venda': float(self.preco_unitario_venda) if self.preco_unitario_venda is not None else None,
            'produto_nome': self.produto_nome
        }
