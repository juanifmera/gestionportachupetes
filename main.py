from sqlalchemy import create_engine, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List, Optional
from sqlalchemy.orm import Session

engine = create_engine('sqlite://', echo=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'user_account'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    full_name: Mapped[Optional[str]]

    addresses: Mapped[List['Address']] = relationship(back_populates='user', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'User(id={self.id!r}, name={self.name!r}, full_name={self.full_name!r})'

class Address(Base):
    __tablename__ = 'address'

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey('user_account.id'))

    user: Mapped[User] = relationship(back_populates='addresses')

    def __repr__(self):
        return f'Address(id={self.id!r}, email_address={self.email_address!r})'

Base.metadata.create_all(engine)

user1 = User(name='Juan', full_name='Juan Ignacio Francisco Mera')
user2 = User(name='Sofía', full_name='Sofía Castillo')

# Crear direcciones para user1
address1 = Address(email_address='juan@gmail.com')
address2 = Address(email_address='juan.trabajo@empresa.com')

# Asociar direcciones al usuario
user1.addresses.append(address1)
user1.addresses.append(address2)

# Crear una sesión para interactuar con la DB
with Session(engine) as session:
    session.add_all([user1, user2])  # Guarda usuarios y direcciones porque cascade
    session.commit()

    # Leer los usuarios
    users = session.query(User).all()
    for user in users:
        print(user)
        for addr in user.addresses:
            print(f' → Dirección: {addr.email_address}')


