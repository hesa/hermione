# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging

def fix_hermine_license(license_object):
    if license_object['spdx_id'] == 'GPL-2.0-only WITH Classpath-exception-2.0':
        for obligation in license_object['obligations']:
            # some obligations miss 'generic', so we need to try/except
            try:
                if obligation['generic'][0] == 'Strong Copyleft':
                    obligation['exception'] = [ 'dynamic-linking',
                                                'static-linking']

                    logging.debug("ADD DATA TO GPL W CP " + str(obligation))
            except:
                pass
    return license_object

def fix_hermine_generic(generic_object):
    if generic_object['name'] == 'License agreement : allow reverse engineering':
        generic_object['generic'] = ['allow reverse engineering']
        logging.debug("FIX FIX..." + str(generic_object))
    elif generic_object['name'] == 'Independance from external data and code':
        generic_object['generic'] = ['Independance from external data and code']
        logging.debug("FIX FIX..." + str(generic_object))
    elif generic_object['name'] == 'License agreement : allow reverse engineering and moification for private use':
        generic_object['generic'] = ['allow reverse engineering and moification for private use']
        logging.debug("FIX FIX..." + str(generic_object))
    elif generic_object['name'] == 'Extending 3rd party patent grants to everyone':
        generic_object['generic'] = ['Extending 3rd party patent grants to everyone']
        logging.debug("FIX FIX..." + str(generic_object))
    elif generic_object['name'] == 'Dont implement Anti-Circumvention Law.':
        generic_object['generic'] = ['Dont implement Anti-Circumvention Law.']
        logging.debug("FIX FIX..." + str(generic_object))
    elif generic_object['name'] == 'Modification must be pacakged as patches':
        generic_object['generic'] = ['Modification must be pacakged as patches']
        logging.debug("FIX FIX..." + str(generic_object))
    elif generic_object['name'] == 'License agreement : do not restrict reverse engineering for interoperability':
        generic_object['generic'] = ['do not restrict reverse engineering for interoperability']
        logging.debug("FIX FIX..." + str(generic_object))
    elif generic_object['name'] == 'Default license is Apache-2.0':
        generic_object['generic'] = ['Default license is Apache-2.0']
        logging.debug("FIX FIX..." + str(generic_object))
    return generic_object
