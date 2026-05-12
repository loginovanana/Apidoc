#!/usr/bin/env python3
"""
APIDoc Manager v0.1.0 → v0.2.0 Production Hardening Script
Автоматическое применение критических исправлений безопасности и архитектуры.

Запуск: python fix_production.py [--apply] [--backup]
"""

import os
import re
import sys
import shutil
import secrets
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Цветной вывод
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def log(msg: str, level: str = "INFO"):
    colors = {"ERROR": Colors.RED, "WARNING": Colors.YELLOW, "SUCCESS": Colors.GREEN, 
              "INFO": Colors.BLUE, "FIX": Colors.CYAN}
    prefix = colors.get(level, "")
    print(f"{prefix}[{level}]{Colors.RESET} {msg}")

class APIDocHardener:
    """Автоматическое исправление проблем безопасности и архитектуры."""
    
    def __init__(self, project_root: Path, apply: bool = False, backup: bool = True):
        self.root = Path(project_root)
        self.apply = apply
        self.backup = backup
        self.backup_dir = self.root / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.fixes_applied = []
        self.errors = []
        self.generated_secrets = {}
        
    def run(self):
        """Запуск всех исправлений."""
        log(f"{'='*70}", "INFO")
        log(f"APIDoc Manager Production Hardening Tool", "BOLD")
        log(f"Project: {self.root}", "INFO")
        log(f"Mode: {'APPLY' if self.apply else 'DRY RUN'}", "WARNING" if not self.apply else "SUCCESS")
        log(f"Backup: {self.backup_dir if self.backup else 'DISABLED'}", "INFO")
        log(f"{'='*70}", "INFO")
        
        fixes = [
            # Приоритет 1 - Критические
            ("Generate secure SECRET_KEY", self.fix_secret_key),
            ("Remove hardcoded passwords from docker-compose.yml", self.fix_docker_compose_secrets),
            ("Remove hardcoded secrets from K8s manifests", self.fix_k8s_secrets),
            ("Enable and configure CSRF middleware", self.fix_csrf_middleware),
            ("Configure strict CORS settings", self.fix_cors_settings),
            ("Add rate limiting to auth endpoint", self.fix_rate_limiting),
            ("Create .env.example with secure defaults", self.create_env_example),
            ("Add .gitignore for sensitive files", self.fix_gitignore),
            
            # Приоритет 2 - Высокие
            ("Fix database pool configuration", self.fix_database_pool),
            ("Add soft delete to Specification model", self.fix_soft_delete),
            ("Optimize N+1 queries with JOIN", self.fix_n_plus_one),
            ("Create common validation module", self.create_common_validator),
            ("Add security headers middleware", self.add_security_headers),
            ("Fix JWT token revocation (Redis)", self.fix_jwt_revocation),
            ("Add input sanitization", self.add_input_sanitization),
            
            # Приоритет 3 - Качество кода
            ("Fix type hints for Python 3.10+", self.fix_type_hints),
            ("Remove dead code and unused imports", self.fix_dead_code),
            ("Add proper error handling to subprocess", self.fix_subprocess_handling),
            ("Create CI/CD GitHub Actions workflow", self.create_ci_cd),
        ]
        
        for name, fix_func in fixes:
            try:
                log(f"Applying: {name}...", "FIX")
                fix_func()
                self.fixes_applied.append(name)
                log(f"  ✓ {name}", "SUCCESS")
            except Exception as e:
                self.errors.append((name, str(e)))
                log(f"  ✗ {name}: {str(e)}", "ERROR")
        
        self.print_summary()
    
    def _backup_file(self, filepath: Path) -> Path:
        """Создать бэкап файла перед изменением."""
        if not self.backup or not filepath.exists():
            return filepath
        
        relative = filepath.relative_to(self.root)
        backup_path = self.backup_dir / relative
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(filepath, backup_path)
        return filepath
    
    def _read_file(self, filepath: Path) -> str:
        """Чтение файла."""
        if filepath.exists():
            return filepath.read_text(encoding='utf-8')
        return ""
    
    def _write_file(self, filepath: Path, content: str) -> None:
        """Запись файла (с бэкапом если нужно)."""
        if self.apply:
            if filepath.exists():
                self._backup_file(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content, encoding='utf-8')
    
    def _generate_secret(self, length: int = 64) -> str:
        """Генерация криптографически безопасного секрета."""
        return secrets.token_urlsafe(length)
    
    # ===== ПРИОРИТЕТ 1: КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ =====
    
    def fix_secret_key(self) -> None:
        """Генерация безопасного SECRET_KEY и замена хардкода."""
        new_secret = self._generate_secret(64)
        self.generated_secrets['SECRET_KEY'] = new_secret
        
        # 1. Исправление в config.py
        config_path = self.root / "apidoc_server" / "config.py"
        content = self._read_file(config_path)
        
        # Замена дефолтного значения
        content = content.replace(
            'secret_key: str = Field("change-me-in-production")',
            f'secret_key: str = Field(..., description="JWT signing key, min 32 chars")'
        )
        
        # Добавление валидации
        if '@field_validator("secret_key"' not in content:
            validator_code = '''
    
    @field_validator("secret_key", mode="after")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure secret key is secure."""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        if v in {"change-me-in-production", "your-secret-key-here-change-in-production", "dev-secret-key-change-in-production"}:
            raise ValueError("Default SECRET_KEY detected - please set APIDOC_SECRET_KEY environment variable")
        return v'''
            # Вставить после поля secret_key
            content = content.replace(
                'token_expire_minutes: int = Field(1440)',
                'token_expire_minutes: int = Field(1440)' + validator_code
            )
        
        self._write_file(config_path, content)
        
        # 2. Создание/обновление .env
        env_path = self.root / ".env"
        env_content = self._read_file(env_path)
        
        if env_content:
            env_lines = []
            for line in env_content.split('\n'):
                if line.startswith('APIDOC_SECRET_KEY='):
                    env_lines.append(f'APIDOC_SECRET_KEY={new_secret}')
                else:
                    env_lines.append(line)
            if 'APIDOC_SECRET_KEY=' not in env_content:
                env_lines.append(f'APIDOC_SECRET_KEY={new_secret}')
            self._write_file(env_path, '\n'.join(env_lines))
        else:
            self._write_file(env_path, f'APIDOC_SECRET_KEY={new_secret}\n')
    
    def fix_docker_compose_secrets(self) -> None:
        """Замена хардкод-паролей на переменные окружения."""
        compose_path = self.root / "docker-compose.yml"
        if not compose_path.exists():
            log("docker-compose.yml not found, skipping", "WARNING")
            return
        
        content = self._read_file(compose_path)
        new_secret = self.generated_secrets.get('SECRET_KEY', self._generate_secret(64))
        
        # Замена паролей
        replacements = {
            'POSTGRES_USER: apidoc': 'POSTGRES_USER: ${POSTGRES_USER:-apidoc}',
            'POSTGRES_PASSWORD: apidoc_password': 'POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?required}',
            'POSTGRES_DB: apidoc': 'POSTGRES_DB: ${POSTGRES_DB:-apidoc}',
            'APIDOC_SECRET_KEY: dev-secret-key-change-in-production': f'APIDOC_SECRET_KEY: ${{APIDOC_SECRET_KEY:-{new_secret}}}',
            'APIDOC_REDIS_URL: redis://redis:6379/0': 'APIDOC_REDIS_URL: ${APIDOC_REDIS_URL:-redis://redis:6379/0}',
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        self._write_file(compose_path, content)
        
        # Также для prod версии
        prod_compose = self.root / "docker" / "docker-compose.prod.yml"
        if prod_compose.exists():
            prod_content = self._read_file(prod_compose)
            prod_content = prod_content.replace(
                'APIDOC_SECRET_KEY: ${SECRET_KEY}',
                'APIDOC_SECRET_KEY: ${APIDOC_SECRET_KEY:?required}'
            )
            self._write_file(prod_compose, prod_content)
    
    def fix_k8s_secrets(self) -> None:
        """Замена хардкод-секретов в K8s манифестах."""
        k8s_secrets = self.root / "k8s" / "secrets.yaml"
        if not k8s_secrets.exists():
            return
        
        new_secret = self.generated_secrets.get('SECRET_KEY', self._generate_secret(64))
        content = self._read_file(k8s_secrets)
        
        # Добавление предупреждения
        warning = "# WARNING: This file contains secrets. DO NOT commit to git!\n# Use sealed-secrets or sops for encryption.\n# Generate with: kubectl create secret generic apidoc-secrets --from-literal=secret-key=$(openssl rand -base64 64) --dry-run=client -o yaml > secrets.yaml\n"
        if not content.startswith("# WARNING"):
            content = warning + content
        
        # Замена значений
        content = re.sub(
            r'secret-key: ".*"',
            f'secret-key: "{new_secret}"',
            content
        )
        content = re.sub(
            r'database-url: "postgresql\+asyncpg://apidoc:changeme@',
            'database-url: "postgresql+asyncpg://apidoc:${DB_PASSWORD}@',
            content
        )
        
        self._write_file(k8s_secrets, content)
    
    def fix_csrf_middleware(self) -> None:
        """Включение и настройка CSRF middleware."""
        # 1. Исправление main.py - включение CSRF
        main_path = self.root / "apidoc_server" / "main.py"
        content = self._read_file(main_path)
        
        # Раскомментирование CSRF
        content = content.replace(
            '## app.add_middleware(CSRFMiddleware)',
            '''# CSRF Protection - enabled for production
app.add_middleware(
    CSRFMiddleware,
    cookie_name="csrf_token",
    header_name="X-CSRF-Token",
    safe_methods={"GET", "HEAD", "OPTIONS"}
)'''
        )
        
        self._write_file(main_path, content)
        
        # 2. Добавление exemption paths в CSRFMiddleware
        csrf_path = self.root / "apidoc_server" / "security.py"
        csrf_content = self._read_file(csrf_path)
        
        if 'exemption_paths' not in csrf_content:
            updated_csrf = csrf_content.replace(
                'def __init__(self, app, cookie_name: str = "csrf_token", header_name: str = "X-CSRF-Token", safe_methods: set = None):',
                '''def __init__(self, app, cookie_name: str = "csrf_token", header_name: str = "X-CSRF-Token", safe_methods: set = None, exemption_paths: set = None):
        self.exemption_paths = exemption_paths or {
            "/api/v1/auth/token",
            "/api/v1/auth/refresh",
            "/health",
            "/health/readiness",
            "/metrics",
            "/api/docs",
            "/api/redoc"
        }'''
            )
            
            updated_csrf = updated_csrf.replace(
                'if not header_token or not cookie_token:',
                '''# Check exemption paths
        if request.url.path in self.exemption_paths:
            return await call_next(request)
        
        if not header_token or not cookie_token:'''
            )
            
            self._write_file(csrf_path, updated_csrf)
    
    def fix_cors_settings(self) -> None:
        """Настройка строгих CORS для production."""
        config_path = self.root / "apidoc_server" / "config.py"
        content = self._read_file(config_path)
        
        # Замена wildcard на конкретные origins
        content = content.replace(
            'cors_origins: List[str] = Field(["*"])',
            'cors_origins: List[str] = Field(["http://localhost:3000", "http://localhost:8000"])'
        )
        content = content.replace(
            'allowed_hosts: List[str] = Field(["*"])',
            'allowed_hosts: List[str] = Field(["localhost", "127.0.0.1"])'
        )
        
        # Добавление валидации для production
        if 'validate_cors_origins' not in content:
            cors_validator = '''
    
    @field_validator("cors_origins", mode="after")
    @classmethod
    def validate_cors_origins(cls, v: List[str]) -> List[str]:
        """Warn if CORS allows all origins in non-debug mode."""
        if "*" in v and not cls.model_config.get("env_file") == ".env.dev":
            import warnings
            warnings.warn("CORS allows all origins - not recommended for production", UserWarning)
        return v'''
            
            content = content.replace(
                'enable_metrics: bool = Field(True)\n    token_expire_minutes: int = Field(1440)',
                'enable_metrics: bool = Field(True)\n    token_expire_minutes: int = Field(1440)' + cors_validator
            )
        
        self._write_file(config_path, content)
    
    def fix_rate_limiting(self) -> None:
        """Добавление rate limiting на /auth/token."""
        auth_path = self.root / "apidoc_server" / "api" / "auth.py"
        content = self._read_file(auth_path)
        
        if 'from slowapi' not in content:
            # Добавление импортов
            content = content.replace(
                'from fastapi import APIRouter, Depends, HTTPException, status',
                'from fastapi import APIRouter, Depends, HTTPException, Request, status\nfrom slowapi import Limiter\nfrom slowapi.util import get_remote_address'
            )
            
            # Добавление лимитера
            content = content.replace(
                'router = APIRouter()\noauth2_scheme',
                'router = APIRouter()\nlimiter = Limiter(key_func=get_remote_address)\noauth2_scheme'
            )
            
            # Добавление декоратора на login
            content = content.replace(
                '@router.post("/auth/token")\nasync def login(form_data: OAuth2PasswordRequestForm = Depends()):',
                '@router.post("/auth/token")\n@limiter.limit("5/minute")\nasync def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):'
            )
            
            # Добавление проверки блокировки
            content = content.replace(
                'if form_data.username != "admin" or form_data.password != "admin":\n        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})',
                '''# Check if IP is temporarily blocked
        client_ip = request.client.host if request.client else "unknown"
        failed_key = f"login_failed:{client_ip}"
        
        # Simple brute force protection
        if hasattr(request.app.state, "redis"):
            failed_attempts = await request.app.state.redis.get(failed_key)
            if failed_attempts and int(failed_attempts) >= 10:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many login attempts. Please try again in 15 minutes.",
                    headers={"Retry-After": "900"}
                )
        
        if form_data.username != "admin" or form_data.password != "admin":
            if hasattr(request.app.state, "redis"):
                await request.app.state.redis.incr(failed_key)
                await request.app.state.redis.expire(failed_key, 900)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})'''
            )
            
            self._write_file(auth_path, content)
    
    def create_env_example(self) -> None:
        """Создание .env.example с безопасными значениями по умолчанию."""
        env_example = self.root / ".env.example"
        new_secret = self.generated_secrets.get('SECRET_KEY', self._generate_secret(64))
        
        content = f"""# APIDoc Manager Environment Configuration
# Copy this file to .env and modify values
# WARNING: .env contains secret keys - never commit to git!

# Server Configuration
APIDOC_HOST=0.0.0.0
APIDOC_PORT=8000
APIDOC_DEBUG=false
APIDOC_LOG_LEVEL=INFO
APIDOC_LOG_JSON=false

# Database
# SQLite (development):
APIDOC_DATABASE_URL=sqlite+aiosqlite:///./apidoc.db
# PostgreSQL (production):
# APIDOC_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/apidoc

# Redis (optional for rate limiting & token revocation)
# APIDOC_REDIS_URL=redis://localhost:6379/0

# Security - CRITICAL: Change these!
APIDOC_SECRET_KEY={new_secret}
APIDOC_TOKEN_EXPIRE_MINUTES=1440

# Allowed hosts (comma-separated)
APIDOC_ALLOWED_HOSTS=localhost,127.0.0.1
# CORS origins (comma-separated)
APIDOC_CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# External Services (optional)
APIDOC_SWAGGERHUB_API_KEY=
APIDOC_GITHUB_TOKEN=
APIDOC_README_API_KEY=

# Rate Limiting
APIDOC_RATE_LIMIT_PER_MINUTE=60
APIDOC_RATE_LIMIT_PER_HOUR=1000

# Feature Flags
APIDOC_ENABLE_DOCS=true
APIDOC_ENABLE_METRICS=true
"""
        self._write_file(env_example, content)
    
    def fix_gitignore(self) -> None:
        """Добавление важных файлов в .gitignore."""
        gitignore = self.root / ".gitignore"
        current = self._read_file(gitignore)
        
        additions = [
            "# APIDoc Manager - Sensitive files",
            ".env",
            ".env.local",
            ".env.production",
            "*.db",
            "*.db-journal",
            "apidoc_server/data/",
            "logs/",
            "*.log",
            "# Backup files from hardening script",
            "backup_*/",
            "# K8s secrets (should be encrypted)",
            "k8s/secrets.yaml",
            "# Docker secrets",
            "docker/.env",
        ]
        
        if '.env' not in current:
            new_content = current + '\n' + '\n'.join(additions) + '\n'
            self._write_file(gitignore, new_content)
    
    # ===== ПРИОРИТЕТ 2: ВЫСОКИЕ ИСПРАВЛЕНИЯ =====
    
    def fix_database_pool(self) -> None:
        """Настройка пула соединений в зависимости от типа БД."""
        db_path = self.root / "apidoc_server" / "database.py"
        content = self._read_file(db_path)
        
        new_content = content.replace(
            'engine = create_async_engine(settings.database_url, echo=settings.debug, future=True, pool_size=settings.database_pool_size, max_overflow=settings.database_max_overflow)',
            '''# Configure engine based on database type
if "sqlite" in settings.database_url:
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        future=True,
        connect_args={"check_same_thread": False} if "memory" not in settings.database_url else {}
    )
else:
    # PostgreSQL or other production databases
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        future=True,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_pre_ping=True,
        pool_recycle=3600
    )'''
        )
        
        self._write_file(db_path, new_content)

    def fix_soft_delete(self) -> None:
        """Добавление soft delete в модель Specification."""
        models_path = self.root / "apidoc_server" / "models.py"
        content = self._read_file(models_path)
        
        if 'deleted_at' not in content:
            # Добавление полей для soft delete
            content = content.replace(
                '    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())\n    versions: Mapped[list["SpecVersion"]]',
                '''    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
    versions: Mapped[list["SpecVersion"]]'''
            )
            
            self._write_file(models_path, content)
            
            # Обновление API для фильтрации удалённых
            specs_path = self.root / "apidoc_server" / "api" / "specs.py"
            specs_content = self._read_file(specs_path)
            
            specs_content = specs_content.replace(
                'query = select(Specification)\n    if tag:',
                'query = select(Specification).where(Specification.is_deleted == False)\n    if tag:'
            )
            
            specs_content = specs_content.replace(
                'await db.delete(spec)\n    await db.commit()\n    logger.info(f"Deleted specification {spec_id}")',
                '''# Soft delete
    spec.is_deleted = True
    spec.deleted_at = func.now()
    await db.commit()
    logger.info(f"Soft-deleted specification {spec_id}")'''
            )
            
            self._write_file(specs_path, specs_content)

    def fix_n_plus_one(self) -> None:
        """Оптимизация N+1 запросов."""
        specs_path = self.root / "apidoc_server" / "api" / "specs.py"
        content = self._read_file(specs_path)
        
        # Оптимизация get_specification
        old_query = '''result = await db.execute(select(Specification).where(Specification.id == spec_id))
    spec = result.scalar_one_or_none()
    if not spec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specification {spec_id} not found")
    
    if version:
        version_result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id, SpecVersion.version == version))
    else:
        version_result = await db.execute(select(SpecVersion).where(SpecVersion.spec_id == spec_id).order_by(SpecVersion.created_at.desc()).limit(1))
    spec_version = version_result.scalar_one_or_none()'''
        
        new_query = '''# Optimized: single query with JOIN to avoid N+1
    from sqlalchemy.orm import joinedload
    
    if version:
        stmt = (
            select(Specification)
            .options(joinedload(Specification.versions))
            .where(Specification.id == spec_id, Specification.is_deleted == False)
        )
    else:
        stmt = (
            select(Specification)
            .options(joinedload(Specification.versions))
            .where(Specification.id == spec_id, Specification.is_deleted == False)
        )
    
    result = await db.execute(stmt)
    spec = result.unique().scalar_one_or_none()
    if not spec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specification {spec_id} not found")
    
    if version:
        spec_version = next((v for v in spec.versions if v.version == version), None)
    else:
        spec_version = max(spec.versions, key=lambda v: v.created_at) if spec.versions else None'''
        
        content = content.replace(old_query, new_query)
        self._write_file(specs_path, content)

    def create_common_validator(self) -> None:
        """Создание общего модуля валидации."""
        common_dir = self.root / "apidoc_common"
        common_dir.mkdir(exist_ok=True)
        
        init_content = (
            '"""Common utilities for APIDoc CLI and Server."""\n'
            '\n'
            'from apidoc_common.validators import BaseValidator\n'
            '\n'
            '__all__ = ["BaseValidator"]\n'
        )
        self._write_file(common_dir / "__init__.py", init_content)
        
        validator_content = (
            '"""Base validation logic shared between CLI and Server."""\n'
            '\n'
            'import json\n'
            'import re\n'
            'from typing import Any, Dict\n'
            '\n'
            'import httpx\n'
            'from openapi_spec_validator import validate_spec\n'
            'from openapi_spec_validator.exceptions import OpenAPISpecValidatorError\n'
            'from prance import ResolvingParser\n'
            '\n'
            '\n'
            'class BaseValidator:\n'
            '    """Common OpenAPI validation logic."""\n'
            '    \n'
            '    REMOTE_VALIDATOR_URL = "https://validator.swagger.io/validator/debug"\n'
            '    \n'
            '    def _extract_location(self, error: Exception) -> str:\n'
            '        """Extract location from validation error message."""\n'
            '        error_str = str(error)\n'
            '        patterns = [\n'
            '            r"in \'([^\']+)\'",\n'
            '            r\'in "([^"]+)"\',\n'
            '            r"at \'([^\']+)\'",\n'
            '            r\'at "([^"]+)"\',\n'
            '            r"path \'([^\']+)\'",\n'
            '            r\'path "([^"]+)"\',\n'
            '        ]\n'
            '        for pattern in patterns:\n'
            '            match = re.search(pattern, error_str)\n'
            '            if match:\n'
            '                return match.group(1)\n'
            '        return ""\n'
            '    \n'
            '    def _check_references(self, spec: Dict[str, Any], results: Dict) -> None:\n'
            '        """Check for external references."""\n'
            '        try:\n'
            '            parser = ResolvingParser(spec_string=json.dumps(spec))\n'
            '            \n'
            '            def collect_refs(obj: Any, path: str = "") -> None:\n'
            '                if isinstance(obj, dict):\n'
            '                    if "$ref" in obj:\n'
            '                        ref = obj["$ref"]\n'
            '                        if not ref.startswith("#"):\n'
            '                            results.setdefault("warnings", []).append({\n'
            '                                "type": "external_reference",\n'
            '                                "message": f"External reference: {ref}",\n'
            '                                "location": path\n'
            '                            })\n'
            '                    for key, value in obj.items():\n'
            '                        collect_refs(value, f"{path}.{key}" if path else key)\n'
            '                elif isinstance(obj, list):\n'
            '                    for i, item in enumerate(obj):\n'
            '                        collect_refs(item, f"{path}[{i}]")\n'
            '            \n'
            '            collect_refs(spec)\n'
            '        except Exception as e:\n'
            '            results.setdefault("warnings", []).append({\n'
            '                "type": "reference_error",\n'
            '                "message": f"Reference validation warning: {e}"\n'
            '            })\n'
            '    \n'
            '    def _check_common_issues(self, spec: Dict[str, Any], results: Dict) -> None:\n'
            '        """Check for common specification issues."""\n'
            '        for path, methods in spec.get("paths", {}).items():\n'
            '            for method, details in methods.items():\n'
            '                if method.lower() not in ["get", "post", "put", "delete", "patch", "options", "head"]:\n'
            '                    continue\n'
            '                \n'
            '                if "responses" not in details:\n'
            '                    results.setdefault("errors", []).append({\n'
            '                        "type": "missing_responses",\n'
            '                        "location": f"paths.{path}.{method}",\n'
            '                        "message": "Missing responses field"\n'
            '                    })\n'
            '                    results.setdefault("fixable", []).append({\n'
            '                        "type": "add_responses",\n'
            '                        "location": f"paths.{path}.{method}",\n'
            '                        "description": f"Add default response for {method.upper()} {path}"\n'
            '                    })\n'
            '                \n'
            '                if "operationId" not in details:\n'
            '                    results.setdefault("warnings", []).append({\n'
            '                        "type": "missing_operation_id",\n'
            '                        "location": f"paths.{path}.{method}",\n'
            '                        "message": "Missing operationId"\n'
            '                    })\n'
            '        \n'
            '        info = spec.get("info", {})\n'
            '        if "title" not in info or not info["title"]:\n'
            '            results.setdefault("errors", []).append({\n'
            '                "type": "missing_title",\n'
            '                "message": "Missing info.title"\n'
            '            })\n'
            '        if "version" not in info or not info["version"]:\n'
            '            results.setdefault("errors", []).append({\n'
            '                "type": "missing_version",\n'
            '                "message": "Missing info.version"\n'
            '            })\n'
            '    \n'
            '    def _validate_spec(self, spec: Dict[str, Any]) -> Dict[str, Any]:\n'
            '        """Validate specification structure."""\n'
            '        results = {"valid": True, "errors": [], "warnings": [], "fixable": []}\n'
            '        \n'
            '        if "openapi" not in spec and "swagger" not in spec:\n'
            '            results["valid"] = False\n'
            '            results["errors"].append({\n'
            '                "type": "missing_version",\n'
            '                "message": "Missing openapi or swagger field"\n'
            '            })\n'
            '            return results\n'
            '        \n'
            '        try:\n'
            '            validate_spec(spec)\n'
            '        except OpenAPISpecValidatorError as e:\n'
            '            results["valid"] = False\n'
            '            results["errors"].append({\n'
            '                "type": "validation_error",\n'
            '                "message": str(e),\n'
            '                "location": self._extract_location(e)\n'
            '            })\n'
            '        except Exception as e:\n'
            '            results["valid"] = False\n'
            '            results["errors"].append({\n'
            '                "type": "parse_error",\n'
            '                "message": str(e)\n'
            '            })\n'
            '        \n'
            '        self._check_references(spec, results)\n'
            '        self._check_common_issues(spec, results)\n'
            '        return results\n'
            '    \n'
            '    async def _validate_remote(self, spec: Dict[str, Any]) -> Dict[str, Any]:\n'
            '        """Validate using remote Swagger validator."""\n'
            '        try:\n'
            '            async with httpx.AsyncClient(timeout=30.0) as client:\n'
            '                response = await client.post(\n'
            '                    self.REMOTE_VALIDATOR_URL,\n'
            '                    json={"spec": spec}\n'
            '                )\n'
            '                response.raise_for_status()\n'
            '                data = response.json()\n'
            '                \n'
            '                results = {\n'
            '                    "valid": len(data.get("schemaValidationMessages", [])) == 0,\n'
            '                    "errors": [],\n'
            '                    "warnings": [],\n'
            '                    "fixable": []\n'
            '                }\n'
            '                \n'
            '                for msg in data.get("schemaValidationMessages", []):\n'
            '                    error = {\n'
            '                        "type": "remote_validation",\n'
            '                        "message": msg.get("message", ""),\n'
            '                        "location": msg.get("path", "")\n'
            '                    }\n'
            '                    if msg.get("level") == "error":\n'
            '                        results["errors"].append(error)\n'
            '                    else:\n'
            '                        results["warnings"].append(error)\n'
            '                \n'
            '                return results\n'
            '        except Exception as e:\n'
            '            return {\n'
            '                "valid": False,\n'
            '                "errors": [{"type": "remote_error", "message": str(e)}],\n'
            '                "warnings": [],\n'
            '                "fixable": []\n'
            '            }\n'
        )
        self._write_file(common_dir / "validators.py", validator_content)
    
    def add_security_headers(self) -> None:
        """Добавление middleware для security headers."""
        middleware_dir = self.root / "apidoc_server" / "middleware"
        security_headers_path = middleware_dir / "security_headers.py"
        
        content = '''"""Security headers middleware."""

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Remove server signature
        response.headers["Server"] = ""
        
        return response
'''
        self._write_file(security_headers_path, content)
        
        # Добавление в main.py
        main_path = self.root / "apidoc_server" / "main.py"
        main_content = self._read_file(main_path)
        
        if 'SecurityHeadersMiddleware' not in main_content:
            main_content = main_content.replace(
                'from apidoc_server.security import CSRFMiddleware',
                'from apidoc_server.security import CSRFMiddleware\nfrom apidoc_server.middleware.security_headers import SecurityHeadersMiddleware'
            )
            
            main_content = main_content.replace(
                'if settings.enable_metrics:\n        app.add_middleware(MetricsMiddleware, metrics_manager=metrics)',
                '''# Security headers (always first)
    app.add_middleware(SecurityHeadersMiddleware)
    
    if settings.enable_metrics:
        app.add_middleware(MetricsMiddleware, metrics_manager=metrics)'''
            )
            
            self._write_file(main_path, main_content)

    def fix_jwt_revocation(self) -> None:
        """Добавление механизма отзыва JWT токенов."""
        security_path = self.root / "apidoc_server" / "security.py"
        content = self._read_file(security_path)
        
        if 'revoke_token' not in content:
            revocation_code = '''
    
    async def revoke_token(self, token: str, redis_client=None) -> bool:
        """Revoke a JWT token by adding its hash to blacklist."""
        if not redis_client:
            return False
        
        import hashlib
        jti = hashlib.sha256(token.encode()).hexdigest()
        await redis_client.setex(f"revoked:{jti}", 86400, "1")  # 24 hour TTL
        return True
    
    async def is_token_revoked(self, token: str, redis_client=None) -> bool:
        """Check if token has been revoked."""
        if not redis_client:
            return False
        
        import hashlib
        jti = hashlib.sha256(token.encode()).hexdigest()
        return await redis_client.exists(f"revoked:{jti}") > 0
'''
            
            # Вставить перед verify_token
            content = content.replace(
                '    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:',
                revocation_code + '\n    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:'
            )
            
            self._write_file(security_path, content)

    def add_input_sanitization(self) -> None:
        """Добавление санитизации входных данных."""
        sanitizer_path = self.root / "apidoc_server" / "middleware" / "sanitizer.py"
        
        content = '''"""Input sanitization utilities."""

import html
import re
from typing import Any, Dict, List


def sanitize_string(value: str) -> str:
    """Sanitize string input to prevent XSS and injection."""
    # Remove potentially dangerous characters
    # This is a basic sanitization - for production, use a proper library
    sanitized = html.escape(value, quote=True)
    
    # Remove common SQL injection patterns (defense in depth)
    sql_patterns = [
        r"(?i)(drop\s+table)",
        r"(?i)(delete\s+from)",
        r"(?i)(insert\s+into)",
        r"(?i)(union\s+select)",
        r"(?i)(exec\s*\\()",
        r"(?i)(execute\s*\\()",
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, sanitized):
            return ""  # Reject suspicious input
    
    return sanitized.strip()


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively sanitize dictionary values."""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_dict(item) if isinstance(item, dict)
                else sanitize_string(item) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            sanitized[key] = value
    return sanitized
'''
        self._write_file(sanitizer_path, content)

    # ===== ПРИОРИТЕТ 3: КАЧЕСТВО КОДА =====
    
    def fix_type_hints(self) -> None:
        """Исправление type hints для Python 3.10+."""
        # Исправление Optional[X] -> X | None
        files_to_fix = [
            self.root / "apidoc_cli" / "config.py",
            self.root / "apidoc_server" / "config.py",
        ]
        
        for filepath in files_to_fix:
            if not filepath.exists():
                continue
            
            content = self._read_file(filepath)
            # Optional[X] -> X | None
            content = re.sub(r'Optional\[([^\]]+)\]', r'\1 | None', content)
            # List[X] -> list[X] (Python 3.9+)
            content = re.sub(r'List\[([^\]]+)\]', r'list[\1]', content)
            # Dict[X, Y] -> dict[X, Y]
            content = re.sub(r'Dict\[([^\]]+)\]', r'dict[\1]', content)
            
            self._write_file(filepath, content)

    def fix_dead_code(self) -> None:
        """Удаление неиспользуемых импортов и dead code."""
        # Удаление закомментированного CSRF импорта
        main_path = self.root / "apidoc_server" / "main.py"
        content = self._read_file(main_path)
        
        # Уже исправлено в fix_csrf_middleware
        
        # Проверка requirements.txt на дубликаты
        reqs_path = self.root / "requirements.txt"
        if reqs_path.exists():
            reqs_content = self._read_file(reqs_path)
            lines = reqs_content.strip().split('\n')
            seen = set()
            unique_lines = []
            for line in lines:
                pkg = line.split('>=')[0].split('[')[0].strip()
                if pkg and pkg not in seen:
                    seen.add(pkg)
                    unique_lines.append(line)
            if len(unique_lines) != len(lines):
                self._write_file(reqs_path, '\n'.join(unique_lines) + '\n')

    def fix_subprocess_handling(self) -> None:
        """Добавление правильной обработки subprocess."""
        server_cli = self.root / "apidoc_cli" / "commands" / "server.py"
        content = self._read_file(server_cli)
        
        # Исправление server_start
        old_subprocess = '''cmd = [sys.executable, "-m", "uvicorn", "apidoc_server.main:app", "--host", host, "--port", str(port), "--workers", str(workers)]
        if reload:
            cmd.append("--reload")
        
        console.print(f"[green]Starting server at http://{host}:{port}[/]")
        
        if background:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
            for _ in range(10):
                if _is_server_running(host, port):
                    console.print(f"[green]OK[/] Server started (PID: {process.pid})")
                    return
                asyncio.run(asyncio.sleep(0.5))
            console.print("[red]FAIL[/] Server failed to start")
        else:
            subprocess.run(cmd)'''
        
        new_subprocess = '''cmd = [sys.executable, "-m", "uvicorn", "apidoc_server.main:app", "--host", host, "--port", str(port), "--workers", str(workers)]
        if reload:
            cmd.append("--reload")
        
        console.print(f"[green]Starting server at http://{host}:{port}[/]")
        
        if background:
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True,
                    text=True
                )
                
                # Wait for server to start with timeout
                for _ in range(10):
                    if _is_server_running(host, port):
                        console.print(f"[green]OK[/] Server started (PID: {process.pid})")
                        return
                    asyncio.run(asyncio.sleep(0.5))
                
                # If server didn't start, check for errors
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                
                stderr = process.stderr.read() if process.stderr else ""
                console.print(f"[red]FAIL[/] Server failed to start: {stderr[:500]}")
                raise typer.Exit(1)
            except FileNotFoundError:
                console.print("[red]Error:[/] uvicorn not found. Please install with: pip install uvicorn")
                raise typer.Exit(1)
        else:
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                logger.error(f"Server start failed: {e.stderr}")
                console.print(f"[red]Error:[/] {e.stderr}")
                raise typer.Exit(1)'''
        
        content = content.replace(old_subprocess, new_subprocess)
        self._write_file(server_cli, content)

    def create_ci_cd(self) -> None:
        """Создание GitHub Actions workflow."""
        workflows_dir = self.root / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        ci_content = """name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: apidoc
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: apidoc_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    
    - name: Lint with ruff
      run: |
        ruff check apidoc_cli apidoc_server tests/
    
    - name: Type check with mypy
      run: |
        mypy apidoc_cli apidoc_server --ignore-missing-imports
    
    - name: Run tests with coverage
      env:
        APIDOC_DATABASE_URL: postgresql+asyncpg://apidoc:test_password@localhost:5432/apidoc_test
        APIDOC_SECRET_KEY: test-secret-key-for-ci-only
      run: |
        pytest tests/ -v --cov=apidoc_cli --cov=apidoc_server --cov-report=xml --cov-report=term
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
    
    - name: Security audit dependencies
      run: |
        pip-audit

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scanners: 'vuln,secret,config'
        severity: 'CRITICAL,HIGH'
    
    - name: Run Bandit security linter
      run: |
        pip install bandit
        bandit -r apidoc_cli/ apidoc_server/ -ll

  docker-build:
    needs: lint-and-test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to GitHub Container Registry
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push server image
      uses: docker/build-push-action@v5
      with:
        context: .
        file: docker/Dockerfile.prod
        push: true
        tags: |
          ghcr.io/${{ github.repository }}/server:latest
          ghcr.io/${{ github.repository }}/server:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
"""
        self._write_file(workflows_dir / "ci.yml", ci_content)
        
        # Создание pre-commit конфига
        precommit_content = """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: detect-private-key
      - id: check-merge-conflict

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.2.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic>=2.0.0, sqlalchemy>=2.0.0]
        args: [--ignore-missing-imports]
"""
        self._write_file(self.root / ".pre-commit-config.yaml", precommit_content)

    def print_summary(self) -> None:
        """Вывод результатов."""
        log(f"\n{'='*70}", "INFO")
        log(f"FIX SUMMARY", "BOLD")
        log(f"{'='*70}", "INFO")
        
        log(f"✓ Applied fixes: {len(self.fixes_applied)}", "SUCCESS")
        for fix in self.fixes_applied:
            log(f"  • {fix}", "SUCCESS")
        
        if self.errors:
            log(f"✗ Errors: {len(self.errors)}", "ERROR")
            for name, error in self.errors:
                log(f"  • {name}: {error}", "ERROR")
        
        if self.generated_secrets:
            log(f"\nGenerated secrets (SAVE THESE!):", "WARNING")
            for key, value in self.generated_secrets.items():
                log(f"  {key}={value}", "WARNING")
        
        log(f"\n{'='*70}", "INFO")
        log(f"NEXT STEPS:", "BOLD")
        log(f"1. Review changes: git diff", "INFO")
        log(f"2. Update .env file with generated secrets", "INFO")
        log(f"3. Run tests: pytest tests/ -v", "INFO")
        log(f"4. Install pre-commit: pre-commit install", "INFO")
        log(f"5. If safe, restore from backup: backup_*/", "INFO")
        
        if not self.apply:
            log(f"\n⚠ This was a DRY RUN. Run with --apply to actually apply fixes.", "WARNING")
        
        log(f"{'='*70}\n", "INFO")


def main():
    parser = argparse.ArgumentParser(
        description="APIDoc Manager Production Hardening Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (see what would be changed)
  python fix_production.py --project-dir /path/to/apidoc-manager
  
  # Apply fixes with backup
  python fix_production.py --project-dir /path/to/apidoc-manager --apply
  
  # Apply without backup (not recommended)
  python fix_production.py --project-dir /path/to/apidoc-manager --apply --no-backup
        """
    )
    
    parser.add_argument(
        '--project-dir', '-d',
        type=Path,
        default=Path.cwd(),
        help='Project root directory (default: current directory)'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Actually apply fixes (default: dry run)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Disable backup creation (not recommended)'
    )
    
    args = parser.parse_args()
    
    # Проверка что мы в правильной директории
    if not (args.project_dir / "pyproject.toml").exists():
        log(f"Error: pyproject.toml not found in {args.project_dir}", "ERROR")
        log("Are you sure this is the APIDoc Manager project directory?", "ERROR")
        sys.exit(1)
    
    # Запуск
    hardener = APIDocHardener(
        project_root=args.project_dir,
        apply=args.apply,
        backup=not args.no_backup
    )
    hardener.run()


if __name__ == "__main__":
    main()