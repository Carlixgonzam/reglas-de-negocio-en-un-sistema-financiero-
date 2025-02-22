from antlr4 import *

from ReglasFinancierasLexer import ReglasFinancierasLexer
from ReglasFinancierasParser import ReglasFinancierasParser

# Funciones Auxiliares


def calcular_interes(monto, tasa):
    return monto * tasa


def contar_transacciones(contexto, cliente_id, periodo, ubicacion):
    historial_transacciones = contexto["historial"]
    transacciones_cliente = [
        t for t in historial_transacciones if t["clienteId"] == cliente_id
    ]

    if periodo == "1 HORA":
        from datetime import datetime, timedelta

        hora_actual = datetime.now()
        hora_limite = hora_actual - timedelta(hours=1)
        transacciones_periodo = [
            t
            for t in transacciones_cliente
            if datetime.strptime(t["fecha"], "%Y-%m-%d %H:%M:%S") >= hora_limite
        ]
    else:
        transacciones_periodo = transacciones_cliente

    transacciones_ubicacion = [
        t for t in transacciones_periodo if t["ubicacion"] != ubicacion
    ]
    return len(transacciones_ubicacion)


# Funciones del Evaluador


def evaluar_regla(ctx, contexto):
    if ctx.definicion_variable():
        evaluar_definicion_variable(ctx.definicion_variable(), contexto)
    condicion_resultado = evaluar_condicion(ctx.condicion(), contexto)
    if condicion_resultado:
        evaluar_accion(ctx.accion(), contexto)


def evaluar_definicion_variable(ctx, contexto):
    nombre_variable = ctx.variable().getText()
    valor = evaluar_expresion(ctx.expresion(), contexto)
    contexto["variables"][nombre_variable] = valor


def evaluar_condicion(ctx, contexto):
    return evaluar_expresion_booleana(ctx.expresion_booleana(), contexto)


def evaluar_expresion_booleana(ctx, contexto):
    if ctx.expresion_relacional():
        return evaluar_expresion_relacional(ctx.expresion_relacional(), contexto)
    if ctx.AND():
        left = evaluar_expresion_booleana(ctx.expresion_booleana(0), contexto)
        right = evaluar_expresion_booleana(ctx.expresion_booleana(1), contexto)
        return left and right
    if ctx.OR():
        left = evaluar_expresion_booleana(ctx.expresion_booleana(0), contexto)
        right = evaluar_expresion_booleana(ctx.expresion_booleana(1), contexto)
        return left or right
    if ctx.NOT():
        return not evaluar_expresion_booleana(ctx.expresion_booleana(0), contexto)
    return False  # Caso por defecto


def evaluar_expresion_relacional(ctx, contexto):
    left = evaluar_expresion(ctx.expresion(0), contexto)
    right = evaluar_expresion(ctx.expresion(1), contexto)
    op = ctx.operador_relacional().getText()

    if op == ">":
        return left > right
    elif op == "<":
        return left < right
    elif op == ">=":
        return left >= right
    elif op == "<=":
        return left <= right
    elif op == "==":
        return left == right
    elif op == "!=":
        return left != right
    elif op == "IN":
        return left in evaluar_lista(ctx.lista(), contexto)

    return False  # Caso por defecto


def evaluar_lista(ctx, contexto):
    if ctx.ID():
        return contexto["listas"][ctx.ID().getText()]
    lst = []
    for constante in ctx.constante():
        lst.append(evaluar_constante(constante))
    return lst


def evaluar_expresion(ctx, contexto):
    if len(ctx.termino()) == 1:
        return evaluar_termino(ctx.termino(0), contexto)
    else:
        resultado = evaluar_expresion(ctx.expresion(0), contexto)
        for i in range(len(ctx.termino()) - 1):
            termino = evaluar_termino(ctx.termino(i + 1), contexto)
            op = ctx.getChild(2 * i + 1).getText()
            if op == "+":
                resultado += termino
            elif op == "-":
                resultado -= termino
            elif op == "*":
                resultado *= termino
            elif op == "/":
                resultado /= termino  # Considerar división por cero
        return resultado


def evaluar_termino(ctx, contexto):
    if ctx.ID():
        return contexto["variables"].get(ctx.ID().getText())
    elif ctx.NUMBER():
        return float(ctx.NUMBER().getText())
    elif ctx.STRING():
        return ctx.STRING().getText()[1:-1]
    elif ctx.atributo():
        return evaluar_atributo(ctx.atributo(), contexto)
    elif ctx.funcion():
        return evaluar_funcion(ctx.funcion(), contexto)
    elif ctx.getText() == "true":
        return True
    elif ctx.getText() == "false":
        return False
    return None  # Caso por defecto


def evaluar_atributo(ctx, contexto):
    nombre_entidad = ctx.getChild(0).getText()
    nombre_atributo = ctx.ID().getText()

    if nombre_entidad == "transaccion":
        return contexto["transaccion"][nombre_atributo]
    elif nombre_entidad == "cliente":
        return contexto["cliente"][nombre_atributo]
    elif nombre_entidad == "cuenta":
        return contexto["cuenta"][nombre_atributo]
    return None  # Caso por defecto
    # ... (agregar otros casos) ...


