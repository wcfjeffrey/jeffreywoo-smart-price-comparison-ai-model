import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_credentials():
    creds = None
    
    # Token file stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
        print("✓ Loaded existing token")
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("✓ Token refreshed")
        else:
            print("Opening browser for authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            
            # Use a fixed port to avoid issues
            creds = flow.run_local_server(port=8080, open_browser=True)
            print("✓ Authentication complete")
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        print("✓ Token saved to token.pickle")
    
    return creds

if __name__ == '__main__':
    try:
        creds = get_credentials()
        print("")
        print("=" * 50)
        print("✅ OAuth setup completed successfully!")
        print("=" * 50)
        print(f"Token file: token.pickle")
        print(f"Token valid: {creds.valid}")
        if creds.expiry:
            print(f"Token expires: {creds.expiry}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("")
        print("Troubleshooting tips:")
        print("1. Make sure credentials.json is in the correct location")
        print("2. Check that you selected 'Desktop app' as application type")
        print("3. Ensure your email is added as a test user in OAuth consent screen")
