
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import requests
import base64
import jwt
import json

# Thanks to https://robertoprevato.github.io/Validating-JWT-Bearer-tokens-from-Azure-AD-in-Python/

def ensure_bytes(key):
    if isinstance(key, str):
        key = key.encode('utf-8')
    return key

def decode_value(val):
    decoded = base64.urlsafe_b64decode(ensure_bytes(val) + b'==')
    return int.from_bytes(decoded, 'big')

def rsa_pem_from_jwk(jwk):
    return RSAPublicNumbers(
        n=decode_value(jwk['n']),
        e=decode_value(jwk['e'])
        ).public_key(default_backend()).public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )


class JWT:
    def __init__(self, openid_configuration, issuer, audiences):
        self.openid_configuration = openid_configuration
        self.issuer = issuer
        self.audiences = audiences

    def get(self, base_url):
        get_http = requests.get(base_url)
        return get_http.json()

    def decode_token_header(self, access_token):
        split_token = f'{access_token.split(".")[0]}=='
        decoded_token = base64.b64decode(split_token)

        print(base64.b64decode(f'{access_token.split(".")[1]}=='))
        return json.loads(decoded_token)

    def validate(self, access_token):
        jwks_uri = self.get(self.openid_configuration)['jwks_uri']
        jwk_keys = self.get(jwks_uri)
        decoded_token_header = self.decode_token_header(access_token)

        x5c = None
        for key in jwk_keys['keys']:
            if key['kid'] == decoded_token_header['kid']:
                x5c = key
    
        if x5c == None:
            raise jwt.exceptions.InvalidIssuerError()
        
        public_key = rsa_pem_from_jwk(x5c)

        # Exceptions handled in the custom exception handling class
        jwt_decoded = jwt.decode(access_token, public_key, verify=True,
            algorithms=[decoded_token_header['alg']], audience=self.audiences,
            issuer=self.issuer
        )
        return jwt_decoded