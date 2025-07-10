import sqlite3
from sqlite3 import Error
import bcrypt
import secrets

# Configuração do banco de dados
DATABASE = "finance.db"

def create_connection():
    """Cria conexão com o SQLite e ativa chaves estrangeiras."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        conn.execute("PRAGMA foreign_keys = ON")  # Ativa FK
        print("Conexão com SQLite estabelecida.")
        return conn
    except Error as e:
        print(f"Erro ao conectar ao SQLite: {e}")
        return None

def create_tables(conn):
    """Cria as tabelas users e transactions."""
    sql_users = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT
);
"""
    sql_transactions = """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        amount INTEGER NOT NULL,
        type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
        category TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql_users)
        cursor.execute(sql_transactions)
        conn.commit()
        print("Tabelas criadas com sucesso!")
    except Error as e:
        print(f"Erro ao criar tabelas: {e}")

def add_sample_data(conn):
    """Adiciona usuários e transações de exemplo."""
    users = [
        ("user1@test.com", bcrypt.hashpw(b"senha123", bcrypt.gensalt()).decode()),
        ("user2@test.com", bcrypt.hashpw(b"outrasenha", bcrypt.gensalt()).decode())
    ]
    transactions = [
        ("Salário", 58000, "income", "other", 1),
        ("Aluguel", 2000, "expense", "housing", 1),
        ("Compras", 1500, "expense", "food", 2)
    ]
    try:
        cursor = conn.cursor()
        cursor.executemany("INSERT INTO users (email, password_hash) VALUES (?, ?)", users)
        cursor.executemany(
            "INSERT INTO transactions (description, amount, type, category, user_id) VALUES (?, ?, ?, ?, ?)",
            transactions
        )
        conn.commit()
        print("Dados de exemplo inseridos!")
    except Error as e:
        print(f"Erro ao inserir dados: {e}")

def test_queries(conn):
    """Testa consultas para verificar a associação usuário-transações."""
    print("\n--- Testando consultas ---")
    cursor = conn.cursor()
    
    # Listar transações do usuário 1
    cursor.execute("SELECT * FROM transactions WHERE user_id = 1")
    print("\nTransações do User 1:")
    for row in cursor.fetchall():
        print(row)
    
    # Tentar inserir transação com user_id inválido (deve falhar)
    try:
        cursor.execute(
            "INSERT INTO transactions (description, amount, type, category, user_id) VALUES (?, ?, ?, ?, ?)",
            ("Teste inválido", 1000, "expense", "food", 999)  # user_id 999 não existe
        )
        conn.commit()
    except Error as e:
        print(f"\nErro esperado (user_id inválido): {e}")

def main():
    conn = create_connection()
    if conn:
        create_tables(conn)
        add_sample_data(conn)  # Comente esta linha se não quiser dados de exemplo
        test_queries(conn)
        conn.close()

if __name__ == "__main__":
    main()