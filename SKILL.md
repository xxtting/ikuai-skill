---
name: ikuai-router
description: This skill should be used when working with iKuai (爱快) routers. It provides comprehensive management capabilities for iKuai routers via the official OpenAPI, including user authentication management, account management, online user monitoring, router status checking, whitelist management, and VPN configuration. Use this skill when users request to manage iKuai routers, check router status, manage network users, configure authentication settings, or perform any administrative tasks on iKuai router systems.
---

# iKuai Router Management Skill

This skill provides comprehensive management capabilities for iKuai (爱快) routers using the official OpenAPI (open.ikuai8.com). It enables authentication management, account administration, online user monitoring, router status monitoring, and network configuration.

## Overview

The iKuai Router Management skill integrates with the iKuai OpenAPI platform to provide programmatic control over iKuai router functionalities. It supports both router 2.x and 3.x versions with different API endpoints and authentication mechanisms.

## When to Use This Skill

Activate this skill when users request:
- Managing router user authentication and accounts
- Monitoring online users and network status
- Checking router system information
- Configuring router settings (whitelist, routes, etc.)
- Setting up or managing VPN connections
- Performing batch operations on user accounts
- Querying network statistics and usage data

## Prerequisites

Before using this skill, the following must be configured:

1. **iKuai OpenAPI Credentials**
   - Access Token obtained from https://open.ikuai8.com
   - Application ID (app_id) and secret key
   - Device authorization: Router must be bound to the OpenAPI account

2. **Router Access**
   - Router must be accessible via the OpenAPI platform
   - Device ID (dev_id) for the target router
   - Router IP address and login credentials (for local management)

3. **Network Requirements**
   - Access to open.ikuai8.com (for API calls)
   - Stable internet connection
   - Proper firewall rules allowing API access

## API Authentication

The iKuai OpenAPI uses token-based authentication:

1. **Get Access Token**
   - Endpoint: `https://open.ikuai8.com/api/v1/token`
   - Method: POST
   - Parameters: app_id, app_secret
   - Response: access_token, expires_in

2. **Refresh Access Token**
   - Use refresh_token before expiration
   - Typically valid for 24 hours

3. **API Request Format**
   - Base URL: `https://open.ikuai8.com/apis/<action>/<open_id>/<dev_id>/<api_id>`
   - Method: POST (recommended) or GET
   - Headers: Authorization: Bearer {access_token}
   - Content-Type: application/json

## Core Functionalities

### 1. User Authentication Management

#### Get Account List
- API ID: 1 (Router 2.x) or documented equivalent in 3.x
- Purpose: Retrieve all user accounts with their status and details
- Response: Account ID, username, group, upload/download speeds, online status

#### Get Online Users
- API ID: 4 (Router 2.x)
- Purpose: List all currently online users with their IP, MAC, and session details
- Use Case: Real-time network monitoring, traffic analysis

#### Kick User Offline
- API ID: 3 (Router 2.x)
- Parameters: account_id or session_id
- Purpose: Force disconnect a specific user from the network
- Use Case: Security response, bandwidth management

### 2. Account Management

#### Add Account
- API ID: 5 (Router 2.x)
- Parameters: username, password, group, comments
- Purpose: Create new user accounts
- Validation: Username uniqueness, password strength

#### Modify Account
- API ID: 6 (Router 2.x)
- Parameters: account_id, username, password (optional), group, comments
- Purpose: Update existing account details

#### Enable/Disable Account
- API ID: 7 (Router 2.x)
- Parameters: account_id(s), state (up/down)
- Purpose: Suspend or reactivate user accounts without deletion

#### Delete Account
- API ID: 8 (Router 2.x)
- Parameters: account_id(s)
- Purpose: Permanently remove user accounts
- Warning: This action cannot be undone

#### Query Account
- API ID: 11 (Router 2.x)
- Parameters: account_id
- Purpose: Get detailed information for a specific account

### 3. Router Status Monitoring

#### Get Router Status
- API ID: 9 (Router 2.x)
- Purpose: Retrieve comprehensive router status including:
  - CPU and memory usage
  - Network interface status
  - Connection counts
  - Uptime
  - Firmware version

#### Get Router Basic Info
- API ID: Router 3.x equivalent
- Purpose: Basic router information (model, serial, version)

### 4. Network Configuration

#### Set Router Whitelist
- API ID: 10 (Router 2.x)
- Parameters: IP addresses or MAC addresses
- Purpose: Configure allowed devices bypassing authentication
- Use Cases: IoT devices, trusted systems

### 5. VPN Management (OpenVPN)

For OpenVPN configuration on iKuai routers:

#### Server Configuration
- Navigate to: 认证计费 -> OpenVPN 服务端
- Configure:
  - Server port (default: 1194)
  - VPN subnet and mask
  - CA certificate
  - Server certificate
  - Diffie-Hellman parameters

#### Client Configuration
- Navigate to: 网络设置 -> VPN 客户端 -> OpenVPN -> 添加
- Configure:
  - Server IP address
  - Server port
  - CA certificate (copy from server)
  - Client certificate
  - Client key

#### Static Routing (Required for Inter-VPN Communication)
- Navigate to: 网络设置 -> 静态路由 -> 添加
- Add routes for remote subnets through VPN interface

## Error Handling

Common error codes:
- `errno: 0` - Success
- `errno: 1` - Invalid parameters
- `errno: 2` - Authentication failed
- `errno: 3` - Permission denied
- `errno: 4` - Resource not found
- `errno: 5` - Rate limit exceeded

