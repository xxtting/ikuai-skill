# iKuai OpenAPI Error Codes Reference

Complete reference for all error codes returned by iKuai OpenAPI.

## Error Response Format

All API errors follow this format:

```json
{
  "errno": 0,
  "errmsg": "success",
  "data": null
}
```

- **errno**: Numeric error code (0 = success)
- **errmsg**: Human-readable error message
- **data**: Response data (null for errors)

## Success Code

| errno | Description |
|-------|-------------|
| 0 | Operation successful |

## Authentication Errors

| errno | Description | Solution |
|-------|-------------|----------|
| 2 | Authentication failed | Check app_id and app_secret |
| 3 | Permission denied | Verify account has required permissions |
| 1001 | Invalid access token | Refresh or obtain new token |
| 1002 | Token expired | Refresh token |
| 1003 | Invalid app_id or app_secret | Verify credentials from open.ikuai8.com |
| 1004 | Account locked | Contact iKuai support |

## Request Errors

| errno | Description | Solution |
|-------|-------------|----------|
| 1 | Invalid parameters | Check request format and required fields |
| 101 | Missing required parameter | Include all required parameters |
| 102 | Invalid parameter format | Use correct data types and formats |
| 103 | Parameter value out of range | Use values within allowed range |
| 104 | Invalid JSON format | Fix JSON syntax in request body |

## Account Management Errors

| errno | Description | Solution |
|-------|-------------|----------|
| 100 | Account already exists | Use different username |
| 101 | Invalid username | Check username format (3-32 chars, alphanumeric) |
| 102 | Invalid password | Check password format (6-32 chars) |
| 103 | Group not found | Use existing group name |
| 104 | Account not found | Verify account ID is correct |
| 105 | User is online | Cannot delete or modify online user |
| 106 | Account is disabled | Enable account first |
| 107 | Account limit reached | Delete unused accounts or upgrade plan |
| 108 | Invalid account ID | Use correct account ID format |

## Device Errors

| errno | Description | Solution |
|-------|-------------|----------|
| 201 | Device not found | Verify device_id is correct |
| 202 | Device offline | Check router is powered on and connected |
| 203 | Device not authorized | Bind device to your OpenAPI account |
| 204 | Device busy | Wait and retry later |
| 205 | Device firmware too old | Update router firmware |
| 206 | Device operation timeout | Retry operation |
| 207 | Device quota exceeded | Wait before making more requests |

## Network Errors

| errno | Description | Solution |
|-------|-------------|----------|
| 301 | Network unreachable | Check internet connectivity |
| 302 | DNS resolution failed | Check DNS settings |
| 303 | Connection timeout | Retry with longer timeout |
| 304 | SSL/TLS error | Check SSL certificate validity |
| 305 | Connection refused | Verify server is running |
| 306 | Connection reset | Network instability, retry |

## Rate Limiting Errors

| errno | Description | Solution |
|-------|-------------|----------|
| 5 | Rate limit exceeded | Reduce request frequency |
| 501 | Too many requests (minute) | Wait before retrying |
| 502 | Too many requests (hour) | Wait before retrying |
| 503 | Too many requests (day) | Wait before retrying |
| 504 | API key quota exceeded | Upgrade your plan |
| 505 | Device rate limit exceeded | Reduce requests to specific device |

## VPN Errors

| errno | Description | Solution |
|-------|-------------|----------|
| 401 | VPN service not enabled | Enable OpenVPN service in router |
| 402 | Invalid VPN configuration | Check VPN settings |
| 403 | VPN certificate error | Verify certificates are correct |
| 404 | VPN connection failed | Check network connectivity and firewall |
| 405 | VPN client limit reached | Disconnect unused clients |
| 406 | VPN subnet conflict | Use different subnet for VPN |
| 407 | VPN port in use | Use different port or stop conflicting service |
| 408 | VPN authentication failed | Check username/password or certificates |

## System Errors

| errno | Description | Solution |
|-------|-------------|----------|
| 601 | Internal server error | Retry operation |
| 602 | Database error | Contact support |
| 603 | Service unavailable | Wait and retry |
| 604 | Maintenance mode | Wait for maintenance to complete |
| 605 | Feature not supported | Check router firmware version |

## File Errors

