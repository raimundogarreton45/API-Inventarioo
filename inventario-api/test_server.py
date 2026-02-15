#!/usr/bin/env python3
"""
🚀 SERVIDOR ALTERNATIVO - Sin dependencias complejas
Sirve solo para testing del frontend
"""

import sys
import os

# Verificar que FastAPI está instalado
try:
    from fastapi import FastAPI, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from sqlalchemy import create_engine, Column, Integer, String, DateTime
    from sqlalchemy.orm import sessionmaker, declarative_base, Session
    from sqlalchemy.ext.declarative import declarative_base
    import uvicorn
    from datetime import datetime
    from pydantic import BaseModel, EmailStr
    import hashlib
    import secrets
except ImportError as e:
    print(f"❌ Error: Falta instalar: {e}")
    print("\nEjecuta:")
    print("  pip install fastapi uvicorn sqlalchemy python-multipart")
    sys.exit(1)

# ============================================
# CONFIGURACIÓN BASE
# ============================================

# Info sobre cuando se creó pruebas - sin cargar desde .env
DATABASE_URL = "sqlite:///./test.db"  # SQLite simple para pruebas

Base = declarative_base()

# ============================================
# MODELOS
# ============================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================================
# SCHEMAS
# ============================================

class UserCreate(BaseModel):
    nombre: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    nombre: str
    email: str
    api_key: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# ============================================
# DATABASE
# ============================================

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear tablas
Base.metadata.create_all(bind=engine)

# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

def hash_password(password: str) -> str:
    """Hash simple de contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_api_key() -> str:
    """Generar API Key"""
    return secrets.token_urlsafe(32)

# ============================================
# APP
# ============================================

app = FastAPI(
    title="API Inventario PYME - Modo Test",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# RUTAS
# ============================================

@app.get("/")
def root():
    return {
        "message": "API de Inventario PYME - Modo Test",
        "status": "OK",
        "docs": "http://localhost:8000/docs"
    }

@app.post("/auth/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""
    
    # Validar que no exista
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        return {
            "detail": "El email ya está registrado"
        }
    
    # Crear usuario
    new_user = User(
        nombre=user_data.nombre,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        api_key=generate_api_key()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.post("/auth/login", response_model=Token)
async def login(username: str, password: str, db: Session = Depends(get_db)):
    """Login de usuario"""
    
    user = db.query(User).filter(User.email == username).first()
    
    if not user or user.hashed_password != hash_password(password):
        return {
            "detail": "Email o contraseña incorrectos"
        }
    
    return {
        "access_token": user.api_key,
        "token_type": "bearer",
        "user": user
    }

@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    """Listar productos (mock)"""
    return []

@app.get("/sales")
def get_sales(db: Session = Depends(get_db)):
    """Listar ventas (mock)"""
    return []

@app.post("/products")
def create_product(db: Session = Depends(get_db)):
    """Crear producto (mock)"""
    return {"id": 1, "message": "Producto creado"}

@app.post("/sales")
def create_sale(db: Session = Depends(get_db)):
    """Crear venta (mock)"""
    return {"id": 1, "message": "Venta registrada"}

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║  🚀 API INVENTARIO PYME - MODO TEST                       ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  📍 http://localhost:8000                                  ║
║  📖 Docs: http://localhost:8000/docs                       ║
║                                                            ║
║  Base de datos: SQLite (test.db)                          ║
║  Usuarios registrados aquí                                ║
║                                                            ║
║  Presiona CTRL+C para detener                             ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False
    )
