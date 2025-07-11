import sqlite3
from sqlite3 import Error
import bcrypt
from datetime import datetime

DATABASE = "finance.db"

def create_connection():
    """Cria conexão com o SQLite e ativa chaves estrangeiras."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        conn.execute("PRAGMA foreign_keys = ON")
        print("Conexão com SQLite estabelecida.")
        return conn
    except Error as e:
        print(f"Erro ao conectar ao SQLite: {e}")
        return None

def create_tables(conn):
    """Cria todas as tabelas necessárias."""
    tables = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
            category TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS user_salary (
            user_id INTEGER PRIMARY KEY,
            amount REAL NOT NULL,
            payment_day INTEGER NOT NULL CHECK (payment_day BETWEEN 1 AND 31),
            currency TEXT DEFAULT 'BRL',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS category_limits (
            user_id INTEGER,
            category TEXT,
            monthly_limit REAL NOT NULL,
            PRIMARY KEY (user_id, category),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS financial_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            target_amount REAL NOT NULL,
            target_date DATE NOT NULL,
            current_amount REAL DEFAULT 0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    ]
    
    try:
        cursor = conn.cursor()
        for table in tables:
            cursor.execute(table)
        conn.commit()
        print("Tabelas criadas com sucesso!")
    except Error as e:
        print(f"Erro ao criar tabelas: {e}")

def add_sample_data(conn):
    """Adiciona dados de exemplo para testes."""
    try:
        cursor = conn.cursor()
        
        tables = [
            "financial_goals",
            "category_limits",
            "transactions",
            "user_salary",
            "users"
        ]
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")

        users = [
            ("user1@test.com", bcrypt.hashpw(b"senha123", bcrypt.gensalt()).decode(), "João Silva"),
            ("user2@test.com", bcrypt.hashpw(b"outrasenha", bcrypt.gensalt()).decode(), "Maria Souza")
        ]
        cursor.executemany(
            "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)", 
            users
        )

        salaries = [
            (1, 5800.00, 5, 'BRL'),  # User 1, R$5800, dia 5
            (2, 8500.50, 10, 'BRL')   # User 2, R$8500.50, dia 10
        ]
        cursor.executemany(
            "INSERT INTO user_salary (user_id, amount, payment_day, currency) VALUES (?, ?, ?, ?)",
            salaries
        )

        categories = [
            (1, "food", 1500.00),
            (1, "transport", 800.00),
            (1, "entertainment", 500.00),
            (2, "food", 2000.00),
            (2, "transport", 1200.00)
        ]
        cursor.executemany(
            "INSERT INTO category_limits (user_id, category, monthly_limit) VALUES (?, ?, ?)",
            categories
        )

        transactions = [
            (1, "Salário ACME", 5800.00, "income", "salary", "2023-06-05"),
            (1, "Aluguel", 2500.00, "expense", "housing", "2023-06-10"),
            (1, "Supermercado", 450.50, "expense", "food", "2023-06-12"),
            (1, "Uber", 35.00, "expense", "transport", "2023-06-15"),
            (2, "Salário XYZ", 8500.50, "income", "salary", "2023-06-10"),
            (2, "IPVA", 1200.00, "expense", "transport", "2023-06-15"),
            (2, "Restaurante", 120.00, "expense", "food", "2023-06-20")
        ]
        cursor.executemany(
            """INSERT INTO transactions 
               (user_id, description, amount, type, category, date) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            transactions
        )

        goals = [
            (1, 10000.00, "2023-12-31", "Reserva de emergência", 2500.00),
            (2, 20000.00, "2024-06-01", "Entrada para apartamento", 5000.00)
        ]
        cursor.executemany(
            """INSERT INTO financial_goals 
               (user_id, target_amount, target_date, description, current_amount) 
               VALUES (?, ?, ?, ?, ?)""",
            goals
        )

        conn.commit()
        print("Dados de exemplo inseridos com sucesso!")
        
    except Error as e:
        conn.rollback()
        print(f"Erro ao inserir dados de exemplo: {e}")

def test_queries(conn):
    """Testa consultas importantes."""
    print("\n--- Testando consultas ---")
    cursor = conn.cursor()
    
    print("\n[TESTE 1] Transações do usuário 1 com salário:")
    cursor.execute("""
        SELECT t.description, t.amount, t.type, t.category, t.date, s.amount as salary
        FROM transactions t
        LEFT JOIN user_salary s ON t.user_id = s.user_id
        WHERE t.user_id = 1
        ORDER BY t.date DESC
    """)
    for row in cursor.fetchall():
        print(row)
    
    print("\n[TESTE 2] Limites de categoria:")
    cursor.execute("""
        SELECT u.email, cl.category, cl.monthly_limit 
        FROM category_limits cl
        JOIN users u ON cl.user_id = u.id
        ORDER BY cl.user_id
    """)
    for row in cursor.fetchall():
        print(f"Usuário: {row[0]} | Categoria: {row[1]} | Limite: R${row[2]:.2f}")
    
    print("\n[TESTE 3] Metas financeiras:")
    cursor.execute("""
        SELECT u.email, fg.target_amount, fg.current_amount, 
               fg.target_date, fg.description
        FROM financial_goals fg
        JOIN users u ON fg.user_id = u.id
    """)
    for row in cursor.fetchall():
        progresso = (row[2]/row[1])*100
        print(f"Usuário: {row[0]} | Meta: {row[4]} | Valor: R${row[1]:.2f} | Progresso: {progresso:.1f}%")
    
    print("\n[TESTE 4] Tentando inserir transação com user_id inválido:")
    try:
        cursor.execute(
            "INSERT INTO transactions (user_id, description, amount, type, category) VALUES (?, ?, ?, ?, ?)",
            (999, "Teste inválido", 100.00, "expense", "food")
        )
        conn.commit()
    except Error as e:
        print(f"ERRO ESPERADO: {e}")

def main():
    conn = create_connection()
    if conn:
        create_tables(conn)
        add_sample_data(conn)
        test_queries(conn)
        conn.close()

if __name__ == "__main__":
    main()