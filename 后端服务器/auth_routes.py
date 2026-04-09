"""
auth_routes.py - 用户认证API路由

功能说明：
- 用户注册
- 用户登录
- 获取当前用户信息
- 修改密码
- 重置密码
- 用户管理

依赖：FastAPI, user_auth
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timedelta
import secrets
import string

from user_auth import (
    get_db, User, PasswordResetToken, LoginLog,
    UserRegister, UserLogin, UserResponse, TokenResponse,
    ChangePasswordRequest, ResetPasswordRequest, ResetPasswordConfirm,
    hash_password, verify_password, create_access_token, verify_token,
    authenticate_user, log_login, get_current_user, get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# 创建路由
router = APIRouter(prefix="/api/auth", tags=["auth"])

# 在main.py中，我们还需要注册一个独立的路由到/api/change-password
# 为了支持前端的直接调用


# ==================== 用户注册 ====================

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    用户注册
    
    参数：
    - username: 用户名（3-50字符）
    - email: 邮箱
    - password: 密码（至少8位，包含大小写字母和数字）
    - phone: 手机号（可选）
    - real_name: 真实姓名（可选）
    
    返回：
    - 注册成功信息
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被注册"
        )
    
    # 检查邮箱是否已存在
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建新用户
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        phone=user_data.phone,
        real_name=user_data.real_name,
        role='doctor',  # 默认角色
        is_active=True,
        is_verified=False
    )
    
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )
    
    return {
        "success": True,
        "message": "注册成功",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role
        }
    }


# ==================== 用户登录 ====================

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """
    用户登录
    
    参数：
    - username: 用户名或邮箱
    - password: 密码
    
    返回：
    - access_token: JWT令牌
    - token_type: 令牌类型
    - user: 用户信息
    """
    # 获取客户端IP
    client_ip = request.client.host if request.client else None
    
    # 验证用户
    user = authenticate_user(db, user_data.username, user_data.password, client_ip)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            real_name=user.real_name,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login_time=user.last_login_time
        )
    }


# ==================== 获取当前用户信息 ====================

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    获取当前用户信息
    
    需要认证
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        phone=current_user.phone,
        real_name=current_user.real_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login_time=current_user.last_login_time
    )


# ==================== 修改密码 ====================

class ChangePasswordRequestFrontend(BaseModel):
    """修改密码请求模型（前端版本）"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


async def change_password(
    password_data: ChangePasswordRequestFrontend,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    修改密码
    
    参数：
    - current_password: 当前密码
    - new_password: 新密码（至少6位）
    
    需要认证
    """
    # 验证当前密码
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )
    
    # 验证新密码强度
    if len(password_data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度至少6位"
        )
    
    # 检查新密码是否与当前密码相同
    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与当前密码相同"
        )
    
    # 更新密码
    current_user.password_hash = hash_password(password_data.new_password)
    current_user.password_changed_at = datetime.now()
    
    db.commit()
    
    return {
        "success": True,
        "message": "密码修改成功"
    }


# 在auth路由中注册修改密码端点
@router.post("/change-password")
async def auth_change_password(
    password_data: ChangePasswordRequestFrontend,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """auth路由中的修改密码端点"""
    return await change_password(password_data, current_user, db)


# ==================== 请求重置密码 ====================

@router.post("/reset-password")
async def request_password_reset(
    reset_data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    请求重置密码
    
    参数：
    - email: 邮箱
    
    返回：
    - 重置令牌（实际应用中应该通过邮件发送）
    """
    # 查找用户
    user = db.query(User).filter(User.email == reset_data.email).first()
    
    if not user:
        # 为了安全，即使用户不存在也返回成功
        return {
            "success": True,
            "message": "如果该邮箱已注册，重置链接已发送"
        }
    
    # 生成重置令牌
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(minutes=15)  # 15分钟有效期
    
    # 删除该用户之前的未使用令牌
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.is_used == False,
        PasswordResetToken.expires_at > datetime.now()
    ).delete()
    
    # 创建新的重置令牌
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    
    db.add(reset_token)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成重置令牌失败: {str(e)}"
        )
    
    # 实际应用中，这里应该发送邮件
    # send_reset_email(user.email, token)
    
    # 为了演示，返回令牌（生产环境不要这样做）
    return {
        "success": True,
        "message": "重置链接已发送到您的邮箱",
        "token": token,  # 仅用于演示，生产环境请删除
        "reset_url": f"/api/auth/reset-password-confirm?token={token}"
    }


# ==================== 确认重置密码 ====================

@router.post("/reset-password-confirm")
async def confirm_password_reset(
    reset_data: ResetPasswordConfirm,
    db: Session = Depends(get_db)
):
    """
    确认重置密码
    
    参数：
    - token: 重置令牌
    - new_password: 新密码
    
    返回：
    - 重置结果
    """
    # 查找有效的重置令牌
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == reset_data.token,
        PasswordResetToken.is_used == False,
        PasswordResetToken.expires_at > datetime.now()
    ).first()
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重置令牌无效或已过期"
        )
    
    # 获取用户
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 验证新密码强度
    if len(reset_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度至少8位"
        )
    
    if not any(c.isupper() for c in reset_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码必须包含至少一个大写字母"
        )
    
    if not any(c.islower() for c in reset_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码必须包含至少一个小写字母"
        )
    
    if not any(c.isdigit() for c in reset_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码必须包含至少一个数字"
        )
    
    # 更新密码
    user.password_hash = hash_password(reset_data.new_password)
    user.password_changed_at = datetime.now()
    user.failed_login_attempts = 0  # 重置失败次数
    user.locked_until = None  # 解锁账号
    
    # 标记令牌为已使用
    reset_token.is_used = True
    reset_token.used_at = datetime.now()
    
    db.commit()
    
    return {
        "success": True,
        "message": "密码重置成功，请使用新密码登录"
    }


# ==================== 获取用户列表（管理员） ====================

@router.get("/users", response_model=list[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取用户列表（仅管理员）
    
    参数：
    - skip: 跳过数量
    - limit: 返回数量
    
    需要认证
    """
    # 检查权限
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            real_name=user.real_name,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login_time=user.last_login_time
        )
        for user in users
    ]


# ==================== 更新用户状态（管理员） ====================

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    is_active: bool,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新用户状态（仅管理员）
    
    参数：
    - user_id: 用户ID
    - is_active: 是否激活
    
    需要认证
    """
    # 检查权限
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 不能修改自己的状态
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的状态"
        )
    
    # 查找用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新状态
    user.is_active = is_active
    db.commit()
    
    return {
        "success": True,
        "message": f"用户状态已更新为：{'激活' if is_active else '禁用'}"
    }


# ==================== 获取登录日志（管理员） ====================

@router.get("/login-logs")
async def get_login_logs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取登录日志（仅管理员）
    
    参数：
    - skip: 跳过数量
    - limit: 返回数量
    
    需要认证
    """
    # 检查权限
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    logs = db.query(LoginLog).order_by(LoginLog.login_time.desc()).offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "logs": [
            {
                "id": log.id,
                "username": log.username,
                "login_ip": log.login_ip,
                "login_status": log.login_status,
                "failure_reason": log.failure_reason,
                "login_time": log.login_time
            }
            for log in logs
        ]
    }