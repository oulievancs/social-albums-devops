import os
from fastapi import HTTPException

from fastapi.security import OAuth2AuthorizationCodeBearer, SecurityScopes
from fastapi import Security, HTTPException, status
from keycloak import KeycloakOpenID


from pydantic import Json
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# This is just for fastapi docs
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=os.environ.get('AUTHORIZATION_URL'),
    tokenUrl=os.environ.get('TOKEN_URL')
)

# This actually does the auth checks
keycloak_openid = KeycloakOpenID(
    server_url=os.environ.get('AUTHORIZATION_URL'),
    client_id=os.environ.get('KEYCLOAK_CLIENT_ID'),
    realm_name=os.environ.get('KEYCLOAK_REALM'),
    client_secret_key=os.environ.get('KEYCLOAK_CLIENT_SECRET'),
    verify=True
)


async def get_idp_public_key():
    return (
        "-----BEGIN PUBLIC KEY-----\n"
        f"{keycloak_openid.public_key()}"
        "\n-----END PUBLIC KEY-----"
    )
    # filename = os.environ.get('KEYCLOAK_PUBLIC_CERT')
    # if os.path.exists(filename):
    #     with open(filename) as f:
    #         return f.read()


async def get_auth(security_scopes: SecurityScopes, token: str = Security(oauth2_scheme)) -> Json:
    try:
        print('decode token')
        payload = keycloak_openid.decode_token(
            token,
            key=await get_idp_public_key(),
            options={
                'verify_signature': False,
                'verify_aud': False,
                'exp': True
            }
        )
        print(payload)
        payload_scopes = payload['realm_access']['roles']
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),  # "Invalid authentication credentials",
            headers={'WWW-Authenticate': 'Bearer'},
        )

    for scope in security_scopes.scopes:
        print(scope)
        if scope not in payload_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return payload