def evaluar_funcion(ctx, contexto):
    nombre_funcion = ctx.ID().getText()
    argumentos = [evaluar_expresion(expr, contexto) for expr in ctx.expresion()]

    if nombre_funcion == "calcularInteres":
        return calcular_interes(argumentos[0], argumentos[1])
    elif nombre_funcion == "contarTransacciones":
        cliente_id = argumentos[0]
        periodo = argumentos[1]
        ubicacion = argumentos[2]
        return contar_transacciones(contexto, cliente_id, periodo, ubicacion)
    # ... (otras funciones) ...
    else:
        raise ValueError(f"Función desconocida: {nombre_funcion}")


def evaluar_accion(ctx, contexto):
    if ctx.APROBAR():
        contexto["transaccion"]["estado"] = "APROBADA"
    elif ctx.RECHAZAR():
        contexto["transaccion"]["estado"] = "RECHAZADA"
    elif ctx.REVISAR():
        contexto["transaccion"]["estado"] = "REVISION"
    elif ctx.BLOQUEAR():
        contexto["transaccion"]["estado"] = "BLOQUEADA"
    elif ctx.ALERTAR():
        mensaje = ctx.STRING().getText()[1:-1]
        print(f"ALERTA: {mensaje}")
    elif ctx.requiereAprobacion():
        rol = ctx.STRING().getText()[1:-1]
        print(f"Se requiere aprobacion de: {rol}")
    elif ctx.MARCAR_COMO_SOSPECHOSO():
        print("Se ha marcado la transacción como sospechosa")
    elif ctx.variable():
        nombre_variable = ctx.variable().getText()
        valor = evaluar_expresion(ctx.expresion(), contexto)
        contexto["variables"][nombre_variable] = valor


def evaluar_constante(ctx):
    if ctx.NUMBER():
        return float(ctx.NUMBER().getText())
    elif ctx.STRING():
        return ctx.STRING().getText()[1:-1]
    elif ctx.getText() == "true":
        return True
    elif ctx.getText() == "false":
        return False
    return None


# --- Programa Principal ---


def ejecutar_reglas(reglas_texto, contexto):
    input_stream = InputStream(reglas_texto)
    lexer = ReglasFinancierasLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ReglasFinancierasParser(stream)
    tree = parser.regla()  #  O 'programa' si tu regla inicial es diferente

    # En lugar de crear un objeto Evaluador, llamamos directamente a evaluar_regla
    evaluar_regla(tree, contexto)
    return contexto


# --- Datos de Ejemplo y Ejecución ---

# Datos de ejemplo (simulando una base de datos/API)
historial_transacciones = [
    {"clienteId": "C1", "fecha": "2024-07-26 10:00:00", "ubicacion": "A", "monto": 100},
    {"clienteId": "C1", "fecha": "2024-07-26 10:15:00", "ubicacion": "B", "monto": 200},
    {"clienteId": "C1", "fecha": "2024-07-26 10:30:00", "ubicacion": "C", "monto": 300},
    {"clienteId": "C1", "fecha": "2024-07-26 10:45:00", "ubicacion": "A", "monto": 400},
    {"clienteId": "C1", "fecha": "2024-07-26 11:00:00", "ubicacion": "B", "monto": 500},
    {
        "clienteId": "C2",
        "fecha": "2024-07-26 12:00:00",
        "ubicacion": "C",
        "monto": 1000,
    },
]

contexto = {
    "transaccion": {
        "id": "T123",
        "cuentaOrigenId": "C1",
        "cuentaDestinoId": "C2",
        "monto": 6000,
        "moneda": "USD",
        "tipo": "transferencia",
        "fecha": "2024-07-27 15:30:00",
        "esInternacional": False,
        "paisOrigen": "USA",
        "paisDestino": "MEX",
        "ubicacion": "D",
        "estado": "PENDIENTE",
    },
    "cliente": {
        "id": "C1",
        "nombre": "Juan Perez",
        "tipo": "persona",
        "antiguedad": 180,
        "scoreRiesgo": 650,
        "documentacionCompleta": True,
        "ingresoMensual": 5000,
        "deudaTotal": 1000,
        "paisResidencia": "USA",
        "montoPromedioTransacciones": 500,
    },
    "cuenta": {
        "id": "CC123",
        "clienteId": "C1",
        "tipo": "corriente",
        "saldo": 10000,
        "moneda": "USD",
        "fechaApertura": "2023-01-15",
    },
    "variables": {},  # Diccionario para almacenar variables
    "listas": {  # Listas predefinidas
        "paisesAltoRiesgo": ["CU", "IR", "KP", "SY"],
        "paisesListaNegra": [],  # Por ahora vacia
    },
    "historial": historial_transacciones,
}


reglas = """
transaccion.monto > 5000 => RECHAZAR;
cliente.scoreRiesgo < 300 => APROBAR;
LET comision = transaccion.monto * 0.01;
comision > 10 => ALERTAR('Comisión alta');
transaccion.paisDestino IN paisesAltoRiesgo => BLOQUEAR;
contarTransacciones(cliente.id, "1 HORA", transaccion.ubicacion) > 4 => MARCAR_COMO_SOSPECHOSO;
"""


contexto_final = ejecutar_reglas(reglas, contexto)


print(contexto_final["transaccion"])
