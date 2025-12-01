# Keycloak OAuth2/OIDC Authentication Setup

This guide explains how to use Keycloak authentication in the RAG PDF Assistant application.

## Overview

The application now uses Keycloak as an OAuth2/OIDC identity provider for centralized authentication across all services.

### Architecture

- **Keycloak Server**: Runs on `http://localhost:8080`
- **Frontend**: React app with Keycloak integration
- **Backend Services**: 4 FastAPI microservices with JWT token validation
- **Authentication Flow**: Authorization Code Flow with PKCE (recommended for SPAs)

## Quick Start

### 1. Start All Services

```bash
docker-compose up -d
```

This will start:
- Keycloak (port 8080)
- All microservices (ports 8000-8003)
- Frontend (port 3000)
- Supporting services (Postgres, Redis, RabbitMQ, Qdrant)

### 2. Access Keycloak Admin Console

- URL: http://localhost:8080
- Username: `admin`
- Password: `admin`

### 3. Test User Credentials

A test user is pre-configured:
- Username: `testuser`
- Password: `testpass123`
- Email: `testuser@example.com`

### 4. Access the Application

Navigate to http://localhost:3000

You'll be automatically redirected to Keycloak login page. Use the test user credentials to log in.

## Configuration Details

### Keycloak Realm: `rag-assistant`

**Clients:**

1. **rag-frontend** (Public Client)
   - Client ID: `rag-frontend`
   - Access Type: Public
   - Valid Redirect URIs: `http://localhost:3000/*`
   - Web Origins: `http://localhost:3000`
   - PKCE: Enabled (S256)

2. **rag-backend** (Bearer-only Client)
   - Client ID: `rag-backend`
   - Access Type: Bearer-only
   - Used by microservices for token validation

**Roles:**
- `user` (default role for all users)
- `admin` (for administrative access)

**Token Settings:**
- Access Token Lifespan: 15 minutes (900 seconds)
- SSO Session Idle: 30 minutes
- SSO Session Max: 10 hours

## Frontend Integration

### Keycloak Configuration

Located in `frontend/src/auth/keycloakConfig.ts`:

```typescript
const keycloakConfig = {
  url: 'http://localhost:8080',
  realm: 'rag-assistant',
  clientId: 'rag-frontend',
};
```

### Authentication Flow

1. User visits the application
2. ReactKeycloakProvider checks authentication status
3. If not authenticated, redirects to Keycloak login
4. User logs in with credentials
5. Keycloak redirects back with authorization code
6. Frontend exchanges code for access token
7. Token is stored in memory and used for API calls

### API Client

The `apiClient` in `frontend/src/utils/apiClient.ts` automatically:
- Adds `Authorization: Bearer <token>` header to all requests
- Refreshes tokens when they expire
- Redirects to login if refresh fails

### Using Authentication in Components

```typescript
import { useKeycloak } from '@react-keycloak/web';

function MyComponent() {
  const { keycloak, initialized } = useKeycloak();

  if (!initialized) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <p>Welcome, {keycloak.tokenParsed?.preferred_username}!</p>
      <button onClick={() => keycloak.logout()}>Logout</button>
    </div>
  );
}
```

## Backend Integration

### Token Validation

All microservices use the shared authentication module in `common/auth/`:

**Key Components:**

1. **KeycloakValidator** (`common/auth/keycloak_validator.py`)
   - Fetches public keys from Keycloak JWKS endpoint
   - Validates JWT signature, expiration, issuer, audience
   - Extracts user information from token claims

2. **FastAPI Dependencies** (`common/auth/dependencies.py`)
   - `get_current_user`: Requires authentication
   - `get_current_user_optional`: Optional authentication
   - `require_role(role)`: Requires specific role

### Protecting Routes

```python
from fastapi import APIRouter, Depends
from typing import Dict, Any
from common.auth.dependencies import get_current_user, require_role

router = APIRouter()

# Requires authentication
@router.get("/protected")
async def protected_route(user: Dict[str, Any] = Depends(get_current_user)):
    return {"message": f"Hello {user['username']}"}

# Requires admin role
@router.get("/admin")
async def admin_route(user: Dict[str, Any] = Depends(require_role("admin"))):
    return {"message": "Admin access granted"}
```

### Token Claims

The validated token provides:

```python
{
  "user_id": "uuid",
  "username": "testuser",
  "email": "testuser@example.com",
  "email_verified": True,
  "name": "Test User",
  "given_name": "Test",
  "family_name": "User",
  "roles": ["user"],
  "claims": {...}  # Full JWT claims
}
```

### Environment Variables

Each service requires these environment variables (already configured):

```env
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=rag-assistant
KEYCLOAK_CLIENT_ID=rag-backend
```

## Adding Social Login (Google & Apple)

### Google SSO Setup

1. **Create Google OAuth2 Credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google+ API
   - Go to Credentials → Create Credentials → OAuth 2.0 Client ID
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:8080/realms/rag-assistant/broker/google/endpoint`
   - Copy Client ID and Client Secret

2. **Configure in Keycloak**
   - Login to Keycloak Admin Console
   - Select `rag-assistant` realm
   - Go to Identity Providers → Add provider → Google
   - Enter Client ID and Client Secret
   - Save

3. **Update Realm Configuration**

   Edit `infrastructure/keycloak/realm-export.json`:

   ```json
   {
     "alias": "google",
     "enabled": true,
     "config": {
       "clientId": "YOUR_GOOGLE_CLIENT_ID",
       "clientSecret": "YOUR_GOOGLE_CLIENT_SECRET"
     }
   }
   ```

4. **Restart Keycloak**
   ```bash
   docker-compose restart keycloak
   ```

### Apple SSO Setup

1. **Create Apple Sign In Service**
   - Go to [Apple Developer Portal](https://developer.apple.com/)
   - Certificates, Identifiers & Profiles → Identifiers
   - Register a new Services ID
   - Enable Sign In with Apple
   - Configure domains and return URLs:
     - Domain: `localhost` (for development)
     - Return URL: `http://localhost:8080/realms/rag-assistant/broker/apple/endpoint`
   - Create a private key for Sign In with Apple
   - Download the key file (.p8)

