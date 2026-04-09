# 数据库配置指南

本指南将帮助您配置医学数据融合科研系统的数据库。

## 前置要求

- MySQL 8.0 或更高版本
- MySQL root用户或具有创建数据库权限的用户

## 快速开始

### 1. 创建数据库

```bash
cd 数据库/BuildingTables
mysql -u root -p < create_all_tables.sql
```

这将自动创建名为 `medical_research_system` 的数据库和所有必需的表。

### 2. 创建数据库用户（可选但推荐）

```sql
-- 登录MySQL
mysql -u root -p

-- 创建专用用户
CREATE USER 'medical_user'@'localhost' IDENTIFIED BY 'your_secure_password';

-- 授予权限
GRANT ALL PRIVILEGES ON medical_research_system.* TO 'medical_user'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- 退出
EXIT;
```

### 3. 配置后端连接

编辑 `后端服务器/.env` 文件：

```env
DATABASE_URL=mysql+pymysql://medical_user:your_secure_password@localhost:3306/medical_research_system
```

## 数据库表结构

系统包含以下主要数据表：

- `patients` - 患者基本信息
- `demographic_data` - 人口学信息  
- `surgery_history` - 手术史
- `lab_results` - 检查结果
- `imaging_reports` - 影像报告
- `users` - 系统用户
- `login_logs` - 登录日志
- `file_uploads` - 文件上传记录

## 验证安装

```sql
-- 连接到数据库
mysql -u medical_user -p medical_research_system

-- 查看所有表
SHOW TABLES;

-- 查看患者表结构
DESCRIBE patients;
```

## 常见问题

### 连接失败

**问题**: 无法连接到数据库

**解决方案**:
```bash
# 检查MySQL服务状态
# Windows:
net start mysql

# Linux:
sudo systemctl status mysql

# 测试连接
mysql -u medical_user -p -h localhost medical_research_system
```

### 权限错误

**问题**: Access denied for user

**解决方案**:
```sql
-- 重新授予权限
GRANT ALL PRIVILEGES ON medical_research_system.* TO 'medical_user'@'localhost';
FLUSH PRIVILEGES;
```

### 字符集问题

**问题**: 中文乱码

**解决方案**:
```sql
-- 确保数据库使用utf8mb4字符集
ALTER DATABASE medical_research_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 备份与恢复

### 备份数据库

```bash
mysqldump -u medical_user -p medical_research_system > backup_$(date +%Y%m%d).sql
```

### 恢复数据库

```bash
mysql -u medical_user -p medical_research_system < backup_20260409.sql
```

## 安全建议

1. 使用强密码
2. 限制数据库用户权限
3. 定期备份数据
4. 启用SSL连接（生产环境）
5. 限制远程访问

## 性能优化

### 添加索引

系统已包含必要的索引，如需优化：

```sql
-- 分析查询性能
EXPLAIN SELECT * FROM patients WHERE patient_name = '张三';

-- 添加索引
CREATE INDEX idx_patient_name ON patients(patient_name);
```

### 配置优化

编辑 `my.cnf` 或 `my.ini`：

```ini
[mysqld]
innodb_buffer_pool_size=1G
max_connections=200
query_cache_size=64M
```

---

**注意**: 请确保在生产环境中修改默认密码并实施适当的安全措施。