| errno | Description | Solution |
|-------|-------------|----------|
| 701 | File not found | Verify file path is correct |
| 702 | File too large | Reduce file size |
| 703 | Invalid file format | Use correct file format |
| 704 | File upload failed | Check network and retry |
| 705 | File type not allowed | Use allowed file types |

## API Version Errors

| errno | Description | Solution |
|-------|-------------|----------|
| 801 | API version not supported | Use supported API version |
| 802 | Feature not available in this version | Upgrade API version |
| 803 | Deprecated API endpoint | Use new API endpoint |

## Common Error Handling Patterns

### 1. Token Expiry Handling

```python
try:
    result = client.get_accounts(dev_id)
    if result.get('errno') == 1002 or result.get('errno') == 1001:
        # Token expired, refresh
        client.refresh_access_token()
        result = client.get_accounts(dev_id)
except Exception as e:
    print(f"Error: {str(e)}")
```

### 2. Rate Limiting Handling

```python
import time

def make_api_request_with_retry(client, dev_id, max_retries=3):
    for attempt in range(max_retries):
        result = client.get_accounts(dev_id)
        
        if result.get('errno') == 0:
            return result
        elif result.get('errno') in [5, 501, 502]:
            # Rate limit exceeded, wait and retry
            wait_time = (attempt + 1) * 5  # 5, 10, 15 seconds
            print(f"Rate limited, waiting {wait_time}s...")
            time.sleep(wait_time)
        else:
            # Other error, don't retry
            return result
    
    return result  # Return last result after retries
```

### 3. Network Error Handling

```python
from requests.exceptions import RequestException

try:
    result = client.get_online_users(dev_id)
except RequestException as e:
    if 'timeout' in str(e):
        print("Request timeout, retrying...")
    elif 'connection' in str(e):
        print("Connection error, check network")
    else:
        print(f"Network error: {str(e)}")
```

### 4. Account Creation Handling

```python
def create_account_with_validation(client, dev_id, username, password):
    # Check if account exists
    accounts = client.get_accounts(dev_id)
    if accounts.get('errno') == 0:
        for acc in accounts.get('data', []):
            if acc.get('username') == username:
                return {'errno': 100, 'errmsg': 'Account already exists'}
    
    # Create account
    result = client.add_account(dev_id, username, password)
    
    # Handle specific errors
    if result.get('errno') == 101:
        return {'errno': 101, 'errmsg': 'Invalid username'}
    elif result.get('errno') == 102:
        return {'errno': 102, 'errmsg': 'Invalid password'}
    
    return result
```

## Debugging Tips

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

### Check Error Details

Always log full error response:

```python
result = client.get_accounts(dev_id)
if result.get('errno') != 0:
    print(f"Error {result['errno']}: {result['errmsg']}")
    print(f"Full response: {result}")
```

### Validate Request Parameters

Before making API calls:

```python
def validate_add_account_params(username, password, group, comments):
    errors = []
    
    if not username or len(username) < 3 or len(username) > 32:
        errors.append("Username must be 3-32 characters")
    
    if not password or len(password) < 6 or len(password) > 32:
        errors.append("Password must be 6-32 characters")
    
    return errors if errors else None
```

### Test with Known Good Values

Use test accounts and known working device_id to isolate issues:

```python
# Test with simple request first
test_result = client.get_router_status(dev_id)
if test_result.get('errno') != 0:
    print(f"Basic request failed: {test_result}")
```

## Getting Help

If you encounter an error not listed here:

1. **Check Logs**: Review router logs for detailed error information
2. **Verify Configuration**: Ensure all settings are correct
3. **Test Connectivity**: Verify network connectivity to open.ikuai8.com
4. **Contact Support**: Reach out to iKuai support via:
   - Website: https://www.ikuai8.com
   - Forum: https://bbs.ikuai8.com
   - Email: support@ikuai8.com

## Error Code Ranges Summary

- **0**: Success
- **1-199**: Request and authentication errors
- **200-299**: Device-related errors
- **300-399**: Network errors
- **400-499**: VPN errors
- **500-599**: Rate limiting errors
- **600-699**: System errors
- **700-799**: File errors
- **800-899**: API version errors
- **1000-1999**: Platform-specific errors
