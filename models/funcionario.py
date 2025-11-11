from datetime import date
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class Funcionario:
    id_funcionario: int
    id_usuario: int
    cargo: Optional[str] = None
    salario: Optional[Decimal] = None
    data_contratacao: Optional[date] = None
    # Atributos do usuário (quando fazer JOIN)
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    ativo: Optional[bool] = None

    @staticmethod
    def from_dict(data: dict) -> 'Funcionario':
        """
        Cria uma instância de Funcionário a partir de um dicionário
        """
        # Converte o salário para Decimal se existir
        if 'salario' in data and data['salario'] is not None:
            data['salario'] = Decimal(str(data['salario']))
        
        # Converte a data de contratação para date se existir
        if 'data_contratacao' in data and data['data_contratacao'] is not None:
            if isinstance(data['data_contratacao'], str):
                data['data_contratacao'] = date.fromisoformat(data['data_contratacao'])

        return Funcionario(
            id_funcionario=data['id_funcionario'],
            id_usuario=data['id_usuario'],
            nome=data.get('nome'),
            cargo=data.get('cargo'),
            salario=data.get('salario'),
            data_contratacao=data.get('data_contratacao'),
            email=data.get('email'),
            telefone=data.get('telefone'),
            ativo=data.get('ativo')
        )

    def to_dict(self) -> dict:
        """
        Converte a instância de Funcionário para um dicionário
        """
        return {
            'id_funcionario': self.id_funcionario,
            'id_usuario': self.id_usuario,
            'nome': self.nome,
            'cargo': self.cargo,
            'salario': float(self.salario) if self.salario is not None else None,
            'data_contratacao': self.data_contratacao.isoformat() if self.data_contratacao is not None else None,
            'email': self.email,
            'telefone': self.telefone,
            'ativo': self.ativo
        }