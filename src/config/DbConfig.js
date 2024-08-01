const sql = require('mssql');

const dbConfig = {
    user: 'adminhbc',
    password: '9gBHG8#bcb',
    server: 'parcelaspagashcb.database.windows.net',
    port: 1433,
    database: 'parcelasPagashbc',
    options: {
        encrypt: true // Necessário para Azure SQL
    }
};

async function conn() {
    try {
        const pool = await sql.connect(dbConfig);
        console.log('Connected to the database');
        return pool;
    } catch (err) {
        console.error('Error ao conecta a database', err);
    }
}

module.exports = conn;