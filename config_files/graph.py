import msal


def get_access_token():
    client_id = '2e9c933e-b1e7-49b4-9b97-4bd93cc8c298'
    client_secret = 'TwU8Q~iW1BIVSlZAJAIvad3gfEc7juWzcWMxJbXe'
    authority = 'https://login.microsoftonline.com/35f0bfd2-54a7-4a76-bad8-f169d5d01bb9'
    scope = ['https://graph.microsoft.com/.default']
    # Create an MSAL instance providing the client_id, authority and client_credential parameters
    client = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)
    # First, try to lookup an access token in cache
    token_result = client.acquire_token_silent(scope, account=None)
    # If the token is available in cache, save it to a variable
    if token_result:
        access_token = 'Bearer ' + token_result['access_token']
        print('Access token was loaded from cache')
        return access_token
    # If the token is not available in cache, acquire a new one from Azure AD and save it to a variable
    if not token_result:
        token_result = client.acquire_token_for_client(scopes=scope)
        access_token = 'Bearer ' + token_result['access_token']
        print('New access token was acquired from Azure AD')
        return access_token