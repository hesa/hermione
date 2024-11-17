#!/bin/env python3

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import glob
import json
import logging
import os
import re
import sys

#logging.basicConfig(level=logging.DEBUG)


from fix_hermine_data import fix_hermine_license
from fix_hermine_data import fix_hermine_generic
from clause_matrix import clause_matrix
from flame.license_db import FossLicenses # noqa: I900

from flict.flictlib.arbiter import Arbiter

modified_triggers = ['Altered', 'Unmodified']
triggers = ['DistributionSource', 'DistributionNonSource']

HERMINE_DATA_DIR = os.path.join('..','hermine-data')
HERMINE_LICENSES_DIR = os.path.join(HERMINE_DATA_DIR, 'licenses')
HERMINE_GENERICS_DIR = os.path.join(HERMINE_DATA_DIR, 'generics')

HERMIONE_LICENSE_DIR = os.path.join('var','licenses')
HERMIONE_GENERICS_DIR = os.path.join('var','generics')

LICENSE_DIRS = [ HERMINE_LICENSES_DIR, HERMIONE_LICENSE_DIR ] 
CLAUSE_DIRS = [ HERMINE_GENERICS_DIR ]
CLAUSE_DIRS = [ HERMINE_GENERICS_DIR, HERMIONE_GENERICS_DIR ]

licenses = None
generics = None

COMPATIBLE_YES = "yes"
COMPATIBLE_NO = "no"
COMPATIBLE_UNKNOWN = "unknown"

fl = FossLicenses()


def read_generics():
    generics = []
    for dir in CLAUSE_DIRS:
        for i in glob.glob(f'{dir}/*.json'):
            with open(i) as fp:
                data = json.load(fp)
                generics.append(data)
    return generics

def read_licenses():
    licenses = []
    for dir in LICENSE_DIRS:
        logging.debug("reading dir " + str(dir))
        for i in glob.glob(f'{dir}/*.json'):
            logging.debug(" reading file" + str(i))
            with open(i) as fp:
                data = json.load(fp)
                if HERMINE_LICENSES_DIR in i:
                    data = fix_hermine_license(data)
                    for obligation in data['obligations']:
                        #logging.debug("obligation: " + str(obligation))
                        obligation = fix_hermine_generic(obligation)
            licenses.append(data)
    return licenses

def _assert_obligation_exists(obligation, generics):
    if not obligation['generic']:
        return True

    obligation_name = obligation['name']
    obligation_generic = obligation['generic'][0]
    for generic in generics:
        generic_name = generic['name']
        if generic_name == obligation_generic:
            return True

    logging.debug("Could not find: " + str(obligation_generic) + " in " + str(obligation))
    for generic in generics:
        logging.debug(" generic " + str(generic['name']))
        
#    sys.exit(0)

def obligation_is_restriction(obligation):
    # if the obligation is listed amoing defaults, then it is not a resticted obligation
    return clause_matrix[obligation].get('restriction', False)

def obligation_is_not_restriction(obligation):
    logging.debug(obligation + "   " + str(obligation_is_restriction(obligation)))
    return not obligation_is_restriction(obligation)

def license_has_obligation(lic, obligation):
    logging.debug("--------------------")
    for _lic in licenses:
        if _lic['spdx_id'] == lic:
            return obligation in [obligation_name(x) for x in _lic['obligations']]

def obligation_is_excepted(license_spdxid, obligation_indata):
    try:
        lic = get_license(license_spdxid)
        obligation = get_obligation(lic, obligation_indata)
        logging.debug(f'EXCEPTION GRANTED: for "{license_spdxid}" :: "{obligation_indata}" ==> {obligation["exception"]}')
        logging.debug(f'EXCEPTION GRANTED: for "{license_spdxid}" :: "{obligation_indata}"')
        return obligation.get('exception')
    except:
        logging.debug(f'EXCEPTION NOT GRANTED: for "{license_spdxid}" :: "{obligation_indata}"')
        return False

