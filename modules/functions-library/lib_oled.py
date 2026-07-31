# ===== Funciones de impresion en display Oled =====

# Imprime una linea determinada en display Oled.
def FProled(oled, texto: str = "clear", linea: int = 1) -> None:
    if texto == "clear":  # texto='clear' borra display
        oled.fill(0)
    else:
        oled.fill_rect(0, ((linea - 1) * 8), 128, 8, 0)
        oled.text(texto, 0, ((linea - 1) * 8), 1)
    oled.show()

# Imprime lineas en el display Oled en forma secuencial a partir de la 1ra
def FDisplay_lineas(oled, lineas: tuple) -> None:
    oled.fill_rect(0, 0, 128, 63, 0)
    i = 0
    for linea in lineas:
        oled.text(linea, 0, (i * 8), 1)
        i += 1
    oled.show()
