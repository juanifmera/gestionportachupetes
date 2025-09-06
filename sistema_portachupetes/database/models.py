from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped
from sqlalchemy import Integer, String, ForeignKey, DateTime
from typing import Optional, List
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Materiales(Base):
    __tablename__ = 'materiales'

    id_material: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    codigo_material:Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    descripcion:Mapped[str] = mapped_column(String(50), nullable=False)
    color:Mapped[str] = mapped_column(String, nullable=False)
    categoria:Mapped[str] = mapped_column(String, nullable=False)
    subcategoria:Mapped[str] = mapped_column(String, nullable=False)
    fecha_ingreso:Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    comentarios:Mapped[Optional[str]] = mapped_column(String, nullable=True)
    stock:Mapped['Stock'] = relationship(back_populates='material', uselist=False)

    def __repr__(self):
        return f'Material Generado: {self.codigo_material}, Categoria: {self.categoria}, Subcategoria: {self.subcategoria}'

class Stock(Base):
    __tablename__ = 'stock'

    id_stock:Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    codigo_material:Mapped[str] = mapped_column(ForeignKey('materiales.codigo_material'), nullable=False)
    cantidad:Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_modificacion:Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    material:Mapped['Materiales'] = relationship(back_populates='stock')

    def __repr__(self):
        return f'Stock Generado: {self.codigo_material}, Cantidad Actual{self.cantidad}, Fecha de Modificacion: {self.fecha_modificacion}'