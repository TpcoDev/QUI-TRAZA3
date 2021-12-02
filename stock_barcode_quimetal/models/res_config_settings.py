from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    save_file_config = fields.Boolean()
    host_name = fields.Char("Host Name")
    shared_folder = fields.Char("Shared Folder")
    protocol = fields.Selection([('tcp', 'TCP'), ('ftp', 'FTP')], string="Protocol", default="tcp")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            host_name=self.env["ir.config_parameter"].sudo().get_param("host_name"),
            save_file_config=self.env["ir.config_parameter"].sudo().get_param("save_file_config"),
            protocol=self.env["ir.config_parameter"].sudo().get_param("protocol"),
            shared_folder=self.env["ir.config_parameter"].sudo().get_param("shared_folder"),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        for record in self:
            self.env['ir.config_parameter'].sudo().set_param("host_name", record.host_name)
            self.env['ir.config_parameter'].sudo().set_param("save_file_config", record.save_file_config)
            self.env['ir.config_parameter'].sudo().set_param("protocol", record.protocol)
            self.env['ir.config_parameter'].sudo().set_param("shared_folder", record.shared_folder)
