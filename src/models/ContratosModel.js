const conn = require('../config/DbConfig');
class ContratosModel{
    constructor(conn){
        this.conn = conn;
    }
    async buscarContratos(documento){
        try{
        const sql = 'SELECT Documento, Nome, Agencia, Conta, Digito, Valor, Data_Debito, Parceiro FROM PARCELAS_PAGAS WHERE Documento = @documento';
        const pool = await this.conn().pool;
        const data = await pool.request()
            .input('documento', documento)
            .query(sql);
        return data;
        }catch(err){
            console.error('Database connection failed: ', err);
            return [];
        }
    }
}

module.exports = new ContratosModel(conn);