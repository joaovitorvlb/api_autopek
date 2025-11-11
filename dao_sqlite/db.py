import os
import sqlite3
import threading
from contextlib import contextmanager
from flask import g, has_request_context

# Configuração global
_db_path = None
_db_lock = threading.Lock()


def init_db(db_config: dict = None, minconn: int = 1, maxconn: int = 5):
    """Inicializa o caminho do banco SQLite.
    
    db_config: dict com chave 'database' (caminho do arquivo SQLite).
      Exemplo: {'database': 'app_sqlite.db'}
    Se db_config for None, usa variável de ambiente SQLITE_DB ou padrão 'banco_api.sqlite'.
    
    Os parâmetros minconn e maxconn são ignorados (compatibilidade com interface PostgreSQL).
    """
    global _db_path
    if _db_path is not None:
        return
    
    if db_config is None:
        _db_path = os.getenv('SQLITE_DB', 'banco_api.sqlite')
    else:
        _db_path = db_config.get('database', 'banco_api.sqlite')


def get_db_connection():
    """
    Obtém a conexão do banco para a requisição atual (Flask g object).
    Reutiliza a mesma conexão durante toda a requisição.
    
    Returns:
        sqlite3.Connection: Conexão ativa do SQLite
    """
    if _db_path is None:
        raise RuntimeError("Database path não inicializado. Chame init_db(...) primeiro.")
    
    # Se estamos em contexto de requisição Flask, usar g
    if has_request_context():
        if 'db_conn' not in g:
            # Criar nova conexão para esta requisição
            # isolation_level='DEFERRED' para controle explícito mas com transações normais
            conn = sqlite3.connect(_db_path, timeout=30.0, isolation_level='DEFERRED', check_same_thread=False)
            conn.row_factory = sqlite3.Row
            
            # Configurações para melhor performance
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=memory")
            
            g.db_conn = conn
        
        return g.db_conn
    else:
        # Fora de contexto Flask (scripts, testes unitários)
        # Criar conexão temporária
        conn = sqlite3.connect(_db_path, timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=memory")
        return conn


def close_db_connection(error=None):
    """
    Fecha a conexão do banco ao fim da requisição Flask.
    Deve ser registrada como teardown_appcontext no Flask.
    """
    conn = g.pop('db_conn', None)
    if conn is not None:
        try:
            conn.close()
        except Exception:
            pass


@contextmanager
def get_cursor(commit: bool = True):
    """Context manager que fornece um cursor SQLite da mesma conexão.
    
    Durante uma requisição Flask, REUTILIZA a mesma conexão (Flask g object).
    Fora do Flask (scripts), cria conexão isolada com modo transação normal.
    
    Uso:
      from dao_sqlite.db import get_cursor
      with get_cursor() as cur:
          cur.execute("SELECT ...")
          rows = cur.fetchall()
    
    O commit é executado automaticamente se nenhum erro for lançado.
    """
    in_flask_context = has_request_context()
    
    if in_flask_context:
        # ===== DENTRO DE FLASK: usar pool de conexões =====
        conn = get_db_connection()
        
        try:
            cur = conn.cursor()
            yield cur
            
            # Commit se solicitado (usa commit() normal do sqlite3)
            if commit:
                conn.commit()
                try:
                    conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
                except:
                    pass
                
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            raise
        finally:
            try:
                cur.close()
            except Exception:
                pass
    
    else:
        # ===== FORA DE FLASK: conexão isolada para scripts =====
        if _db_path is None:
            raise RuntimeError("Database path não inicializado. Chame init_db(...) primeiro.")
        
        # Criar conexão com modo transação normal (não autocommit)
        conn = sqlite3.connect(_db_path, timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        
        # Configurações para performance
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=memory")
        
        cur = conn.cursor()
        try:
            yield cur
            
            # Commit automático se solicitado
            if commit:
                conn.commit()
                
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            raise
        finally:
            try:
                cur.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass


def close_pool():
    """Fecha o pool (compatibilidade com interface PostgreSQL).
    Para SQLite, apenas reseta o caminho do banco.
    """
    global _db_path
    _db_path = None

