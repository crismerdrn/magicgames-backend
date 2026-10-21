from sqlalchemy import Column, BigInteger, String, Numeric, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# Tabla 1: Ludotecas / Sucursales
class Ludoteca(Base):
    __tablename__ = "ludotecas"
    id_ludoteca = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(String, default="Sede Central")

    stocks = relationship("Stock", back_populates="ludoteca")

# Tabla 2: Categorías (Juegos de Mesa, Snacks y Bebidas)
class Categoria(Base):
    __tablename__ = "categorias"
    id_categoria = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(80), nullable=False)

    productos = relationship("Product", back_populates="categoria")

# Tabla 3: Unidades de Medida / Presentación (Copia, Unidad)
class Medida(Base):
    __tablename__ = "medidas"
    id_medida = Column(BigInteger, primary_key=True, index=True)
    abreviatura = Column(String(10), nullable=False)
    descripcion = Column(String(50), nullable=False)

    productos = relationship("Product", back_populates="medida")

# Tabla 4: Catálogo Maestro de Productos
class Product(Base):
    __tablename__ = "products"
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    id_categoria = Column(BigInteger, ForeignKey("categorias.id_categoria"), nullable=False)
    id_medida = Column(BigInteger, ForeignKey("medidas.id_medida"), nullable=False)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    categoria = relationship("Categoria", back_populates="productos")
    medida = relationship("Medida", back_populates="productos")
    stocks = relationship("Stock", back_populates="producto", cascade="all, delete-orphan")

# Tabla 5: Existencias de Inventario (Stock por Ludoteca)
class Stock(Base):
    __tablename__ = "stock"
    id = Column(BigInteger, primary_key=True, index=True)
    id_producto = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    id_ludoteca = Column(BigInteger, ForeignKey("ludotecas.id_ludoteca"), nullable=False)
    stock_actual = Column(Integer, default=0, nullable=False)
    stock_minimo = Column(Integer, default=2, nullable=False)

    producto = relationship("Product", back_populates="stocks")
    ludoteca = relationship("Ludoteca", back_populates="stocks")