def build_expression_is_restriction(expr, out_lic, in_lic, out_obl, in_obl, trigger, modified_trigger):
    IS_RESTRICTION_RE=r'\bis\ba\brestriction\n'
    IS_NOT_RESTRICTION_RE=r'[ ]+is[ ]+not[ ]+a[ ]+restriction[ ]*'
    if re.search(IS_RESTRICTION_RE, expr):
        logging.debug("||| yiha...")
        expr = re.sub(r'([a-z_]*)' + IS_RESTRICTION_RE, r"obligation_is_restriction(\1)", expr)
    elif re.search(IS_NOT_RESTRICTION_RE, expr):
        logging.debug("||| yiha... not")
        expr = re.sub(r'([a-z_]*)' + IS_NOT_RESTRICTION_RE, r"obligation_is_not_restriction(\1)", expr)
        logging.debug("||| yiha... not  ==> " + str(expr))

        
    return expr

def build_expression_has_obligation(expr, out_lic, in_lic, out_obl, in_obl, trigger, modified_trigger):
    IS_OBLIGATION_RE=r'[ ]+has[ ]+obligation[ ]*'
    IS_NOT_OBLIGATION_RE=r'[ ]+has[ ]+not[ ]+obligation[ ]*'
    if re.search(IS_OBLIGATION_RE, expr):
        logging.debug("||| yihaa... ")
        expr = re.sub(r'([a-z_]*)' + IS_OBLIGATION_RE + r'([a-z_]*)', r"license_has_obligation(\1, \2)", expr).replace("\\","")
    elif re.search(IS_NOT_OBLIGATION_RE, expr):
        logging.debug("||| yihaa... not " + str(expr))
        expr = re.sub(r'([a-z_]*)' + IS_NOT_OBLIGATION_RE + r"\"([a-zA-Z_ -]*)\"", r"not license_has_obligation(\1, \"\2\")", expr).replace("\\","")
        logging.debug("||| yihaa... not  ==> " + str(expr))
        logging.debug("||| yihaa... not  ==> " + str(expr.replace("\\","")))

    return expr

def build_expression_excepted(expr, out_lic, in_lic, out_obl, in_obl, trigger, modified_trigger):
    logging.debug("EXCEPTED")
    IS_EXCEPTED_RE=r'[ ]+is[ ]+excepted[ ]*'
    if re.search(IS_EXCEPTED_RE, expr):
        logging.debug("||| yihaa... ")
        expr = re.sub(r'([a-z_]*)' + IS_EXCEPTED_RE , r"obligation_is_excepted(inbound_license, \1)", expr)

    return expr

def build_expression_same_as(expr, out_lic, in_lic, out_obl, in_obl, trigger, modified_trigger):
    if "same as" in expr:
        
        normalized_inbound = fl.expression_license(in_lic['spdx_id'])['identified_license']
        dual_inbounds = normalized_inbound.replace(" ","").split("OR")
        
        normalized_outbound = fl.expression_license(out_lic['spdx_id'])['identified_license']
        dual_outbounds = normalized_outbound.replace(" ","").split("OR")

        # inbound_license same as outbound_license
        
        # A same as B
        # A1 OR A2 same as B1 or B2
        # ( A1 same as B1 or A1 same as B2 or A2 same as B1 or A2 same as B2  )
        # ( A1 == B1 or A1 == B2 or A2 == B1 or A2 == B2  )
        logging.debug("::: " + str(dual_inbounds) + "::: " + str(dual_outbounds) )
        exprs = []
        for dual_inbound in dual_inbounds:
            for dual_outbound in dual_outbounds:
                exprs.append(f'"{dual_inbound}" same as "{dual_outbound}"')
                logging.debug("::: " + str(exprs))
        dual_expr = " ( " + " or ".join(exprs) + " ) "
        logging.debug("normalized: " + str(dual_expr))
        expr = re.sub('inbound_license same as outbound_license', dual_expr, expr)
        expr = re.sub('outbound_license same as inbound_license', dual_expr, expr)
        
        logging.debug("same as: " + str(expr) + f'     in:{in_lic["spdx_id"]}  out:{out_lic["spdx_id"]}')
        expr = expr.replace("same as", "==")
        logging.debug("expr: " + str(expr))
    return expr
    
