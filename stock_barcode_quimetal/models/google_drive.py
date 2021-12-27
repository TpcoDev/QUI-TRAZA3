import requests
import json
import logging

from odoo.exceptions import UserError, Warning
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class GoogleDriveConfig(models.Model):
    _inherit = 'google.drive.config'

    @api.model
    def upload_pdf(self, file_name, file_content):
        access_token = self.get_access_token()
        folder_id = self.env['ir.config_parameter'].sudo().get_param('google_drive_folder')

        headers = {"Authorization": "Bearer " + access_token}
        try:
            para = {
                "name": file_name,
                "parents": [folder_id],
            }
            files = {
                "data": ("metadata", json.dumps(para), "application/json; charset=UTF-8"),
                "file": file_content
            }
            req = requests.post("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
                                headers=headers, files=files)
            if req.status_code == 200:
                json_res = json.loads(req.text)
                doc_id = json_res['id']
                _logger.info("Upload file %s to google drive successfully" % file_name)
                raise Warning(_("Upload file %s to google drive successfully" % file_name))
            else:
                raise UserError(
                    'There is a problem with the connection to Google Drive. Please contact your administrator.')

        except requests.HTTPError:
            raise UserError(_("The Google Template cannot be found. Maybe it has been deleted."))
