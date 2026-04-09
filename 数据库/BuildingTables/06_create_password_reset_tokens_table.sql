-- =====================================================
-- 密码重置令牌表 (password_reset_tokens)
-- =====================================================
-- 功能：存储密码重置令牌
-- 创建时间：2026-03-26
-- =====================================================

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    -- 主键
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '令牌ID',
    
    -- 关联用户
    user_id INT NOT NULL COMMENT '用户ID',
    
    -- 令牌信息
    token VARCHAR(255) NOT NULL UNIQUE COMMENT '重置令牌',
    expires_at DATETIME NOT NULL COMMENT '过期时间',
    
    -- 状态
    is_used BOOLEAN DEFAULT FALSE COMMENT '是否已使用',
    used_at DATETIME COMMENT '使用时间',
    
    -- 时间戳
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    -- 外键约束
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- 索引
    INDEX idx_user_id (user_id),
    INDEX idx_token (token),
    INDEX idx_expires_at (expires_at),
    INDEX idx_is_used (is_used)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='密码重置令牌表';

-- 添加表注释
ALTER TABLE password_reset_tokens COMMENT = '密码重置令牌表，用于密码重置功能';