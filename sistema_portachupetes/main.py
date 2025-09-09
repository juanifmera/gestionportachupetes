from database.models import Base
from database.engine import engine

try:
    Base.metadata.create_all(bind=engine)
    print('Modelos generados con exito')
    
except Exception as e:
    print(f'Ocurrio un error a la hora de generar los Modelos en la Base de Datos. Error: {e}')