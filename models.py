from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Polleria(Base):
    __tablename__ = "polleria"
    id_polleria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(250), nullable=False)
    direccion = Column(String(250), nullable=False)
    telefono = Column(String(100), nullable=False)
    estado = Column(Boolean, default=True)

class Medida(Base):
    __tablename__ = "medidas"
    id_medida = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(250), nullable=False)
    abreviatura = Column(String(20), nullable=False)

class TipoProducto(Base):
    __tablename__ = "tipo_producto"
    id_tipo_producto = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(250), nullable=False)

class Producto(Base):
    __tablename__ = "producto"
    id_producto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(250), nullable=False)
    descripcion = Column(String(500), nullable=True)
    precio_venta = Column(Numeric(10, 2), nullable=False)
    image_url = Column(String, nullable=True)
    estado = Column(Boolean, default=True)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
    id_medida = Column(Integer, ForeignKey("medidas.id_medida"), nullable=False)
    id_tipo_producto = Column(Integer, ForeignKey("tipo_producto.id_tipo_producto"), nullable=False)

    medida = relationship("Medida")
    tipo_producto = relationship("TipoProducto")
    stocks = relationship("Stock", back_populates="producto")

class Stock(Base):
    __tablename__ = "stock"
    id_stock = Column(Integer, primary_key=True, index=True)
    stock_actual = Column(Numeric(10, 2), default=0, nullable=False)
    stock_minimo = Column(Numeric(10, 2), default=0, nullable=False)
    fecha_ultimo_movimiento = Column(DateTime(timezone=True), server_default=func.now())
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    id_polleria = Column(Integer, ForeignKey("polleria.id_polleria"), nullable=False)

    producto = relationship("Producto", back_populates="stocks")
    polleria = relationship("Polleria")