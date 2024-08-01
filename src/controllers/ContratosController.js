const ContratosModel = require('../models/ContratosModel.js');
class ContratosController {
    constructor() {
        this.model = ContratosModel;
    }

    async index(req, res) {
        res.render('index', { tableData: [] });
    }

    async buscarContratos(req, res) {
        try {
            const documento = req.body.documento;
            let tableData = [];
            const data = await this.model.buscarContratos(documento);
            tableData = data.recordset.map(row => ({
                Documento: row.Documento,
                Nome: row.Nome,
                Agencia: row.Agencia,
                Conta: row.Conta,
                Digito: row.Digito,
                Valor: row.Valor,
                Data_Debito: row.Data_Debito,
                Parceiro: row.Parceiro
            }));
            res.render('index', { tableData });
        } catch (err) {
            console.error('Erro ao conectar ou consultar o banco de dados:', err);
        }
    }
}

module.exports = new ContratosController();