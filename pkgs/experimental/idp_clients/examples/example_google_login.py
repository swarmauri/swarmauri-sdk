import os, asyncio
from idp_clients.google import GoogleOIDC10Login, GoogleOAuth21Login, GoogleOAuth20Login

async def main():
    secret = os.urandom(32)
    oidc = GoogleOIDC10Login(
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        redirect_uri=os.environ["GOOGLE_REDIRECT_URI"],
        state_secret=secret,
    )
    print("OIDC login URL:", (await oidc.auth_url())["url"])

    o21 = GoogleOAuth21Login(
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        redirect_uri=os.environ["GOOGLE_REDIRECT_URI"],
        state_secret=secret,
    )
    print("OAuth2.1-aligned URL:", (await o21.auth_url())["url"])

    o20 = GoogleOAuth20Login(
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        redirect_uri=os.environ["GOOGLE_REDIRECT_URI"],
        state_secret=secret,
    )
    print("OAuth2.0 URL:", (await o20.auth_url())["url"])

asyncio.run(main())
