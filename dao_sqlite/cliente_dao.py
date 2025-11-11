"""
DAO para Cliente - Apenas operações de banco de dados (SQLite)
Nova modelagem: Cliente herda de Usuario (1-para-1 via id_usuario)
Regras de negócio devem estar no módulo service
"""
from .db import get_cursor

class ClienteDAO:
    """DAO para operações CRUD na tabela Cliente"""
    
    def listar_todos(self, apenas_ativos=True):
        """Retorna todos os clientes com dados do usuário
        
        Args:
            apenas_ativos (bool): Se True, retorna apenas clientes ativos. Default: True
        """
        with get_cursor() as cur:
            if apenas_ativos:
                cur.execute("""
                    SELECT c.id_cliente, c.id_usuario, c.cpf, c.endereco,
                           u.nome, u.email, u.telefone, u.ativo, u.data_criacao,
                           na.nome as nivel_acesso_nome
                    FROM Cliente c
                    JOIN usuario u ON c.id_usuario = u.id_usuario
                    JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                    WHERE u.ativo = 1
                    ORDER BY u.nome
                """)
            else:
                cur.execute("""
                    SELECT c.id_cliente, c.id_usuario, c.cpf, c.endereco,
                           u.nome, u.email, u.telefone, u.ativo, u.data_criacao,
                           na.nome as nivel_acesso_nome
                    FROM Cliente c
                    JOIN usuario u ON c.id_usuario = u.id_usuario
                    JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                    ORDER BY u.nome
                """)
            return [dict(row) for row in cur.fetchall()]
    
    def buscar_por_id(self, id_cliente):
        """Busca cliente por ID"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT c.id_cliente, c.id_usuario, c.cpf, c.endereco,
                       u.nome, u.email, u.telefone, u.ativo, u.data_criacao,
                       na.nome as nivel_acesso_nome
                FROM Cliente c
                JOIN usuario u ON c.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE c.id_cliente = ?
            """, (id_cliente,))
            row = cur.fetchone()
            return dict(row) if row else None
    
    def buscar_por_usuario(self, id_usuario):
        """Busca cliente pelo ID do usuário"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT c.id_cliente, c.id_usuario, c.cpf, c.endereco,
                       u.nome, u.email, u.telefone, u.ativo, u.data_criacao,
                       na.nome as nivel_acesso_nome
                FROM Cliente c
                JOIN usuario u ON c.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE c.id_usuario = ?
            """, (id_usuario,))
            row = cur.fetchone()
            return dict(row) if row else None
    
    def buscar_por_cpf(self, cpf):
        """Busca cliente por CPF"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT c.id_cliente, c.id_usuario, c.cpf, c.endereco,
                       u.nome, u.email, u.telefone, u.ativo, u.data_criacao,
                       na.nome as nivel_acesso_nome
                FROM Cliente c
                JOIN usuario u ON c.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE c.cpf = ?
            """, (cpf,))
            row = cur.fetchone()
            return dict(row) if row else None
    
    def buscar_por_email(self, email):
        """Busca cliente por email (via usuario)"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT c.id_cliente, c.id_usuario, c.cpf, c.endereco,
                       u.nome, u.email, u.telefone, u.ativo, u.data_criacao,
                       na.nome as nivel_acesso_nome
                FROM Cliente c
                JOIN usuario u ON c.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE u.email = ?
            """, (email,))
            row = cur.fetchone()
            return dict(row) if row else None
    
    def inserir(self, id_usuario, cpf, endereco=None):
        """Insere novo cliente vinculado a um usuário"""
        with get_cursor() as cur:
            cur.execute("""
                INSERT INTO Cliente (id_usuario, cpf, endereco)
                VALUES (?, ?, ?)
            """, (id_usuario, cpf, endereco))
            return cur.lastrowid
    
    def atualizar(self, id_cliente, cpf=None, endereco=None):
        """Atualiza dados específicos do cliente (nome, email, telefone são atualizados via usuario)"""
        campos = []
        valores = []
        
        if cpf is not None:
            campos.append("cpf = ?")
            valores.append(cpf)
        if endereco is not None:
            campos.append("endereco = ?")
            valores.append(endereco)
        
        if not campos:
            return 0
        
        valores.append(id_cliente)
        query = f"UPDATE Cliente SET {', '.join(campos)} WHERE id_cliente = ?"
        
        with get_cursor() as cur:
            cur.execute(query, valores)
            return cur.rowcount
    
    def deletar(self, id_cliente):
        """Deleta cliente (o usuario associado não é deletado automaticamente)"""
        with get_cursor() as cur:
            cur.execute("DELETE FROM Cliente WHERE id_cliente = ?", (id_cliente,))
            return cur.rowcount
    
    def verificar_cpf_existe(self, cpf, excluir_id=None):
        """Verifica se CPF já existe (útil para validação)"""
        with get_cursor() as cur:
            if excluir_id:
                cur.execute(
                    "SELECT COUNT(*) as total FROM Cliente WHERE cpf = ? AND id_cliente != ?",
                    (cpf, excluir_id)
                )
            else:
                cur.execute(
                    "SELECT COUNT(*) as total FROM Cliente WHERE cpf = ?",
                    (cpf,)
                )
            result = cur.fetchone()
            return dict(result)['total'] > 0
    
    def verificar_usuario_ja_cliente(self, id_usuario):
        """Verifica se um usuário já está cadastrado como cliente"""
        with get_cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) as total FROM Cliente WHERE id_usuario = ?",
                (id_usuario,)
            )
            result = cur.fetchone()
            return dict(result)['total'] > 0
    
    def listar_clientes_ativos(self):
        """Retorna apenas clientes com usuários ativos"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT c.id_cliente, c.id_usuario, c.cpf, c.endereco,
                       u.nome, u.email, u.telefone, u.ativo, u.data_criacao,
                       na.nome as nivel_acesso_nome
                FROM Cliente c
                JOIN usuario u ON c.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE u.ativo = 1
                ORDER BY u.nome
            """)
            return [dict(row) for row in cur.fetchall()]
