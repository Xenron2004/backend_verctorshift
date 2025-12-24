# HubSpot Integration Setup Instructions

This document provides step-by-step instructions for setting up and testing the HubSpot OAuth integration.

## Overview

The HubSpot integration allows users to:
- Authenticate via OAuth 2.0
- Retrieve Contacts, Companies, and Deals from HubSpot CRM
- Display integration items with proper metadata

## Prerequisites

1. Node.js and npm installed
2. Python 3.7+ installed
3. Redis server installed and running
4. A HubSpot developer account

## Step 1: Create a HubSpot App

1. Go to [HubSpot Developer Portal](https://developers.hubspot.com/)
2. Sign in or create a HubSpot developer account
3. Navigate to "Apps" in the top menu
4. Click "Create app"
5. Fill in the app details:
   - **App name**: Choose a descriptive name (e.g., "VectorShift Integration")
   - **Description**: Brief description of your app

## Step 2: Configure OAuth Settings

1. In your HubSpot app, navigate to the "Auth" tab
2. Configure the following settings:
   - **Redirect URL**: `http://localhost:8000/integrations/hubspot/oauth2callback`

3. Under "Scopes", add the following scopes:
   - `crm.objects.contacts.read`
   - `crm.objects.companies.read`
   - `crm.objects.deals.read`

4. Save your changes

## Step 3: Get Your Credentials

1. In the "Auth" tab, you'll find:
   - **Client ID**: Copy this value
   - **Client Secret**: Click "Show" and copy this value

2. Open `/backend/integrations/hubspot.py`

3. Replace the placeholder values:
   ```python
   CLIENT_ID = 'your-actual-client-id-here'
   CLIENT_SECRET = 'your-actual-client-secret-here'
   ```

## Step 4: Install Dependencies

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Step 5: Start Redis Server

Make sure Redis is running:

```bash
redis-server
```

## Step 6: Start the Application

### Terminal 1: Start Backend

```bash
cd backend
uvicorn main:app --reload
```

The backend will run on `http://localhost:8000`

### Terminal 2: Start Frontend

```bash
cd frontend
npm start
```

The frontend will run on `http://localhost:3000`

## Step 7: Test the Integration

1. Open your browser and navigate to `http://localhost:3000`

2. Fill in the test credentials:
   - **User**: TestUser (or any test user ID)
   - **Organization**: TestOrg (or any test org ID)

3. Select "HubSpot" from the Integration Type dropdown

4. Click "Connect to HubSpot"
   - A popup window will open
   - Log in to your HubSpot account
   - Authorize the app
   - The popup will close automatically

5. Once connected, the button will turn green showing "HubSpot Connected"

6. Click "Load Data" to fetch your HubSpot items

7. Check the backend console to see the detailed list of integration items printed

## Expected Output

When you click "Load Data", you should see output in the backend console similar to:

```
HubSpot Integration Items (Total: 45):
  - Type: Contact, ID: 12345, Name: John Doe
  - Type: Contact, ID: 12346, Name: Jane Smith
  - Type: Company, ID: 67890, Name: Acme Corp
  - Type: Company, ID: 67891, Name: Tech Solutions Inc
  - Type: Deal, ID: 11111, Name: Q4 Enterprise Deal
  ...
```

## Integration Details

### OAuth Flow

1. **Authorization**: User clicks "Connect to HubSpot" → Redirected to HubSpot login
2. **Callback**: HubSpot redirects back with authorization code
3. **Token Exchange**: Backend exchanges code for access token
4. **Storage**: Credentials stored temporarily in Redis (10 minutes)

### Data Retrieved

The integration fetches three types of CRM objects:

1. **Contacts**: Individual people in your CRM
   - Properties: ID, firstname, lastname, email

2. **Companies**: Organizations in your CRM
   - Properties: ID, name, domain

3. **Deals**: Sales opportunities
   - Properties: ID, dealname, amount

### Integration Item Structure

Each item includes:
- `id`: Unique identifier from HubSpot
- `name`: Display name (firstname for contacts, name for companies/deals)
- `type`: Object type (Contact, Company, or Deal)
- `creation_time`: When the object was created
- `last_modified_time`: When the object was last updated

## Troubleshooting

### Issue: "No credentials found" error

**Solution**: Make sure Redis is running and the OAuth flow completed successfully

### Issue: OAuth popup doesn't close

**Solution**: Check that the redirect URI in HubSpot app settings exactly matches:
`http://localhost:8000/integrations/hubspot/oauth2callback`

### Issue: "State does not match" error

**Solution**: The OAuth state token may have expired. Try connecting again within 10 minutes

### Issue: No data returned

**Solution**:
- Verify you have data in your HubSpot CRM
- Check that all required scopes are added in HubSpot app settings
- Ensure your access token has the correct permissions

## API Endpoints Used

- **Authorization**: `https://app.hubspot.com/oauth/authorize`
- **Token Exchange**: `https://api.hubapi.com/oauth/v1/token`
- **Contacts**: `https://api.hubapi.com/crm/v3/objects/contacts`
- **Companies**: `https://api.hubapi.com/crm/v3/objects/companies`
- **Deals**: `https://api.hubapi.com/crm/v3/objects/deals`

## Additional Resources

- [HubSpot OAuth Documentation](https://developers.hubspot.com/docs/api/oauth-quickstart-guide)
- [HubSpot CRM API Documentation](https://developers.hubspot.com/docs/api/crm/understanding-the-crm)
- [HubSpot Scopes Reference](https://developers.hubspot.com/docs/api/oauth/scopes)

## Notes for Production

Before deploying to production:

1. Update the `REDIRECT_URI` to your production domain
2. Store `CLIENT_ID` and `CLIENT_SECRET` as environment variables
3. Update CORS origins in `backend/main.py`
4. Implement proper error logging
5. Consider implementing token refresh logic for long-term storage
6. Add rate limiting to API calls
7. Implement proper credential encryption

## Architecture Overview

```
Frontend (React)
    ↓
    ├── User clicks "Connect to HubSpot"
    ↓
Backend (FastAPI) /authorize
    ↓
    ├── Generate OAuth URL with state
    ├── Store state in Redis
    ↓
HubSpot OAuth
    ↓
    ├── User authorizes
    ↓
Backend (FastAPI) /oauth2callback
    ↓
    ├── Validate state
    ├── Exchange code for access token
    ├── Store credentials in Redis
    ↓
Frontend retrieves credentials
    ↓
Frontend clicks "Load Data"
    ↓
Backend /load
    ↓
    ├── Fetch Contacts
    ├── Fetch Companies
    ├── Fetch Deals
    ├── Create IntegrationItem objects
    ↓
Return list of items to frontend
```

## Success Criteria

Your integration is working correctly if:

1. OAuth flow completes without errors
2. Credentials are successfully retrieved
3. Data loads and displays item count
4. Backend console shows detailed item list
5. No error messages in browser or terminal

## Support

For issues or questions:
- Check HubSpot API status: https://status.hubspot.com/
- Review HubSpot Developer Forum: https://community.hubspot.com/t5/APIs-Integrations/ct-p/apis
