# OpenVPN Configuration Guide for iKuai Routers

Complete guide for setting up OpenVPN site-to-site connections on iKuai routers.

## Overview

OpenVPN on iKuai routers supports:
- Site-to-site VPN connections
- Remote access VPN
- Certificate-based authentication
- Routing between VPN networks

## Prerequisites

1. **iKuai Router** (OpenVPN support enabled in firmware)
2. **Network Connectivity** between sites
3. **Static IP addresses** or DDNS for router public IPs
4. **OpenVPN Client Software** for testing

## Server Configuration

### Step 1: Configure Authentication Accounts

1. Log in to iKuai router web interface
2. Navigate to: **认证计费** → **帐号管理** → **添加**

**Account Settings:**
```
用户名: vpn_user1
密码: [Strong Password]
用户组: default
备注: VPN User 1
```

3. Click **保存** (Save)

### Step 2: Configure OpenVPN Server

1. Navigate to: **认证计费** → **OpenVPN 服务端**
2. Check **开启** (Enable)
3. Configure server settings:

**Basic Settings:**
```
监听端口: 1194 (默认)
服务器网段: 10.8.0.0
服务器掩码: 255.255.255.0
```

**Certificate Settings:**
```
CA证书: [Paste CA certificate content]
服务器证书: [Paste server certificate]
服务器密钥: [Paste server private key]
DH参数: [Paste Diffie-Hellman parameters]
```

**Advanced Settings:**
```
协议: UDP (推荐, 更快) 或 TCP
压缩: 启用 LZO 压缩
TLS认证: 启用
最大客户端数: 100
```

4. Click **保存** (Save)

### Step 3: Generate Certificates

Use OpenSSL to generate certificates:

**Generate CA Certificate:**
```bash
openssl genrsa -out ca.key 2048
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt -subj "/CN=iKuai VPN CA"
```

**Generate Server Certificate:**
```bash
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/CN=server"
openssl x509 -req -days 3650 -in server.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out server.crt
```

**Generate Client Certificate:**
```bash
openssl genrsa -out client1.key 2048
openssl req -new -key client1.key -out client1.csr -subj "/CN=client1"
openssl x509 -req -days 3650 -in client1.csr -CA ca.crt -CAkey ca.key -set_serial 02 -out client1.crt
```

**Generate DH Parameters:**
```bash
openssl dhparam -out dh.pem 2048
```

### Step 4: Configure Client on Router (for Site-to-Site)

1. Navigate to: **网络设置** → **VPN客户端** → **OpenVPN** → **添加**

**Client Settings:**
```
服务器IP: [Remote Router Public IP]
服务器端口: 1194
协议: UDP
```

**Certificate Settings:**
```
CA证书: [Copy from server]
客户端证书: [Paste client1.crt content]
客户端密钥: [Paste client1.key content]
```

**Connection Settings:**
```
自动重连: 启用
认证方式: 证书认证
```

2. Click **保存** (Save)

### Step 5: Add Static Routes (Critical!)

**On Server Router:**

1. Navigate to: **网络设置** → **静态路由** → **添加**

**Route to Client Network:**
```
目的地址: [Client LAN Network, e.g., 172.16.2.0]
子网掩码: [Client LAN Mask, e.g., 255.255.255.0]
网关: [VPN Interface Gateway, e.g., 10.8.0.2]
接口: tap0 (VPN接口)
```

2. Click **保存** (Save)

**On Client Router:**

1. Navigate to: **网络设置** → **静态路由** → **添加**

**Route to Server Network:**
```
目的地址: [Server LAN Network, e.g., 172.16.1.0]
子网掩码: [Server LAN Mask, e.g., 255.255.255.0]
网关: [VPN Interface Gateway, e.g., 10.8.0.1]
接口: tap0 (VPN接口)
```

2. Click **保存** (Save)

## Testing the Connection

### 1. Check VPN Status

**On Server:**
- Navigate to: **网络设置** → **VPN客户端**
- Check connection status should be "已连接"

**On Client:**
- Navigate to: **网络设置** → **VPN客户端**
- Check connection status should be "已连接"

### 2. Test Connectivity

**From Server Network:**
```bash
# Ping client network gateway
ping [Client LAN Gateway IP]

# Ping client network host
ping [Client LAN Host IP]

# Traceroute
tracert [Client LAN Host IP]
```

