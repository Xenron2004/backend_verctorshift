# hubspot.py

import json
import secrets
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import asyncio
import urllib.parse
import requests
from integrations.integration_item import IntegrationItem

from redis_client import add_key_value_redis, get_value_redis, delete_key_redis

CLIENT_ID = 'YOUR_HUBSPOT_CLIENT_ID'
CLIENT_SECRET = 'YOUR_HUBSPOT_CLIENT_SECRET'
REDIRECT_URI = 'http://localhost:8000/integrations/hubspot/oauth2callback'
SCOPES = 'crm.objects.contacts.read crm.objects.companies.read crm.objects.deals.read'

authorization_url = f'https://app.hubspot.com/oauth/authorize'

async def authorize_hubspot(user_id, org_id):
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }
    encoded_state = json.dumps(state_data)
    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', encoded_state, expire=600)

    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPES,
        'state': encoded_state
    }

    auth_url = f'{authorization_url}?{urllib.parse.urlencode(params)}'
    return auth_url

async def oauth2callback_hubspot(request: Request):
    if request.query_params.get('error'):
        raise HTTPException(status_code=400, detail=request.query_params.get('error'))

    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')
    state_data = json.loads(encoded_state)

    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')

    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')

    if not saved_state or original_state != json.loads(saved_state).get('state'):
        raise HTTPException(status_code=400, detail='State does not match.')

    async with httpx.AsyncClient() as client:
        response, _ = await asyncio.gather(
            client.post(
                'https://api.hubapi.com/oauth/v1/token',
                data={
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': REDIRECT_URI,
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET
                },
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            ),
            delete_key_redis(f'hubspot_state:{org_id}:{user_id}'),
        )

    await add_key_value_redis(f'hubspot_credentials:{org_id}:{user_id}', json.dumps(response.json()), expire=600)

    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)

async def get_hubspot_credentials(user_id, org_id):
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    credentials = json.loads(credentials)
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    await delete_key_redis(f'hubspot_credentials:{org_id}:{user_id}')

    return credentials

def create_integration_item_metadata_object(
    response_json: dict, item_type: str, parent_id=None, parent_name=None
) -> IntegrationItem:
    integration_item_metadata = IntegrationItem(
        id=str(response_json.get('id', '')),
        name=response_json.get('properties', {}).get('name', response_json.get('properties', {}).get('firstname', 'Unknown')),
        type=item_type,
        parent_id=parent_id,
        parent_path_or_name=parent_name,
        creation_time=response_json.get('createdAt'),
        last_modified_time=response_json.get('updatedAt'),
    )

    return integration_item_metadata

def fetch_paginated_items(access_token: str, url: str, item_type: str) -> list:
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    all_items = []
    after = None

    while True:
        params = {'limit': 100}
        if after:
            params['after'] = after

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])

            for item in results:
                all_items.append(create_integration_item_metadata_object(item, item_type))

            paging = data.get('paging', {})
            if 'next' in paging:
                after = paging['next'].get('after')
            else:
                break
        else:
            break

    return all_items

async def get_items_hubspot(credentials) -> list[IntegrationItem]:
    credentials = json.loads(credentials)
    access_token = credentials.get('access_token')

    list_of_integration_item_metadata = []

    contacts_url = 'https://api.hubapi.com/crm/v3/objects/contacts'
    companies_url = 'https://api.hubapi.com/crm/v3/objects/companies'
    deals_url = 'https://api.hubapi.com/crm/v3/objects/deals'

    contacts = fetch_paginated_items(access_token, contacts_url, 'Contact')
    list_of_integration_item_metadata.extend(contacts)

    companies = fetch_paginated_items(access_token, companies_url, 'Company')
    list_of_integration_item_metadata.extend(companies)

    deals = fetch_paginated_items(access_token, deals_url, 'Deal')
    list_of_integration_item_metadata.extend(deals)

    print(f'HubSpot Integration Items (Total: {len(list_of_integration_item_metadata)}):')
    for item in list_of_integration_item_metadata:
        print(f'  - Type: {item.type}, ID: {item.id}, Name: {item.name}')

    return list_of_integration_item_metadata
