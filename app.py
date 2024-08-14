import pyodbc
import logging
import bcrypt
from flask import Flask, request, render_template, redirect, url_for, session, flash
from prettytable import PrettyTable

# Configuração básica do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = 'hbcbusiness'  # Substitua com uma chave secreta segura

# Configuração do banco de dados
DB_CONFIG = {
    'server': '168.75.106.250,5433',
    'database': 'parcelaspagasHBC',
    'username': 'suporte.financob',
    'password': 'tQ@8csc.AGPz472e',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

def get_connection():
    connection_string = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']}"
    )
    return pyodbc.connect(connection_string)

@app.route('/', methods=['GET', 'POST'])
def search_documents():
    table_html = None
    num_results = None
    if 'user_id' in session:
        if request.method == 'POST':
            documento = request.form['documento']
            try:
                with get_connection() as conn:
                    logging.info("Conexão com o banco de dados estabelecida com sucesso.")
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT Documento, Nome, Agencia, Conta, Digito, Valor, Data_Debito, Parceiro "
                        "FROM PARCELAS_PAGAS WHERE Documento = ?", (documento,)
                    )
                    logging.info("Consulta executada com sucesso para o documento: %s", documento)

                    rows = cursor.fetchall()
                    num_results = len(rows)

                    if rows:
                        table = PrettyTable()
                        table.field_names = ['Documento', 'Nome', 'Agência', 'Conta', 'Dígito', 'Valor', 'Data de Débito', 'Parceiro']
                        for row in rows:
                            table.add_row(row)
                        table_html = table.get_html_string(attributes={"class": "pretty-table"})
                    else:
                        table_html = "<p class='message'>Nenhum resultado encontrado para o documento {}</p>".format(documento)
                        logging.info("Nenhum resultado encontrado para o documento: %s", documento)

            except pyodbc.Error as db_err:
                logging.error(f"Erro ao conectar ou consultar o banco de dados: {db_err}")
                table_html = "<p class='message'>Erro ao conectar ao banco de dados. Por favor, tente novamente mais tarde.</p>"
            except Exception as e:
                logging.error(f"Erro inesperado: {e}")
                table_html = "<p class='message'>Ocorreu um erro inesperado. Por favor, tente novamente mais tarde.</p>"

        return render_template('search.html', table=table_html, num_results=num_results)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            with get_connection() as conn:
                logging.info("Conexão com o banco de dados estabelecida com sucesso.")
                cursor = conn.cursor()
                cursor.execute("SELECT id, password FROM users WHERE email = ?", (email,))
                user = cursor.fetchone()

                if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                    session['user_id'] = user.id
                    return redirect(url_for('search_documents'))
                else:
                    flash('Email ou senha inválidos.', 'danger')

        except pyodbc.Error as db_err:
            logging.error(f"Erro ao conectar ou consultar o banco de dados: {db_err}")
            flash('Erro ao conectar ao banco de dados. Por favor, tente novamente mais tarde.', 'danger')
        except Exception as e:
            logging.error(f"Erro inesperado: {e}")
            flash('Ocorreu um erro inesperado. Por favor, tente novamente mais tarde.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return render_template('register.html')

        if len(password) < 8 or len(password) > 16:
            flash('A senha deve ter entre 8 e 16 caracteres.', 'danger')
            return render_template('register.html')

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            with get_connection() as conn:
                logging.info("Conexão com o banco de dados estabelecida com sucesso.")
                cursor = conn.cursor()
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
                    CREATE TABLE users (
                        id INT PRIMARY KEY IDENTITY(1,1),
                        name NVARCHAR(100),
                        email NVARCHAR(100) UNIQUE,
                        phone NVARCHAR(20),
                        password NVARCHAR(255)  -- Aumentando o tamanho da coluna password
                    )
                """)
                cursor.execute("INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)", (name, email, phone, hashed_password.decode('utf-8')))
                conn.commit()
                flash('Registro realizado com sucesso. Você pode fazer login agora.', 'success')
                return redirect(url_for('login'))

        except pyodbc.Error as db_err:
            logging.error(f"Erro ao conectar ou consultar o banco de dados: {db_err}")
            flash('Erro ao conectar ao banco de dados. Por favor, tente novamente mais tarde.', 'danger')
        except Exception as e:
            logging.error(f"Erro inesperado: {e}")
            flash('Ocorreu um erro inesperado. Por favor, tente novamente mais tarde.', 'danger')

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except SystemExit as e:
        logging.error(f"Erro ao iniciar o servidor: {e}")
