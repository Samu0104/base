# Importação das bibliotecas permitidas
from flask import Flask, render_template, request, redirect, session
import sqlite3
import re

# Criação da aplicação Flask
app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessário para usar sessões

# Função para obter a conexão com o banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect('BancoDeDados.db')
    conn.row_factory = sqlite3.Row
    return conn

# Função para criar tabelas no banco de dados, caso não existam
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Criação da tabela 'conta'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_sobrenome TEXT NOT NULL,
            data_nasc TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')
    # Criação da tabela 'compra'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compra (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            nTelefone TEXT NOT NULL,
            cep TEXT NOT NULL,
            nCasa TEXT NOT NULL,
            idproduto INTEGER NOT NULL,
            qtd INTEGER NOT NULL,
            FOREIGN KEY (idproduto) REFERENCES produto(id)
        )
    ''')
    # Criação da tabela 'produto'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produto (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            tamanho TEXT NOT NULL,
            id_setor INTEGER NOT NULL,
            FOREIGN KEY(id_setor) REFERENCES setor(id)
        )
    ''')
    # Criação da tabela 'setor'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS setor (
            id INTEGER PRIMARY KEY,
            genero TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Rota para a página inicial
@app.route('/')
def homepage():
    return render_template("index.html")

# Rota para a página de login
@app.route('/entrar', methods=['GET', 'POST'])
def entrar():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']
        if not email or not senha:
            return "Erro: Todos os campos são obrigatórios."
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM conta WHERE email = ? AND senha = ?', (email, senha))
            usuario = cursor.fetchone()
            if usuario:
                session['usuario_id'] = usuario['id']  # Armazena o ID do usuário na sessão
                session['usuario_nome'] = usuario['nome_sobrenome']  # Armazena o nome do usuário na sessão
                return redirect('/dashboard')  # Redireciona para a página do dashboard
            else:
                return "Erro: Usuário ou senha inválida."
        except sqlite3.Error as e:
            return f"Erro no banco de dados: {str(e)}"
        finally:
            conn.close()
    return render_template("entrar.html")

# Rota para a página do dashboard do usuário
@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect('/entrar')  # Redireciona para login se não estiver logado
    return render_template('dashboard.html', usuario_nome=session['usuario_nome'])

# Rota para a página de logout
@app.route('/sair')
def sair():
    session.pop('usuario_id', None)  # Remove o ID do usuário da sessão
    session.pop('usuario_nome', None)  # Remove o nome do usuário da sessão
    return redirect('/')  # Redireciona para a página inicial

# Outras rotas (como cadastrar, comprar, etc.) permanecem as mesmas

if __name__ == '__main__':
    create_table()
    app.run(debug=True)