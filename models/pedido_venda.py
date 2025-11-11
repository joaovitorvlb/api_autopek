from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

@dataclass
class PedidoVenda:
    id_pedido_venda: int
    id_cliente: int
    id_funcionario: Optional[int]
    data_pedido: date
    status: str  # Pendente, Confirmado, Separado, Enviado, Entregue, Cancelado
    total: Decimal
    # Atributos de outras tabelas (quando fazer JOIN)
    cliente_nome: Optional[str] = None
    funcionario_nome: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> 'PedidoVenda':
        """
        Cria uma instância de PedidoVenda a partir de um dicionário
        """
        # Converte o total para Decimal se existir
        if 'total' in data and data['total'] is not None:
            data['total'] = Decimal(str(data['total']))
        
        # Converte a data do pedido para date se existir
        if 'data_pedido' in data and data['data_pedido'] is not None:
            if isinstance(data['data_pedido'], str):
                data['data_pedido'] = date.fromisoformat(data['data_pedido'])

        return PedidoVenda(
            id_pedido_venda=data['id_pedido_venda'],
            id_cliente=data['id_cliente'],
            id_funcionario=data.get('id_funcionario'),
            data_pedido=data['data_pedido'],
            status=data.get('status', 'Pendente'),
            total=data['total'],
            cliente_nome=data.get('cliente_nome'),
            funcionario_nome=data.get('funcionario_nome')
        )

    def to_dict(self) -> dict:
        """
        Converte a instância de PedidoVenda para um dicionário
        """
        return {
            'id_pedido_venda': self.id_pedido_venda,
            'id_cliente': self.id_cliente,
            'id_funcionario': self.id_funcionario,
            'data_pedido': self.data_pedido.isoformat() if self.data_pedido is not None else None,
            'status': self.status,
            'total': float(self.total) if self.total is not None else None,
            'cliente_nome': self.cliente_nome,
            'funcionario_nome': self.funcionario_nome
        }