Always check `errno` and `errmsg` in API responses before proceeding.

## Working with Scripts

This skill includes the following scripts in `scripts/` directory:

### `ikuai_api_client.py`
Python client library for iKuai OpenAPI with the following features:
- Automatic token management (obtain and refresh)
- Simplified API call functions for common operations
- Error handling and retry logic
- Support for both 2.x and 3.x API versions

Usage:
```python
from ikuai_api_client import IkuaiAPIClient

client = IkuaiAPIClient(app_id, app_secret)
client.get_access_token()

# Get online users
online_users = client.get_online_users(dev_id)

# Kick user offline
client.kick_user(dev_id, account_id)
```

### `batch_user_management.py`
Batch operations for user account management:
- Import users from CSV
- Bulk enable/disable accounts
- Bulk delete accounts
- Export user list to CSV

Usage:
```python
from batch_user_management import BatchUserManager

manager = BatchUserManager(client, dev_id)
manager.import_users('users.csv')
manager.bulk_enable(['user1', 'user2'])
```

### `router_monitor.py`
Real-time router monitoring and alerting:
- Periodic status checks
- Threshold-based alerts (CPU, memory, bandwidth)
- Historical data logging
- Webhook notifications

Usage:
```python
from router_monitor import RouterMonitor

monitor = RouterMonitor(client, dev_id)
monitor.set_alerts(cpu_threshold=80, memory_threshold=85)
monitor.start_monitoring(interval=60)
```

## Reference Documentation

Detailed API documentation is available in `references/` directory:

- `api_2x_reference.md` - Complete API reference for router 2.x version
- `api_3x_reference.md` - Complete API reference for router 3.x version
- `error_codes.md` - Detailed error code documentation
- `vpn_setup_guide.md` - Step-by-step OpenVPN configuration guide
- `best_practices.md` - Recommended usage patterns and security considerations

Load these reference files when working with specific API endpoints or troubleshooting issues.

## Common Workflows

### Workflow 1: Add New User Account
1. Authenticate and obtain access token
2. Check if username exists (Get Account List)
3. Call Add Account API with user details
4. Verify account creation (Query Account)
5. Optionally add to whitelist if needed

### Workflow 2: Monitor and Manage Bandwidth
1. Get online users list
2. Sort by upload/download bandwidth
3. Identify high-bandwidth users
4. Check account details and group assignments
5. Modify user group or kick user if necessary

### Workflow 3: Batch Import Users
1. Prepare CSV with user data (username, password, group, comments)
2. Use `batch_user_management.py` script
3. Validate CSV format
4. Execute import with dry-run option first
5. Review results and proceed with actual import

### Workflow 4: Setup OpenVPN Site-to-Site
1. Configure OpenVPN server on router 1
2. Configure OpenVPN client on router 2
3. Generate and exchange certificates
4. Add static routes for inter-subnet communication
5. Test connectivity between networks

### Workflow 5: Respond to Security Incident
1. Get online users list
2. Identify suspicious sessions (high traffic, unusual times)
3. Kick suspicious users offline
4. Disable compromised accounts
5. Review and update whitelist if needed
6. Check router logs for additional indicators

## Security Considerations

1. **Credential Management**
   - Store app_id and app_secret securely
   - Rotate access tokens regularly
   - Never log or expose tokens

2. **Network Security**
   - Use HTTPS for all API calls
   - Validate SSL certificates
   - Implement rate limiting to prevent abuse

3. **User Privacy**
   - Minimize data collection
   - Anonymize logs when possible
   - Follow data protection regulations

4. **Access Control**
   - Implement principle of least privilege
   - Audit API access regularly
   - Revoke unused tokens

## Troubleshooting

### Authentication Issues
- Verify app_id and app_secret are correct
- Check network connectivity to open.ikuai8.com
- Ensure device is authorized in the OpenAPI account
- Refresh expired access tokens

### API Call Failures
- Check dev_id corresponds to correct router
- Verify router is online and accessible
- Review error codes in response
- Check rate limiting status

### Connection Issues
- Ensure router has internet connectivity
- Verify firewall rules allow API access
- Check DNS resolution for open.ikuai8.com
- Test with alternative network if possible

## Version Compatibility

- **Router 2.x**: Uses specific API IDs (1-11 for core operations)
- **Router 3.x**: Enhanced API with additional features
- **Backward Compatibility**: 3.x APIs support most 2.x operations
- **Deprecation Warning**: Some 2.x endpoints may be deprecated in future versions

## Limitations

1. API rate limits: Maximum requests per minute/hour
2. Concurrent connections: Limited number of simultaneous sessions
3. Batch operations: Maximum number of items per request
4. Historical data: Limited retention period for logs and statistics

## Best Practices

1. **Token Management**: Always refresh tokens before expiration
2. **Error Handling**: Implement retry logic for transient failures
3. **Rate Limiting**: Respect API rate limits to avoid being blocked
4. **Logging**: Maintain detailed logs for auditing and debugging
5. **Testing**: Test all operations in non-production environment first
6. **Backup**: Backup critical data before bulk operations
7. **Monitoring**: Continuously monitor router status and alerts

## Extending This Skill

To add new functionalities:

1. **Add API Wrappers**: Extend `ikuai_api_client.py` with new API endpoints
2. **Create New Scripts**: Add specialized scripts for specific use cases
3. **Update References**: Document new APIs and workflows in reference files
4. **Test Thoroughly**: Ensure new features work correctly before deployment
