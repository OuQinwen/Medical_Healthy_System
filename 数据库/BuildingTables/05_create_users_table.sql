-- =====================================================
-- 用户表 (users)
-- =====================================================
-- 功能：存储用户账号信息和认证数据
-- 创建时间：2026-03-26
-- =====================================================

CREATE TABLE IF NOT EXISTS users (
    -- 主键
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    
    -- 基本信息
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名（唯一）',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱（唯一）',
    phone VARCHAR(20) COMMENT '手机号（可选）',
    real_name VARCHAR(100) COMMENT '真实姓名',
    
    -- 密码相关
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希值（bcrypt加密）',
    
    -- 角色和权限
    role ENUM('admin', 'researcher', 'viewer') NOT NULL DEFAULT 'viewer' COMMENT '用户角色：admin-管理员，researcher-研究者，viewer-查看者',
    
    -- 状态管理
    is_active BOOLEAN DEFAULT TRUE COMMENT '账号是否激活',
    is_verified BOOLEAN DEFAULT FALSE COMMENT '邮箱是否验证',
    failed_login_attempts INT DEFAULT 0 COMMENT '登录失败次数',
    locked_until DATETIME COMMENT '锁定到期时间',
    
    -- 安全相关
    last_login_time DATETIME COMMENT '最后登录时间',
    last_login_ip VARCHAR(45) COMMENT '最后登录IP',
    password_changed_at DATETIME COMMENT '密码最后修改时间',
    
    -- 时间戳
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    deleted_at DATETIME COMMENT '软删除时间',
    
    -- 备注
    notes TEXT COMMENT '备注信息',
    
    -- 索引
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_phone (phone),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active),
    INDEX idx_created_at (created_at),
    INDEX idx_last_login_time (last_login_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 添加表注释
ALTER TABLE users COMMENT = '用户表，存储用户账号信息和认证数据';