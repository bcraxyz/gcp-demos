import os
import json
import logging
from auth import user, get_unverified_jwt_info
from flask import Flask, render_template, request

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Disable browser caching so changes in each step are always shown
@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def say_hello():
    # Get IAP headers (these are set by Google Cloud IAP)
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')
    user_id = request.headers.get('X-Goog-Authenticated-User-ID')
    serverless_auth = request.headers.get('X-Serverless-Authorization')
    iap_jwt = request.headers.get('X-Goog-IAP-JWT-Assertion')

    # Get unverified JWT info for debugging
    jwt_header, jwt_claims = get_unverified_jwt_info()
    
    # Get all headers for debugging
    all_headers = dict(request.headers)
    
    # Get IAP-related environment variables
    env_vars = dict(os.environ)
    iap_env_vars = {k: v for k, v in env_vars.items() if 'IAP' in k or 'CLIENT' in k or 'GOOGLE' in k}

    # Handle the case where user() returns None (no IAP)
    user_result = user()

    if user_result is None:
        # No IAP authentication - use default values
        verified_email = None
        verified_id = None
        verified_aud = None
        verified_iss = None
        verified_hd = None
        verified_goog = {}
        logger.info("Running without IAP authentication")
    else:
        # Unpack the tuple when we know it's not None
        verified_email, verified_id, verified_aud, verified_iss, verified_hd, verified_goog = user_result
        logger.info(f"IAP authentication successful for {verified_email}")

    page = render_template('index.html',
        # Basic IAP headers
        email=user_email,
        id=user_id,
        serverless_auth=serverless_auth,
        iap_jwt=iap_jwt,
        iap_jwt_preview=iap_jwt[:100] + '...' if iap_jwt else None,
        
        # Verified JWT claims
        verified_email=verified_email,
        verified_id=verified_id,
        verified_aud=verified_aud,
        verified_iss=verified_iss,
        verified_hd=verified_hd,
        verified_goog=verified_goog,
        
        # Debugging info
        iap_client_id=iap_client_id,
        jwt_header=json.dumps(jwt_header, indent=2) if jwt_header else None,
        jwt_claims=json.dumps(jwt_claims, indent=2) if isinstance(jwt_claims, dict) else str(jwt_claims),
        all_headers=json.dumps(all_headers, indent=2),
        iap_env_vars=json.dumps(iap_env_vars, indent=2) if iap_env_vars else None,
        
        # Request info
        request_url=request.url,
        request_method=request.method,
        request_remote_addr=request.remote_addr,
        request_host=request.host,
        request_user_agent=request.headers.get('User-Agent', 'Not set')
    )
    return page

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
