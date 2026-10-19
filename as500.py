#!/usr/bin/env python3
"""AS/500: terminal estilo AS/500 con interfaz a color, controlada con el teclado numérico."""
import os
import random
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime

os.system("")  # activa los códigos ANSI en Windows

# ------------------------------------------------------------------ paleta

BLANCO = 255
GRIS = 245
GRIS_OSCURO = 238
FONDO_AZUL = 24
FONDO_PIE = 236
FONDO_CAMPO = 235
CIAN = 45
VERDE = 83
AMBAR = 214
ROJO = 203
NEGRO = 16
AZUL = 39

RESET = "\033[0m"
OCULTAR_CURSOR = "\033[?25l"
MOSTRAR_CURSOR = "\033[?25h"

ANCHO = 80
SISTEMA = "AS500-DEV01"
PASOS_TOTALES = 8
LARGO_ACCESO = 12
CARACTERES_RUIDO = "#%&@$*+=<>?/\\|0123456789ABCDEF"
CUADROS_GIRO = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
DEGRADADO_LOGO = [51, 45, 39, 33, 27, 21]
DEGRADADO_BARRA = [27, 33, 39, 45, 51, 50, 49, 48, 47, 46]
DEGRADADO_TRANSICION = [17, 18, 19, 20, 21, 27, 33, 39]
PATRON_ANSI = re.compile(r"\033\[[0-9;]*m")

LOGO = (
    "  █████╗ ███████╗   ███████╗ ██████╗  ██████╗ ",
    " ██╔══██╗██╔════╝   ██╔════╝██╔═████╗██╔═████╗",
    " ███████║███████╗   ███████╗██║██╔██║██║██╔██║",
    " ██╔══██║╚════██║   ╚════██║████╔╝██║████╔╝██║",
    " ██║  ██║███████║   ███████║╚██████╔╝╚██████╔╝",
    " ╚═╝  ╚═╝╚══════╝   ╚══════╝ ╚═════╝  ╚═════╝ ",
)

COMPROBACIONES = (
    "Verificando autorización del usuario",
    "Comprobando biblioteca QGPL",
    "Reservando memoria en QINTER",
    "Bloqueando objeto *FILE exclusivo",
    "Consultando al oráculo del sistema",
)


class Cancelar(Exception):
    """Esc: vuelve al menú principal."""


# ------------------------------------------------------------- estilo y cajas

def estilo(texto, fg=None, fondo=None, negrita=False):
    codigos = []
    if negrita:
        codigos.append("1")
    if fg is not None:
        codigos.append(f"38;5;{fg}")
    if fondo is not None:
        codigos.append(f"48;5;{fondo}")
    if not codigos:
        return texto
    return f"\033[{';'.join(codigos)}m{texto}{RESET}"


def largo_visible(texto):
    return len(PATRON_ANSI.sub("", texto))


def rellenar(texto, ancho):
    return texto + " " * max(0, ancho - largo_visible(texto))


def insignia(texto, fondo=AMBAR):
    return estilo(f" {texto} ", NEGRO, fondo, True)


def imprimir_caja(lineas, titulo="", borde=CIAN, ancho=ANCHO - 4):
    interior = ancho - 2
    if titulo:
        rotulo = f" {titulo} "
        arriba = (
            estilo("╭─", borde)
            + estilo(rotulo, BLANCO, negrita=True)
            + estilo("─" * (interior - 1 - len(rotulo)) + "╮", borde)
        )
    else:
        arriba = estilo("╭" + "─" * interior + "╮", borde)
    print("  " + arriba)
    for linea in lineas:
        print("  " + estilo("│", borde) + rellenar(" " + linea, interior) + estilo("│", borde))
    print("  " + estilo("╰" + "─" * interior + "╯", borde))


# ---------------------------------------------------------------- animaciones

def limpiar():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def pausa(segundos):
    time.sleep(segundos)


def escribir_maquina(texto, fg=VERDE, retardo=0.015, salto=True):
    for letra in texto:
        sys.stdout.write(estilo(letra, fg))
        sys.stdout.flush()
        pausa(retardo)
    if salto:
        print()


