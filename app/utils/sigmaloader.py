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
from app.schemas.sigma import SigmaIn, SigmaOut, SigmaRules
from app.database.models.techniques import Techniques
import sigma.backends.discovery as backends
from jinja2 import Template
import json
import yaml
import io
import tarfile

ERR_SIGMA_PARSING       = 4
ERR_BACKEND             = 8
ERR_NOT_SUPPORTED       = 9
ERR_NOT_IMPLEMENTED     = 42


class Splunk:
    def __init__(self, rules):
        self.rules = rules
        self.techniques = json.loads(Techniques.objects().to_json())

    def to_archive(self):
        # Create tar archive in Splunk app format
        tar_object = io.BytesIO()
        tar = tarfile.open(fileobj=tar_object, mode='w:gz')

        # Add app.conf
        app_conf = io.BytesIO(self.app_conf.encode('utf-8'))
        app_conf_info = tarfile.TarInfo(name='default/app.conf')
        app_conf_info.size = app_conf.getbuffer().nbytes
        tar.addfile(tarinfo=app_conf_info, fileobj=app_conf)

        # Add savedsearches.conf
        saved_searches = io.BytesIO(self.saved_searches.encode('utf-8'))
        saved_searches_info = tarfile.TarInfo(name='default/savedsearches.conf')
        saved_searches_info.size = saved_searches.getbuffer().nbytes
        tar.addfile(tarinfo=saved_searches_info, fileobj=saved_searches)

        # Generate techniques lookup
        lf_techniques = io.BytesIO(self.lookup_techniques.encode('utf-8'))
        lf_techniques_info = tarfile.TarInfo(name='lookups/attck_techniques.conf')
        lf_techniques_info.size = lf_techniques.getbuffer().nbytes
        tar.addfile(tarinfo=lf_techniques_info, fileobj=lf_techniques)

        # Generate actors to technique lookup
        lf_actors = io.BytesIO(self.lookup_techniques_by_actors.encode('utf-8'))
        lf_actors_info = tarfile.TarInfo(name='lookups/attck_actors.conf')
        lf_actors_info.size = lf_actors.getbuffer().nbytes
        tar.addfile(tarinfo=lf_actors_info, fileobj=lf_actors)
    
        return tar_object


    @property
    def app_conf(self):
        template = Template(
            open('app/templates/splunk/default/app.conf.j2').read(),
            trim_blocks=True,
            lstrip_blocks=True
        )
        # TODO dynamic config
        appconf = template.render()
        return appconf

    @property
    def saved_searches(self):
        template = Template(
            open('app/templates/splunk/default/savedsearches.conf.j2').read(),
            trim_blocks=True,
            lstrip_blocks=True
        )
        searches = template.render(rules=self.rules['success'])
        return searches

    @property
    def lookup_techniques(self):
        template = Template(
            open('app/templates/splunk/lookups/attck_techniques.csv.j2').read(),
            trim_blocks=True,
            lstrip_blocks=True
        )
        techniques = template.render(techniques=self.techniques)
        return techniques

    @property
    def lookup_techniques_by_actors(self):
        template = Template(
            open('app/templates/splunk/lookups/attck_actors.csv.j2').read(),
            trim_blocks=True,
            lstrip_blocks=True
        )
        techniques = template.render(techniques=self.techniques)
        return techniques


class Sigma:
    def __init__(self, rules):
        self.rules = rules

    @staticmethod
    def __load_config(config='splunk-windows'):
        config_object = SigmaConfigurationChain()
        scm = SigmaConfigurationManager()

        order  = 0
        for conf_name in config.split(','):
            sigmaconfig = scm.get(conf_name)
            if sigmaconfig.order is not None:
                order = sigmaconfig.order
            config_object.append(sigmaconfig)

        return config_object

    def export(self, target='splunk', config='splunk-windows', rule_filter=None):
        config_object = Sigma.__load_config(config)
        backend_class = backends.getBackend(target)
        backend = backend_class(config_object, BackendOptions(None, None))
        loaded_rules = { 'success': [], 'failed': []}

        format_rules = SigmaRules(**{'each_rule': self.rules}).dict(by_alias=True, exclude_none=True)
        for num, rule in enumerate(format_rules['each_rule']):
            sigmaio = io.StringIO(yaml.dump(rule))
            try:
                parser = SigmaCollectionParser(sigmaio, config_object, rule_filter)
                results = parser.generate(backend)
                loaded_rules['success'].append({'context': self.rules[num], 'export': [result for result in results]})

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