**From Client Network:**
```bash
# Ping server network gateway
ping [Server LAN Gateway IP]

# Ping server network host
ping [Server LAN Host IP]
```

### 3. Verify Routing

**On Server:**
```bash
# Check routing table
route print

# Should show route to client network via VPN interface
```

**On Client:**
```bash
# Check routing table
route print

# Should show route to server network via VPN interface
```

## Client Configuration for Remote Access

For remote access (client computers), create client configuration file:

**client.ovpn:**
```ini
client
dev tun
proto udp
remote [Server Public IP] 1194
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
comp-lzo
verb 3

<ca>
-----BEGIN CERTIFICATE-----
[Paste ca.crt content]
-----END CERTIFICATE-----
</ca>

<cert>
-----BEGIN CERTIFICATE-----
[Paste client1.crt content]
-----END CERTIFICATE-----
</cert>

<key>
-----BEGIN PRIVATE KEY-----
[Paste client1.key content]
-----END PRIVATE KEY-----
</key>
```

Use this file with OpenVPN client software (Windows, Mac, Linux, iOS, Android).

## Troubleshooting

### Connection Issues

**Problem:** Client cannot connect to server

**Solutions:**
1. Check firewall allows UDP port 1194
2. Verify server has public IP or DDNS working
3. Check certificates are correct
4. Verify server is listening on correct port

**Problem:** Connected but cannot access remote network

**Solutions:**
1. **Most common:** Static routes not configured correctly
2. Check VPN interface status
3. Verify subnet configurations don't overlap
4. Check firewall rules between networks

### Certificate Issues

**Problem:** Certificate validation failed

**Solutions:**
1. Verify CA certificate is same on both sides
2. Check client certificate signed by correct CA
3. Verify certificates not expired
4. Check certificate and key files match

### Performance Issues

**Problem:** Slow VPN connection

**Solutions:**
1. Use UDP instead of TCP
2. Enable compression
3. Check internet bandwidth
4. Verify MTU settings (try 1400)
5. Consider using AES-NI acceleration

## Security Best Practices

1. **Use Strong Certificates:**
   - 2048-bit or 4096-bit keys
   - Valid for reasonable period (1-2 years)
   - Rotate certificates regularly

2. **Enable TLS Authentication:**
   - Use tls-auth or tls-crypt
   - Protects against DoS attacks

3. **Limit Access:**
   - Use firewall rules
   - Restrict to specific client IPs
   - Implement fail2ban for brute force protection

4. **Monitor VPN Traffic:**
   - Log all VPN connections
   - Monitor bandwidth usage
   - Set up alerts for unusual activity

5. **Keep Firmware Updated:**
   - Update iKuai router firmware
   - Patch security vulnerabilities
   - Test updates in non-production first

## Advanced Configuration

### Multiple Site Connections

For connecting multiple sites (hub-and-spoke):

1. Configure all remote sites as VPN clients
2. Each client needs unique VPN subnet
3. Add static routes on hub router for all client networks
4. Add static routes on each client for all other client networks

**Example:**
```
Hub: 10.8.0.0/24
Client 1: 10.8.1.0/24, LAN: 172.16.1.0/24
Client 2: 10.8.2.0/24, LAN: 172.16.2.0/24
Client 3: 10.8.3.0/24, LAN: 172.16.3.0/24
```

### Load Balancing

For higher bandwidth with multiple internet connections:

1. Configure multiple OpenVPN instances
2. Use different ports (1194, 1195, 1196)
3. Configure routing tables for load balancing
4. Use policy-based routing

### Failover Configuration

For redundancy:

1. Configure backup server
2. Use connection failover in client config
3. Implement keepalive checks
4. Set up monitoring and alerts

## API Integration

Use the iKuai API to automate VPN management:

```python
from ikuai_api_client import IkuaiAPIClient

client = IkuaiAPIClient(app_id, app_secret)
client.get_access_token()

# Get router status (check VPN interface)
status = client.get_router_status(dev_id)

# Check online VPN users
online_users = client.get_online_users(dev_id)

# Kick VPN user if needed
client.kick_user(dev_id, vpn_user_id)
```

## Support Resources

- iKuai Official Documentation: https://www.ikuai8.com
- OpenVPN Documentation: https://openvpn.net/community-resources/
- iKuai Community Forum: https://bbs.ikuai8.com
