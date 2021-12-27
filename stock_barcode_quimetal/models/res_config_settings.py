from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    google_drive_folder = fields.Char("Google Drive Folder", default="1hepo62atArDlCxGtNuxwuHHeCHRx0yEs")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            google_drive_folder=self.env["ir.config_parameter"].sudo().get_param("google_drive_folder"),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        for record in self:
            self.env['ir.config_parameter'].sudo().set_param("google_drive_folder", record.google_drive_folder)
