"""
CONEXIÓN A LA BASE DE DATOS

Este archivo configura SQLAlchemy para conectarse a PostgreSQL (Supabase).

CONCEPTOS CLAVE:
- Engine: El "motor" que se conecta a la basepython test_api.py de datos
- SessionLocal: Una "sesión" es como una conversación con la base de datos
- Base: La clase base de la que heredan todos tus modelos
"""

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

# Cargar variables de entorno
load_dotenv()

# Obtener configuración
settings = get_settings()

# ============================================
# CREAR EL "MOTOR" DE LA BASE DE DATOS
# ============================================
# Este motor es el encargado de comunicarse con PostgreSQL

# Intentar conectar con la URL configurada; si falla, usar SQLite local como fallback
try:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        echo=True
    )
    print("🔗 Intentando conectar a la base de datos externa...")
except Exception as e:
    # Fallback a SQLite local para permitir pruebas sin Supabase
    fallback_url = 'sqlite:///./dev.sqlite3'
    engine = create_engine(fallback_url, connect_args={"check_same_thread": False}, echo=True)
    print("⚠️  No se pudo conectar a la BD externa. Usando SQLite local:", fallback_url)


# ============================================
# CREAR EL "FABRICANTE DE SESIONES"
# ============================================
# Cada vez que necesites hablar con la BD, crearás una sesión

SessionLocal = sessionmaker(
    autocommit=False,  # No guardar cambios automáticamente
    autoflush=False,   # No enviar cambios automáticamente
    bind=engine        # Conectar al motor que creamos arriba
)


# ============================================
# CLASE BASE PARA TODOS LOS MODELOS
# ============================================
# Todos tus modelos (User, Product, Sale) heredarán de esta clase

Base = declarative_base()


# ============================================
# FUNCIÓN PARA OBTENER UNA SESIÓN
# ============================================
def get_db():
    """
    Generador que proporciona una sesión de base de datos.
    
    Esta función se usa en FastAPI con "Depends(get_db)"
    Garantiza que la sesión siempre se cierre, incluso si hay un error.
    
    Yield:
        Session: Sesión de base de datos
    
    Ejemplo de uso:
        @app.get("/productos")
        def listar_productos(db: Session = Depends(get_db)):
            productos = db.query(Product).all()
            return productos
    """
    db = SessionLocal()
    try:
        # Yield "presta" la sesión a quien la necesite
        yield db
    finally:
        # Siempre cierra la sesión cuando termine
        db.close()


# ============================================
# FUNCIÓN PARA CREAR TODAS LAS TABLAS
# ============================================
def init_db():
    """
    Crea todas las tablas en la base de datos.
    
    Esto se ejecuta cuando inicias la aplicación por primera vez.
    Lee todos los modelos que heredan de "Base" y crea sus tablas.
    """
    try:
        # Importar todos los modelos para que Base los conozca
        from app.models import user, product, sale
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente")
    except Exception as e:
        print(f"⚠️  No se pudieron inicializar las tablas: {str(e)}")
        print("💡 Verifica la conexión a la base de datos en .env")
        print("⏭️  Continuando de todas formas...")


# Para crear las tablas manualmente desde la terminal:
# python -c "from app.database import init_db; init_db()"