def build_expression(expr, out_lic, in_lic, out_obl, in_obl, trigger, modified_trigger):

    logging.debug("||| " + str(expr))
    expr = build_expression_same_as(expr, out_lic, in_lic, out_obl, in_obl, trigger, modified_trigger)
    logging.debug("||| " + str(expr))
    expr = build_expression_is_restriction(expr, out_lic, in_lic, out_obl, in_obl, trigger, modified_trigger)
    logging.debug("||| " + str(expr))
    expr = build_expression_has_obligation(expr, out_lic, in_lic, out_obl, in_obl, trigger, modified_trigger)    
    logging.debug("||| " + str(expr))
    expr = build_expression_excepted(expr, out_lic, in_lic, out_obl, in_obl, trigger, modified_trigger)
    logging.debug("||| " + str(expr))

    replacements = {
        'inbound_license': f'"{in_lic["spdx_id"]}"',
        'outbound_license': f'"{out_lic["spdx_id"]}"',
	'inbound_obligation': f'"{obligation_name(in_obl)}"',
        'outbound_obligation': f'"{obligation_name(out_obl)}"'
    }
    for k,v in replacements.items():
        expr = expr.replace(k,v)

    logging.debug("||| " + str(expr))
    logging.debug("expr: " + str(expr))
    return expr


def __boolean_to_compatible_status(val):
    if val:
        return COMPATIBLE_YES
    return COMPATIBLE_NO

def __compatible_status_to_boolean(val):
    return val == COMPATIBLE_YES


def obligations_untriggered(out_lic, in_lic, out_obl, in_obl, trigger, modified_trigger):
    if out_obl['name'] == '__dummy_obligation__':
        out_obl_triggered = False
        in_obl_triggered = trigger in in_obl['trigger_expl']
    else:
        out_obl_triggered = trigger in out_obl['trigger_expl']
        in_obl_triggered = trigger in in_obl['trigger_expl']

    if not (out_obl_triggered and in_obl_triggered):
        logging.debug(f'NOT TRIGGERED: ----------------------------------- expl')
        logging.debug(f'NOT TRIGGERED: license      "{out_lic["spdx_id"]}" "{in_lic["spdx_id"]}"')
        logging.debug(f'NOT TRIGGERED: obligation   "{obligation_name(out_obl)}" "{obligation_name(in_obl)}"')
        logging.debug(f'NOT TRIGGERED: trigger      "{trigger}"')
#        logging.debug(f'NOT TRIGGERED: trigger_expl "{out_obl["trigger_expl"]}" "{in_obl["trigger_expl"]}"')
        logging.debug(f'NOT TRIGGERED: triggered    "{out_obl_triggered}" "{in_obl_triggered}"')
        ret_val = {
            "inbound": in_obl,
            "outbound": out_obl,
            "compatible": "yes",
            "reason": f'trigger "{trigger}" resulted in:  {obligation_name(out_obl)}: {out_obl_triggered}, {obligation_name(in_obl)}: {in_obl_triggered}',
            "problems": []
        }
        logging.debug("NOT TRIGGERED: returning   " + str(ret_val["reason"]))
        return ret_val

def obligations_modified_untriggered(out_lic, in_lic, out_obl, in_obl, trigger, modified_trigger):
    out_obl_triggered = modified_trigger in out_obl['trigger_mdf']
    in_obl_triggered = modified_trigger in in_obl['trigger_mdf']

    if not (out_obl_triggered and in_obl_triggered):
        logging.debug(f'NOT TRIGGERED: ----------------------------------- modified')
        logging.debug(f'NOT TRIGGERED: license      "{out_lic["spdx_id"]}" "{in_lic["spdx_id"]}"')
        logging.debug(f'NOT TRIGGERED: obligation   "{obligation_name(out_obl)}" "{obligation_name(in_obl)}"')
        logging.debug(f'NOT TRIGGERED: trigger      "{modified_trigger}"')
        logging.debug(f'NOT TRIGGERED: obl_trigger  out: "{out_obl["trigger_mdf"]}" in: "{in_obl["trigger_mdf"]}"')
        logging.debug(f'NOT TRIGGERED: triggered    out: "{out_obl_triggered}" in: "{in_obl_triggered}"')
        ret_val = {
            "inbound": in_obl,
            "outbound": out_obl,
            "compatible": "yes",
            "reason": f'trigger "{trigger}" resulted in {obligation_name(out_obl)}: {out_obl_triggered}, {obligation_name(in_obl)}: {in_obl_triggered}',
            "problems": []
        }
        logging.debug("NOT TRIGGERED: returning   " + str(ret_val["reason"]))
        return ret_val
    

