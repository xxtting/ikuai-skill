# iKuai Router Management Skill

用于管理爱快路由器的 OpenClaw Skill，提供用户认证管理、在线用户监控、路由器状态查询、网络配置等功能。

## 功能特性

### 核心功能

- ✅ **用户认证管理**: 创建、修改、删除、启用/停用用户账户
- ✅ **在线用户监控**: 实时查看在线用户列表、带宽使用情况
- ✅ **路由器状态监控**: CPU、内存、温度、在线用户数等实时数据
- ✅ **批量操作**: 批量导入/导出用户、批量启用/停用账户
- ✅ **VPN 配置**: OpenVPN 站点间连接配置指南
- ✅ **白名单管理**: 配置路由器白名单，允许特定设备无需认证
- ✅ **实时监控**: 基于阈值的路由器监控和告警

### API 支持

- 爱快路由器 OpenAPI 2.x
- 爱快路由器 OpenAPI 3.x
- 完整的账户管理接口
- 实时在线用户查询
- 路由器状态监控

## 快速开始

### 1. 准备工作

在开始使用之前，您需要：

1. **注册爱快开放平台账号**
   - 访问 [https://open.ikuai8.com](https://open.ikuai8.com)
   - 注册并登录账号

2. **获取 API 凭证**
   - 在开放平台创建应用
   - 获取 `app_id` 和 `app_secret`

3. **授权路由器**
   - 将路由器绑定到您的开放平台账号
   - 获取路由器的 `dev_id`

### 2. 使用 Skill

在对话中直接提出您的需求即可激活此 Skill：

#### 示例 1: 查看路由器状态

```
帮我查看爱快路由器的状态，包括 CPU、内存使用情况
```

#### 示例 2: 查看在线用户

```
查看当前有多少用户在线
```

#### 示例 3: 创建新用户

```
帮我创建一个新用户账户
用户名: zhangsan
密码: Pass123456
用户组: default
```

#### 示例 4: 踢用户下线

```
把用户 lisi 踢下线
```

#### 示例 5: 批量导入用户

```
帮我从 users.csv 文件批量导入用户
```

#### 示例 6: 配置 OpenVPN

```
帮我配置爱快路由器的 OpenVPN 站点间连接
```

#### 示例 7: 监控路由器

```
开始监控路由器状态，当 CPU 超过 80% 时通知我
```

## 目录结构

```
ikuai-router/
├── SKILL.md                 # Skill 主文件（必需）
├── README.md               # 使用说明（本文件）
├── scripts/                # 可执行脚本
│   ├── ikuai_api_client.py        # API 客户端库
│   ├── batch_user_management.py   # 批量用户管理
│   └── router_monitor.py          # 路由器监控
└── references/             # 参考文档
    ├── api_2x_reference.md       # 2.x API 参考
    ├── api_3x_reference.md       # 3.x API 参考
    ├── error_codes.md            # 错误代码参考
    ├── vpn_setup_guide.md        # VPN 配置指南
    └── best_practices.md         # 最佳实践
```

## 脚本使用指南

### ikuai_api_client.py

API 客户端库，提供所有爱快 OpenAPI 的访问接口。

```python
from ikuai_api_client import IkuaiAPIClient

# 初始化客户端
client = IkuaiAPIClient(app_id="your_app_id", app_secret="your_app_secret")

# 获取访问令牌
client.get_access_token()

# 查询在线用户
online_users = client.get_online_users(dev_id="your_dev_id")

# 踢用户下线
client.kick_user(dev_id="your_dev_id", account_id="account_id")

# 关闭连接
client.close()
```

### batch_user_management.py

批量用户管理工具，支持批量导入、导出、启用、停用用户。

```python
from batch_user_management import BatchUserManager

# 初始化管理器
manager = BatchUserManager(client, dev_id="your_dev_id")

# 批量导入用户（CSV 格式）
manager.import_users_from_csv('users.csv', dry_run=True)

# 批量启用用户
manager.bulk_enable_accounts(['user1', 'user2', 'user3'])

# 导出用户列表
manager.export_users_to_csv('users_export.csv')

# 生成用户报告
manager.generate_user_report('user_report.json')
```

**CSV 格式示例：**

```csv
username,password,group,comments
zhangsan,Pass123456,default,部门A
lisi,Pass789012,default,部门B
wangwu,Pass345678,vip,VIP用户
```

### router_monitor.py

路由器实时监控工具，支持阈值告警和历史数据记录。

```python
from router_monitor import RouterMonitor

# 初始化监控
monitor = RouterMonitor(client, dev_id="your_dev_id")

# 设置告警阈值
monitor.set_thresholds(
    cpu_percent=80,
    memory_percent=85,
    temperature_celsius=70
)

# 设置监控间隔（秒）
monitor.set_interval(30)

# 添加告警回调
def alert_callback(alert_type, alert_data):
    print(f"告警: {alert_type}")
    print(f"数据: {alert_data}")

monitor.add_alert_callback(alert_callback)

# 开始监控（Ctrl+C 停止）
monitor.start_monitoring()

# 或者只执行一次检查
monitor.check_once()

# 查看历史数据
history = monitor.get_history(limit=100)

# 查看统计信息
monitor.print_statistics(hours=24)
```

## 常见使用场景

### 场景 1: 日常用户管理

1. 查看所有账户
2. 创建新账户
3. 为新用户分配用户组
4. 设置带宽限制
5. 验证账户创建成功

### 场景 2: 网络流量监控

1. 查看在线用户列表
2. 按带宽使用排序
3. 识别高流量用户
4. 查看用户详细信息
5. 必要时踢用户下线

### 场景 3: 批量用户操作

1. 准备用户数据（CSV 格式）
2. 执行批量导入（先试运行）
3. 验证导入结果
4. 批量启用账户
5. 导出用户列表备份

### 场景 4: OpenVPN 站点间连接

1. 在服务器端配置 OpenVPN 服务端
2. 生成必要的证书
3. 在客户端配置 OpenVPN 客户端
4. 添加静态路由
5. 测试连通性

### 场景 5: 安全响应

1. 查看在线用户
2. 识别可疑会话
3. 踢出可疑用户
4. 停用受损账户
5. 审查路由器日志

## 配置说明

### 环境变量

建议使用环境变量存储敏感信息：

```bash
# Linux/Mac
export IKUAI_APP_ID="your_app_id"
export IKUAI_APP_SECRET="your_app_secret"
export IKUAI_DEV_ID="your_dev_id"

# Windows
set IKUAI_APP_ID=your_app_id
set IKUAI_APP_SECRET=your_app_secret
set IKUAI_DEV_ID=your_dev_id
```

### 配置文件示例

```python
# config.py
import os

class Config:
    IKUAI_APP_ID = os.getenv('IKUAI_APP_ID')
    IKUAI_APP_SECRET = os.getenv('IKUAI_APP_SECRET')
    DEFAULT_DEV_ID = os.getenv('IKUAI_DEV_ID')
    LOG_LEVEL = 'INFO'
```

## 故障排除

### 常见问题

**问题 1: 无法获取访问令牌**
- 检查 app_id 和 app_secret 是否正确
- 确认网络可以访问 open.ikuai8.com
- 验证账户状态是否正常

**问题 2: API 调用失败**
- 检查 dev_id 是否正确
- 确认路由器在线
- 查看错误代码和错误信息

**问题 3: 用户创建失败**
- 确认用户名格式正确（3-32 个字符）
- 检查密码强度（6-32 个字符）
- 确认用户组存在

**问题 4: 踢用户下线失败**
- 用户可能不在线
- 检查 account_id 是否正确
- 确认账户状态正常

## 最佳实践

1. **凭证安全**
   - 永远不要在代码中硬编码凭证
   - 使用环境变量或密钥管理工具
   - 定期轮换访问令牌

2. **错误处理**
   - 始终检查 API 返回的 errno
   - 实现适当的重试逻辑
   - 记录详细的错误日志

3. **性能优化**
   - 使用连接池
   - 合理使用缓存
   - 批量操作替代单次操作

4. **监控告警**
   - 设置合理的告警阈值
   - 定期检查路由器状态
   - 及时响应异常情况

## 参考文档

- [API 2.x 参考](references/api_2x_reference.md) - 爱快路由器 2.x API 完整文档
- [API 3.x 参考](references/api_3x_reference.md) - 爱快路由器 3.x API 完整文档
- [错误代码](references/error_codes.md) - 所有错误代码及解决方案
- [VPN 配置指南](references/vpn_setup_guide.md) - OpenVPN 站点间连接详细指南
- [最佳实践](references/best_practices.md) - 推荐的使用模式和开发实践

## 支持的资源

- **爱快官网**: [https://www.ikuai8.com](https://www.ikuai8.com)
- **开放平台**: [https://open.ikuai8.com](https://open.ikuai8.com)
- **技术论坛**: [https://bbs.ikuai8.com](https://bbs.ikuai8.com)
- **文档中心**: [https://open.ikuai8.com/docs](https://open.ikuai8.com/docs)

## 版本信息

- **Skill 版本**: 1.0.0
- **支持的 API 版本**: 2.x, 3.x
- **Python 要求**: 3.7+
- **依赖库**: requests

## 许可证

本 Skill 供学习使用，请遵守爱快开放平台的使用条款。

## 贡献

欢迎提交问题和改进建议！

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持爱快路由器 2.x 和 3.x API
- 提供完整的用户认证管理功能
- 包含批量操作工具
- 提供路由器监控工具
- 完整的文档和示例

## 联系方式

如有问题或建议，请通过以下方式联系：
- 爱快技术支持: support@ikuai8.com
- 技术论坛: [https://bbs.ikuai8.com](https://bbs.ikuai8.com)
