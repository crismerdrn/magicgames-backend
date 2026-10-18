from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class CatalogoItem(BaseModel):
    id: int
    nombre: str

class ProductoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio_venta: float
    id_medida: int
    id_tipo_producto: int
    id_polleria: int
    stock_inicial: float
    image_url: Optional[str] = None

class ProductoRead(BaseModel):
    id_producto: int
    nombre: str
    descripcion: Optional[str]
    precio_venta: float
    categoria: str
    medida: str
    stock_actual: float
    image_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)