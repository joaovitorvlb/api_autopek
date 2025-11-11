"""
DAO para usuario - Apenas operações de banco de dados
Nova modelagem: Usuario é a base para Cliente e Funcionario (herança)
Regras de negócio devem estar no módulo service
"""
from .db import get_cursor

class UsuarioDAO:
    """DAO para operações CRUD na tabela usuario"""
    
    def listar_todos(self, apenas_ativos=True):
        """Retorna todos os usuários"""
        with get_cursor() as cur:
            if apenas_ativos:
                cur.execute("""
                    SELECT u.id_usuario, u.nome, u.email, u.telefone, 
                           u.ativo, u.data_criacao, u.id_nivel_acesso,
                           na.nome as nivel_acesso_nome
                    FROM usuario u
                    JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                    WHERE u.ativo = 1
                    ORDER BY u.nome
                """)
            else:
                cur.execute("""
                    SELECT u.id_usuario, u.nome, u.email, u.telefone, 
                           u.ativo, u.data_criacao, u.id_nivel_acesso,
                           na.nome as nivel_acesso_nome
                    FROM usuario u
                    JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                    ORDER BY u.nome
                """)
            return cur.fetchall()
    
    def buscar_por_id(self, id_usuario):
        """Busca usuário por ID (sem senha para segurança)"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT u.id_usuario, u.nome, u.email, u.telefone,
                       u.ativo, u.data_criacao, u.id_nivel_acesso,
                       na.nome as nivel_acesso_nome
                FROM usuario u
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE u.id_usuario = %s
            """, (id_usuario,))
            return cur.fetchone()
    
    def buscar_por_id_com_senha(self, id_usuario):
        """Busca usuário por ID incluindo senha_hash (usar apenas para autenticação)"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT u.id_usuario, u.nome, u.email, u.senha_hash, u.telefone,
                       u.ativo, u.data_criacao, u.id_nivel_acesso,
                       na.nome as nivel_acesso_nome
                FROM usuario u
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE u.id_usuario = %s
            """, (id_usuario,))
            return cur.fetchone()
    
    def buscar_por_email(self, email):
        """Busca usuário por email (sem senha)"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT u.id_usuario, u.nome, u.email, u.telefone,
                       u.ativo, u.data_criacao, u.id_nivel_acesso,
                       na.nome as nivel_acesso_nome
                FROM usuario u
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE u.email = %s
            """, (email,))
            return cur.fetchone()
    
    def buscar_por_email_com_senha(self, email):
        """Busca usuário por email incluindo senha_hash (usar apenas para autenticação)"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT u.id_usuario, u.nome, u.email, u.senha_hash, u.telefone,
                       u.ativo, u.data_criacao, u.id_nivel_acesso,
                       na.nome as nivel_acesso_nome
                FROM usuario u
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE u.email = %s
            """, (email,))
            return cur.fetchone()
    
    def inserir(self, nome, email, senha_hash, telefone, id_nivel_acesso, ativo=1):
        """Insere novo usuário"""
        with get_cursor() as cur:
            cur.execute("""
                INSERT INTO usuario (nome, email, senha_hash, telefone, ativo, id_nivel_acesso)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nome, email, senha_hash, telefone, ativo, id_nivel_acesso))
            return cur.lastrowid
    
    def atualizar(self, id_usuario, nome=None, email=None, telefone=None, id_nivel_acesso=None):
        """Atualiza dados do usuário (exceto senha)"""
        campos = []
        valores = []
        
        if nome is not None:
            campos.append("nome = %s")
            valores.append(nome)
        if email is not None:
            campos.append("email = %s")
            valores.append(email)
        if telefone is not None:
            campos.append("telefone = %s")
            valores.append(telefone)
        if id_nivel_acesso is not None:
            campos.append("id_nivel_acesso = %s")
            valores.append(id_nivel_acesso)
        
        if not campos:
            return 0
        
        valores.append(id_usuario)
        query = f"UPDATE usuario SET {', '.join(campos)} WHERE id_usuario = %s"
        
        with get_cursor() as cur:
            cur.execute(query, valores)
            return cur.rowcount
    
    def atualizar_senha(self, id_usuario, nova_senha_hash):
        """Atualiza apenas a senha do usuário"""
        with get_cursor() as cur:
            cur.execute(
                "UPDATE usuario SET senha_hash = %s WHERE id_usuario = %s",
                (nova_senha_hash, id_usuario)
            )
            return cur.rowcount
    
    def ativar_desativar(self, id_usuario, ativo):
        """Ativa ou desativa usuário (soft delete)"""
        with get_cursor() as cur:
            cur.execute(
                "UPDATE usuario SET ativo = %s WHERE id_usuario = %s",
                (1 if ativo else 0, id_usuario)
            )
            return cur.rowcount
    
    def deletar(self, id_usuario):
        """Deleta usuário permanentemente (cuidado: CASCADE para Cliente/Funcionario)"""
        with get_cursor() as cur:
            cur.execute("DELETE FROM usuario WHERE id_usuario = %s", (id_usuario,))
            return cur.rowcount
    
    def verificar_email_existe(self, email, excluir_id=None):
        """Verifica se email já existe (útil para validação)"""
        with get_cursor() as cur:
            if excluir_id:
                cur.execute(
                    "SELECT COUNT(*) as total FROM usuario WHERE email = %s AND id_usuario != %s",
                    (email, excluir_id)
                )
            else:
                cur.execute(
                    "SELECT COUNT(*) as total FROM usuario WHERE email = %s",
                    (email,)
                )
            result = cur.fetchone()
            return result['total'] > 0
    
    def buscar_usuarios_por_nivel(self, id_nivel_acesso, apenas_ativos=True):
        """Busca todos os usuários de um determinado nível de acesso"""
        with get_cursor() as cur:
            if apenas_ativos:
                cur.execute("""
                    SELECT u.id_usuario, u.nome, u.email, u.telefone,
                           u.ativo, u.data_criacao, u.id_nivel_acesso,
                           na.nome as nivel_acesso_nome
                    FROM usuario u
                    JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                    WHERE u.id_nivel_acesso = %s AND u.ativo = 1
                    ORDER BY u.nome
                """, (id_nivel_acesso,))
            else:
                cur.execute("""
                    SELECT u.id_usuario, u.nome, u.email, u.telefone,
                           u.ativo, u.data_criacao, u.id_nivel_acesso,
                           na.nome as nivel_acesso_nome
                    FROM usuario u
                    JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                    WHERE u.id_nivel_acesso = %s
                    ORDER BY u.nome
                """, (id_nivel_acesso,))
            return cur.fetchall()
