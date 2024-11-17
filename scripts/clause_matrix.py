# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

clause_matrix = {
    "Preserve legal mentions in source code": {},
    "Preserve legal mentions in source code": {},
    "Reproduce license and legal mentions in documentation": {},
    "Do not use project or contributor names for endorsement or promotion.": {},
    "Add specific legal mentions in the documentation": {},
    "Add specific legal mentions in the user interface (if applicable)": {},
    "Add specific mentions in the source code": {},
    "Display legal mentions in the user interface (if applicable)": {},
    "Do not use project or contributor names for endorsement or promotion.": {},
    "Inability to Comply Due to Statute or Regulation": {},
    "Indemnify contributors against claims": {},
    "Libraries must stay libraries": {},
    "Preserve legal mentions in source code": {},
    "Providing an offer": {},
    "Providing CSC to end user": {},
    "Reproduce license and legal mentions in documentation": {},
    "Respect trademarks": {},
    "Track and mention modifications in the source code": {},
    "Default license is Apache-2.0": {},
    "Add specific mentions in advertising": {
        "restriction": True
    },
    "Do not enforce patent rights (Patent peace)": {
        "restriction": True
    },
    "Do not restrict the rights of the license": {    
        "restriction": False,
        "outbound_expression": "inbound_obligation is not a restriction"
    },
    "Don't sell the software in itself": {
        "restriction": True,
    },
    "Inform about potential additionnal IP rights": {
        "restriction": True,
    },
    "License Agreement must exclude other contributors for additionnal terms": {
        "restriction": True,
    },
    "Non Tivoization": {
        "restriction": True,
    },
    "Providing Modifications to original author": {
        "restriction": True,
    },
    "Strong Copyleft": {
        "restriction": False,
        "inbound_expression": "inbound_license same as outbound_license or inbound_obligation is excepted",
        # if the inbound obligation is Copyleft, then outbound license must be the same as inbound license
        "outbound_expression": "inbound_license has not obligation \"Strong Copyleft\" or inbound_license same as outbound_license"
        # if the outbound obligation is Copyleft, then either incoming is not Copyleft or outbound license must be the same as inbound license
    },
    "Weak Copyleft": {},
    "Dont implement Anti-Circumvention Law.": {
        "restriction": True
    },
    "Independance from external data and code":{
        "restriction": False,
    },
    "Extending 3rd party patent grants to everyone": {
        "restriction": True,
    },
    "Modification must be pacakged as patches": {
        "restriction": True,
    },
    "allow reverse engineering and moification for private use": {},
    "__dummy_obligation__": {
        "restriction": True,
    }
}

unused = {
    "Maintain display of branding (trademark and logo)": {
        "restriction": True
    },
    "Making modified version substituable": {
        "restriction": True
    },
    "SaaS : mentions": {
        "restriction": True
    },
    "SaaS : network Copyleft": {
        "restriction": True
    },
    "alllow reverse engineering": {
        "inbound_compatible": "yes",
    },
    "License agreement : do not restrict reverse engineering for interoperability": {
        "inbound_compatible": "yes",
    },
}


