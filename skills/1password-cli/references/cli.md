# op CLI examples
## Sign in
- `eval $(op signin)` - sign in and create a session
- `op whoami` - check current session

## Read, List, Write Items
1. Read
- `op item get "Anthropic" --vault Private --field username` - get reference for a specific field. Output: op://Private/GitHub/password
- `op read "op://app-prod/db/password"` 
- `op read "op://app-prod/db/one-time password?attribute=otp"`
- `op read "op://app-prod/ssh key/private key?ssh-format=openssh"`
- `op read --out-file ./key.pem "op://app-prod/server/ssh/key.pem"`

2. List
- `op vault list` - list all vaults
- `op item list --vault "Private"` - list all items in vault
- `op item list --categories "Login, SSH Key"` - list items in categories

3. Create
- `op item create --category "API Credential" --title "My API Key" --vault "dev" --fields "api-key=sk-abc123"`
- `op item create --category Login --title "Service Account" --vault Private --fields "username=admin,password=secret123"`

4. Update
- `op item edit "My API Key" --vault dev "api-key=sk-newkey456"`


## Injecting Secrets into Environment Variables
1. `op run` - most secure way - secrets exist only during command execution:
```bash
export DB_PASSWORD="op://app-prod/database/password" # Set secret reference in environment
op run -- ./my-script.sh # Run command with secrets injected
op run -- printenv DB_PASSWORD  # secrets are masked - shows: <concealed by 1Password>
op run --no-masking -- printenv DB_PASSWORD # disable masking if needed
```
2. Environment files
Create a `.env` file with secret references
```bash
# .env file
DATABASE_URL="op://dev/postgres/connection-string"
API_KEY="op://dev/my-api/key"
SECRET_TOKEN="op://dev/app/secret-token"
```
Run with the env file:
```bash
op run --env-file=.env -- npm start
op run --env-file=.env -- python app.py
```

## Common Use Cases
1. Retrieve API Keys for Development
```bash
OPENAI_KEY=$(op read "op://Private/Anthropic/api-key") # Get a single API key
curl -H "Authorization: Bearer $(op read 'op://Private/Anthropic/api-key')" ... # Use in a command
```
2. Populate Environment for Local Development
```bash 
cat > .env.local << 'EOF'
SUPABASE_URL="op://dev/Supabase/url"
SUPABASE_KEY="op://dev/Supabase/service-role-key"
ANTHROPIC_API_KEY="op://dev/Anthropic/api-key"
EOF # Create .env.local with secret references
op run --env-file=.env.local -- npm run dev # Start development server with secrets
```
3. Export Secrets to Shell Session
```bash
# Export secrets for current shell session
export GITHUB_TOKEN=$(op read "op://Private/GitHub/token")
export NPM_TOKEN=$(op read "op://Private/npm/token")
```
4. Use in Scripts
```bash
#!/bin/bash
# deploy.sh - uses 1Password for secrets
# Ensure we have access
op whoami > /dev/null 2>&1 || eval $(op signin)
# Get deployment credentials
DEPLOY_KEY=$(op read "op://prod/deploy/ssh-key")
API_TOKEN=$(op read "op://prod/api/token")
# Use in deployment...
```
