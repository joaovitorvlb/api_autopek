from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Fornecedor:
    id_fornecedor: int
    razao_social: str
    nome_fantasia: str
    cnpj: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    ativo: bool = True
    data_criacao: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> 'Fornecedor':
        """
        Cria uma instância de Fornecedor a partir de um dicionário
        """
        return Fornecedor(
            id_fornecedor=data['id_fornecedor'],
            razao_social=data['razao_social'],
            nome_fantasia=data['nome_fantasia'],
            cnpj=data['cnpj'],
            email=data.get('email'),
            telefone=data.get('telefone'),
            endereco=data.get('endereco'),
            ativo=bool(data.get('ativo', 1)),
            data_criacao=data.get('data_criacao')
        )

    def to_dict(self) -> dict:
        """
        Converte a instância de Fornecedor para um dicionário
        """
        return {
            'id_fornecedor': self.id_fornecedor,
            'razao_social': self.razao_social,
            'nome_fantasia': self.nome_fantasia,
            'cnpj': self.cnpj,
            'email': self.email,
            'telefone': self.telefone,
            'endereco': self.endereco,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao
        }
