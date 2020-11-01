
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import requests
import base64
import jwt
import json

# Thanks to https://robertoprevato.github.io/Validating-JWT-Bearer-tokens-from-Azure-AD-in-Python/
openid_state = { }

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
        print(access_token)
        split_token = f'{access_token.split(".")[0]}=='
        decoded_token = base64.b64decode(split_token)
        return json.loads(decoded_token)

    def get_public_key(self, decoded_token_header):
        jwks_uri = self.get(self.openid_configuration)['jwks_uri']
        jwk_keys = self.get(jwks_uri)
        
        x5c = None
        for key in jwk_keys['keys']:
            if key['kid'] == decoded_token_header['kid']:
                x5c = key
    
        if x5c == None:
            raise jwt.exceptions.InvalidIssuerError()
        
        public_key = rsa_pem_from_jwk(x5c)
        openid_state[self.openid_configuration] = public_key
        return public_key
   
    def decode(self, access_token, verify=True):
        decoded_token_header = self.decode_token_header(access_token)
        if verify:
            if self.openid_configuration in openid_state:
                public_key = openid_state[self.openid_configuration]
            else: 
                public_key = self.get_public_key(decoded_token_header)

            jwt_decoded = jwt.decode(access_token, public_key, verify=True,
                algorithms=[decoded_token_header['alg']], audience=self.audiences,
                issuer=self.issuer
            )
        else:
            jwt_decoded = jwt.decode(access_token, verify=False,
                algorithms=[decoded_token_header['alg']]
            ) 
        return jwt_decoded