2. **Configure in Keycloak**
   - Login to Keycloak Admin Console
   - Select `rag-assistant` realm
   - Go to Identity Providers → Add provider → Apple
   - Enter:
     - Client ID: Your Services ID
     - Team ID: Your Apple Team ID
     - Key ID: Your Key ID
     - Private Key: Contents of .p8 file
   - Save

3. **Update Realm Configuration**

   Edit `infrastructure/keycloak/realm-export.json`:

   ```json
   {
     "alias": "apple",
     "enabled": true,
     "config": {
       "clientId": "YOUR_APPLE_SERVICE_ID",
       "teamId": "YOUR_APPLE_TEAM_ID",
       "keyId": "YOUR_APPLE_KEY_ID",
       "privateKey": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
     }
   }
   ```

4. **Restart Keycloak**
   ```bash
   docker-compose restart keycloak
   ```

### Testing Social Login

1. Navigate to http://localhost:3000
2. You'll see login options for:
   - Username/Password
   - Google
   - Apple
3. Click on Google or Apple to test SSO

## Production Considerations

### Security

1. **HTTPS Required**
   - Keycloak requires HTTPS for external identity providers
   - Use a reverse proxy (nginx, Traefik) with SSL certificates
   - Update all URLs to use HTTPS

2. **Change Default Credentials**
   ```env
   KEYCLOAK_ADMIN=your-admin-username
   KEYCLOAK_ADMIN_PASSWORD=strong-password-here
   ```

3. **Secure Secrets**
   - Use environment variables or secret management (AWS Secrets Manager, HashiCorp Vault)
   - Never commit secrets to version control

4. **Token Security**
   - Tokens are stored in memory (not localStorage) for better security
   - Automatic token refresh prevents session interruption
   - Short token lifespan (15 minutes) limits exposure

### Scaling

1. **Keycloak Clustering**
   - Use external database (PostgreSQL) instead of dev-file
   - Configure multiple Keycloak instances behind load balancer
   - Enable distributed caching

2. **JWKS Caching**
   - Public keys are cached to reduce Keycloak requests
   - Cache is automatically cleared on validation errors
   - Consider Redis for distributed caching

### Monitoring

1. **Keycloak Metrics**
   - Enable Keycloak metrics endpoint
   - Monitor login success/failure rates
   - Track token issuance and validation

2. **Application Logs**
   - All authentication events are logged
   - Monitor 401 errors for authentication issues
   - Track token refresh patterns

## Troubleshooting

### Frontend Issues

**Problem**: Infinite redirect loop
- **Solution**: Clear browser cookies and localStorage, restart Keycloak

**Problem**: CORS errors
- **Solution**: Verify `allow_origins` in backend CORS middleware includes frontend URL

**Problem**: Token not included in requests
- **Solution**: Check that `keycloak.authenticated` is true before making requests

### Backend Issues

**Problem**: 401 Unauthorized errors
- **Solution**:
  - Verify Keycloak is running and accessible
  - Check KEYCLOAK_URL environment variable
  - Ensure token is being sent in Authorization header

**Problem**: Token validation fails
- **Solution**:
  - Verify realm and client_id match configuration
  - Check token hasn't expired
  - Clear JWKS cache: `validator.clear_cache()`

**Problem**: Cannot fetch JWKS
- **Solution**:
  - Verify Keycloak URL is accessible from backend container
  - Check network connectivity: `docker exec file-service curl http://keycloak:8080`

### Keycloak Issues

**Problem**: Keycloak won't start
- **Solution**:
  - Check logs: `docker logs keycloak`
  - Verify port 8080 is not in use
  - Ensure realm-export.json is valid JSON

**Problem**: Social login not working
- **Solution**:
  - Verify redirect URIs match exactly
  - Check client credentials are correct
  - Enable HTTPS for production

## API Endpoints

### Protected Endpoints

All endpoints now require authentication:

**File Service (port 8000)**
- `POST /files/upload` - Upload PDF file
- `GET /files/` - List all files
- `GET /files/jobs/{job_id}/status` - Check job status
- `DELETE /files/{filename}` - Delete file

**RAG Service (port 8002)**
- `POST /rag/ask` - Ask question about document

### Testing with cURL

```bash
# Get token (using password grant - for testing only)
TOKEN=$(curl -X POST "http://localhost:8080/realms/rag-assistant/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser" \
  -d "password=testpass123" \
  -d "grant_type=password" \
  -d "client_id=rag-frontend" | jq -r '.access_token')

# Use token in API request
curl -X GET "http://localhost:8000/files/" \
  -H "Authorization: Bearer $TOKEN"
```

## Additional Resources

- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [OAuth 2.0 Specification](https://oauth.net/2/)
- [OpenID Connect](https://openid.net/connect/)
- [PKCE RFC](https://tools.ietf.org/html/rfc7636)

## Support

For issues or questions:
1. Check Keycloak logs: `docker logs keycloak`
2. Check service logs: `docker logs <service-name>`
3. Verify configuration in `infrastructure/keycloak/realm-export.json`
4. Review environment variables in `infrastructure/env/*.env`
