"""
DAO para Cliente - Apenas operações de banco de dados
Nova modelagem: Cliente herda de Usuario (1-para-1 via id_usuario)
Regras de negócio devem estar no módulo service
"""
from .db_pythonanywhere import get_cursor

class ClienteDAO:
    """DAO para operações CRUD na tabela Cliente"""
    
    def listar_todos(self):
        """Retorna todos os clientes com dados do usuário"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT c.id_cliente, c.id_usuario, c.data_cadastro, c.origem_cadastro,
                       u.nome, u.cpf, u.email, u.telefone, u.ativo, u.data_criacao,
                       u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       na.nome as nivel_acesso_nome
                FROM Cliente c
                JOIN usuario u ON c.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                ORDER BY u.nome
            """)
            return cur.fetchall()
    
    def buscar_por_id(self, id_cliente):
        """Busca cliente por ID"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT c.id_cliente, c.id_usuario, c.data_cadastro, c.origem_cadastro,
                       u.nome, u.cpf, u.email, u.telefone, u.ativo, u.data_criacao,
                       u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       na.nome as nivel_acesso_nome
                FROM Cliente c
                JOIN usuario u ON c.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE c.id_cliente = %s
            """, (id_cliente,))
            return cur.fetchone()
    
    def buscar_por_usuario(self, id_usuario):
        """Busca cliente pelo ID do usuário"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT c.id_cliente, c.id_usuario, c.data_cadastro, c.origem_cadastro,
                       u.nome, u.cpf, u.email, u.telefone, u.ativo, u.data_criacao,
                       u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       na.nome as nivel_acesso_nome
                FROM Cliente c
                JOIN usuario u ON c.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE c.id_usuario = %s
            """, (id_usuario,))
            return cur.fetchone()
    
    def buscar_por_cpf(self, cpf):
        """Busca cliente por CPF (agora CPF está na tabela usuario)"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT c.id_cliente, c.id_usuario, c.data_cadastro, c.origem_cadastro,
                       u.nome, u.cpf, u.email, u.telefone, u.ativo, u.data_criacao,
                       u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       na.nome as nivel_acesso_nome
                FROM Cliente c
                JOIN usuario u ON c.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE u.cpf = %s
            """, (cpf,))
            return cur.fetchone()
    
    def buscar_por_email(self, email):
        """Busca cliente por email (via usuario)"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT c.id_cliente, c.id_usuario, c.data_cadastro, c.origem_cadastro,
                       u.nome, u.cpf, u.email, u.telefone, u.ativo, u.data_criacao,
                       u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       na.nome as nivel_acesso_nome
                FROM Cliente c
                JOIN usuario u ON c.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE u.email = %s
            """, (email,))
            return cur.fetchone()
    
    def inserir(self, id_usuario, origem_cadastro='loja_fisica'):
        """Insere novo cliente vinculado a um usuário"""
        with get_cursor() as cur:
            cur.execute("""
                INSERT INTO Cliente (id_usuario, data_cadastro, origem_cadastro)
                VALUES (%s, NOW(), %s)
            """, (id_usuario, origem_cadastro))
            return cur.lastrowid
    
    def atualizar(self, id_cliente, origem_cadastro=None):
        """Atualiza dados específicos do cliente (nome, cpf, email, telefone, endereço são atualizados via usuario)"""
        campos = []
        valores = []
        
        if origem_cadastro is not None:
            campos.append("origem_cadastro = %s")
            valores.append(origem_cadastro)
        
        if not campos:
            return 0
        
        valores.append(id_cliente)
        query = f"UPDATE Cliente SET {', '.join(campos)} WHERE id_cliente = %s"
        
        with get_cursor() as cur:
            cur.execute(query, valores)
            return cur.rowcount
    
    def deletar(self, id_cliente):
        """Deleta cliente (o usuario associado não é deletado automaticamente)"""
        with get_cursor() as cur:
            cur.execute("DELETE FROM Cliente WHERE id_cliente = %s", (id_cliente,))
            return cur.rowcount
    
    def verificar_usuario_ja_cliente(self, id_usuario):
        """Verifica se um usuário já está cadastrado como cliente"""
        with get_cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) as total FROM Cliente WHERE id_usuario = %s",
                (id_usuario,)
            )
            result = cur.fetchone()
            return result['total'] > 0
    
    def listar_clientes_ativos(self):
        """Retorna apenas clientes com usuários ativos"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT c.id_cliente, c.id_usuario, c.data_cadastro, c.origem_cadastro,
                       u.nome, u.cpf, u.email, u.telefone, u.ativo, u.data_criacao,
                       u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       na.nome as nivel_acesso_nome
                FROM Cliente c
                JOIN usuario u ON c.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE u.ativo = 1
                ORDER BY u.nome
            """)
            return cur.fetchall()
    
    def listar_por_origem_cadastro(self, origem_cadastro):
        """Retorna clientes filtrados por origem de cadastro"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT c.id_cliente, c.id_usuario, c.data_cadastro, c.origem_cadastro,
                       u.nome, u.cpf, u.email, u.telefone, u.ativo, u.data_criacao,
                       u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       na.nome as nivel_acesso_nome
                FROM Cliente c
                JOIN usuario u ON c.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE c.origem_cadastro = %s
                ORDER BY c.data_cadastro DESC
            """, (origem_cadastro,))
            return cur.fetchall()
    
    def obter_estatisticas_por_origem(self):
        """Retorna estatísticas de clientes por origem de cadastro"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT 
                    c.origem_cadastro,
                    COUNT(c.id_cliente) as total_clientes,
                    COUNT(DISTINCT CASE WHEN u.ativo = 1 THEN c.id_cliente END) as clientes_ativos,
                    MIN(c.data_cadastro) as primeira_data,
                    MAX(c.data_cadastro) as ultima_data
                FROM Cliente c
                JOIN usuario u ON c.id_usuario = u.id_usuario
                GROUP BY c.origem_cadastro
                ORDER BY total_clientes DESC
            """)
            return cur.fetchall()
