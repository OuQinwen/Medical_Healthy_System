"""
user_auth.py - 用户认证模块

功能说明：
- 用户注册
- 用户登录
- 密码重置
- 用户信息管理
- JWT token生成和验证
- 登录日志记录

依赖：FastAPI, SQLAlchemy, bcrypt, pyjwt
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr, Field, validator
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost/medical_system")

# 创建数据库引擎
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# JWT 配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 默认24小时

# 密码加密配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


# ==================== 数据库模型 ====================

class User(Base):
    """用户表模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20))
    real_name = Column(String(100))
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum('admin', 'doctor'), default='doctor', nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    last_login_time = Column(DateTime)
    last_login_ip = Column(String(45))
    password_changed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = Column(DateTime)
    notes = Column(Text)
    
    # 关系
    login_logs = relationship("LoginLog", back_populates="user")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user")


class PasswordResetToken(Base):
    """密码重置令牌模型"""
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    user = relationship("User", back_populates="password_reset_tokens")


class LoginLog(Base):
    """登录日志模型"""
    __tablename__ = "login_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    username = Column(String(50))
    login_ip = Column(String(45))
    user_agent = Column(Text)
    login_status = Column(Enum('success', 'failed', 'locked'), nullable=False)
    failure_reason = Column(String(255))
    country = Column(String(100))
    city = Column(String(100))
    login_time = Column(DateTime, default=datetime.now)
    
    # 关系
    user = relationship("User", back_populates="login_logs")


# 创建所有表
Base.metadata.create_all(bind=engine)

# ==================== Pydantic 模型 ====================

class UserRegister(BaseModel):
    """用户注册模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=8, max_length=100, description="密码")
    phone: Optional[str] = Field(None, description="手机号")
    real_name: Optional[str] = Field(None, description="真实姓名")
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum() and '_' not in v:
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v.lower()
    
    @validator('password')
    def validate_password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    phone: Optional[str]
    real_name: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_time: Optional[datetime]
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token响应模型"""
    access_token: str
    token_type: str
    user: UserResponse


class ChangePasswordRequest(BaseModel):
    """修改密码请求模型"""
    old_password: str
    new_password: str


class ResetPasswordRequest(BaseModel):
    """重置密码请求模型"""
    email: str


class ResetPasswordConfirm(BaseModel):
    """确认重置密码模型"""
    token: str
    new_password: str


# ==================== 密码工具函数 ====================

def hash_password(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


# ==================== JWT 工具函数 ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ==================== 依赖注入 ====================

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="账号未激活")
    return current_user


# ==================== 认证函数 ====================

def authenticate_user(db: Session, username: str, password: str, login_ip: str = None) -> Optional[User]:
    """验证用户登录"""
    # 查找用户（支持用户名或邮箱登录）
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user:
        # 记录登录失败日志
        log_login(db, username, login_ip, 'failed', '用户不存在')
        return None
    
    # 检查账号是否被锁定
    if user.locked_until and user.locked_until > datetime.now():
        # 记录登录失败日志
        log_login(db, username, login_ip, 'locked', '账号已被锁定')
        return None
    
    # 验证密码
    if not verify_password(password, user.password_hash):
        # 增加失败次数
        user.failed_login_attempts += 1
        
        # 检查是否需要锁定账号
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.now() + timedelta(minutes=30)
            log_login(db, username, login_ip, 'locked', '密码错误次数过多，账号已锁定')
        else:
            log_login(db, username, login_ip, 'failed', '密码错误')
        
        db.commit()
        return None
    
    # 登录成功，重置失败次数
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_time = datetime.now()
    if login_ip:
        user.last_login_ip = login_ip
    
    # 记录登录成功日志
    log_login(db, user.username, login_ip, 'success', None, user.id)
    
    db.commit()
    return user


def log_login(db: Session, username: str, login_ip: str, status: str, failure_reason: str = None, user_id: int = None):
    """记录登录日志"""
    login_log = LoginLog(
        user_id=user_id,
        username=username,
        login_ip=login_ip,
        login_status=status,
        failure_reason=failure_reason
    )
    db.add(login_log)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"记录登录日志失败: {str(e)}")


# ==================== 生成密码哈希（用于初始化） ====================

def generate_password_hash_for_admin(password: str) -> str:
    """为管理员生成密码哈希"""
    return hash_password(password)


if __name__ == "__main__":
    # 生成管理员密码哈希
    print("=== 用户认证模块 - 密码哈希生成工具 ===")
    password = input("请输入要加密的密码: ")
    if password:
        hash_result = generate_password_hash_for_admin(password)
        print(f"\n密码哈希（请复制到数据库）：")
        print(hash_result)
        print(f"\n在数据库中插入管理员用户：")
        print(f"INSERT INTO users (username, email, password_hash, role, is_active) VALUES")
        print(f"('admin', 'admin@example.com', '{hash_result}', 'admin', TRUE);")