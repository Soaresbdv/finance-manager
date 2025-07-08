# Crie um arquivo check_db.py no backend/ com:
from db import get_db

with get_db() as db:
    print("Estrutura da tabela users:")
    print(db.execute("PRAGMA table_info(users)").fetchall())
    
    print("\nDados na tabela users:")
    print(db.execute("SELECT * FROM users").fetchall())