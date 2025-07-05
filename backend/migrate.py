from db import get_db

def table_exists(db, table_name):
    """Verifica se uma tabela existe no banco de dados"""
    cursor = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return cursor.fetchone() is not None

def column_exists(db, table_name, column_name):
    """Verifica se uma coluna existe em uma tabela"""
    cursor = db.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]
    return column_name in columns

def migrate():
    with get_db() as db:
        try:
            if not table_exists(db, 'transactions'):
                db.execute('''
                    CREATE TABLE transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        description TEXT NOT NULL,
                        amount REAL NOT NULL,
                        type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                        category TEXT NOT NULL DEFAULT 'other',
                        date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                ''')
                print("Tabela 'transactions' criada com sucesso!")
            else:
                print("Tabela 'transactions' já existe. Verificando colunas...")
                if not column_exists(db, 'transactions', 'category'):
                    db.execute('''
                        ALTER TABLE transactions 
                        ADD COLUMN category TEXT NOT NULL DEFAULT 'other'
                    ''')
                    print("Coluna 'category' adicionada com sucesso!")
                else:
                    print("Coluna 'category' já existe.")
                
            db.commit()
            
        except Exception as e:
            print("Erro na migração:", str(e))
            db.rollback()

if __name__ == '__main__':
    migrate()