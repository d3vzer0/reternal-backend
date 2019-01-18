class ExecShell:
    def __init__(self, output, magic, response):
        self.output = output
        self.magic = magic
        self.response = response

    def process(self):
        magic = 'text/plain'
        return self.output, magic