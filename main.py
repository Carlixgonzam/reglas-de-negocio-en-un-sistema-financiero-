from antlr4 import *
from ReglasFinancierasLexer import ReglasFinancierasLexer
from ReglasFinancierasParser import ReglasFinancierasParser
from evaluador import evaluar_regla  # Importa la función, NO la clase



historial_transacciones = [
    {'clienteId': 'C1', 'fecha': '2024-07-26 10:00:00', 'ubicacion': 'A', 'monto': 100},
    {'clienteId': 'C1', 'fecha': '2024-07-26 10:15:00', 'ubicacion': 'B', 'monto': 200},
    {'clienteId': 'C1', 'fecha': '2024-07-26 10:30:00', 'ubicacion': 'C', 'monto': 300},
    {'clienteId': 'C1', 'fecha': '2024-07-26 10:45:00', 'ubicacion': 'A', 'monto': 400},
    {'clienteId': 'C1', 'fecha': '2024-07-26 11:00:00', 'ubicacion': 'B', 'monto': 500},
    {'clienteId': 'C2', 'fecha': '2024-07-26 12:00:00', 'ubicacion': 'C', 'monto': 1000},
]

contexto_inicial = {
    'transaccion': {
        'id': 'T123',
        'cuentaOrigenId': 'C1',
        'cuentaDestinoId': 'C2',
        'monto': 6000,
        'moneda': 'USD',
        'tipo': 'transferencia',
        'fecha': '2024-07-27 15:30:00',
        'esInternacional': False,
        'paisOrigen': 'USA',
        'paisDestino': 'MEX',
        'ubicacion': 'D',
        'estado': 'PENDIENTE'
    },
    'cliente': {
        'id': 'C1',
        'nombre': 'Juan Perez',
        'tipo': 'persona',
        'antiguedad': 180,
        'scoreRiesgo': 650,
        'documentacionCompleta': True,
        'ingresoMensual': 5000,
        'deudaTotal': 1000,
        'paisResidencia': 'USA',
        'montoPromedioTransacciones': 500
    },
    'cuenta': {
        'id': 'CC123',
        'clienteId': 'C1',
        'tipo': 'corriente',
        'saldo': 10000,
        'moneda': 'USD',
        'fechaApertura': '2023-01-15'
    },
    'variables': {},
    'listas': {
        'paisesAltoRiesgo': ['CU', 'IR', 'KP', 'SY'],
        'paisesListaNegra': []
    },
    'historial': historial_transacciones
}



def cargar_reglas_desde_archivo(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta_archivo}'")
        return ""
    except Exception as e:
        print(f"Error al leer el archivo '{ruta_archivo}': {e}")
        return ""




def ejecutar_reglas(reglas_texto, contexto):
    input_stream = InputStream(reglas_texto)
    lexer = ReglasFinancierasLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ReglasFinancierasParser(stream)
    tree = parser.regla()  # Asume que la regla inicial es 'regla'

    evaluar_regla(tree, contexto)  # Llama a la función del evaluador
    return contexto



if __name__ == '__main__':
    # Opción 1: Cargar reglas desde un archivo
    # ruta_reglas = "reglas.txt"  # Cambia esto a la ruta de tu archivo
    # reglas_texto = cargar_reglas_desde_archivo(ruta_reglas)

    # Opción 2:  Reglas directamente en una cadena (más fácil para pruebas)
    reglas_texto = """
    transaccion.monto > 7000 => RECHAZAR;
    cliente.scoreRiesgo < 600 => REVISAR;
    LET comision = transaccion.monto * 0.01;
    comision > 10 => ALERTAR('Comisión alta');
    transaccion.paisDestino IN paisesAltoRiesgo => BLOQUEAR;
    contarTransacciones(cliente.id, "1 HORA", transaccion.ubicacion) > 4 => MARCAR_COMO_SOSPECHOSO;
    """

    if reglas_texto:  # Solo ejecuta si hay reglas
        contexto_final = ejecutar_reglas(reglas_texto, contexto_inicial.copy()) #Usamos copy para no modificar el original

        print("Estado final de la transacción:")
        print(contexto_final['transaccion'])
        print("\nVariables:")
        print(contexto_final['variables'])