"""
DAO para manipulação da tabela Fornecedor no SQLite
"""

from typing import List, Optional
from dao_sqlite.db import get_cursor


class FornecedorDAO:
    """
    Data Access Object para Fornecedor
    """

    def criar(self, razao_social: str, nome_fantasia: str, cnpj: str, 
              email: str = None, telefone: str = None, endereco: str = None) -> Optional[int]:
        """
        Cria um novo fornecedor
        
        Args:
            razao_social: Razão social do fornecedor (nome jurídico - obrigatório)
            nome_fantasia: Nome fantasia do fornecedor (nome comercial - obrigatório)
            cnpj: CNPJ do fornecedor (deve ser único)
            email: Email do fornecedor (opcional)
            telefone: Telefone do fornecedor (opcional)
            endereco: Endereço do fornecedor (opcional)
        
        Returns:
            ID do fornecedor criado ou None se houver erro
        """
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Fornecedor (razao_social, nome_fantasia, cnpj, email, telefone, endereco)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (razao_social, nome_fantasia, cnpj, email, telefone, endereco))
                
                return cursor.lastrowid
        except Exception as e:
            return None

    def buscar_por_id(self, id_fornecedor: int) -> Optional[dict]:
        """
        Busca fornecedor por ID
        
        Args:
            id_fornecedor: ID do fornecedor
        
        Returns:
            Dicionário com dados do fornecedor ou None se não encontrado
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT id_fornecedor, razao_social, nome_fantasia, cnpj, 
                           email, telefone, endereco, ativo, data_criacao
                    FROM Fornecedor
                    WHERE id_fornecedor = ?
                """, (id_fornecedor,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            return None

    def buscar_por_cnpj(self, cnpj: str) -> Optional[dict]:
        """
        Busca fornecedor por CNPJ
        
        Args:
            cnpj: CNPJ do fornecedor
        
        Returns:
            Dicionário com dados do fornecedor ou None se não encontrado
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT id_fornecedor, razao_social, nome_fantasia, cnpj, 
                           email, telefone, endereco, ativo, data_criacao
                    FROM Fornecedor
                    WHERE cnpj = ?
                """, (cnpj,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            return None

    def listar_todos(self, apenas_ativos: bool = True) -> List[dict]:
        """
        Lista todos os fornecedores
        
        Args:
            apenas_ativos: Se True, lista apenas fornecedores ativos
        
        Returns:
            Lista de dicionários com dados dos fornecedores
        """
        try:
            with get_cursor(commit=False) as cursor:
                if apenas_ativos:
                    cursor.execute("""
                        SELECT id_fornecedor, razao_social, nome_fantasia, cnpj, 
                               email, telefone, endereco, ativo, data_criacao
                        FROM Fornecedor
                        WHERE ativo = 1
                        ORDER BY nome_fantasia
                    """)
                else:
                    cursor.execute("""
                        SELECT id_fornecedor, razao_social, nome_fantasia, cnpj, 
                               email, telefone, endereco, ativo, data_criacao
                        FROM Fornecedor
                        ORDER BY nome_fantasia
                    """)
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return None

    def buscar_por_nome(self, nome: str, apenas_ativos: bool = True) -> List[dict]:
        """
        Busca fornecedores por nome (busca parcial em razão social ou nome fantasia, case-insensitive)
        
        Args:
            nome: Nome ou parte do nome do fornecedor
            apenas_ativos: Se True, busca apenas fornecedores ativos
        
        Returns:
            Lista de dicionários com dados dos fornecedores encontrados
        """
        try:
            with get_cursor(commit=False) as cursor:
                if apenas_ativos:
                    cursor.execute("""
                        SELECT id_fornecedor, razao_social, nome_fantasia, cnpj, 
                               email, telefone, endereco, ativo, data_criacao
                        FROM Fornecedor
                        WHERE (razao_social LIKE ? OR nome_fantasia LIKE ?) AND ativo = 1
                        ORDER BY nome_fantasia
                    """, (f'%{nome}%', f'%{nome}%'))
                else:
                    cursor.execute("""
                        SELECT id_fornecedor, razao_social, nome_fantasia, cnpj, 
                               email, telefone, endereco, ativo, data_criacao
                        FROM Fornecedor
                        WHERE razao_social LIKE ? OR nome_fantasia LIKE ?
                        ORDER BY nome_fantasia
                    """, (f'%{nome}%', f'%{nome}%'))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return None

    def atualizar(self, id_fornecedor: int, razao_social: str = None, 
                  nome_fantasia: str = None, cnpj: str = None, email: str = None,
                  telefone: str = None, endereco: str = None) -> bool:
        """
        Atualiza dados do fornecedor
        
        Args:
            id_fornecedor: ID do fornecedor
            razao_social: Nova razão social (opcional)
            nome_fantasia: Novo nome fantasia (opcional)
            cnpj: Novo CNPJ (opcional)
            email: Novo email (opcional)
            telefone: Novo telefone (opcional)
            endereco: Novo endereço (opcional)
        
        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            campos = []
            valores = []
            
            if razao_social is not None:
                campos.append("razao_social = ?")
                valores.append(razao_social)
            
            if nome_fantasia is not None:
                campos.append("nome_fantasia = ?")
                valores.append(nome_fantasia)
            
            if cnpj is not None:
                campos.append("cnpj = ?")
                valores.append(cnpj)
            
            if email is not None:
                campos.append("email = ?")
                valores.append(email)
            
            if telefone is not None:
                campos.append("telefone = ?")
                valores.append(telefone)
            
            if endereco is not None:
                campos.append("endereco = ?")
                valores.append(endereco)
            
            if not campos:
                return False
            
            valores.append(id_fornecedor)
            
            with get_cursor() as cursor:
                query = f"""
                    UPDATE Fornecedor
                    SET {', '.join(campos)}
                    WHERE id_fornecedor = ?
                """
                cursor.execute(query, valores)
                
                return cursor.rowcount > 0
        except Exception as e:
            return False

    def desativar(self, id_fornecedor: int) -> bool:
        """
        Desativa um fornecedor (soft delete)
        
        Args:
            id_fornecedor: ID do fornecedor
        
        Returns:
            True se desativado com sucesso, False caso contrário
        """
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    UPDATE Fornecedor
                    SET ativo = 0
                    WHERE id_fornecedor = ?
                """, (id_fornecedor,))
                
                return cursor.rowcount > 0
        except Exception as e:
            return False

    def ativar(self, id_fornecedor: int) -> bool:
        """
        Ativa um fornecedor
        
        Args:
            id_fornecedor: ID do fornecedor
        
        Returns:
            True se ativado com sucesso, False caso contrário
        """
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    UPDATE Fornecedor
                    SET ativo = 1
                    WHERE id_fornecedor = ?
                """, (id_fornecedor,))
                
                return cursor.rowcount > 0
        except Exception as e:
            return False

    def deletar(self, id_fornecedor: int) -> bool:
        """
        Deleta um fornecedor permanentemente
        ATENÇÃO: Só deve ser usado se não houver pedidos de compra relacionados
        
        Args:
            id_fornecedor: ID do fornecedor
        
        Returns:
            True se deletado com sucesso, False caso contrário
        """
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    DELETE FROM Fornecedor
                    WHERE id_fornecedor = ?
                """, (id_fornecedor,))
                
                return cursor.rowcount > 0
        except Exception as e:
            return False

    def contar_pedidos_compra(self, id_fornecedor: int) -> int:
        """
        Conta quantos pedidos de compra o fornecedor possui
        
        Args:
            id_fornecedor: ID do fornecedor
        
        Returns:
            Número de pedidos de compra
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as total
                    FROM Pedido_Compra
                    WHERE id_fornecedor = ?
                """, (id_fornecedor,))
                
                row = cursor.fetchone()
                return row['total'] if row else 0
        except Exception as e:
            return 0

    def obter_estatisticas(self, id_fornecedor: int) -> Optional[dict]:
        """
        Obtém estatísticas de compras de um fornecedor
        
        Args:
            id_fornecedor: ID do fornecedor
        
        Returns:
            Dicionário com estatísticas ou None se houver erro
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_pedidos,
                        SUM(total) as valor_total,
                        AVG(total) as valor_medio,
                        MAX(data_pedido) as ultima_compra
                    FROM Pedido_Compra
                    WHERE id_fornecedor = ? AND status = 'Recebido'
                """, (id_fornecedor,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            return None
