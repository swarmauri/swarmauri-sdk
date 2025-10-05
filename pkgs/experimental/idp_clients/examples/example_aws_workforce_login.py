import os, asyncio
from idp_clients.aws_workforce import AwsWorkforceOAuth21Login, AwsWorkforceIdentityResolver

async def main():
    login = AwsWorkforceOAuth21Login(
        authorization_endpoint=os.environ["AWS_AUTHZ_ENDPOINT"],
        token_endpoint=os.environ["AWS_TOKEN_ENDPOINT"],
        client_id=os.environ["AWS_CLIENT_ID"],
        client_secret=os.environ["AWS_CLIENT_SECRET"],
        redirect_uri=os.environ["AWS_REDIRECT_URI"],
        state_secret=os.urandom(32),
    )
    step1 = await login.auth_url()
    print("Visit:", step1["url"])
    # After redirect: tokens = await login.exchange(code, step1["state"])
    # resolver = AwsWorkforceIdentityResolver(
    #     region="us-east-1", sso_region="us-east-1",
    #     identity_store_id=os.environ["IDENTITY_STORE_ID"],
    #     account_id=os.environ["READER_ACCOUNT_ID"], role_name=os.environ["READER_ROLE_NAME"],
    # )
    # who = resolver.lookup_user_min(tokens["tokens"]["access_token"])
    # print(who)

asyncio.run(main())
