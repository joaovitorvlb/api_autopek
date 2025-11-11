from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

@dataclass
class PedidoCompra:
    id_pedido_compra: int
    id_fornecedor: int
    id_funcionario: int
    data_pedido: date
    status: str  # Pendente, Recebido, Cancelado
    total: Decimal
    # Atributos de outras tabelas (quando fazer JOIN)
    fornecedor_nome: Optional[str] = None
    funcionario_nome: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> 'PedidoCompra':
        """
        Cria uma instância de PedidoCompra a partir de um dicionário
        """
        # Converte o total para Decimal se existir
        if 'total' in data and data['total'] is not None:
            data['total'] = Decimal(str(data['total']))
        
        # Converte a data do pedido para date se existir
        if 'data_pedido' in data and data['data_pedido'] is not None:
            if isinstance(data['data_pedido'], str):
                data['data_pedido'] = date.fromisoformat(data['data_pedido'])

        return PedidoCompra(
            id_pedido_compra=data['id_pedido_compra'],
            id_fornecedor=data['id_fornecedor'],
            id_funcionario=data['id_funcionario'],
            data_pedido=data['data_pedido'],
            status=data.get('status', 'Pendente'),
            total=data['total'],
            fornecedor_nome=data.get('fornecedor_nome'),
            funcionario_nome=data.get('funcionario_nome')
        )

    def to_dict(self) -> dict:
        """
        Converte a instância de PedidoCompra para um dicionário
        """
        return {
            'id_pedido_compra': self.id_pedido_compra,
            'id_fornecedor': self.id_fornecedor,
            'id_funcionario': self.id_funcionario,
            'data_pedido': self.data_pedido.isoformat() if self.data_pedido is not None else None,
            'status': self.status,
            'total': float(self.total) if self.total is not None else None,
            'fornecedor_nome': self.fornecedor_nome,
            'funcionario_nome': self.funcionario_nome
        }
