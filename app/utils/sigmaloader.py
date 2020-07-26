#!/usr/bin/env python3
# A Sigma to SIEM converter, slightly modified to act as a library in Reternal
# Original Copyright 2016-2017 Thomas Patzke, Florian Roth

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sigma.parser.collection import SigmaCollectionParser
from sigma.parser.exceptions import SigmaCollectionParseError, SigmaParseError
from sigma.configuration import SigmaConfiguration, SigmaConfigurationChain
from sigma.config.collection import SigmaConfigurationManager
from sigma.config.exceptions import SigmaConfigParseError, SigmaRuleFilterParseException
from sigma.backends.base import BackendOptions
from sigma.backends.exceptions import BackendError, NotSupportedError, PartialMatchError, FullMatchError
import sigma.backends.discovery as backends
import yaml
import io

ERR_SIGMA_PARSING       = 4
ERR_BACKEND             = 8
ERR_NOT_SUPPORTED       = 9
ERR_NOT_IMPLEMENTED     = 42


class SigmaLoader:
    def __init__(self, target='splunk', config='splunk-windows', rule_filter=None):
        self.rule_filter = rule_filter
        self.config = config
        self.target = target
        
    def load_config(self):
        config_object = SigmaConfigurationChain()
        scm = SigmaConfigurationManager()

        order  = 0
        for conf_name in self.config.split(','):
            sigmaconfig = scm.get(conf_name)
            if sigmaconfig.order is not None:
                order = sigmaconfig.order
            config_object.append(sigmaconfig)

        return config_object

    def convert_rules(self, rule_list):
        config_object = self.load_config()
        backend_class = backends.getBackend(self.target)
        backend = backend_class(config_object, BackendOptions(None, None))

        loaded_rules = { 'success': [], 'failed': []}
        for rule in rule_list:
            sigmaio = io.StringIO(yaml.dump(rule))
            try:
                parser = SigmaCollectionParser(sigmaio, config_object, self.rule_filter)
                results = parser.generate(backend)
                for result in results:
                    loaded_rules['success'].append(result)

            except (SigmaParseError, SigmaCollectionParseError) as err:
                error = {'id': rule['id'], 'reason': str(err), 'code': ERR_SIGMA_PARSING}
                loaded_rules['failed'].append(error)
            
            except NotImplementedError as err:
                error = {'id': rule['id'], 'reason': str(err), 'code': ERR_NOT_IMPLEMENTED}
                loaded_rules['failed'].append(error)

            except NotImplementedError as err:
                error = {'id': rule['id'], 'reason': str(err), 'code': ERR_NOT_SUPPORTED}
                loaded_rules['failed'].append(error)
    
            except BackendError as err:
                error = {'id': rule['id'], 'reason': str(err), 'code': ERR_BACKEND}
                loaded_rules['failed'].append(error)

        return loaded_rules