def revelar(texto, fg=VERDE, fotogramas=3, retardo=0.012, prefijo="  ", negrita=False):
    """Cambio de texto: ruido que se resuelve letra por letra."""
    fijo = ""
    for letra in texto:
        for _ in range(fotogramas):
            ruido = "".join(
                random.choice(CARACTERES_RUIDO) for _ in range(len(texto) - len(fijo))
            )
            sys.stdout.write(f"\r{prefijo}{estilo(fijo, fg, negrita=negrita)}{estilo(ruido, AMBAR)}")
            sys.stdout.flush()
            pausa(retardo)
        fijo += letra
    sys.stdout.write(f"\r{prefijo}{estilo(texto, fg, negrita=negrita)}\n")
    sys.stdout.flush()


def transicion():
    """Barrido de pantalla con degradado entre pantallas."""
    filas = shutil.get_terminal_size((ANCHO, 24)).lines
    sys.stdout.write("\033[H")
    for fila in range(filas):
        color = DEGRADADO_TRANSICION[fila * len(DEGRADADO_TRANSICION) // filas]
        sys.stdout.write(estilo(" " * ANCHO, fondo=color) + ("\n" if fila < filas - 1 else ""))
        sys.stdout.flush()
        pausa(0.008)
    limpiar()


def barra_progreso(etiqueta, duracion=2.0, ancho=36):
    for paso in range(101):
        llenos = ancho * paso // 100
        celdas = "".join(
            estilo("█", DEGRADADO_BARRA[i * len(DEGRADADO_BARRA) // ancho]) for i in range(llenos)
        ) + estilo("░" * (ancho - llenos), GRIS_OSCURO)
        sys.stdout.write(
            f"\r  {estilo(etiqueta.ljust(22), CIAN)}{celdas} {estilo(f'{paso:3d}%', BLANCO, negrita=True)}"
        )
        sys.stdout.flush()
        pausa(duracion / 100)
    sys.stdout.write(estilo(" ✔", VERDE, negrita=True) + "\n")


def girar(etiqueta, duracion=1.2):
    for indice in range(max(1, int(duracion / 0.07))):
        cuadro = CUADROS_GIRO[indice % len(CUADROS_GIRO)]
        sys.stdout.write(f"\r  {estilo(cuadro, AMBAR, negrita=True)} {estilo(etiqueta, GRIS)}")
        sys.stdout.flush()
        pausa(0.07)
    sys.stdout.write(
        f"\r  {estilo('✔', VERDE, negrita=True)} {estilo(etiqueta, BLANCO)} {insignia('OK', VERDE)}\n"
    )
    sys.stdout.flush()


# ------------------------------------------------------------------- teclado

def vaciar_teclado():
    """Descarta teclas pulsadas durante las animaciones."""
    try:
        if os.name == "nt":
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getwch()
        else:
            import termios
            termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
    except Exception:
        pass


def leer_tecla():
    if os.name == "nt":
        import msvcrt
        while True:
            letra = msvcrt.getwch()
            if letra in ("\x00", "\xe0"):
                msvcrt.getwch()
                continue
            break
    else:
        import termios
        import tty
        descriptor = sys.stdin.fileno()
        anterior = termios.tcgetattr(descriptor)
        try:
            tty.setraw(descriptor)
            letra = sys.stdin.read(1)
        finally:
            termios.tcsetattr(descriptor, termios.TCSADRAIN, anterior)
    if letra == "\x03":
        raise KeyboardInterrupt
    if letra in ("\r", "\n"):
        return "ENTER"
    if letra in ("\x08", "\x7f"):
        return "RETROCESO"
    if letra == "\x1b":
        return "ESC"
    return letra


def elegir(validas):
    """Pide una opción: se escribe el número y se confirma con INTRO."""
    seleccion = ""

    def armar(con_cursor, aviso):
        cursor = "▌" if con_cursor and not seleccion else ""
        campo = (" " + seleccion + cursor).ljust(4)
        if aviso:
            ayuda = estilo(f"  ✖ {aviso}", ROJO, negrita=True)
        elif con_cursor:
            ayuda = estilo("  escriba el número y pulse INTRO", GRIS)
        else:
            ayuda = ""
        return (
            "  " + estilo("Opción".ljust(22), CIAN) + estilo("▸ ", AMBAR)
            + estilo(campo, VERDE, FONDO_CAMPO, True) + ayuda + "\033[K"
        )

    print()
    vaciar_teclado()
    aviso = ""
    while True:
        sys.stdout.write("\r" + armar(True, aviso))
        sys.stdout.flush()
        tecla = leer_tecla()
        aviso = ""
        if tecla == "ENTER" and seleccion:
            sys.stdout.write("\r" + armar(False, "") + "\n")
            return seleccion
        if tecla == "RETROCESO":
            seleccion = ""
        elif len(tecla) == 1 and tecla in "0123456789":
            if tecla in validas:
                seleccion = tecla
            else:
                aviso = "Opción no válida"


def leer_campo(etiqueta, longitud, ocultar=False, permitir_negativo=False,
               solo_digitos=True, convertir=str):
    texto = ""

    def contenido():
        return texto.lstrip("-") if solo_digitos else texto

    def armar(con_cursor):
        visible = "●" * len(texto) if ocultar else texto
        cursor = "▌" if con_cursor and len(contenido()) < longitud else ""
        campo = (" " + visible + cursor).ljust(longitud + 3)
        return (
            "  " + estilo(etiqueta.ljust(22), CIAN) + estilo("▸ ", AMBAR)
            + estilo(campo, VERDE, FONDO_CAMPO, True)
        )

    vaciar_teclado()
    while True:
        sys.stdout.write("\r" + armar(True))
        sys.stdout.flush()
        tecla = leer_tecla()
        if tecla == "ESC":
            print()
            raise Cancelar
        if tecla == "ENTER" and contenido():
            sys.stdout.write("\r" + armar(False) + "\n")
            return convertir(texto)
        if tecla == "RETROCESO":
            texto = texto[:-1]
        elif solo_digitos:
            if len(tecla) == 1 and tecla in "0123456789" and len(contenido()) < longitud:
                texto += tecla
            elif tecla == "-" and permitir_negativo and not texto:
                texto = "-"
        elif len(tecla) == 1 and tecla.isprintable() and tecla != " " and len(contenido()) < longitud:
            texto += tecla


def leer_numero(etiqueta, longitud=8, permitir_negativo=False, convertir=int):
    return leer_campo(etiqueta, longitud, False, permitir_negativo, True, convertir)


def leer_texto(etiqueta, longitud=12, ocultar=False, convertir=str):
    return leer_campo(etiqueta, longitud, ocultar, False, False, convertir)


# ------------------------------------------------------------ marco de pantalla

def encabezado(codigo, titulo, paso=None):
    ahora = datetime.now()
    izquierda = f"  AS/500  ▸  {titulo}"
    derecha = f"{SISTEMA}  "
    print(estilo(izquierda + " " * (ANCHO - len(izquierda) - len(derecha)) + derecha,
                 BLANCO, FONDO_AZUL, True))
    izquierda = f"  Pantalla {codigo}"
    derecha = f"{ahora:%d/%m/%Y  %H:%M:%S}  "
    print(estilo(izquierda + " " * (ANCHO - len(izquierda) - len(derecha)) + derecha,
                 GRIS, FONDO_PIE))
    if paso:
        puntos = ""
        for numero in range(1, PASOS_TOTALES + 1):
            if numero < paso:
                puntos += estilo("● ", VERDE)
            elif numero == paso:
                puntos += estilo("● ", AMBAR, negrita=True)
            else:
                puntos += estilo("○ ", GRIS_OSCURO)
        print("  " + estilo(f"Paso {paso} de {PASOS_TOTALES}", GRIS) + "   " + puntos)
    else:
        print()
    print()


def dibujar_pie(teclas):
    """Barra inferior con las teclas disponibles."""
    filas = shutil.get_terminal_size((ANCHO, 24)).lines
    barra = ""
    for tecla, texto in teclas:
        barra += (
            estilo(" ", fondo=FONDO_PIE) + insignia(tecla)
            + estilo(f" {texto}  ", BLANCO, FONDO_PIE)
        )
    barra += estilo(" " * max(0, ANCHO - largo_visible(barra)), fondo=FONDO_PIE)
    sys.stdout.write(f"\0337\033[{filas};1H{barra}\0338")
    sys.stdout.flush()


# ------------------------------------------------------------------- pantallas

def pantalla_inicio_sesion():
    limpiar()
    encabezado("SIGNON", "Inicio de sesión")
    for linea, color in zip(LOGO, DEGRADADO_LOGO):
        escribir_maquina(linea, color, 0.002)
    print()
    revelar("Sistema operativo i5/OS  ·  Versión V7R5M0", CIAN)
    print()
    imprimir_caja(
        [estilo("Escriba su usuario y su clave con el teclado y pulse INTRO.", GRIS)],
        "Acceso",
    )
    print()
    dibujar_pie([("A-Z 0-9", "Escribir"), ("INTRO", "Aceptar"), ("Retr", "Borrar"), ("Esc", "Salir")])
    usuario = leer_texto("Usuario", LARGO_ACCESO, convertir=str.upper)
    leer_texto("Clave", LARGO_ACCESO, ocultar=True)
    girar("Autenticando contra QSECOFR", 1.0)
    return usuario


def pantalla_menu_principal(usuario):
    limpiar()
    encabezado("MAIN", "Menú principal")
    print("  " + estilo("Usuario activo ", GRIS) + estilo(usuario, AMBAR, negrita=True)
          + estilo("   ·   Subsistema QINTER", GRIS))
    print()
    lineas = []
    for tecla, (_, titulo, descripcion, _, _) in OPERACIONES.items():
        lineas.append(insignia(tecla) + "  " + estilo(titulo, BLANCO, negrita=True))
        lineas.append("      " + estilo(descripcion, GRIS))
        lineas.append("")
    lineas.append(insignia("9", AZUL) + "  " + estilo("Cerrar sesión", BLANCO, negrita=True))
    lineas.append(insignia("0", ROJO) + "  " + estilo("Salir del sistema", BLANCO, negrita=True))
    imprimir_caja(lineas, "¿Qué desea hacer?")
    dibujar_pie(
        [(tecla, datos[1].split()[0]) for tecla, datos in OPERACIONES.items()]
        + [("9", "Cerrar sesión"), ("0", "Salir")]
    )
    return elegir("".join(OPERACIONES) + "90")


def pantalla_confirmar(codigo, titulo, pregunta, detalle, color, texto_si):
    limpiar()
    encabezado(codigo, titulo)
    imprimir_caja(
        [estilo(pregunta, BLANCO, negrita=True), estilo(detalle, GRIS)],
        "Confirmación",
        color,
    )
    dibujar_pie([("1", texto_si), ("2", "No, volver")])
    return elegir("12") == "1"


# --------------------------------------------------------- flujo redundante

def pantalla_seleccion(codigo, titulo, descripcion):
    transicion()
    encabezado(f"{codigo}01", "Trabajar con operaciones", 1)
    imprimir_caja(
        [
            estilo("Operación    ", GRIS) + estilo(titulo, BLANCO, negrita=True),
            estilo("Descripción  ", GRIS) + estilo(descripcion, BLANCO),
            estilo("Tipo         ", GRIS) + estilo("*PGM", CIAN),
            estilo("Biblioteca   ", GRIS) + estilo("QGPL", CIAN),
            estilo("Estado       ", GRIS) + estilo("● ACTIVO", VERDE, negrita=True),
        ],
        "Objeto seleccionado",
    )
    dibujar_pie([("1", "Seleccionar"), ("2", "Detalles"), ("3", "Volver")])
    detalles_mostrados = False
    while True:
        tecla = elegir("123")
        if tecla == "1":
            return
        if tecla == "3":
            raise Cancelar
        if not detalles_mostrados:
            detalles_mostrados = True
            print()
            for texto in (
                "Autor . . . . . . : QSYS",
                "Compilado . . . . : 2026",
                "Líneas útiles . . : 1 (y 340 de burocracia)",
            ):
                revelar(texto, GRIS)


def pantalla_parametros(codigo, titulo, campos):
    transicion()
    encabezado(f"{codigo}02", "Indicar parámetros", 2)
    imprimir_caja(
        [estilo(f"{titulo}: escriba cada valor y pulse INTRO.", GRIS)],
        "Parámetros",
    )
    print()
    dibujar_pie([("0-9", "Dígitos"), ("INTRO", "Aceptar"), ("Retr", "Borrar"), ("Esc", "Cancelar")])
    return [leer_numero(etiqueta, longitud, permitir_negativo=True) for etiqueta, longitud in campos]


def pantalla_verificacion(codigo, campos, valores):
    transicion()
    encabezado(f"{codigo}03", "Verificar parámetros", 3)
    print(estilo("  Parámetros recibidos:", GRIS))
    print()
    for (etiqueta, _), valor in zip(campos, valores):
        revelar(f"{etiqueta.ljust(22)}▸ {valor}", BLANCO)
    print()
    print(estilo("  ¿Son correctos los parámetros?", AMBAR, negrita=True))
    dibujar_pie([("1", "Confirmar"), ("2", "Corregir"), ("3", "Cancelar")])
    tecla = elegir("123")
    if tecla == "3":
        raise Cancelar
    return tecla == "1"


def pantalla_validacion(codigo):
    transicion()
    encabezado(f"{codigo}04", "Validación de la solicitud", 4)
    dibujar_pie([("···", "Procesando, espere")])
    for comprobacion in COMPROBACIONES:
        girar(comprobacion, random.uniform(0.6, 1.2))


def pantalla_envio(codigo):
    transicion()
    encabezado(f"{codigo}05", "Envío al subsistema", 5)
    dibujar_pie([("···", "Procesando, espere")])
    revelar("Enviando solicitud al subsistema QBATCH...", AMBAR)
    print()
    barra_progreso("Cola de trabajos", 1.6)
    barra_progreso("Ejecución", 2.0)
    barra_progreso("Liberación de bloqueo", 1.0)


def pantalla_mensajes(codigo):
    transicion()
    encabezado(f"{codigo}06", "Mensajes del sistema", 6)
    mensajes = (
        ("CPC1221", VERDE, "Operación finalizada normalmente."),
        ("CPI0009", CIAN, f"Trabajo {random.randint(100000, 999999)}/QUSER/{codigo} completado."),
        ("CPI1124", AMBAR, "Se liberaron los bloqueos del objeto."),
    )
    for clave, color, texto in mensajes:
        sys.stdout.write("  " + insignia(clave, color) + " ")
        escribir_maquina(texto, BLANCO)
        print()
    dibujar_pie([("1", "Continuar"), ("2", "Bitácora")])
    bitacora_mostrada = False
    while True:
        if elegir("12") == "1":
            return
        if not bitacora_mostrada:
            bitacora_mostrada = True
            ahora = f"{datetime.now():%H:%M:%S}"
            for texto in (
                f"[{ahora}] QINTER   solicitud recibida",
                f"[{ahora}] QBATCH   trabajo en ejecución",
                f"[{ahora}] QSYSWRK  resultado entregado",
            ):
                revelar(texto, GRIS)


def pantalla_resultado(codigo, resultado):
    transicion()
    encabezado(f"{codigo}07", "Visualizar resultado", 7)
    print(estilo("  El resultado de la operación es:", GRIS))
    print()
    print(estilo("  " + "━" * 44, AMBAR))
    print()
    revelar(f"{resultado}", AMBAR, fotogramas=6, retardo=0.02,
            prefijo=estilo("    ▶  ", VERDE, negrita=True), negrita=True)
    print()
    print(estilo("  " + "━" * 44, AMBAR))
    dibujar_pie([("1", "Continuar")])
    elegir("1")


def pantalla_fin(codigo):
    """Devuelve True si el usuario quiere repetir la operación."""
    transicion()
    encabezado(f"{codigo}08", "Confirmar fin de la solicitud", 8)
    imprimir_caja(
        [
            estilo("¿Desea finalizar la solicitud?", BLANCO, negrita=True),
            estilo("Podrá repetir la operación o volver al menú.", GRIS),
        ],
        "Fin de solicitud",
        VERDE,
    )
    dibujar_pie([("1", "Finalizar"), ("2", "Repetir"), ("3", "Menú")])
    tecla = elegir("123")
    if tecla == "1":
        print()
        girar("Cerrando solicitud", 0.8)
    return tecla == "2"


def flujo_redundante(codigo, titulo, descripcion, campos, calcular):
    """Ejecuta una función sencilla pasando por ocho pantallas innecesarias."""
    pantalla_seleccion(codigo, titulo, descripcion)
    while True:
        valores = pantalla_parametros(codigo, titulo, campos)
        if pantalla_verificacion(codigo, campos, valores):
            break
    pantalla_validacion(codigo)
    pantalla_envio(codigo)
    resultado = calcular(*valores)
    pantalla_mensajes(codigo)
    pantalla_resultado(codigo, resultado)
    return pantalla_fin(codigo)


# ------------------------------------------------------------------ funciones

def sumar_dos_numeros(numero_a, numero_b):
    return numero_a + numero_b


def determinar_paridad(numero):
    return f"{numero} es {'PAR' if numero % 2 == 0 else 'IMPAR'}"


def invertir_numero(numero):
    signo = "-" if numero < 0 else ""
    return signo + str(abs(numero))[::-1]


OPERACIONES = {
    "1": ("SUM", "Sumar dos números", "Suma dos enteros y muestra el total.",
          [("Primer número", 8), ("Segundo número", 8)], sumar_dos_numeros),
    "2": ("PAR", "Par o impar", "Indica si un entero es par o impar.",
          [("Número entero", 9)], determinar_paridad),
    "3": ("INV", "Invertir un número", "Escribe los dígitos de un entero al revés.",
          [("Número entero", 9)], invertir_numero),
}


def ciclo_sesion(usuario):
    """Atiende el menú de una sesión. Devuelve True si se debe salir del sistema."""
    while True:
        try:
            tecla = pantalla_menu_principal(usuario)
            if tecla == "9":
                if pantalla_confirmar(
                    "OUT", "Cerrar sesión", f"¿Desea cerrar la sesión de {usuario}?",
                    "Volverá a la pantalla de inicio de sesión.", AMBAR, "Sí, cerrar",
                ):
                    print()
                    girar(f"Cerrando sesión de {usuario}", 1.0)
                    return False
            elif tecla == "0":
                if pantalla_confirmar(
                    "EXIT", "Salir del sistema", "¿Desea salir del sistema?",
                    "Se cerrará la aplicación.", ROJO, "Sí, salir",
                ):
                    return True
            else:
                while flujo_redundante(*OPERACIONES[tecla]):
                    pass
        except Cancelar:
            print()
            print(estilo("  CPF9899 · Solicitud cancelada.", AMBAR))
            pausa(1.0)


def principal():
    sys.stdout.write(OCULTAR_CURSOR)
    try:
        try:
            salir = False
            while not salir:
                try:
                    usuario = pantalla_inicio_sesion()
                except Cancelar:
                    break
                salir = ciclo_sesion(usuario)
                if not salir:
                    transicion()
        except (KeyboardInterrupt, EOFError):
            pass
        transicion()
        revelar("Sesión finalizada. Cerrando conexión con el sistema...", VERDE)
    finally:
        sys.stdout.write(MOSTRAR_CURSOR + RESET + "\n")


def abrir_en_pestana_nueva():
    """Abre la aplicación en una pestaña/ventana propia. Devuelve True si lo logró."""
    if os.name != "nt":
        return False
    ruta = os.path.abspath(__file__)
    try:
        if shutil.which("wt"):
            subprocess.Popen([
                "wt", "-w", "0", "new-tab", "--title", "AS/500",
                "--startingDirectory", os.path.dirname(ruta),
                sys.executable, ruta, "--pestana",
            ])
        else:
            subprocess.Popen(
                [sys.executable, ruta, "--pestana"],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        return True
    except OSError:
        return False


if __name__ == "__main__":
    if "--aqui" in sys.argv:
        principal()
    elif "--pestana" in sys.argv:
        principal()
        sys.stdout.write(estilo("Pulse cualquier tecla para cerrar esta pestaña...", GRIS))
        sys.stdout.flush()
        try:
            leer_tecla()
        except KeyboardInterrupt:
            pass
    elif not abrir_en_pestana_nueva():
        principal()