def obligations_compatible(out_lic, in_lic, out_obl, in_obl, trigger, modified_trigger):
    in_obl_name = obligation_name(in_obl)
    out_obl_name = obligation_name(out_obl)

    untriggered = obligations_untriggered(out_lic, in_lic, out_obl, in_obl, trigger, modified_trigger)
    if untriggered:
        return untriggered
    
    untriggered = obligations_modified_untriggered(out_lic, in_lic, out_obl, in_obl, trigger, modified_trigger)
    if untriggered:
        return untriggered
    
    
    
    #
    # check inbound obligation
    # 
    inbound_result = None

    logging.debug("oc")

    
    # if inbound has non default compatible value ("inbound_compatible")
    try:
        specific_compatibility = clause_matrix[in_obl_name][out_obl_name]        
    except:
        logging.debug(f'No specific value for {in_obl_name}{out_obl_name}')
        specific_compatibility = None

    try:
        common_expr = clause_matrix[in_obl_name]['inbound_expression']
    except:
        logging.debug(f'No common expressions for {in_obl_name}')
        common_expr = None

    if specific_compatibility:
        logging.debug("INBOUND CHECK specific")
        inbound_result = {
            "inbound": in_obl,
            "outbound": out_obl,
            "compatible": compatibility,
            "reason": f'Specific compatiblity between {in_obl_name} and {out_obl_name}'
        }
    elif common_expr:
        logging.debug("INBOUND CHECK expr")
        built_expr = build_expression(common_expr, out_lic, in_lic, out_obl, in_obl, trigger, modified_trigger)
        result = eval(built_expr)
        logging.debug("INBOUND CHECK expr: " + str(built_expr))
        logging.debug("INBOUND CHECK expr: " + str(result))
        
        inbound_result = {
            "inbound": in_obl,
            "outbound": out_obl,
            "compatible": __boolean_to_compatible_status(result),
            "reason": f'Evaluated expression  \"{built_expr}\" (from \"{common_expr}\") for inbound obligation \"{in_obl_name}\"'
        }
    else:
        logging.debug("INBOUND CHECK common")
        inbound_result = {
            "inbound": in_obl,
            "outbound": out_obl,
            "compatible": __boolean_to_compatible_status(True),
            "reason": f'common compatiblity between \"{out_obl_name}\" and \"{in_obl_name}\" is implicit"'
        }
        
    assert inbound_result
    

    logging.debug("oc outbound")
    #
    # check outbound obligation
    #
    outbound_result = None
    # if outbound obligation using inbound obligation has an expression, use it
    try:
        logging.debug("INBOUND CHECK 1")
        logging.debug("out obl: " + str(out_obl_name))
        expr = clause_matrix[out_obl_name]['outbound_expression']
        built_expr = build_expression(expr, out_lic, in_lic, out_obl, in_obl, trigger, modified_trigger)
        result = eval(built_expr)
        logging.debug("BUILT TO SPILL : " + str(expr))
        logging.debug("BUILT TO SPILL : " + str(built_expr) + " => " + str(result))

        outbound_result = {
            "inbound": in_obl,
            "outbound": out_obl,
            "compatible": __boolean_to_compatible_status(result),
            "reason": f'Evaluated expression \"{built_expr}\" (from \"{expr}\") for outbound obligation \"{out_obl_name}\"'
        }
        logging.debug("expression: " + expr)
        logging.debug("expression: " + built_expr)
        logging.debug("expression: " + str(result))
    except KeyError as e:
        logging.debug(f'Nothing to check for outbound obligation {out_obl_name}')
        #logging.debug(str(e))
        import traceback


    #
    # summarise and return
    #
    
    compatible_result = True
    problems = []
    if outbound_result:
        logging.debug("OBLIG out: " + str(outbound_result['compatible']))
        is_compatible = outbound_result['compatible'] == "yes"
        compatible_result = compatible_result and is_compatible
        if not is_compatible:
            problems.append(outbound_result['reason'])
        
    logging.debug("OBLIG in:  " + str(inbound_result['compatible']))
    is_compatible = inbound_result['compatible'] == "yes"
    compatible_result = compatible_result and is_compatible
    if not is_compatible:
        problems.append(inbound_result['reason'])

    if compatible_result:
        compatible_result_string = "yes"
    else:
        compatible_result_string = "no"
        
    return {
        "inbound": in_obl,
        "outbound": out_obl,
        "compatible": compatible_result_string,
        "reason": "",
        "problems": f'{list(set(problems))}'
    }

    # an obligation that is part of the outbound license's obligations
    if obligation_name(in_obl) in [obligation_name(x) for x in out_lic['obligations']]:
        return {
            "inbound": in_obl,
            "outbound": out_obl,
            "compatible": COMPATIBLE_YES,
            "reason": f'Inbound obligation \"{obligation_name(in_obl)}\" is present in outbound license \"{out_lic["spdx_id"]}\"',
            "problems": []
        }

    default_compatibility = False
    if default_compatibility:
        return {
            "inbound": in_obl,
            "outbound": out_obl,
            "compatible": default_compatibility,
            "reason": "default compatiblity",
            "problems": problems
        }
    

    
