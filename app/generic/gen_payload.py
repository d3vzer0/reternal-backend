import shlex
import hashlib

class PayloadID:
    def __init__(self, platform, arch, base_url):
        self.platform = platform
        self.arch = arch
        self.base_url = base_url

    def create(self):
        escaped_url = shlex.quote(self.base_url)
        combined_id = '{}{}{}'.format(self.platform,self.arch,escaped_url)
        build_id = hashlib.sha1(combined_id.encode('utf-8')).hexdigest()    
        return build_id
