# backend/migrate.py
from db import get_db
import sqlite3
import os

def drop_tables(db):
    """Remove tabelas existentes para recriação"""
    db.execute("DROP TABLE IF EXISTS transactions")
    db.execute("DROP TABLE IF EXISTS users")
    print("Tabelas antigas removidas")

def create_tables(db):
    """Cria todas as tabelas com estrutura correta"""
    # Tabela users com ID autoincrementável
    db.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela transactions com chave estrangeira
    db.execute('''
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            category TEXT NOT NULL,
            date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Índices para melhor performance
    db.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON transactions(user_id)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_user_email ON users(email)')
    
    print("Tabelas criadas com sucesso")

def migrate():
    try:
        # Remove o arquivo do banco existente se quiser recriar do zero
        if os.path.exists('finance.db'):
            os.remove('finance.db')
            print("Banco de dados antigo removido")
            
        with get_db() as db:
            # Cria todas as tabelas
            create_tables(db)
            db.commit()
            
            # Verificação
            print("\nEstrutura verificada:")
            print("Users:", db.execute("PRAGMA table_info(users)").fetchall())
            print("Transactions:", db.execute("PRAGMA table_info(transactions)").fetchall())
            
        print("\nMigração concluída com sucesso!")
        
    except Exception as e:
        print(f"Erro durante migração: {str(e)}")
        if 'db' in locals():
            db.rollback()

if __name__ == '__main__':
    migrate()