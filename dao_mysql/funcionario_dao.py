from .db_pythonanywhere import get_cursor

class FuncionarioDAO:
    """
    DAO para tabela Funcionario.
    Herda dados de usuario via id_usuario (FK).
    Contém apenas operações de banco de dados.
    Lógicas de negócio devem ficar no módulo service.
    """
    
    def __init__(self):
        pass

    def listar_todos(self, apenas_ativos=True):
        """
        Lista todos os funcionários com JOIN em usuario, nivel_acesso e departamento.
        """
        with get_cursor() as cur:
            query = """
                SELECT f.id_funcionario, f.id_usuario, f.cargo, f.salario, f.data_contratacao,
                       f.id_departamento,
                       u.nome, u.cpf, u.email, u.telefone, u.ativo, u.data_criacao,
                       u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       na.nome as nivel_acesso_nome,
                       d.nome as departamento_nome, d.centro_custo
                FROM Funcionario f
                JOIN usuario u ON f.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                LEFT JOIN Departamento d ON f.id_departamento = d.id_departamento
            """
            if apenas_ativos:
                query += " WHERE u.ativo = TRUE"
            query += " ORDER BY u.nome"
            
            cur.execute(query)
            return cur.fetchall()

    def buscar_por_id(self, id_funcionario):
        """
        Busca funcionário por id_funcionario com dados completos de usuario e departamento.
        """
        with get_cursor() as cur:
            cur.execute("""
                SELECT f.id_funcionario, f.id_usuario, f.cargo, f.salario, f.data_contratacao,
                       f.id_departamento,
                       u.nome, u.cpf, u.email, u.telefone, u.ativo, u.data_criacao,
                       u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       na.nome as nivel_acesso_nome,
                       d.nome as departamento_nome, d.centro_custo
                FROM Funcionario f
                JOIN usuario u ON f.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                LEFT JOIN Departamento d ON f.id_departamento = d.id_departamento
                WHERE f.id_funcionario = %s
            """, (id_funcionario,))
            return cur.fetchone()

    def buscar_por_usuario(self, id_usuario):
        """
        Busca funcionário por id_usuario.
        """
        with get_cursor() as cur:
            cur.execute("""
                SELECT f.id_funcionario, f.id_usuario, f.cargo, f.salario, f.data_contratacao,
                       f.id_departamento,
                       u.nome, u.cpf, u.email, u.telefone, u.ativo, u.data_criacao,
                       u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       na.nome as nivel_acesso_nome,
                       d.nome as departamento_nome, d.centro_custo
                FROM Funcionario f
                JOIN usuario u ON f.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                LEFT JOIN Departamento d ON f.id_departamento = d.id_departamento
                WHERE f.id_usuario = %s
            """, (id_usuario,))
            return cur.fetchone()

    def buscar_por_email(self, email):
        """
        Busca funcionário por email (do usuario associado).
        """
        with get_cursor() as cur:
            cur.execute("""
                SELECT f.id_funcionario, f.id_usuario, f.cargo, f.salario, f.data_contratacao,
                       f.id_departamento,
                       u.nome, u.cpf, u.email, u.telefone, u.ativo, u.data_criacao,
                       u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       na.nome as nivel_acesso_nome,
                       d.nome as departamento_nome, d.centro_custo
                FROM Funcionario f
                JOIN usuario u ON f.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                LEFT JOIN Departamento d ON f.id_departamento = d.id_departamento
                WHERE u.email = %s
            """, (email,))
            return cur.fetchone()

    def inserir(self, id_usuario, cargo, salario, data_contratacao, id_departamento=None):
        """
        Insere um novo funcionário vinculado a um usuario existente.
        O usuario já deve existir na tabela usuario.
        Retorna o id_funcionario gerado.
        """
        with get_cursor() as cur:
            cur.execute("""
                INSERT INTO Funcionario (id_usuario, cargo, salario, data_contratacao, id_departamento)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_usuario, cargo, salario, data_contratacao, id_departamento))
            return cur.lastrowid

    def atualizar(self, id_funcionario, cargo=None, salario=None, data_contratacao=None, id_departamento=None):
        """
        Atualiza campos específicos do funcionário (não mexe em usuario).
        Para atualizar nome, cpf, email, telefone, endereço, usar UsuarioDAO.
        """
        campos = []
        valores = []
        
        if cargo is not None:
            campos.append("cargo = %s")
            valores.append(cargo)
        if salario is not None:
            campos.append("salario = %s")
            valores.append(salario)
        if data_contratacao is not None:
            campos.append("data_contratacao = %s")
            valores.append(data_contratacao)
        if id_departamento is not None:
            campos.append("id_departamento = %s")
            valores.append(id_departamento)
        
        if not campos:
            return
        
        valores.append(id_funcionario)
        query = f"UPDATE Funcionario SET {', '.join(campos)} WHERE id_funcionario = %s"
        
        with get_cursor() as cur:
            cur.execute(query, tuple(valores))

    def deletar(self, id_funcionario):
        """
        Deleta funcionário por id_funcionario.
        CUIDADO: não deleta o usuario associado. Use soft delete (ativar_desativar) se possível.
        """
        with get_cursor() as cur:
            cur.execute("DELETE FROM Funcionario WHERE id_funcionario = %s", (id_funcionario,))

    def verificar_usuario_ja_funcionario(self, id_usuario):
        """
        Verifica se o usuario já está associado a um funcionário.
        Retorna True se já existe, False caso contrário.
        """
        with get_cursor() as cur:
            cur.execute("SELECT COUNT(*) as count FROM Funcionario WHERE id_usuario = %s", (id_usuario,))
            result = cur.fetchone()
            return result['count'] > 0

    def listar_funcionarios_ativos(self):
        """
        Lista apenas funcionários ativos (usuario.ativo = TRUE).
        """
        with get_cursor() as cur:
            cur.execute("""
                SELECT f.id_funcionario, f.id_usuario, f.cargo, f.salario, f.data_contratacao,
                       f.id_departamento,
                       u.nome, u.cpf, u.email, u.telefone, u.data_criacao,
                       u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       na.nome as nivel_acesso_nome,
                       d.nome as departamento_nome, d.centro_custo
                FROM Funcionario f
                JOIN usuario u ON f.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                LEFT JOIN Departamento d ON f.id_departamento = d.id_departamento
                WHERE u.ativo = TRUE
                ORDER BY u.nome
            """)
            return cur.fetchall()

    def listar_por_cargo(self, cargo):
        """
        Lista funcionários por cargo específico.
        """
        with get_cursor() as cur:
            cur.execute("""
                SELECT f.id_funcionario, f.id_usuario, f.cargo, f.salario, f.data_contratacao,
                       f.id_departamento,
                       u.nome, u.cpf, u.email, u.telefone, u.ativo, u.data_criacao,
                       u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       na.nome as nivel_acesso_nome,
                       d.nome as departamento_nome, d.centro_custo
                FROM Funcionario f
                JOIN usuario u ON f.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                LEFT JOIN Departamento d ON f.id_departamento = d.id_departamento
                WHERE f.cargo = %s AND u.ativo = TRUE
                ORDER BY u.nome
            """, (cargo,))
            return cur.fetchall()
    
    def listar_por_departamento(self, id_departamento, apenas_ativos=True):
        """
        Lista funcionários de um departamento específico.
        """
        with get_cursor() as cur:
            query = """
                SELECT f.id_funcionario, f.id_usuario, f.cargo, f.salario, f.data_contratacao,
                       f.id_departamento,
                       u.nome, u.cpf, u.email, u.telefone, u.ativo, u.data_criacao,
                       u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       na.nome as nivel_acesso_nome,
                       d.nome as departamento_nome, d.centro_custo
                FROM Funcionario f
                JOIN usuario u ON f.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                LEFT JOIN Departamento d ON f.id_departamento = d.id_departamento
                WHERE f.id_departamento = %s
            """
            if apenas_ativos:
                query += " AND u.ativo = TRUE"
            query += " ORDER BY u.nome"
            
            cur.execute(query, (id_departamento,))
            return cur.fetchall()
    
    def buscar_por_cpf(self, cpf):
        """
        Busca funcionário por CPF (agora CPF está na tabela usuario).
        """
        with get_cursor() as cur:
            cur.execute("""
                SELECT f.id_funcionario, f.id_usuario, f.cargo, f.salario, f.data_contratacao,
                       f.id_departamento,
                       u.nome, u.cpf, u.email, u.telefone, u.ativo, u.data_criacao,
                       u.data_nascimento, u.ultimo_login,
                       u.cep, u.logradouro, u.numero, u.bairro, u.cidade, u.estado,
                       na.nome as nivel_acesso_nome,
                       d.nome as departamento_nome, d.centro_custo
                FROM Funcionario f
                JOIN usuario u ON f.id_usuario = u.id_usuario
                JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
                LEFT JOIN Departamento d ON f.id_departamento = d.id_departamento
                WHERE u.cpf = %s
            """, (cpf,))
            return cur.fetchone()
    
    def obter_estatisticas_por_departamento(self):
        """
        Retorna estatísticas de funcionários por departamento.
        """
        with get_cursor() as cur:
            cur.execute("""
                SELECT 
                    d.id_departamento,
                    d.nome as departamento_nome,
                    d.centro_custo,
                    COUNT(f.id_funcionario) as total_funcionarios,
                    COUNT(CASE WHEN u.ativo = 1 THEN 1 END) as funcionarios_ativos,
                    SUM(f.salario) as folha_salarial,
                    AVG(f.salario) as salario_medio,
                    MIN(f.data_contratacao) as primeira_contratacao,
                    MAX(f.data_contratacao) as ultima_contratacao
                FROM Departamento d
                LEFT JOIN Funcionario f ON d.id_departamento = f.id_departamento
                LEFT JOIN usuario u ON f.id_usuario = u.id_usuario
                GROUP BY d.id_departamento, d.nome, d.centro_custo
                ORDER BY total_funcionarios DESC
            """)
            return cur.fetchall()

    def buscar_funcionario(self, id_funcionario):
        """
        Método legado mantido para compatibilidade.
        Recomenda-se usar buscar_por_id().
        """
        return self.buscar_por_id(id_funcionario)

    def inserir_funcionario_obj(self, funcionario):
        """
        Método legado mantido para compatibilidade.
        Insere funcionário a partir de objeto (assumindo que tenha id_usuario).
        """
        return self.inserir(
            funcionario.id_usuario,
            funcionario.cargo,
            funcionario.salario,
            funcionario.data_contratacao
        )