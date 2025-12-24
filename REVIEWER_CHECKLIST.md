# Reviewer Testing Checklist

## Pre-Testing Setup (5 minutes)

### Step 1: Create HubSpot App
- [ ] Go to https://developers.hubspot.com/
- [ ] Sign in or create account
- [ ] Click "Apps" → "Create app"
- [ ] Name your app (e.g., "VectorShift Test")

### Step 2: Configure OAuth
- [ ] Go to "Auth" tab
- [ ] Add redirect URI: `http://localhost:8000/integrations/hubspot/oauth2callback`
- [ ] Add scopes:
  - [ ] `crm.objects.contacts.read`
  - [ ] `crm.objects.companies.read`
  - [ ] `crm.objects.deals.read`
- [ ] Save settings

### Step 3: Get Credentials
- [ ] Copy Client ID
- [ ] Copy Client Secret (click "Show")
- [ ] Open `backend/integrations/hubspot.py`
- [ ] Replace line 15: `CLIENT_ID = 'your-client-id'`
- [ ] Replace line 16: `CLIENT_SECRET = 'your-client-secret'`
- [ ] Save file

### Step 4: Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

---

## Testing Process (10 minutes)

### Step 1: Start Services

#### Terminal 1: Redis
- [ ] Run: `redis-server`
- [ ] Verify: Should see "Ready to accept connections"

#### Terminal 2: Backend
- [ ] Run: `cd backend && uvicorn main:app --reload`
- [ ] Verify: Should see "Uvicorn running on http://127.0.0.1:8000"
- [ ] No import errors

#### Terminal 3: Frontend
- [ ] Run: `cd frontend && npm start`
- [ ] Verify: Browser opens to http://localhost:3000
- [ ] No compilation errors

---

### Step 2: Test UI Initialization

- [ ] Page loads without errors
- [ ] See "User" field (default: TestUser)
- [ ] See "Organization" field (default: TestOrg)
- [ ] See "Integration Type" dropdown
- [ ] Dropdown contains: Notion, Airtable, HubSpot

---

### Step 3: Test HubSpot OAuth Flow

#### Part A: Initiate Connection
- [ ] Select "HubSpot" from dropdown
- [ ] "Parameters" section appears
- [ ] See "Connect to HubSpot" button (blue)
- [ ] Click "Connect to HubSpot"
- [ ] Popup window opens (600x600)
- [ ] Button shows loading spinner
- [ ] Button is disabled during loading

#### Part B: Authorize on HubSpot
- [ ] HubSpot login page loads in popup
- [ ] Log in to HubSpot account
- [ ] See authorization screen
- [ ] App name is displayed
- [ ] Scopes are listed
- [ ] Click "Authorize" or "Connect app"

