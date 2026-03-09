# iKuai OpenAPI Reference - Router 3.x

Complete API reference for iKuai Router 3.x version.

## Overview

Router 3.x provides enhanced APIs with additional features and improved functionality. While most 2.x operations are supported, 3.x introduces new endpoints and better organization.

## Base URL

```
https://open.ikuai8.com/api/v3/{endpoint}
```

## Authentication

Authentication uses OAuth2-style flow:

### Get Access Token

**Endpoint:** `/api/v3/token`

**Method:** POST

**Request:**
```json
{
  "app_id": "your_app_id",
  "app_secret": "your_app_secret"
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600,
    "open_id": "open_abc123"
  }
}
```

### Refresh Access Token

**Endpoint:** `/api/v3/token/refresh`

**Method:** POST

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response:** Same as Get Access Token

## API Categories

### 1. Platform Authentication (`/api/v3/platform/auth`)

#### Get Authorized Device List

**Endpoint:** `/api/v3/platform/auth/devices`

**Method:** GET

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success",
  "data": {
    "devices": [
      {
        "dev_id": "dev_abc123",
        "name": "Main Router",
        "model": "IK-R3000",
        "status": "online",
        "last_seen": "2024-01-01 12:00:00",
        "ip_address": "192.168.1.1"
      }
    ],
    "total": 1
  }
}
```

### 2. Router System Settings (`/api/v3/system`)

#### Get Router Basic Info

**Endpoint:** `/api/v3/system/info`

**Method:** POST

**Request:**
```json
{
  "dev_id": "dev_abc123"
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success",
  "data": {
    "dev_id": "dev_abc123",
    "model": "IK-R3000",
    "version": "3.5.12",
    "serial": "SN123456789",
    "hostname": "Router01",
    "uptime": 86400,
    "interfaces": [
      {
        "name": "wan1",
        "type": "wan",
        "status": "up",
        "ip": "203.0.113.1",
        "mac": "00:11:22:33:44:55"
      },
      {
        "name": "lan1",
        "type": "lan",
        "status": "up",
        "ip": "192.168.1.1",
        "mac": "00:11:22:33:44:56"
      }
    ]
  }
}
```

#### Get Router Status

**Endpoint:** `/api/v3/system/status`

**Method:** POST

**Request:**
```json
{
  "dev_id": "dev_abc123"
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success",
  "data": {
    "cpu": {
      "usage": 45,
      "cores": 4
    },
    "memory": {
      "usage": 67,
      "total": 8192,
      "available": 2703
    },
    "temperature": {
      "cpu": 55,
      "system": 50
    },
    "network": {
      "upload": 1024000,
      "download": 2048000,
      "sessions": 1234
    },
    "online_users": 10
  }
}
```

#### Set Router Whitelist

**Endpoint:** `/api/v3/system/whitelist`

**Method:** POST

**Request:**
```json
{
  "dev_id": "dev_abc123",
  "data": "192.168.1.100,00:11:22:33:44:55"
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success"
}
```

### 3. User Authentication and Billing (`/api/v3/auth`)

#### Get Account List

**Endpoint:** `/api/v3/auth/accounts`

**Method:** POST

**Request:**
```json
{
  "dev_id": "dev_abc123",
  "page": 1,
  "page_size": 100,
  "filters": {
    "group": "default",
    "state": "up"
  }
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success",
  "data": {
    "accounts": [
      {
        "id": "acc_123",
        "username": "user1",
        "group": "default",
        "state": "up",
        "up_speed": 1024,
        "down_speed": 1024,
        "up_used": 1073741824,
        "down_used": 2147483648,
        "online_time": 3600,
        "comments": "Regular user"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 100
  }
}
```

#### Get Online Users

**Endpoint:** `/api/v3/auth/online`

**Method:** POST

**Request:**
```json
{
  "dev_id": "dev_abc123"
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success",
  "data": {
    "users": [
      {
        "account_id": "acc_123",
        "username": "user1",
        "ip": "192.168.1.100",
        "mac": "00:11:22:33:44:55",
        "interface": "lan1",
        "up_speed": 512,
        "down_speed": 1024,
        "online_time": 3600,
        "login_time": "2024-01-01 10:00:00"
      }
    ],
    "total": 10
  }
}
```

#### Kick User Offline

**Endpoint:** `/api/v3/auth/kick`

**Method:** POST

**Request:**
```json
{
  "dev_id": "dev_abc123",
  "account_id": "acc_123",
  "session_id": "session_456"
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success"
}
```

#### Add Account

**Endpoint:** `/api/v3/auth/account/add`

**Method:** POST

**Request:**
```json
{
  "dev_id": "dev_abc123",
  "username": "newuser",
  "password": "password123",
  "group": "default",
  "up_speed": 1024,
  "down_speed": 1024,
  "comments": "New user account",
  "expire_date": "2024-12-31"
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success",
  "data": {
    "account_id": "acc_new123"
  }
}
```

#### Modify Account

**Endpoint:** `/api/v3/auth/account/modify`

**Method:** POST

**Request:**
```json
{
  "dev_id": "dev_abc123",
  "account_id": "acc_123",
  "username": "updateduser",
  "password": "newpassword",
  "group": "vip",
  "up_speed": 2048,
  "down_speed": 2048,
  "comments": "Updated account"
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success"
}
```

#### Enable/Disable Account

**Endpoint:** `/api/v3/auth/account/toggle`

**Method:** POST

**Request:**
```json
{
  "dev_id": "dev_abc123",
  "account_ids": ["acc_123", "acc_456"],
  "state": "up"
}
```

**State Values:**
- `up`: Enable
- `down`: Disable

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success",
  "data": {
    "succeeded": ["acc_123", "acc_456"],
    "failed": []
  }
}
```

#### Delete Account

**Endpoint:** `/api/v3/auth/account/delete`

**Method:** POST

**Request:**
```json
{
  "dev_id": "dev_abc123",
  "account_ids": ["acc_123", "acc_456"]
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success",
  "data": {
    "deleted": 2
  }
}
```

#### Query Account

**Endpoint:** `/api/v3/auth/account/query`

**Method:** POST

**Request:**
```json
{
  "dev_id": "dev_abc123",
  "account_id": "acc_123"
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success",
  "data": {
    "id": "acc_123",
    "username": "user1",
    "group": "default",
    "state": "up",
    "up_speed": 1024,
    "down_speed": 1024,
    "up_used": 1073741824,
    "down_used": 2147483648,
    "online_time": 86400,
    "comments": "Regular user",
    "created_at": "2024-01-01 00:00:00",
    "last_login": "2024-01-01 10:00:00",
    "expire_date": null
  }
}
```

### 4. Coupon Management (`/api/v3/coupon`)

#### Add Coupon

**Endpoint:** `/api/v3/coupon/add`

**Method:** POST

**Request:**
```json
{
  "dev_id": "dev_abc123",
  "code": "FREE2024",
  "group": "vip",
  "duration_days": 30,
  "max_uses": 100,
  "expire_date": "2024-12-31"
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success"
}
```

#### Delete Coupon

**Endpoint:** `/api/v3/coupon/delete`

**Method:** POST

**Request:**
```json
{
  "dev_id": "dev_abc123",
  "code": "FREE2024"
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success"
}
```

#### Get Coupon List

**Endpoint:** `/api/v3/coupon/list`

**Method:** POST

**Request:**
```json
{
  "dev_id": "dev_abc123"
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success",
  "data": {
    "coupons": [
      {
        "code": "FREE2024",
        "group": "vip",
        "duration_days": 30,
        "max_uses": 100,
        "used_count": 25,
        "expire_date": "2024-12-31",
        "status": "active"
      }
    ]
  }
}
```

### 5. Custom Authentication (`/api/v3/custom-auth`)

#### Push Custom Auth Info

**Endpoint:** `/api/v3/custom-auth/push`

**Method:** POST

**Request:**
```json
{
  "dev_id": "dev_abc123",
  "data": {
    "username": "external_user",
    "password": "hashed_password",
    "attributes": {
      "department": "IT",
      "level": "admin"
    }
  }
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success"
}
```

#### Get Custom Auth Users

**Endpoint:** `/api/v3/custom-auth/users`

**Method:** POST

**Request:**
```json
{
  "dev_id": "dev_abc123"
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success",
  "data": {
    "users": [
      {
        "username": "external_user",
        "attributes": {
          "department": "IT",
          "level": "admin"
        },
        "last_sync": "2024-01-01 12:00:00"
      }
    ]
  }
}
```

## New Features in 3.x

### 1. Pagination Support

All list operations now support pagination:

```json
{
  "page": 1,
  "page_size": 100
}
```

### 2. Filtering and Sorting

Enhanced filtering capabilities:

```json
{
  "filters": {
    "group": "vip",
    "state": "up"
  },
  "sort": {
    "field": "username",
    "order": "asc"
  }
}
```

### 3. Batch Operations

Improved batch operations with detailed results:

```json
{
  "succeeded": ["acc_1", "acc_2"],
  "failed": [
    {"account_id": "acc_3", "error": "Account not found"}
  ]
}
```

### 4. Webhook Support

Subscribe to events:

**Endpoint:** `/api/v3/webhook/subscribe`

**Request:**
```json
{
  "dev_id": "dev_abc123",
  "webhook_url": "https://your-server.com/webhook",
  "events": ["user_login", "user_logout", "account_created"]
}
```

### 5. Advanced Statistics

Get detailed usage statistics:

**Endpoint:** `/api/v3/statistics/usage`

**Request:**
```json
{
  "dev_id": "dev_abc123",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "group_by": "user"
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success",
  "data": {
    "statistics": [
      {
        "username": "user1",
        "upload_bytes": 1073741824,
        "download_bytes": 2147483648,
        "online_time": 86400,
        "login_count": 30
      }
    ]
  }
}
```

## Error Codes

Same error codes as 2.x, plus additional codes:

| errno | Description |
|-------|-------------|
| 901 | Feature not available in 3.x |
| 902 | Invalid API version |
| 903 | Batch operation partial failure |
| 904 | Webhook URL invalid |
| 905 | Webhook subscription failed |

## Migration from 2.x

### API Endpoint Changes

- 2.x: `/apis/action/{open_id}/{dev_id}/{api_id}`
- 3.x: `/api/v3/{category}/{endpoint}`

### Breaking Changes

1. **Request Format**: Use structured JSON instead of parameter strings
2. **Response Format**: Enhanced response with pagination and metadata
3. **Authentication**: OAuth2-style tokens with longer expiration

### Compatibility Layer

Most 2.x operations are still supported via compatibility endpoints. To use 2.x style APIs:

```
https://open.ikuai8.com/api/v3/compatibility/{api_id}
```

## Rate Limiting

Same as 2.x:
- 60 requests per minute
- 1000 requests per hour

Enhanced rate limiting for batch operations:
- Batch size limit: 100 items per request
- Concurrent batch requests: 5 per minute

## Webhook Events

Available webhook events:

- `user_login`: User logs in
- `user_logout`: User logs out
- `account_created`: Account is created
- `account_modified`: Account is modified
- `account_deleted`: Account is deleted
- `quota_exceeded`: User quota exceeded
- `router_status_change`: Router status changes

**Webhook Payload Example:**
```json
{
  "event": "user_login",
  "dev_id": "dev_abc123",
  "timestamp": "2024-01-01T10:00:00Z",
  "data": {
    "username": "user1",
    "ip": "192.168.1.100",
    "mac": "00:11:22:33:44:55"
  }
}
```
