from odoo import fields,models,api, _

class res_config(models.TransientModel): 
    _inherit='res.config.settings'
        

    as_url = fields.Char(string='Dirección de Enpoint')
    as_login = fields.Char(string='Login')
    as_password = fields.Char(string='Password')
    
    @api.model
    def get_values(self):
        res = super(res_config, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(as_url = str(params.get_param('as_equimetal_webservice.as_url')))
        res.update(as_login = str(params.get_param('as_equimetal_webservice.as_login')))
        res.update(as_password = str(params.get_param('as_equimetal_webservice.as_password')))
        return res
    
    def set_values(self):
        res = super(res_config,self).set_values()
        ir_parameter = self.env['ir.config_parameter'].sudo()        
        ir_parameter.set_param('as_equimetal_webservice.as_url', self.as_url)
        ir_parameter.set_param('as_equimetal_webservice.as_login', self.as_login)
        ir_parameter.set_param('as_equimetal_webservice.as_password', self.as_password)
        return res
        