#### Part C: Verify Connection
- [ ] Popup closes automatically
- [ ] Button changes to green
- [ ] Button text: "HubSpot Connected"
- [ ] Button is disabled (can't click again)
- [ ] No error alerts

#### Expected Backend Console Output:
```
# Should see no errors
# May see successful token exchange logs
```

---

### Step 4: Test Credential Retrieval

- [ ] "Load Data" button appears below connection button
- [ ] "Clear Data" button appears
- [ ] "Loaded Data" text field visible (empty)

---

### Step 5: Test Data Loading

#### Part A: Load Data
- [ ] Click "Load Data" button
- [ ] Button is clickable (not disabled)
- [ ] Request completes (may take 2-10 seconds)

#### Part B: Verify Backend Console Output
- [ ] Backend console shows: `HubSpot Integration Items (Total: X):`
- [ ] Each line shows: `- Type: {Contact/Company/Deal}, ID: {number}, Name: {name}`
- [ ] Total count matches number of items listed
- [ ] At least one of each type (Contact, Company, Deal) if data exists

#### Example Expected Output:
```
HubSpot Integration Items (Total: 45):
  - Type: Contact, ID: 12345, Name: John Doe
  - Type: Contact, ID: 12346, Name: Jane Smith
  - Type: Company, ID: 67890, Name: Acme Corp
  - Type: Deal, ID: 11111, Name: Q4 Enterprise Deal
  ...
```

#### Part C: Verify Frontend
- [ ] "Loaded Data" field populates with data
- [ ] Data is a list of objects
- [ ] Each object has: id, type, name

---

### Step 6: Test Error Handling

#### Test A: State Timeout
- [ ] Select HubSpot
- [ ] Click "Connect to HubSpot"
- [ ] Wait >10 minutes (state expires)
- [ ] Try to complete OAuth
- [ ] Should see error: "State does not match"

#### Test B: Missing Credentials
- [ ] Restart backend
- [ ] Try to load data without connecting
- [ ] Should see error: "No credentials found"

#### Test C: Invalid Credentials
- [ ] Use wrong CLIENT_ID/SECRET
- [ ] Try to connect
- [ ] Should see appropriate error

---

## Verification Checklist

### Code Quality
- [ ] No console errors in browser
- [ ] No Python errors in backend
- [ ] Code follows existing patterns
- [ ] Functions are documented
- [ ] Error handling is present

### Functionality
- [ ] OAuth flow completes successfully
- [ ] Credentials are retrieved
- [ ] Data loads from HubSpot
- [ ] All three object types are fetched (Contacts, Companies, Deals)
- [ ] Pagination works (if >100 items)
- [ ] Console output is formatted correctly

### Security
- [ ] State parameter is used
- [ ] State is validated on callback
- [ ] Credentials are stored temporarily (10 min)
- [ ] Credentials are deleted after retrieval

### UI/UX
- [ ] Loading indicators work
- [ ] Connection status is clear
- [ ] Buttons are properly disabled/enabled
- [ ] Error messages are user-friendly
- [ ] Consistent with existing integrations

---

## Expected Results Summary

### Successful Test Indicators:
1. ✅ OAuth popup opens and closes automatically
2. ✅ Button changes from blue "Connect" to green "Connected"
3. ✅ Data loads without errors
4. ✅ Backend console shows formatted list of items
5. ✅ Total count matches number of items
6. ✅ Three object types present (if HubSpot account has data)

### Pass Criteria:
- All checkboxes above are checked
- No critical errors encountered
- Data loads and displays correctly
- Console output is properly formatted

---

## Troubleshooting

### Issue: Popup doesn't open
**Check:**
- [ ] Browser popup blocker disabled
- [ ] CLIENT_ID is correct

### Issue: "State does not match"
**Solution:**
- [ ] Try again (state may have expired)
- [ ] Check Redis is running
- [ ] Verify state expiration time

### Issue: "No credentials found"
**Solution:**
- [ ] Complete OAuth flow first
- [ ] Check Redis is running
- [ ] OAuth must complete within 10 minutes

### Issue: No data in console
**Solution:**
- [ ] Check HubSpot account has CRM data
- [ ] Verify scopes are correct
- [ ] Check access token is valid

### Issue: Cannot connect
**Check:**
- [ ] CLIENT_ID and CLIENT_SECRET are correct
- [ ] Redirect URI matches exactly
- [ ] Scopes are added in HubSpot app
- [ ] Redis is running
- [ ] Backend is running

---

## Documentation Review

- [ ] README.md is clear and complete
- [ ] QUICKSTART.md provides fast setup
- [ ] HUBSPOT_SETUP_INSTRUCTIONS.md is detailed
- [ ] IMPLEMENTATION_NOTES.md explains technical decisions
- [ ] Code comments are helpful

---

## Final Assessment

### Code Quality: [ ] Pass [ ] Fail
- Follows existing patterns
- Proper error handling
- Well documented
- Clean and maintainable

### Functionality: [ ] Pass [ ] Fail
- OAuth works end-to-end
- Data loads correctly
- Pagination handles large datasets
- Console output is correct

### Security: [ ] Pass [ ] Fail
- State validation works
- Credentials handled securely
- No security vulnerabilities

### Documentation: [ ] Pass [ ] Fail
- Setup instructions are clear
- Code is well documented
- Architecture is explained

---

## Overall Assessment

### Score: ___ / 100

**Breakdown:**
- OAuth Implementation (30 pts): ___
- Data Loading (30 pts): ___
- Code Quality (20 pts): ___
- Documentation (10 pts): ___
- UI/UX (10 pts): ___

### Recommendation: [ ] Strong Hire [ ] Hire [ ] No Hire

### Notes:
```
[Reviewer notes here]
```

---

## Time Tracking

- Setup Time: ___ minutes
- Testing Time: ___ minutes
- Total Time: ___ minutes

---

**Testing Date**: _______________
**Reviewer**: _______________
**Result**: [ ] PASS [ ] FAIL
