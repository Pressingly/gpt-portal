import psycopg2
from psycopg2 import pool
from sshtunnel import SSHTunnelForwarder
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import atexit

load_dotenv()

# === CONFIG ===
# SSH Configuration
SSH_MODE = os.getenv('SSH_MODE', 'false').lower() == 'true'
print(f"SSH_MODE: {SSH_MODE}")
SSH_HOST = '54.251.44.10'
SSH_PORT = 22
SSH_USERNAME = 'trungneo'
SSH_KEY_PATH = os.path.join(os.path.dirname(__file__), 'neo')

# Database URL format
DATABASE_URL_LLM = os.getenv('DATABASE_URL_LLM')
LOCAL_BIND_PORT = 6543

# Global variables for connection management
connection_pool = None
tunnel = None

def init_connection_pool():
    """Initialize the connection pool and SSH tunnel if needed"""
    global connection_pool, tunnel
    
    try:
        # Parse the DATABASE_URL
        db_url = urlparse(DATABASE_URL_LLM)
        db_host = db_url.hostname
        db_port = db_url.port or 5432
        db_user = db_url.username
        db_password = db_url.password
        db_name = db_url.path[1:]  # Remove leading slash

        if SSH_MODE:
            # Create SSH tunnel if it doesn't exist
            if tunnel is None or not tunnel.is_active:
                tunnel = SSHTunnelForwarder(
                    (SSH_HOST, SSH_PORT),
                    ssh_username=SSH_USERNAME,
                    ssh_pkey=SSH_KEY_PATH,
                    remote_bind_address=(db_host, db_port),
                    local_bind_address=('localhost', LOCAL_BIND_PORT)
                )
                tunnel.start()
                print(f"✅ SSH Tunnel established on localhost:{tunnel.local_bind_port}")

            # Create connection pool using tunnel
            connection_pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=20,
                host='localhost',
                port=tunnel.local_bind_port,
                user=db_user,
                password=db_password,
                dbname=db_name
            )
        else:
            # Direct connection pool without SSH tunnel
            connection_pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=20,
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                dbname=db_name
            )
        
        print("✅ Connection pool initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing connection pool: {e}")
        raise e

def get_db_connection():
    """Get a connection from the pool"""
    global connection_pool
    
    if connection_pool is None:
        init_connection_pool()
    
    try:
        conn = connection_pool.getconn()
        return conn
    except Exception as e:
        print(f"❌ Error getting connection from pool: {e}")
        raise e

def release_connection(conn):
    """Return a connection to the pool"""
    if connection_pool is not None:
        connection_pool.putconn(conn)

def cleanup():
    """Cleanup function to be called on application shutdown"""
    global connection_pool, tunnel
    
    if connection_pool is not None:
        connection_pool.closeall()
        print("✅ Connection pool closed")
    
    if tunnel is not None and tunnel.is_active:
        tunnel.stop()
        print("✅ SSH tunnel closed")

# Register cleanup function
atexit.register(cleanup)

if __name__ == "__main__":
    # Test the connection
    try:
        print("🔍 Testing database connection...")
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Test query
        cur.execute('SELECT COUNT(*) FROM "LiteLLM_SpendLogs";')
        count = cur.fetchone()[0]
        print(f"✅ Successfully connected to database. Total records: {count}")
        
        cur.close()
        release_connection(conn)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print("\nDetailed error:")
        print(traceback.format_exc())
    finally:
        cleanup() 