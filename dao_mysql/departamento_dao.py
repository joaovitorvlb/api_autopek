"""
DAO para Departamento - Apenas operações de banco de dados
Departamento organiza funcionários por áreas e centros de custo
Regras de negócio devem estar no módulo service
"""
from .db_pythonanywhere import get_cursor

class DepartamentoDAO:
    """DAO para operações CRUD na tabela Departamento"""
    
    def listar_todos(self):
        """Retorna todos os departamentos"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT id_departamento, nome, centro_custo
                FROM Departamento
                ORDER BY nome
            """)
            return cur.fetchall()
    
    def buscar_por_id(self, id_departamento):
        """Busca departamento por ID"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT id_departamento, nome, centro_custo
                FROM Departamento
                WHERE id_departamento = %s
            """, (id_departamento,))
            return cur.fetchone()
    
    def buscar_por_nome(self, nome):
        """Busca departamento por nome (case-insensitive)"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT id_departamento, nome, centro_custo
                FROM Departamento
                WHERE LOWER(nome) = LOWER(%s)
            """, (nome,))
            return cur.fetchone()
    
    def buscar_por_centro_custo(self, centro_custo):
        """Busca departamento por centro de custo"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT id_departamento, nome, centro_custo
                FROM Departamento
                WHERE centro_custo = %s
            """, (centro_custo,))
            return cur.fetchone()
    
    def inserir(self, nome, centro_custo):
        """Insere novo departamento"""
        with get_cursor() as cur:
            cur.execute("""
                INSERT INTO Departamento (nome, centro_custo)
                VALUES (%s, %s)
            """, (nome, centro_custo))
            return cur.lastrowid
    
    def atualizar(self, id_departamento, nome=None, centro_custo=None):
        """Atualiza dados do departamento"""
        campos = []
        valores = []
        
        if nome is not None:
            campos.append("nome = %s")
            valores.append(nome)
        if centro_custo is not None:
            campos.append("centro_custo = %s")
            valores.append(centro_custo)
        
        if not campos:
            return 0
        
        valores.append(id_departamento)
        query = f"UPDATE Departamento SET {', '.join(campos)} WHERE id_departamento = %s"
        
        with get_cursor() as cur:
            cur.execute(query, valores)
            return cur.rowcount
    
    def deletar(self, id_departamento):
        """
        Deleta departamento permanentemente.
        CUIDADO: Pode falhar se houver funcionários vinculados (FK constraint).
        Considere desvincular funcionários antes de deletar.
        """
        with get_cursor() as cur:
            cur.execute("DELETE FROM Departamento WHERE id_departamento = %s", (id_departamento,))
            return cur.rowcount
    
    def verificar_nome_existe(self, nome, excluir_id=None):
        """Verifica se nome do departamento já existe (útil para validação)"""
        with get_cursor() as cur:
            if excluir_id:
                cur.execute(
                    "SELECT COUNT(*) as total FROM Departamento WHERE LOWER(nome) = LOWER(%s) AND id_departamento != %s",
                    (nome, excluir_id)
                )
            else:
                cur.execute(
                    "SELECT COUNT(*) as total FROM Departamento WHERE LOWER(nome) = LOWER(%s)",
                    (nome,)
                )
            result = cur.fetchone()
            return result['total'] > 0
    
    def verificar_centro_custo_existe(self, centro_custo, excluir_id=None):
        """Verifica se centro de custo já existe"""
        with get_cursor() as cur:
            if excluir_id:
                cur.execute(
                    "SELECT COUNT(*) as total FROM Departamento WHERE centro_custo = %s AND id_departamento != %s",
                    (centro_custo, excluir_id)
                )
            else:
                cur.execute(
                    "SELECT COUNT(*) as total FROM Departamento WHERE centro_custo = %s",
                    (centro_custo,)
                )
            result = cur.fetchone()
            return result['total'] > 0
    
    def contar_funcionarios_por_departamento(self, id_departamento):
        """Retorna a quantidade de funcionários em um departamento"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) as total
                FROM Funcionario
                WHERE id_departamento = %s
            """, (id_departamento,))
            result = cur.fetchone()
            return result['total']
    
    def listar_com_estatisticas(self):
        """
        Retorna todos os departamentos com estatísticas de funcionários.
        Inclui: total de funcionários, funcionários ativos, folha salarial, etc.
        """
        with get_cursor() as cur:
            cur.execute("""
                SELECT 
                    d.id_departamento,
                    d.nome,
                    d.centro_custo,
                    COUNT(f.id_funcionario) as total_funcionarios,
                    COUNT(CASE WHEN u.ativo = 1 THEN 1 END) as funcionarios_ativos,
                    COALESCE(SUM(f.salario), 0) as folha_salarial,
                    COALESCE(AVG(f.salario), 0) as salario_medio,
                    MIN(f.data_contratacao) as primeira_contratacao,
                    MAX(f.data_contratacao) as ultima_contratacao
                FROM Departamento d
                LEFT JOIN Funcionario f ON d.id_departamento = f.id_departamento
                LEFT JOIN usuario u ON f.id_usuario = u.id_usuario
                GROUP BY d.id_departamento, d.nome, d.centro_custo
                ORDER BY d.nome
            """)
            return cur.fetchall()
    
    def buscar_por_id_com_estatisticas(self, id_departamento):
        """
        Busca departamento por ID com estatísticas detalhadas.
        """
        with get_cursor() as cur:
            cur.execute("""
                SELECT 
                    d.id_departamento,
                    d.nome,
                    d.centro_custo,
                    COUNT(f.id_funcionario) as total_funcionarios,
                    COUNT(CASE WHEN u.ativo = 1 THEN 1 END) as funcionarios_ativos,
                    COALESCE(SUM(f.salario), 0) as folha_salarial,
                    COALESCE(AVG(f.salario), 0) as salario_medio,
                    MIN(f.data_contratacao) as primeira_contratacao,
                    MAX(f.data_contratacao) as ultima_contratacao
                FROM Departamento d
                LEFT JOIN Funcionario f ON d.id_departamento = f.id_departamento
                LEFT JOIN usuario u ON f.id_usuario = u.id_usuario
                WHERE d.id_departamento = %s
                GROUP BY d.id_departamento, d.nome, d.centro_custo
            """, (id_departamento,))
            return cur.fetchone()
    
    def listar_departamentos_vazios(self):
        """Retorna departamentos sem funcionários vinculados"""
        with get_cursor() as cur:
            cur.execute("""
                SELECT d.id_departamento, d.nome, d.centro_custo
                FROM Departamento d
                LEFT JOIN Funcionario f ON d.id_departamento = f.id_departamento
                WHERE f.id_funcionario IS NULL
                ORDER BY d.nome
            """)
            return cur.fetchall()
    
    def obter_resumo_geral(self):
        """
        Retorna resumo geral de todos os departamentos.
        Útil para dashboards e relatórios gerenciais.
        """
        with get_cursor() as cur:
            cur.execute("""
                SELECT 
                    COUNT(DISTINCT d.id_departamento) as total_departamentos,
                    COUNT(f.id_funcionario) as total_funcionarios,
                    COUNT(CASE WHEN u.ativo = 1 THEN 1 END) as funcionarios_ativos,
                    COALESCE(SUM(f.salario), 0) as folha_salarial_total,
                    COALESCE(AVG(f.salario), 0) as salario_medio_geral,
                    COUNT(DISTINCT CASE WHEN f.id_funcionario IS NULL THEN d.id_departamento END) as departamentos_vazios
                FROM Departamento d
                LEFT JOIN Funcionario f ON d.id_departamento = f.id_departamento
                LEFT JOIN usuario u ON f.id_usuario = u.id_usuario
            """)
            return cur.fetchone()
