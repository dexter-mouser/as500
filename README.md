# Terminal AS/500

Simulador de terminal estilo AS/500 (5250) para consola, con interfaz a color. Las opciones se eligen con el teclado numérico y el inicio de sesión admite el teclado completo. Realiza operaciones sencillas pasando por una cadena deliberadamente excesiva de pantallas, con animaciones.

## Utilidades

- Sumar dos números
- Determinar si un número es par o impar
- Invertir los dígitos de un número

## Requisitos

- Python 3.8 o superior
- Terminal con soporte de colores de 256 tonos y Unicode (80 columnas mínimo)
- Sin dependencias externas

## Uso

```
python as500.py
```

La aplicación se abre en una pestaña propia de Windows Terminal (o en una ventana de consola nueva si no está instalado), separada de la terminal del proyecto. Para ejecutarla en la terminal actual:

```
python as500.py --aqui
```

En sistemas distintos de Windows se ejecuta siempre en la terminal actual.

## Teclas

Las opciones se eligen en la línea `Opción ▸`: se escribe el número y se confirma con `INTRO` para ejecutar la acción.

- `1`, `2`, `3`: opciones de cada pantalla (se muestran en la barra inferior); `Retroceso` cambia la opción escrita antes de confirmar
- `9`: cerrar sesión desde el menú principal (vuelve al inicio de sesión para entrar con otro usuario)
- `0`: salir del sistema desde el menú principal
- `0-9`: dígitos en los campos numéricos; `-` al inicio para números negativos
- `INTRO`: confirmar la opción o aceptar el valor escrito
- `Retroceso`: borrar el último dígito
- `Esc`: cancelar y volver al menú

En el inicio de sesión, usuario y clave se escriben con letras y números del teclado completo (la clave se oculta con puntos). Ambos campos tienen el mismo largo y se acepta cualquier combinación.

## Funcionamiento

Cada operación recorre ocho pantallas, con un indicador de pasos en la parte superior:

1. Selección de la operación (`1` seleccionar, `2` detalles, `3` volver)
2. Captura de parámetros
3. Verificación de parámetros (`1` confirmar, `2` corregir, `3` cancelar)
4. Validación (autorización, bibliotecas, bloqueos)
5. Envío al subsistema (tres barras de progreso)
6. Mensajes del sistema (`2` muestra la bitácora)
7. Visualización del resultado
8. Confirmación de fin (`1` finalizar, `2` repetir, `3` menú)

Efectos visuales:

- Barrido de pantalla con degradado entre pantallas
- Texto que se resuelve desde ruido aleatorio
- Escritura tipo máquina
- Indicadores giratorios y barras de progreso con degradado

Para añadir una operación, defina su función y regístrela en el diccionario `OPERACIONES` con código, título, descripción, campos numéricos y función de cálculo.
