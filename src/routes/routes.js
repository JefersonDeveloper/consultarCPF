const express = require('express');
const routes = express.Router();
const contratos = require('../controllers/ContratosController');

routes.get('/', (req, res) => {
    contratos.index(req, res);
});

routes.post('/', (req, res) => {
    contratos.buscarContratos(req, res);
});

module.exports = routes;