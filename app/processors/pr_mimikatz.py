from app.operations import Credential
import re

class Mimikatz:
    def __init__(self, output, magic, response):
        self.output = output
        self.magic = magic
        self.response = response
     
    def process(self):
        beacon_id = self.response['beacon_id']
        username = self.response['username']
        match = re.findall(r'(Username : (.*)\n.*Domain.*: (.*)\n.*((Password.*: (.*))|(NTLM.*: (.*)\n.*SHA1.*: (.*))))', self.output)
        for pattern in match:
            if not pattern[1] == '(null)':
                username = pattern[1]
                if (pattern[5] !='') and (pattern[5] != '(null)'):
                    # Found password as pattern[5]
                    Credential.create(beacon_id=beacon_id, source_command='mimikatz', username=username, key=pattern[5], key_type='ntlm')

                if (pattern[7] !='') and (pattern[7] != '(null)'):
                    # Found NTLM hash as pattern[7]
                    Credential.create(beacon_id=beacon_id, source_command='mimikatz', username=username, key=pattern[7], key_type='password')

                if (pattern[8] !='') and (pattern[8] != '(null)'):
                    # Found SHA1 hash as pattern[8]
                    Credential.create(beacon_id=beacon_id, source_command='mimikatz', username=username, key=pattern[8], key_type='sha1')

        return self.output, self.magic
