from .db import get_cursor

class NivelAcessoDAO:
    """
    DAO para operações na tabela nivel_acesso (SQLite).
    Contém apenas operações de banco de dados.
    Lógicas de autorização devem ficar no módulo service.
    """
    
    def __init__(self):
        pass

    def listar_niveis_acesso(self):
        """
        Lista todos os níveis de acesso disponíveis.
        """
        with get_cursor() as cur:
            cur.execute("SELECT id_nivel_acesso, nome FROM nivel_acesso ORDER BY nome")
            return [dict(row) for row in cur.fetchall()]

    def buscar_nivel_acesso(self, id_nivel_acesso):
        """
        Busca um nível de acesso específico por ID.
        """
        with get_cursor() as cur:
            cur.execute(
                "SELECT id_nivel_acesso, nome FROM nivel_acesso WHERE id_nivel_acesso = ?",
                (id_nivel_acesso,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def buscar_nivel_acesso_por_nome(self, nome):
        """
        Busca um nível de acesso específico por nome.
        """
        with get_cursor() as cur:
            cur.execute(
                "SELECT id_nivel_acesso, nome FROM nivel_acesso WHERE nome = ?",
                (nome,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def inserir(self, nome):
        """
        Insere um novo nível de acesso.
        Retorna o id_nivel_acesso gerado.
        """
        with get_cursor() as cur:
            cur.execute(
                "INSERT INTO nivel_acesso (nome) VALUES (?)",
                (nome,)
            )
            return cur.lastrowid

    def atualizar(self, id_nivel_acesso, nome):
        """
        Atualiza o nome de um nível de acesso.
        """
        with get_cursor() as cur:
            cur.execute(
                "UPDATE nivel_acesso SET nome = ? WHERE id_nivel_acesso = ?",
                (nome, id_nivel_acesso)
            )

    def deletar(self, id_nivel_acesso):
        """
        Deleta um nível de acesso.
        CUIDADO: irá falhar se houver usuários associados devido à FK.
        """
        with get_cursor() as cur:
            cur.execute("DELETE FROM nivel_acesso WHERE id_nivel_acesso = ?", (id_nivel_acesso,))

    def contar_usuarios(self, id_nivel_acesso):
        """
        Conta quantos usuários estão associados a este nível de acesso.
        Útil para validar antes de deletar.
        """
        with get_cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) as count FROM usuario WHERE id_nivel_acesso = ?",
                (id_nivel_acesso,)
            )
            result = cur.fetchone()
            return dict(result)['count']

    def verificar_nome_existe(self, nome, id_nivel_acesso_excluir=None):
        """
        Verifica se já existe um nível de acesso com o nome fornecido.
        Se id_nivel_acesso_excluir for fornecido, ignora esse registro na verificação.
        Útil para validar duplicatas em atualizações.
        """
        with get_cursor() as cur:
            if id_nivel_acesso_excluir:
                cur.execute(
                    "SELECT COUNT(*) as count FROM nivel_acesso WHERE nome = ? AND id_nivel_acesso != ?",
                    (nome, id_nivel_acesso_excluir)
                )
            else:
                cur.execute(
                    "SELECT COUNT(*) as count FROM nivel_acesso WHERE nome = ?",
                    (nome,)
                )
            result = cur.fetchone()
            return dict(result)['count'] > 0