def obligation_name(obligation):
    if not obligation:
        return None
    if obligation["generic"]:
        return obligation["generic"][0]
    return obligation["name"]
    
def get_license(license_spdxid):
    for lic in licenses:
        if lic['spdx_id'] == license_spdxid:
            return lic

def get_obligation(lic, obligation_indata):
    for obligation in lic['obligations']:
        if obligation_name(obligation) == obligation_indata:
            return obligation
                    
def licenses_compatible(out_lic, in_lic, trigger, modified_trigger):
    logging.debug(f'{out_lic["spdx_id"]} --> {in_lic["spdx_id"]}')
    if out_lic == in_lic:
        return {
            "compatible": COMPATIBLE_YES,
            "reason": f'same license: \"{out_lic["spdx_id"]}\"',
            "problems": []
        }

    license_compatible = True
    problems = set()
    logging.debug(f'checking {out_lic["spdx_id"]} -> {in_lic["spdx_id"]}')
    if out_lic['obligations'] == []:
        logging.debug("uh oh ...")
        out_obl = {
            'name': '__dummy_obligation__',
            'generic': [
                '__dummy_obligation__'
            ]
        }
        for in_obl in in_lic['obligations']:
            ret = obligations_compatible(out_lic, in_lic, out_obl, in_obl, trigger, modified_trigger)
            compatible = ret["compatible"]
            logging.debug(f'  compat_:{compatible}  {obligation_name(out_obl)} --> {obligation_name(in_obl)}: {compatible} {ret["problems"]}')
            if compatible == COMPATIBLE_NO:
                logging.debug(f'    woha: {obligation_name(out_obl)} --> {obligation_name(in_obl)}: {compatible} {ret["problems"]}')
                license_compatible = False
                problems.add(ret['problems'])
    else:
        for out_obl in out_lic['obligations']:
            logging.debug("outer obligation:" + str(out_obl['name']))
            for in_obl in in_lic['obligations']:
                ret = obligations_compatible(out_lic, in_lic, out_obl, in_obl, trigger, modified_trigger)
                compatible = ret["compatible"]
                logging.debug(f'  compat_:{compatible}  {obligation_name(out_obl)} --> {obligation_name(in_obl)}: {compatible} {ret["problems"]}')
                if compatible == COMPATIBLE_NO:
                    logging.debug(f'    woha: {obligation_name(out_obl)} --> {obligation_name(in_obl)}: {compatible} {ret["problems"]}')
                    license_compatible = False
                    problems.add(ret['problems'])
    if license_compatible:
        license_compatible_value = COMPATIBLE_YES
    else:
        license_compatible_value = COMPATIBLE_NO

    return {
        "compatible": license_compatible_value,
        "reason": f'calculated',
        "problems": list(problems)
    }

