from dataclasses import dataclass
from typing import Optional

@dataclass
class Usuario:
    id_usuario: int
    nome: str
    email: str
    senha_hash: str
    id_nivel_acesso: int
    telefone: Optional[str] = None
    ativo: bool = True
    # Atributos do nível de acesso (quando fazer JOIN)
    nivel_acesso_nome: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> 'Usuario':
        """
        Cria uma instância de Usuario a partir de um dicionário
        """
        return Usuario(
            id_usuario=data['id_usuario'],
            nome=data['nome'],
            email=data['email'],
            senha_hash=data['senha_hash'],
            id_nivel_acesso=data['id_nivel_acesso'],
            telefone=data.get('telefone'),
            ativo=data.get('ativo', True),
            nivel_acesso_nome=data.get('nivel_acesso_nome')
        )

    def to_dict(self) -> dict:
        """
        Converte a instância de Usuario para um dicionário
        """
        return {
            'id_usuario': self.id_usuario,
            'nome': self.nome,
            'email': self.email,
            'id_nivel_acesso': self.id_nivel_acesso,
            'telefone': self.telefone,
            'ativo': self.ativo,
            'nivel_acesso_nome': self.nivel_acesso_nome
        }
