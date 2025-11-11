from dataclasses import dataclass

@dataclass
class NivelAcesso:
    id_nivel_acesso: int
    nome: str
    descricao: str = None

    @staticmethod
    def from_dict(data: dict) -> 'NivelAcesso':
        """
        Cria uma instância de NivelAcesso a partir de um dicionário
        """
        return NivelAcesso(
            id_nivel_acesso=data['id_nivel_acesso'],
            nome=data['nome'],
            descricao=data.get('descricao')
        )

    def to_dict(self) -> dict:
        """
        Converte a instância de NivelAcesso para um dicionário
        """
        return {
            'id_nivel_acesso': self.id_nivel_acesso,
            'nome': self.nome,
            'descricao': self.descricao
        }
