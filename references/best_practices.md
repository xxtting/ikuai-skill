# iKuai Router Management Best Practices

Recommended practices and guidelines for managing iKuai routers using the OpenAPI.

## Security Best Practices

### 1. Credential Management

**Store Credentials Securely:**
```python
# Use environment variables
import os

APP_ID = os.getenv('IKUAI_APP_ID')
APP_SECRET = os.getenv('IKUAI_APP_SECRET')

# Or use a secrets management system
# Never hardcode credentials in code
```

**Rotate Access Tokens:**
```python
# Refresh tokens before expiration
if datetime.now() >= client.token_expires_at:
    client.refresh_access_token()
```

**Use Principle of Least Privilege:**
- Create separate API credentials for different applications
- Grant minimum required permissions
- Regularly audit access permissions

### 2. API Security

**Always Use HTTPS:**
- All API requests must use HTTPS
- Verify SSL certificates
- Never disable SSL verification in production

**Implement Rate Limiting:**
```python
import time
from functools import wraps

def rate_limit(max_calls=60, period=60):
    calls = []

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls outside period
            calls[:] = [c for c in calls if c > now - period]

            if len(calls) >= max_calls:
                wait_time = period - (now - calls[0])
                time.sleep(wait_time)

            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

**Validate All Input:**
```python
def validate_username(username):
    if not isinstance(username, str):
        raise ValueError("Username must be a string")
    if len(username) < 3 or len(username) > 32:
        raise ValueError("Username must be 3-32 characters")
    if not username.isalnum():
        raise ValueError("Username must be alphanumeric")
    return True
```

### 3. Network Security

**Use Firewall Rules:**
- Restrict access to open.ikuai8.com
- Block unauthorized API endpoints
- Implement IP whitelisting

**Monitor for Suspicious Activity:**
- Track API call patterns
- Alert on unusual behavior
- Log all authentication attempts

## Performance Best Practices

### 1. Connection Management

**Use Connection Pooling:**
```python
# The IkuaiAPIClient already uses connection pooling
client = IkuaiAPIClient(app_id, app_secret)
client.session  # Reuses connections
```

**Close Connections Properly:**
```python
try:
    # Use client
    client.get_accounts(dev_id)
finally:
    client.close()  # Always close
```

### 2. Caching Strategies

**Cache Account Lists:**
```python
from datetime import datetime, timedelta

class CachedIkuaiClient:
    def __init__(self, client):
        self.client = client
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes

    def get_accounts_cached(self, dev_id):
        cache_key = f'accounts_{dev_id}'

        if cache_key in self.cache:
            cached, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_timeout):
                return cached

        # Cache miss, fetch fresh data
        result = self.client.get_accounts(dev_id)
        self.cache[cache_key] = (result, datetime.now())
        return result
```

### 3. Batch Operations

**Use Batch API Calls:**
```python
# Instead of multiple single calls
for account_id in account_ids:
    client.delete_account(dev_id, account_id)

# Use batch operation
client.batch_delete_accounts(dev_id, account_ids)
```

**Parallel Requests:**
```python
import concurrent.futures

def get_online_users_multiple_devices(client, dev_ids):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(client.get_online_users, dev_id): dev_id
            for dev_id in dev_ids
        }
        results = {}
        for future in concurrent.futures.as_completed(futures):
            dev_id = futures[future]
            results[dev_id] = future.result()
        return results
```

## Reliability Best Practices

### 1. Error Handling

**Implement Retry Logic:**
```python
import time
from functools import wraps

