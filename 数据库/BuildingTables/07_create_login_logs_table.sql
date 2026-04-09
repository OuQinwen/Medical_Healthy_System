-- =====================================================
-- 登录日志表 (login_logs)
-- =====================================================
-- 功能：记录用户登录历史
-- 创建时间：2026-03-26
-- =====================================================

CREATE TABLE IF NOT EXISTS login_logs (
    -- 主键
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    
    -- 关联用户
    user_id INT COMMENT '用户ID（登录成功时记录）',
    
    -- 登录信息
    username VARCHAR(50) COMMENT '用户名',
    login_ip VARCHAR(45) COMMENT '登录IP地址',
    user_agent TEXT COMMENT '用户代理信息',
    
    -- 登录状态
    login_status ENUM('success', 'failed', 'locked') NOT NULL COMMENT '登录状态',
    failure_reason VARCHAR(255) COMMENT '失败原因',
    
    -- 地理位置信息（可选）
    country VARCHAR(100) COMMENT '国家',
    city VARCHAR(100) COMMENT '城市',
    
    -- 时间戳
    login_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
    
    -- 外键约束
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    
    -- 索引
    INDEX idx_user_id (user_id),
    INDEX idx_username (username),
    INDEX idx_login_ip (login_ip),
    INDEX idx_login_status (login_status),
    INDEX idx_login_time (login_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='登录日志表';

-- 添加表注释
ALTER TABLE login_logs COMMENT = '登录日志表，记录用户登录历史和安全事件';