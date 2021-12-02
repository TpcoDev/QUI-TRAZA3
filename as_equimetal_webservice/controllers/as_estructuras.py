# -*- coding: utf-8 -*-
from odoo.tools.translate import _
from odoo import http
from odoo import http
from odoo.http import request
from datetime import datetime
from bs4 import BeautifulSoup
import json
import sys
import uuid
import yaml
import logging

_logger = logging.getLogger(__name__)

from werkzeug import urls
from werkzeug.wsgi import wrap_file

esquema_ws001 = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "type": "object",
    "title": "The root schema",
    "description": "The root schema comprises the entire JSON document.",
    "default": {},
    "examples": [
        {
            "jsonrpc": "2.0",
            "method": "ws001",
            "params": {
                "DocNum": "1234",
                "DocDate": "2021-02-23T18:25:43",
                "CardCode": "5678",
                "CardName": "Nombre Proveedor SAP",
                "WarehouseCode": "01",
                "DatosProdOC": [
                    {
                        "LineNum": 1,
                        "ItemCode": "91011",
                        "ItemDescription": "Nombre de Producto SAP 01",
                        "Quantity": 1.0,
                        "MeasureUnit": "Kg"
                    }
                ]
            },
            "id": 1
        }
    ],
    "required": [],
    "properties": {
        "jsonrpc": {"type": "string"},
        "method": {"type": "string"},
        "params": {"type": "object",
                   "title": "The params schema",
                   "description": "An explanation about the purpose of this instance.",
                   "default": {},
                   "examples": [
                       {
                           "DocNum": "1234",
                           "DocDate": "2021-02-23T18:25:43",
                           "CardCode": "5678",
                           "CardName": "Nombre Proveedor SAP",
                           "WarehouseCode": "01",
                           "DatosProdOC": [
                               {
                                   "LineNum": 1,
                                   "ItemCode": "91011",
                                   "ItemDescription": "Nombre de Producto SAP 01",
                                   "Quantity": 1.0,
                                   "MeasureUnit": "Kg"
                               }
                           ]
                       }
                   ],
                   "required": [],
                   "properties": {
                       "DocNum": {"type": "string"},
                       "DocDate": {"type": "string"},
                       "CardCode": {"type": "string"},
                       "CardName": {"type": "string"},
                       "WarehouseCode": {"type": "string"},
                       "DatosProdOC": {
                           "$id": "#/properties/params/properties/DatosProdOC",
                           "type": "array",
                           "title": "The DatosProdOC schema",
                           "description": "An explanation about the purpose of this instance.",
                           "default": [],
                           "examples": [
                               [
                                   {
                                       "LineNum": 1,
                                       "ItemCode": "91011",
                                       "ItemDescription": "Nombre de Producto SAP 01",
                                       "Quantity": 1.0,
                                       "MeasureUnit": "Kg"
                                   }
                               ]
                           ],
                           "items": {
                               "$id": "#/properties/params/properties/DatosProdOC/items",
                               "type": "object",
                               "title": "The items schema",
                               "description": "An explanation about the purpose of this instance.",
                               "default": {},
                               "examples": [
                                   [
                                       {
                                           "LineNum": 1,
                                           "ItemCode": "91011",
                                           "ItemDescription": "Nombre de Producto SAP 01",
                                           "Quantity": 1.0,
                                           "MeasureUnit": "Kg"
                                       }
                                   ]
                               ],
                               "required": ["LineNum", "ItemCode", "ItemDescription", "Quantity", "MeasureUnit"],
                               "properties": {
                                   "LineNum": 1,
                                   "ItemCode": {"type": "string"},
                                   "ItemDescription": {"type": "string"},
                                   "Quantity": {"type": "number"},
                                   "MeasureUnit": {"type": "string"}
                               }
                           }
                       }
                   }
                   },
        "id": {"type": "integer"}
    }
}