def retry(max_retries=3, delay=1, backoff=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        raise
                    wait_time = delay * (backoff ** (retries - 1))
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator

@retry(max_retries=3, delay=1)
def get_status_with_retry(client, dev_id):
    return client.get_router_status(dev_id)
```

**Log All Errors:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ikuai_api.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('ikuai')

try:
    result = client.get_accounts(dev_id)
    if result.get('errno') != 0:
        logger.error(f"API Error: {result['errmsg']}")
except Exception as e:
    logger.exception(f"Exception occurred: {str(e)}")
```

### 2. Monitoring and Alerting

**Set Up Health Checks:**
```python
def health_check(client, dev_id):
    """Basic health check for router connection."""
    try:
        status = client.get_router_status(dev_id)
        if status.get('errno') == 0:
            data = status.get('data', {})
            return {
                'healthy': True,
                'cpu': data.get('cpu', 0),
                'memory': data.get('mem', 0),
                'online': data.get('online_users', 0)
            }
        else:
            return {'healthy': False, 'error': status.get('errmsg')}
    except Exception as e:
        return {'healthy': False, 'error': str(e)}
```

**Implement Alerting:**
```python
def send_alert(message):
    """Send alert via webhook or notification service."""
    import requests
    webhook_url = "https://your-webhook-url.com"
    requests.post(webhook_url, json={'message': message})

def check_and_alert(client, dev_id):
    health = health_check(client, dev_id)
    if not health['healthy']:
        send_alert(f"Router health check failed: {health['error']}")
    elif health['cpu'] > 90:
        send_alert(f"High CPU usage: {health['cpu']}%")
```

### 3. Backup and Recovery

**Backup Configuration:**
```python
def backup_accounts(client, dev_id, backup_file):
    """Backup all accounts to file."""
    accounts = client.get_accounts(dev_id)
    if accounts.get('errno') == 0:
        import json
        with open(backup_file, 'w') as f:
            json.dump(accounts, f, indent=2)
        print(f"Backed up {len(accounts.get('data', []))} accounts")

def restore_accounts(client, dev_id, backup_file):
    """Restore accounts from backup."""
    import json
    with open(backup_file, 'r') as f:
        accounts_data = json.load(f)

    for account in accounts_data.get('data', []):
        try:
            client.add_account(
                dev_id,
                username=account.get('username'),
                password=account.get('password'),
                group=account.get('group'),
                comments=account.get('comments')
            )
        except Exception as e:
            print(f"Failed to restore {account.get('username')}: {str(e)}")
```

## Data Management Best Practices

### 1. User Account Management

**Standardize Naming Convention:**
- Use consistent naming patterns
- Include organizational info in usernames
- Example: `dept_user_001`, `project_guest_01`

**Implement Account Lifecycle:**
```python
def create_account_with_expiry(client, dev_id, username, password, expiry_days):
    """Create account with tracking."""
    from datetime import datetime, timedelta

    expiry_date = datetime.now() + timedelta(days=expiry_days)

    # Create account
    result = client.add_account(
        dev_id,
        username=username,
        password=password,
        comments=f"Expires: {expiry_date.strftime('%Y-%m-%d')}"
    )

    # Log to your database
    log_account_creation(username, expiry_date)

    return result

def check_expired_accounts(client, dev_id):
    """Find and disable expired accounts."""
    from datetime import datetime

    accounts = client.get_accounts(dev_id)
    if accounts.get('errno') == 0:
        for account in accounts.get('data', []):
            comments = account.get('comments', '')
            if 'Expires:' in comments:
                expiry_str = comments.split('Expires:')[1].strip()
                try:
                    expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d')
                    if datetime.now() > expiry_date:
                        client.disable_account(dev_id, account.get('id'))
                        print(f"Disabled expired account: {account.get('username')}")
                except:
                    pass
```

### 2. Group Management

**Organize Users into Groups:**
```python
GROUPS = {
    'admin': {'priority': 1, 'bandwidth': 'unlimited'},
    'staff': {'priority': 2, 'bandwidth': '10Mbps'},
    'guest': {'priority': 3, 'bandwidth': '2Mbps'}
}

def create_user_in_group(client, dev_id, username, password, user_type):
    """Create user in appropriate group."""
    group_info = GROUPS.get(user_type, GROUPS['guest'])

    result = client.add_account(
        dev_id,
        username=username,
        password=password,
        group=user_type,
        comments=f"Priority: {group_info['priority']}"
    )

    return result
```

### 3. Logging and Auditing

**Maintain Audit Trail:**
```python
def audit_log(action, details):
    """Log all management actions."""
    import json
    from datetime import datetime

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'details': details
    }

    with open('audit.log', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

# Usage
audit_log('account_created', {
    'username': 'user1',
    'group': 'staff',
    'operator': 'admin'
})
```

## Development Best Practices

### 1. Testing

**Write Unit Tests:**
```python
import unittest

class TestIkuaiClient(unittest.TestCase):
    def setUp(self):
        self.client = IkuaiAPIClient('test_app_id', 'test_app_secret')

    def test_validate_username(self):
        self.assertTrue(validate_username('validuser'))
        self.assertRaises(ValueError, validate_username, '')
        self.assertRaises(ValueError, validate_username, 'a')
```

**Use Test Environment:**
- Test in non-production environment first
- Use test device IDs
- Never test with production data

### 2. Code Organization

**Separate Configuration:**
```python
# config.py
class Config:
    IKUAI_APP_ID = os.getenv('IKUAI_APP_ID')
    IKUAI_APP_SECRET = os.getenv('IKUAI_APP_SECRET')
    DEFAULT_DEV_ID = os.getenv('IKUAI_DEV_ID')
    LOG_LEVEL = 'INFO'
```

**Use Modular Functions:**
```python
# accounts.py
def get_user_by_username(client, dev_id, username):
    """Find user by username."""
    accounts = client.get_accounts(dev_id)
    for account in accounts.get('data', []):
        if account.get('username') == username:
            return account
    return None

def get_users_by_group(client, dev_id, group):
    """Get all users in a group."""
    accounts = client.get_accounts(dev_id)
    return [acc for acc in accounts.get('data', []) if acc.get('group') == group]
```

### 3. Documentation

**Document Your Code:**
```python
def create_account(
    client,
    dev_id,
    username: str,
    password: str,
    group: str = 'default',
    comments: str = ''
) -> dict:
    """
    Create a new user account.

    Args:
        client: IkuaiAPIClient instance
        dev_id: Device ID of the router
        username: Account username (3-32 chars, alphanumeric)
        password: Account password (6-32 chars)
        group: User group name (default: 'default')
        comments: Account description

    Returns:
        dict: API response with account creation result

    Raises:
        ValueError: If username or password is invalid
        Exception: If API call fails

    Example:
        >>> result = create_account(client, 'dev123', 'user1', 'pass123')
        >>> print(result.get('errno'))
        0
    """
    # Implementation
```

## Deployment Best Practices

### 1. Environment Configuration

**Use Environment-Specific Configs:**
```python
# config.py
import os

class BaseConfig:
    DEBUG = False

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(BaseConfig):
    LOG_LEVEL = 'WARNING'
    # Additional production settings

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

env = os.getenv('ENV', 'development')
current_config = config.get(env, DevelopmentConfig)()
```

### 2. Containerization

**Dockerfile Example:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

**docker-compose.yml:**
```yaml
version: '3'
services:
  ikuai-manager:
    build: .
    environment:
      - IKUAI_APP_ID=${IKUAI_APP_ID}
      - IKUAI_APP_SECRET=${IKUAI_APP_SECRET}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

### 3. Monitoring

**Use Application Monitoring:**
- Track API response times
- Monitor error rates
- Set up alerts for critical failures

## Troubleshooting Checklist

When issues occur:

1. **Check Credentials:**
   - Verify app_id and app_secret
   - Ensure token is valid
   - Check account permissions

2. **Check Network:**
   - Test connectivity to open.ikuai8.com
   - Verify DNS resolution
   - Check firewall rules

3. **Check Device:**
   - Verify device_id is correct
   - Ensure router is online
   - Check router firmware version

4. **Check Rate Limits:**
   - Review API call frequency
   - Wait if rate limited
   - Implement backoff

5. **Check Logs:**
   - Review application logs
   - Check router logs
   - Review API response details
