# iKuai OpenAPI Reference - Router 2.x

Complete API reference for iKuai Router 2.x version.

## Base URL

```
https://open.ikuai8.com/apis/action/{open_id}/{dev_id}/{api_id}
```

## Authentication

All API requests require:
- HTTP Method: POST (recommended) or GET
- Header: `Authorization: Bearer {access_token}`
- Content-Type: `application/json`

## API Endpoints

### 1. Get Account List

**API ID:** `1`

**Description:** Retrieve all user accounts with their status and details.

**Request Parameters:** None

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success",
  "data": [
    {
      "id": "account_id",
      "username": "user_name",
      "password": "encrypted_password",
      "group": "user_group",
      "up_speed": 1024,
      "down_speed": 1024,
      "state": "up",
      "comments": "user comments",
      "online_time": 0
    }
  ]
}
```

**Fields:**
- `id`: Account unique identifier
- `username`: Account username
- `group`: User group name
- `up_speed`: Upload speed limit (KB/s)
- `down_speed`: Download speed limit (KB/s)
- `state`: Account status ("up"=enabled, "down"=disabled)
- `online_time`: Total online time (seconds)

---

### 2. Kick User Offline

**API ID:** `3`

**Description:** Force disconnect a specific user from the network.

**Request Parameters:**
```json
{
  "id": "account_id"
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success"
}
```

**Multiple Users:** Separate multiple account IDs with commas.

---

### 3. Get Online Users

**API ID:** `4`

**Description:** List all currently online users with their connection details.

**Request Parameters:** None

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success",
  "data": [
    {
      "username": "user_name",
      "account_id": "account_id",
      "ip": "192.168.1.100",
      "mac": "00:11:22:33:44:55",
      "up_speed": 1024,
      "down_speed": 2048,
      "online_time": 3600
    }
  ]
}
```

---

### 4. Add Account

**API ID:** `5`

**Description:** Create a new user account.

**Request Parameters:**
```json
{
  "username": "new_user",
  "password": "password123",
  "group": "default",
  "comments": "Optional comments"
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success",
  "data": {
    "id": "new_account_id"
  }
}
```

**Validation:**
- Username must be unique
- Password length: 6-32 characters
- Group must exist

---

### 5. Modify Account

**API ID:** `6`

**Description:** Update an existing user account.

**Request Parameters:**
```json
{
  "id": "account_id",
  "username": "updated_user",
  "password": "new_password",
  "group": "new_group",
  "comments": "Updated comments"
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success"
}
```

**Note:** Only include fields that need to be changed.

---

### 6. Enable/Disable Account

**API ID:** `7`

**Description:** Enable or disable a user account.

**Request Parameters:**
```json
{
  "id": "account_id",
  "state": "up"
}
```

**State Values:**
- `up`: Enable account
- `down`: Disable account

**Multiple Accounts:** Separate multiple account IDs with commas.

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success"
}
```

---

### 7. Delete Account

**API ID:** `8`

**Description:** Permanently remove a user account.

**Request Parameters:**
```json
{
  "id": "account_id"
}
```

**Multiple Accounts:** Separate multiple account IDs with commas.

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success"
}
```

**Warning:** This action cannot be undone.

---

### 8. Get Router Status

**API ID:** `9`

**Description:** Retrieve comprehensive router status information.

**Request Parameters:** None

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success",
  "data": {
    "cpu": 45,
    "mem": 67,
    "temp": 55,
    "uptime": 86400,
    "online_users": 10,
    "bandwidth": 100,
    "version": "2.x.x.x",
    "model": "router_model"
  }
}
```

**Fields:**
- `cpu`: CPU usage percentage (0-100)
- `mem`: Memory usage percentage (0-100)
- `temp`: Temperature (Celsius)
- `uptime`: System uptime (seconds)
- `online_users`: Current online user count
- `bandwidth`: Current bandwidth usage (Mbps)
- `version`: Firmware version
- `model`: Router model name

---

### 9. Set Router Whitelist

**API ID:** `10`

**Description:** Configure allowed devices that bypass authentication.

**Request Parameters:**
```json
{
  "data": "whitelist_configuration"
}
```

**Whitelist Format:**
- IP addresses: `192.168.1.100,192.168.1.101`
- MAC addresses: `00:11:22:33:44:55,AA:BB:CC:DD:EE:FF`
- Mixed format: `192.168.1.100,00:11:22:33:44:55`

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success"
}
```

---

### 10. Query Account

**API ID:** `11`

**Description:** Get detailed information for a specific account.

**Request Parameters:**
```json
{
  "id": "account_id"
}
```

**Response:**
```json
{
  "errno": 0,
  "errmsg": "success",
  "data": {
    "id": "account_id",
    "username": "user_name",
    "group": "user_group",
    "up_speed": 1024,
    "down_speed": 2048,
    "state": "up",
    "comments": "Account comments",
    "online_time": 86400,
    "last_login": "2024-01-01 12:00:00"
  }
}
```

---

## Error Codes

| errno | Description |
|-------|-------------|
| 0 | Success |
| 1 | Invalid parameters |
| 2 | Authentication failed |
| 3 | Permission denied |
| 4 | Resource not found |
| 5 | Rate limit exceeded |
| 100 | Account already exists |
| 101 | Invalid username |
| 102 | Invalid password |
| 103 | Group not found |
| 104 | Account not found |
| 105 | User is online |

## Rate Limiting

- Maximum requests: 60 per minute
- Maximum requests: 1000 per hour
- Exceeding limits will return errno: 5

## Common Response Fields

All API responses include:

```json
{
  "errno": 0,
  "errmsg": "success",
  "data": {}
}
```

- `errno`: Error code (0 = success)
- `errmsg`: Error message
- `data`: Response data (if applicable)
