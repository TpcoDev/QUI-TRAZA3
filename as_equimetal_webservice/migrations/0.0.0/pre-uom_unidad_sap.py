# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("POST Update --> {}".format(version))

    query = "ALTER TABLE uom_uom DROP COLUMN IF EXISTS unidad_sap;"
    cr.execute(query)