def create_matrix(licenses, trigger, modified_trigger):
    arbiter = Arbiter(license_db='test/data/extended-license-matrix.json', update_dual=False)
    #arbiter = Arbiter()
    matrix = {}
    logging.debug("---------------------------")
    LICENSES_TO_CHECK = [ 'GPL-2.0-only', 'Apache-2.0']     
    LICENSES_TO_CHECK = [ 'MIT', 'GPL-2.0-only', 'BSD-3-Clause', 'Apache-2.0', 'GPL-2.0-or-later', "LGPL-2.1-or-later", "LGPL-2.1-only", "CC0-1.0", "Zlib"]
    for out_lic in licenses:
        matrix[out_lic['spdx_id']] = {}
        for in_lic in licenses:
            ret = licenses_compatible(out_lic, in_lic, trigger, modified_trigger)
            logging.debug("compat: hermione: " + out_lic["spdx_id"] +  " ---> " + in_lic["spdx_id"] +  " ===> " + str(ret['compatible']))
            logging.debug("compat: hermione complete: " + out_lic["spdx_id"] +  " ---> " + in_lic["spdx_id"] +  " ===> " + str(ret))
            flict_ret = arbiter.verify_outbound_inbound([out_lic["spdx_id"]], [in_lic["spdx_id"]])
            logging.debug("compat: flict:    " + str(flict_ret['result']['allowed_outbound_licenses']))

            check = False
            if ret['compatible'] == "yes":
                if len(flict_ret['result']['allowed_outbound_licenses']) > 0:
                    check = True
            elif ret['compatible'] == "no":
                #logging.debug("compat check: problems: " + str(ret['problems']))
                if len(flict_ret['result']['allowed_outbound_licenses']) == 0:
                    check = True

            if check:
                check_str = "correct"
            else:
                check_str = "NOT correct"

            if len(flict_ret['result']['allowed_outbound_licenses']) == 0:
                flict_str = "no"
            else:
                flict_str = "yes"

            matrix[out_lic['spdx_id']][in_lic['spdx_id']] = ret['compatible']
                

    return matrix

    ret = obligations_compatible("Add specific mentions in advertising",
                                 "Add specific mentions in advertising",
                                 trigger, modified_trigger)
    logging.debug(str(ret))

    ret = obligations_compatible("Add specific legal mentions in the documentation",
                                 "Add specific mentions in advertising",
                                 trigger, modified_trigger)
    logging.debug(str(ret))


def setup():
    global licenses
    licenses = read_licenses()
    global generics
    generics = read_generics()

    for lic in licenses:
        for obligation in lic['obligations']:
            logging.debug(str(obligation))
            _assert_obligation_exists(obligation, generics)
            if obligation['generic']:
                pass
            else:
                logging.debug(f'{lic["spdx_id"]}: \"{obligation["name"]}\": generic = null')

    logging.debug(str(len(licenses)))
    logging.debug(str(len(generics)))
    return licenses, generics
    
def main():
    setup()

    for trigger in ['DistributionNonSource', 'DistributionSource']:
        for modified in ['Unmodified', 'Altered']:
            filename = f'hermione-matrix-{trigger}-{modified}.json'
            print(f'Creating {filename}', file=sys.stderr)
            matrix = create_matrix(licenses, trigger, modified)
            license_data = {
                'meta': {
                    'disclaimer': 'This data and the tools come with no guarantee',
                    'created': {
                        'date': f'{datetime.datetime.now()}',
                        'tool': 'https://github.com/hesa/hermione'
                    },
                    'trigger': trigger,
                    'modified': modified
                },
                "licenses": matrix
            }
            with open(filename, 'w') as fp:
                json.dump(license_data, fp, indent=4)

if __name__ == "__main__":
    main()
