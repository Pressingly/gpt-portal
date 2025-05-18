import psycopg2
from sshtunnel import SSHTunnelForwarder
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# === CONFIG ===
# SSH Configuration
SSH_MODE = os.getenv('SSH_MODE', 'false').lower() == 'true'
print(f"SSH_MODE: {SSH_MODE}")
SSH_HOST = '54.251.44.10'
SSH_PORT = 22
SSH_USERNAME = 'trungneo'
SSH_KEY_PATH = os.path.join(os.path.dirname(__file__), 'neo')  # Updated to use neo file in ledger folder

# Database URL format
DATABASE_URL_LLM = os.getenv('DATABASE_URL_LLM')

LOCAL_BIND_PORT = 6543

def get_db_connection():
    """Establish database connection with optional SSH tunnel"""
    try:
        # Parse the DATABASE_URL
        db_url = urlparse(DATABASE_URL_LLM)
        db_host = db_url.hostname
        db_port = db_url.port or 5432
        db_user = db_url.username
        db_password = db_url.password
        db_name = db_url.path[1:]  # Remove leading slash

        if SSH_MODE == True:
            # Step 1: Establish SSH tunnel
            tunnel = SSHTunnelForwarder(
                (SSH_HOST, SSH_PORT),
                ssh_username=SSH_USERNAME,
                ssh_pkey=SSH_KEY_PATH,
                remote_bind_address=(db_host, db_port),
                local_bind_address=('localhost', LOCAL_BIND_PORT))
            tunnel.start()
            print(f"✅ SSH Tunnel established on localhost:{tunnel.local_bind_port}")

            # Step 2: Connect to PostgreSQL through the tunnel
            conn = psycopg2.connect(
                host='localhost',
                port=tunnel.local_bind_port,
                user=db_user,
                password=db_password,
                dbname=db_name)
            print("✅ PostgreSQL connection successful through SSH tunnel.")
            return conn, tunnel
        else:
            # Direct connection without SSH tunnel
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                dbname=db_name)
            print("✅ PostgreSQL connection successful (direct connection).")
            return conn, None

    except Exception as e:
        print(f"❌ Error: {e}")
        raise e

if __name__ == "__main__":
    # Test the connection
    try:
        print("🔍 Testing database connection...")
        conn, tunnel = get_db_connection()
        cur = conn.cursor()
        
        # First, let's check if the table exists and get its structure
        print("\n📊 Checking table structure...")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'LiteLLM_SpendLogs';
        """)
        columns = cur.fetchall()
        print("Table columns:")
        for col in columns:
            print(f"- {col[0]}: {col[1]}")
        
        # Now let's check how many records we have
        print("\n📈 Checking record count...")
        cur.execute('SELECT COUNT(*) FROM "LiteLLM_SpendLogs";')
        count = cur.fetchone()[0]
        print(f"Total records: {count}")
        
        # Let's try the actual query
        print("\n🔍 Executing main query...")
        query = '''SELECT * FROM "LiteLLM_SpendLogs" 
                  WHERE "end_user" = '0834a6d1-b476-4a75-abb8-46055793f134' 
                  ORDER BY "startTime" DESC;'''
        cur.execute(query)
        results = cur.fetchall()

        # Print results with column names
        if results:
            print(f"\n✅ Found {len(results)} records:")
            # Get column names
            colnames = [desc[0] for desc in cur.description]
            print("\nColumns:", colnames)
            
            # Print first 5 records with formatted output
            print("\nFirst 5 records:")
            for i, row in enumerate(results[:5]):
                print(f"\nRecord {i+1}:")
                for col, val in zip(colnames, row):
                    print(f"  {col}: {val}")
        else:
            print("\n❌ No records found for the specified end_user")

        cur.close()
        conn.close()
        if tunnel:
            tunnel.stop()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        print("\nDetailed error:")
        print(traceback.format_exc())
    finally:
        print("\n🔒 Connections closed.") 