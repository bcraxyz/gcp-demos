import os
import json
import logging
from flask import Flask, render_template, request
from jose import jwt

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
    # Get IAP headers (set by Google Cloud IAP)
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')
    user_id = request.headers.get('X-Goog-Authenticated-User-ID')
    serverless_auth = request.headers.get('X-Serverless-Authorization')
    iap_jwt = request.headers.get('X-Goog-IAP-JWT-Assertion')

    # Get all headers for debugging
    all_headers = dict(request.headers)
    
    # Decode JWT without verification (for demo purposes)
    jwt_header = None
    jwt_claims = None
    if iap_jwt:
        try:
            jwt_header = jwt.get_unverified_header(iap_jwt)
            jwt_claims = jwt.get_unverified_claims(iap_jwt)
            logger.info(f"JWT decoded - User: {jwt_claims.get('email')}")
        except Exception as e:
            logger.error(f"Error decoding JWT: {str(e)}")
            jwt_claims = f"Error decoding JWT: {str(e)}"

    page = render_template('index.html',
        # Basic IAP headers
        email=user_email,
        id=user_id,
        serverless_auth=serverless_auth,
        iap_jwt=iap_jwt,
        iap_jwt_preview=iap_jwt[:100] + '...' if iap_jwt else None,
        
        # JWT info (unverified)
        jwt_header=json.dumps(jwt_header, indent=2) if jwt_header else None,
        jwt_claims=json.dumps(jwt_claims, indent=2) if isinstance(jwt_claims, dict) else str(jwt_claims),
        jwt_email=jwt_claims.get('email') if isinstance(jwt_claims, dict) else None,
        jwt_sub=jwt_claims.get('sub') if isinstance(jwt_claims, dict) else None,
        jwt_aud=jwt_claims.get('aud') if isinstance(jwt_claims, dict) else None,
        jwt_iss=jwt_claims.get('iss') if isinstance(jwt_claims, dict) else None,
        jwt_hd=jwt_claims.get('hd') if isinstance(jwt_claims, dict) else None,
        
        # Debugging info
        all_headers=json.dumps(all_headers, indent=2),
        
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