esquema_ws023 = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "type": "object",
    "title": "The root schema",
    "description": "The root schema comprises the entire JSON document.",
    "default": {},
    "examples": [
        {
            "jsonrpc": "2.0",
            "method": "ws023",
            "params": {
                "DocNum": "1234",
                "DocDate": "2021-02-23T18:25:43",
                "WarehouseCodeOrigin": "01",
                "WarehouseCodeDestination": "02",
                "DatosProdOC": [
                    {
                        "ItemCode": "91011",
                        "ItemDescription": "Nombre de Producto SAP 01",
                        "Quantity": 1.0,
                        "MeasureUnit": "Kg",
                        "Detalle": [
                            {
                                "DistNumber": "43554",
                                "Quantity": 3,
                                "DateProduction": "2021-04-23T18:25:43",
                                "DateExpiration": "2021-05-23T18:25:43"
                            }
                        ]
                    }
                ]
            },
            "id": 23
        }
    ],
    "required": [],
    "properties": {
        "jsonrpc": {
            "$id": "#/properties/jsonrpc",
            "type": "string",
            "title": "The jsonrpc schema",
            "description": "An explanation about the purpose of this instance.",
            "default": "",
            "examples": [
                "2.0"
            ]
        },
        "method": {
            "$id": "#/properties/method",
            "type": "string",
            "title": "The method schema",
            "description": "An explanation about the purpose of this instance.",
            "default": "",
            "examples": [
                "ws023"
            ]
        },
        "params": {
            "$id": "#/properties/params",
            "type": "object",
            "title": "The params schema",
            "description": "An explanation about the purpose of this instance.",
            "default": {},
            "examples": [
                {
                    "DocNum": "1234",
                    "DocDate": "2021-02-23T18:25:43",
                    "WarehouseCodeOrigin": "01",
                    "WarehouseCodeDestination": "02",
                    "DatosProdOC": [
                        {
                            "ItemCode": "91011",
                            "ItemDescription": "Nombre de Producto SAP 01",
                            "Quantity": 1.0,
                            "MeasureUnit": "Kg",
                            "Detalle": [
                                {
                                    "DistNumber": "43554",
                                    "Quantity": 3,
                                    "DateProduction": "2021-04-23T18:25:43",
                                    "DateExpiration": "2021-05-23T18:25:43"
                                }
                            ]
                        }
                    ]
                }
            ],
            "required": [],
            "properties": {
                "DocNum": {
                    "$id": "#/properties/params/properties/DocNum",
                    "type": "string",
                    "title": "The DocNum schema",
                    "description": "An explanation about the purpose of this instance.",
                    "default": "",
                    "examples": [
                        "1234"
                    ]
                },
                "DocDate": {
                    "$id": "#/properties/params/properties/DocDate",
                    "type": "string",
                    "title": "The DocDate schema",
                    "description": "An explanation about the purpose of this instance.",
                    "default": "",
                    "examples": [
                        "2021-02-23T18:25:43"
                    ]
                },
                "WarehouseCodeOrigin": {
                    "$id": "#/properties/params/properties/WarehouseCodeOrigin",
                    "type": "string",
                    "title": "The WarehouseCodeOrigin schema",
                    "description": "An explanation about the purpose of this instance.",
                    "default": "",
                    "examples": [
                        "01"
                    ]
                },
                "WarehouseCodeDestination": {
                    "$id": "#/properties/params/properties/WarehouseCodeDestination",
                    "type": "string",
                    "title": "The WarehouseCodeDestination schema",
                    "description": "An explanation about the purpose of this instance.",
                    "default": "",
                    "examples": [
                        "02"
                    ]
                },
                "DatosProdOC": {
                    "$id": "#/properties/params/properties/DatosProdOC",
                    "type": "array",
                    "title": "The DatosProdOC schema",
                    "description": "An explanation about the purpose of this instance.",
                    "default": [],
                    "examples": [
                        [
                            {
                                "ItemCode": "91011",
                                "ItemDescription": "Nombre de Producto SAP 01",
                                "Quantity": 1.0,
                                "MeasureUnit": "Kg",
                                "Detalle": [
                                    {
                                        "DistNumber": "43554",
                                        "Quantity": 3,
                                        "DateProduction": "2021-04-23T18:25:43",
                                        "DateExpiration": "2021-05-23T18:25:43"
                                    }
                                ]
                            }
                        ]
                    ],
                    "items": {
                        "$id": "#/properties/params/properties/DatosProdOC/items",
                        "anyOf": [
                            {
                                "$id": "#/properties/params/properties/DatosProdOC/items/anyOf/0",
                                "type": "object",
                                "title": "The first anyOf schema",
                                "description": "An explanation about the purpose of this instance.",
                                "default": {},
                                "examples": [
                                    {
                                        "ItemCode": "91011",
                                        "ItemDescription": "Nombre de Producto SAP 01",
                                        "Quantity": 1.0,
                                        "MeasureUnit": "Kg",
                                        "Detalle": [
                                            {
                                                "DistNumber": "43554",
                                                "Quantity": 3,
                                                "DateProduction": "2021-04-23T18:25:43",
                                                "DateExpiration": "2021-05-23T18:25:43"
                                            }
                                        ]
                                    }
                                ],
                                "required": [],
                                "properties": {
                                    "ItemCode": {
                                        "$id": "#/properties/params/properties/DatosProdOC/items/anyOf/0/properties/ItemCode",
                                        "type": "string",
                                        "title": "The ItemCode schema",
                                        "description": "An explanation about the purpose of this instance.",
                                        "default": "",
                                        "examples": [
                                            "91011"
                                        ]
                                    },
                                    "ItemDescription": {
                                        "$id": "#/properties/params/properties/DatosProdOC/items/anyOf/0/properties/ItemDescription",
                                        "type": "string",
                                        "title": "The ItemDescription schema",
                                        "description": "An explanation about the purpose of this instance.",
                                        "default": "",
                                        "examples": [
                                            "Nombre de Producto SAP 01"
                                        ]
                                    },
                                    "Quantity": {
                                        "$id": "#/properties/params/properties/DatosProdOC/items/anyOf/0/properties/Quantity",
                                        "type": "number",
                                        "title": "The Quantity schema",
                                        "description": "An explanation about the purpose of this instance.",
                                        "default": 0.0,
                                        "examples": [
                                            1.0
                                        ]
                                    },
                                    "MeasureUnit": {
                                        "$id": "#/properties/params/properties/DatosProdOC/items/anyOf/0/properties/MeasureUnit",
                                        "type": "string",
                                        "title": "The MeasureUnit schema",
                                        "description": "An explanation about the purpose of this instance.",
                                        "default": "",
                                        "examples": [
                                            "Kg"
                                        ]
                                    },
                                    "Detalle": {
                                        "$id": "#/properties/params/properties/DatosProdOC/items/anyOf/0/properties/Detalle",
                                        "type": "array",
                                        "title": "The Detalle schema",
                                        "description": "An explanation about the purpose of this instance.",
                                        "default": [],
                                        "examples": [
                                            [
                                                {
                                                    "DistNumber": "43554",
                                                    "Quantity": 3,
                                                    "DateProduction": "2021-04-23T18:25:43",
                                                    "DateExpiration": "2021-05-23T18:25:43"
                                                }
                                            ]
                                        ],
                                        "items": {
                                            "$id": "#/properties/params/properties/DatosProdOC/items/anyOf/0/properties/Detalle/items",
                                            "anyOf": [
                                                {
                                                    "$id": "#/properties/params/properties/DatosProdOC/items/anyOf/0/properties/Detalle/items/anyOf/0",
                                                    "type": "object",
                                                    "title": "The first anyOf schema",
                                                    "description": "An explanation about the purpose of this instance.",
                                                    "default": {},
                                                    "examples": [
                                                        {
                                                            "DistNumber": "43554",
                                                            "Quantity": 3,
                                                            "DateProduction": "2021-04-23T18:25:43",
                                                            "DateExpiration": "2021-05-23T18:25:43"
                                                        }
                                                    ],
                                                    "required": [
                                                        "DistNumber",
                                                        "Quantity",
                                                        "DateProduction",
                                                        "DateExpiration"
                                                    ],
                                                    "properties": {
                                                        "DistNumber": {
                                                            "$id": "#/properties/params/properties/DatosProdOC/items/anyOf/0/properties/Detalle/items/anyOf/0/properties/DistNumber",
                                                            "type": "string",
                                                            "title": "The DistNumber schema",
                                                            "description": "An explanation about the purpose of this instance.",
                                                            "default": "",
                                                            "examples": [
                                                                "43554"
                                                            ]
                                                        },
                                                        "Quantity": {
                                                            "$id": "#/properties/params/properties/DatosProdOC/items/anyOf/0/properties/Detalle/items/anyOf/0/properties/Quantity",
                                                            "type": "integer",
                                                            "title": "The Quantity schema",
                                                            "description": "An explanation about the purpose of this instance.",
                                                            "default": 0,
                                                            "examples": [
                                                                3
                                                            ]
                                                        },
                                                        "DateProduction": {
                                                            "$id": "#/properties/params/properties/DatosProdOC/items/anyOf/0/properties/Detalle/items/anyOf/0/properties/DateProduction",
                                                            "type": "string",
                                                            "title": "The DateProduction schema",
                                                            "description": "An explanation about the purpose of this instance.",
                                                            "default": "",
                                                            "examples": [
                                                                "2021-04-23T18:25:43"
                                                            ]
                                                        },
                                                        "DateExpiration": {
                                                            "$id": "#/properties/params/properties/DatosProdOC/items/anyOf/0/properties/Detalle/items/anyOf/0/properties/DateExpiration",
                                                            "type": "string",
                                                            "title": "The DateExpiration schema",
                                                            "description": "An explanation about the purpose of this instance.",
                                                            "default": "",
                                                            "examples": [
                                                                "2021-05-23T18:25:43"
                                                            ]
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        },
        "id": {
            "$id": "#/properties/id",
            "type": "integer",
            "title": "The id schema",
            "description": "An explanation about the purpose of this instance.",
            "default": 0,
            "examples": [
                23
            ]
        }
    }
}

esquema_ws001 = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "type": "object",
    "title": "The root schema",
    "description": "The root schema comprises the entire JSON document.",
    "default": {},
    "examples": [
        {
            "jsonrpc": "2.0",
            "method": "ws001",
            "params": {
                "DocNum": "1234",
                "DocDate": "2021-02-23T18:25:43",
                "CardCode": "5678",
                "CardName": "Nombre Proveedor SAP",
                "WarehouseCode": "01",
                "DatosProdOC": [
                    {
                        "ItemCode": "91011",
                        "ItemDescription": "Nombre de Producto SAP 01",
                        "Quantity": 1.0,
                        "MeasureUnit": "Kg"
                    }
                ]
            },
            "id": 1
        }
    ],
    "required": [],
    "properties": {
        "jsonrpc": {"type": "string"},
        "method": {"type": "string"},
        "params": {"type": "object",
                   "title": "The params schema",
                   "description": "An explanation about the purpose of this instance.",
                   "default": {},
                   "examples": [
                       {
                           "DocNum": "1234",
                           "DocDate": "2021-02-23T18:25:43",
                           "CardCode": "5678",
                           "CardName": "Nombre Proveedor SAP",
                           "WarehouseCode": "01",
                           "DatosProdOC": [
                               {
                                   "ItemCode": "91011",
                                   "ItemDescription": "Nombre de Producto SAP 01",
                                   "Quantity": 1.0,
                                   "MeasureUnit": "Kg"
                               }
                           ]
                       }
                   ],
                   "required": [],
                   "properties": {
                       "DocNum": {"type": "string"},
                       "DocDate": {"type": "string"},
                       "CardCode": {"type": "string"},
                       "CardName": {"type": "string"},
                       "WarehouseCode": {"type": "string"},
                       "DatosProdOC": {
                           "$id": "#/properties/params/properties/DatosProdOC",
                           "type": "array",
                           "title": "The DatosProdOC schema",
                           "description": "An explanation about the purpose of this instance.",
                           "default": [],
                           "examples": [
                               [
                                   {
                                       "ItemCode": "91011",
                                       "ItemDescription": "Nombre de Producto SAP 01",
                                       "Quantity": 1.0,
                                       "MeasureUnit": "Kg"
                                   }
                               ]
                           ],
                           "items": {
                               "$id": "#/properties/params/properties/DatosProdOC/items",
                               "type": "object",
                               "title": "The items schema",
                               "description": "An explanation about the purpose of this instance.",
                               "default": {},
                               "examples": [
                                   [
                                       {
                                           "ItemCode": "91011",
                                           "ItemDescription": "Nombre de Producto SAP 01",
                                           "Quantity": 1.0,
                                           "MeasureUnit": "Kg"
                                       }
                                   ]
                               ],
                               "required": ["ItemCode", "ItemDescription", "Quantity", "MeasureUnit"],
                               "properties": {
                                   "ItemCode": {"type": "string"},
                                   "ItemDescription": {"type": "string"},
                                   "Quantity": {"type": "number"},
                                   "MeasureUnit": {"type": "string"}
                               }
                           }
                       }
                   }
                   },
        "id": {"type": "integer"}
    }
}

esquema_ws016 = {
    "definitions": {},
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://example.com/object1616766586.json",
    "title": "Root",
    "type": "object",
    "properties": {
        "jsonrpc": {
            "$id": "#root/jsonrpc",
            "title": "Jsonrpc",
            "type": "string",
            "default": "",
            "pattern": "^.*$"
        },
        "method": {
            "$id": "#root/method",
            "title": "Method",
            "type": "string",
            "default": "",
            "pattern": "^.*$"
        },
        "params": {
            "$id": "#root/params",
            "title": "Params",
            "type": "object",
            "properties": {
                "DocNum": {
                    "$id": "#root/params/DocNum",
                    "title": "Docnum",
                    "type": "string",
                    "default": "",
                    "pattern": "^.*$"
                },
                "DocDate": {
                    "$id": "#root/params/DocDate",
                    "title": "Docdate",
                    "type": "string",
                    "default": "",
                    "pattern": "^.*$"
                },
                "CardCode": {
                    "$id": "#root/params/CardCode",
                    "title": "Cardcode",
                    "type": "string",
                    "default": "",
                    "pattern": "^.*$"
                },
                "CardName": {
                    "$id": "#root/params/CardName",
                    "title": "Cardname",
                    "type": "string",
                    "default": "",
                    "pattern": "^.*$"
                },
                "NumAtcard": {
                    "$id": "#root/params/NumAtcard",
                    "title": "Numatcard",
                    "type": "string",
                    "default": "",
                    "pattern": "^.*$"
                },
                "DocDueDate": {
                    "$id": "#root/params/DocDueDate",
                    "title": "Docduedate",
                    "type": "string",
                    "default": "",
                    "pattern": "^.*$"
                },
                "DatosProdOV": {
                    "$id": "#root/params/DatosProdOV",
                    "title": "Datosprodov",
                    "type": "array",
                    "default": [],
                    "items": {
                        "$id": "#root/params/DatosProdOV/items",
                        "title": "Items",
                        "type": "object",
                        "properties": {
                            "ItemCode": {
                                "$id": "#root/params/DatosProdOV/items/ItemCode",
                                "title": "Itemcode",
                                "type": "string",
                                "default": "",
                                "pattern": "^.*$"
                            },
                            "ItemDescription": {
                                "$id": "#root/params/DatosProdOV/items/ItemDescription",
                                "title": "Itemdescription",
                                "type": "string",
                                "default": "",
                                "pattern": "^.*$"
                            },
                            "Quantity": {
                                "$id": "#root/params/DatosProdOV/items/Quantity",
                                "title": "Quantity",
                                "type": "integer",
                                "default": 0
                            },
                            "MeasureUnit": {
                                "$id": "#root/params/DatosProdOV/items/MeasureUnit",
                                "title": "Measureunit",
                                "type": "string",
                                "default": "",
                                "pattern": "^.*$"
                            }
                        }
                    }

                }
            }
        }
    }
}


class AsWebservice(http.Controller):

    @http.route(['/api/ws001old', ], auth="public", type="json", method=['POST'], csrf=False)
    def request_ws001old(self, **post):
        post = yaml.load(request.httprequest.data)
        res = {}
        token = uuid.uuid4().hex
        try:
            uid = request.session.authenticate(post['db'], post['login'], post['password'])
            if uid:
                res['token'] = token
                request.session.logout()

                es_valido = self.validar_json(post, esquema=esquema_ws001)
                if es_valido:
                    return {
                        "Token": token,
                        "RespCode": 0,
                        "RespMessage": "El JSON ha sido validado y es CORRECTO",
                        "json_recibido": post
                    }
                else:
                    return {
                        "Token": token,
                        "RespCode": 0,
                        "RespMessage": "El JSON ha sido validado y es INCORRECTO",
                        "json_recibido": post
                    }
            else:
                res['error'] = "Login o Password erroneo"
                res_json = json.dumps(res)

                return res_json
        except Exception as e:
            return {
                "Token": token,
                "RespCode": -1,
                "RespMessage": "Error de conexión",
                "error": e.args
            }

    @http.route(['/api/ws001ok', ], auth="public", type="json", method=['POST'], csrf=False)
    def request_ws001ok(self, **post):
        # post = yaml.load(request.httprequest.data)
        res = {}
        token = uuid.uuid4().hex

        try:
            myapikey = request.httprequest.headers.get("Authorization")
            if myapikey == "123":
                res['token'] = token
                # request.session.logout()
                es_valido = self.validar_json(post, esquema=esquema_ws001)

                if es_valido:
                    return {
                        "Token": token,
                        "RespCode": 0,
                        "RespMessage": "OC cargadas correctamente"
                    }
                else:
                    return {
                        "Token": token,
                        "RespCode": -2,
                        "RespMessage": "Error de validación en mensaje de entrada"
                    }
            else:
                res['error'] = "Token inválido"
                res_json = json.dumps(res)

                return res_json
        except Exception as e:
            return {
                "Token": token,
                "RespCode": -1,
                "RespMessage": "Error de conexión",
                "error": e.args
            }

    @http.route(['/api/ws023ok', ], auth="public", type="json", method=['POST'], csrf=False)
    def request_ws023ok(self, **post):
        # post = yaml.load(request.httprequest.data)
        res = {}
        token = uuid.uuid4().hex

        try:
            myapikey = request.httprequest.headers.get("Authorization")
            if myapikey == "123":
                res['token'] = token
                # request.session.logout()
                es_valido = self.validar_json(post, esquema=esquema_ws023)

                if es_valido:
                    return {
                        "Token": token,
                        "RespCode": 0,
                        "RespMessage": "OT recibidas correctamente"
                    }
                else:
                    return {
                        "Token": token,
                        "RespCode": -2,
                        "RespMessage": "Error de validación en mensaje de entrada"
                    }
            else:
                res['error'] = "Token inválido"
                res_json = json.dumps(res)

                return res_json
        except Exception as e:
            return {
                "Token": token,
                "RespCode": -1,
                "RespMessage": "Error de conexión",
                "error": e.args
            }

    @http.route(['/api/ws016ok', ], auth="public", type="json", method=['POST'], csrf=False)
    def request_ws016ok(self, **post):
        # post = yaml.load(request.httprequest.data)
        res = {}
        token = uuid.uuid4().hex

        try:
            myapikey = request.httprequest.headers.get("Authorization")
            if myapikey == "123":
                res['token'] = token
                # request.session.logout()
                es_valido = self.validar_json(post, esquema=esquema_ws016)

                if es_valido:
                    return {
                        "Token": token,
                        "RespCode": 0,
                        "RespMessage": "OV recibidas correctamente"
                    }
                else:
                    return {
                        "Token": token,
                        "RespCode": -2,
                        "RespMessage": "Error de validación en mensaje de entrada"
                    }
            else:
                res['error'] = "Token inválido"
                res_json = json.dumps(res)

                return res_json
        except Exception as e:
            return {
                "Token": token,
                "RespCode": -1,
                "RespMessage": "Error de conexión",
                "error": e.args
            }

    def validar_json(self, el_json, esquema):
        try:
            validate(instance=el_json, schema=esquema)
        except jsonschema.exceptions.ValidationError as err:
            return False
        return True

    @http.route('/api/ws002ok', auth='public', method=['GET'], csrf=False)
    def get_ws001ok(self, **kw):
        try:
            res = '{"Token":"20210219120000", "RespCode":0, "RespMessage":"OC recibidas correctamente"}'
            print('res: ', str(res))
            return Response(res, content_type='application/json;charset=utf-8', status=200)
        except Exception as e:
            print('error: ', str(e))
            return Response(json.dumps({'error': str(e)}), content_type='application/json;charset=utf-8', status=500)
