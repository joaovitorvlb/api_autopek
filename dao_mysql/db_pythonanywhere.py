import os
from contextlib import contextmanager
import mysql.connector
from mysql.connector import pooling

_pool = None

def init_db(db_config: dict = None, minconn: int = 1, maxconn: int = 3):
    """Inicializa o pool de conexões MySQL otimizado para PythonAnywhere
    
    db_config: dict com chaves compatíveis com mysql.connector.connect
    Para PythonAnywhere, use:
      {
        'host': 'SEU_USUARIO.mysql.pythonanywhere-services.com',
        'port': 3306,
        'user': 'SEU_USUARIO',
        'password': 'SUA_SENHA',
        'database': 'SEU_USUARIO$default'
      }
    """
    global _pool
    if _pool is not None:
        return

    if db_config is None:
        # Configuração específica para PythonAnywhere
        db_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': os.getenv('MYSQL_DATABASE', 'e_comerce_flask'),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': False,
            'ssl_disabled': True,  # PythonAnywhere não precisa de SSL
            'connection_timeout': 60
        }

    # Pool menor para PythonAnywhere (limite de conexões no free tier)
    _pool = pooling.MySQLConnectionPool(
        pool_name="mysql_pool",
        pool_size=min(maxconn, 3),  # Máximo 3 conexões no free tier
        pool_reset_session=True,
        **db_config
    )


@contextmanager
def get_cursor(commit: bool = True):
    """Context manager otimizado para PythonAnywhere
    
    Uso:
      from dao_mysql.db import get_cursor
      with get_cursor() as cur:
          cur.execute("SELECT ...")
          rows = cur.fetchall()
    """
    if _pool is None:
        raise RuntimeError("Connection pool não inicializado. Chame init_db() primeiro.")

    conn = None
    cur = None
    try:
        conn = _pool.get_connection()
        cur = conn.cursor(dictionary=True, buffered=True)
        yield cur
        if commit:
            conn.commit()
    except mysql.connector.Error as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        raise e
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        raise e
    finally:
        if cur:
            try:
                cur.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


def close_pool():
    """Fecha o pool de conexões"""
    global _pool
    if _pool is not None:
        try:
            _pool._remove_connections()
        except:
            pass
        _pool = None


def test_connection():
    """Testa a conexão com o banco MySQL"""
    try:
        with get_cursor() as cur:
            cur.execute("SELECT 1 as test")
            result = cur.fetchone()
            return result['test'] == 1
    except Exception as e:
        return False