class Cliente:
    def __init__(self, id_cliente, id_usuario, cpf, endereco=None):
        self.id_cliente = id_cliente
        self.id_usuario = id_usuario
        self.cpf = cpf
        self.endereco = endereco
        # Atributos do usuário (quando fazer JOIN)
        self.nome = None
        self.email = None
        self.telefone = None
        self.ativo = None

    def __repr__(self):
        return (
            f"<Cliente id={self.id_cliente} id_usuario={self.id_usuario} cpf='{self.cpf}' "
            f"nome='{self.nome}' endereco='{self.endereco}'>"
        )

    def to_dict(self):
        return {
            'id_cliente': self.id_cliente,
            'id_usuario': self.id_usuario,
            'cpf': self.cpf,
            'endereco': self.endereco,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'ativo': self.ativo,
        }
