"""
DAO para usuario - Apenas operações de banco de dados
Nova modelagem: Usuario é a base para Cliente e Funcionario (herança)
Regras de negócio devem estar no módulo service
"""
from .db_pythonanywhere import get_cursor

class UsuarioDAO:
    """DAO para operações CRUD na tabela usuario"""
    
    def listar_todos(self, apenas_ativos=True):
        """Retorna todos os usuários"""
        with get_cursor() as cur:
            if apenas_ativos:
                cur.execute("""
                    SELECT u.id_usuario, u.nome, u.cpf, u.email, u.telefone, 
                           u.ativo, u.data_criacao, u.data_nascimento, u.ultimo_login,
                           u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                           u.id_nivel_acesso, na.nome as nivel_acesso_nome
                    FROM usuario u
                    JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                    WHERE u.ativo = 1
                    ORDER BY u.nome
                """)
            else:
                cur.execute("""
                    SELECT u.id_usuario, u.nome, u.cpf, u.email, u.telefone, 
                           u.ativo, u.data_criacao, u.data_nascimento, u.ultimo_login,
                           u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                           u.id_nivel_acesso, na.nome as nivel_acesso_nome
                    FROM usuario u
                    JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                    ORDER BY u.nome
                """)
            return cur.fetchall()
    
    def buscar_por_id(self, id_usuario):
        """Busca usuário por ID (sem senha para segurança)"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT u.id_usuario, u.nome, u.cpf, u.email, u.telefone,
                       u.ativo, u.data_criacao, u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       u.id_nivel_acesso, na.nome as nivel_acesso_nome
                FROM usuario u
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE u.id_usuario = %s
            """, (id_usuario,))
            return cur.fetchone()
    
    def buscar_por_id_com_senha(self, id_usuario):
        """Busca usuário por ID incluindo senha_hash (usar apenas para autenticação)"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT u.id_usuario, u.nome, u.cpf, u.email, u.senha_hash, u.telefone,
                       u.ativo, u.data_criacao, u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       u.id_nivel_acesso, na.nome as nivel_acesso_nome
                FROM usuario u
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE u.id_usuario = %s
            """, (id_usuario,))
            return cur.fetchone()
    
    def buscar_por_email(self, email):
        """Busca usuário por email (sem senha)"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT u.id_usuario, u.nome, u.cpf, u.email, u.telefone,
                       u.ativo, u.data_criacao, u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       u.id_nivel_acesso, na.nome as nivel_acesso_nome
                FROM usuario u
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE u.email = %s
            """, (email,))
            return cur.fetchone()
    
    def buscar_por_email_com_senha(self, email):
        """Busca usuário por email incluindo senha_hash (usar apenas para autenticação)"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT u.id_usuario, u.nome, u.cpf, u.email, u.senha_hash, u.telefone,
                       u.ativo, u.data_criacao, u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       u.id_nivel_acesso, na.nome as nivel_acesso_nome
                FROM usuario u
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE u.email = %s
            """, (email,))
            return cur.fetchone()
    
    def inserir(self, nome, cpf, email, senha_hash, telefone, id_nivel_acesso, 
                data_nascimento=None, cep=None, logradouro=None, numero=None, 
                bairro=None, cidade=None, estado=None, ativo=1):
        """Insere novo usuário"""
        with get_cursor() as cur:
            cur.execute("""
                INSERT INTO usuario (nome, cpf, email, senha_hash, telefone, ativo, id_nivel_acesso,
                                   data_nascimento, cep, logradouro, numero, bairro, cidade, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome, cpf, email, senha_hash, telefone, ativo, id_nivel_acesso,
                  data_nascimento, cep, logradouro, numero, bairro, cidade, estado))
            return cur.lastrowid
    
    def atualizar(self, id_usuario, nome=None, cpf=None, email=None, telefone=None, 
                  id_nivel_acesso=None, data_nascimento=None, cep=None, logradouro=None, 
                  numero=None, bairro=None, cidade=None, estado=None, ativo=None):
        """Atualiza dados do usuário (exceto senha e ultimo_login)"""
        campos = []
        valores = []
        
        if nome is not None:
            campos.append("nome = %s")
            valores.append(nome)
        if cpf is not None:
            campos.append("cpf = %s")
            valores.append(cpf)
        if email is not None:
            campos.append("email = %s")
            valores.append(email)
        if telefone is not None:
            campos.append("telefone = %s")
            valores.append(telefone)
        if id_nivel_acesso is not None:
            campos.append("id_nivel_acesso = %s")
            valores.append(id_nivel_acesso)
        if data_nascimento is not None:
            campos.append("data_nascimento = %s")
            valores.append(data_nascimento)
        if cep is not None:
            campos.append("cep = %s")
            valores.append(cep)
        if logradouro is not None:
            campos.append("logradouro = %s")
            valores.append(logradouro)
        if numero is not None:
            campos.append("numero = %s")
            valores.append(numero)
        if bairro is not None:
            campos.append("bairro = %s")
            valores.append(bairro)
        if cidade is not None:
            campos.append("cidade = %s")
            valores.append(cidade)
        if estado is not None:
            campos.append("estado = %s")
            valores.append(estado)
        if ativo is not None:
            campos.append("ativo = %s")
            valores.append(ativo)
        
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
    
    def atualizar_ultimo_login(self, id_usuario):
        """Atualiza o timestamp do último login do usuário"""
        with get_cursor() as cur:
            cur.execute(
                "UPDATE usuario SET ultimo_login = NOW() WHERE id_usuario = %s",
                (id_usuario,)
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
    
    def verificar_cpf_existe(self, cpf, excluir_id=None):
        """Verifica se CPF já existe (útil para validação)"""
        with get_cursor() as cur:
            if excluir_id:
                cur.execute(
                    "SELECT COUNT(*) as total FROM usuario WHERE cpf = %s AND id_usuario != %s",
                    (cpf, excluir_id)
                )
            else:
                cur.execute(
                    "SELECT COUNT(*) as total FROM usuario WHERE cpf = %s",
                    (cpf,)
                )
            result = cur.fetchone()
            return result['total'] > 0
    
    def buscar_por_cpf(self, cpf):
        """Busca usuário por CPF (sem senha)"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT u.id_usuario, u.nome, u.cpf, u.email, u.telefone,
                       u.ativo, u.data_criacao, u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       u.id_nivel_acesso, na.nome as nivel_acesso_nome
                FROM usuario u
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE u.cpf = %s
            """, (cpf,))
            return cur.fetchone()
    
    def buscar_usuarios_por_nivel(self, id_nivel_acesso, apenas_ativos=True):
        """Busca todos os usuários de um determinado nível de acesso"""
        with get_cursor() as cur:
            if apenas_ativos:
                cur.execute("""
                    SELECT u.id_usuario, u.nome, u.cpf, u.email, u.telefone,
                           u.ativo, u.data_criacao, u.data_nascimento, u.ultimo_login,
                           u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                           u.id_nivel_acesso, na.nome as nivel_acesso_nome
                    FROM usuario u
                    JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                    WHERE u.id_nivel_acesso = %s AND u.ativo = 1
                    ORDER BY u.nome
                """, (id_nivel_acesso,))
            else:
                cur.execute("""
                    SELECT u.id_usuario, u.nome, u.cpf, u.email, u.telefone,
                           u.ativo, u.data_criacao, u.data_nascimento, u.ultimo_login,
                           u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                           u.id_nivel_acesso, na.nome as nivel_acesso_nome
                    FROM usuario u
                    JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                    WHERE u.id_nivel_acesso = %s
                    ORDER BY u.nome
                """, (id_nivel_acesso,))
            return cur.fetchall()
    
    def listar_usuarios_inativos_ou_sem_login(self, dias_sem_login=90):
        """Retorna usuários inativos ou que não fizeram login há muito tempo"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT u.id_usuario, u.nome, u.cpf, u.email, u.telefone,
                       u.ativo, u.data_criacao, u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       u.id_nivel_acesso, na.nome as nivel_acesso_nome,
                       DATEDIFF(NOW(), u.ultimo_login) as dias_sem_login,
                       CASE 
                           WHEN EXISTS (SELECT 1 FROM cliente WHERE id_usuario = u.id_usuario) THEN 'Cliente'
                           WHEN EXISTS (SELECT 1 FROM funcionario WHERE id_usuario = u.id_usuario) THEN 'Funcionário'
                           ELSE 'Sem Tipo'
                       END as tipo_usuario
                FROM usuario u
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                WHERE u.ativo = 0 
                   OR u.ultimo_login IS NULL 
                   OR DATEDIFF(NOW(), u.ultimo_login) > %s
                ORDER BY dias_sem_login DESC
            """, (dias_sem_login,))
            return cur.fetchall()
