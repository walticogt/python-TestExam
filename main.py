###
# Autor: Oscar Huanca
# Version: 0.1
# Revisión: 12 Nov 2024
# Recomendaciones a futuro: 
#   Centrar vertical, del TIP, siempre ponerlo abajo, cambiar color.
#   Menu opciones donde tengamos el Numero de TIP limites q debemos colocar (por defecto 5), versión premium FULL
#   Desbloquear la version PREMIUM con un código que sea autogenerado deacuerdo a la fecha del sistema y nombre equipo + 24
#   Poner un about
###

import customtkinter as ctk
from tkinter import Menu, messagebox, Toplevel, Label, StringVar
import random
import json
import textwrap  # Importar para dar formato al texto

# Cargar preguntas desde archivo JSON
def cargar_preguntas():
    with open("cuestionario1.json", "r", encoding="utf-8") as file:
        return json.load(file)


# Función para centrar los diálogos
def centrar_dialogo(dialogo):
    ventana_x = ventana.winfo_rootx() + ventana.winfo_width() // 2
    ventana_y = ventana.winfo_rooty() + ventana.winfo_height() // 2
    dialogo.geometry(f"+{ventana_x - dialogo.winfo_width() // 2}+{ventana_y - dialogo.winfo_height() // 2}")

# Función para formatear texto con un límite de 70 caracteres por línea
def formatear_texto(texto, limite=70):
    return '\n'.join(textwrap.wrap(texto, width=limite))

# Función para mostrar la justificación y ocultar el botón TIP
def mostrar_justificacion(boton, label_justificacion, justificacion):
    boton.pack_forget()
    label_justificacion.configure(text=formatear_texto(justificacion))
    label_justificacion.pack(pady=5)

# Función para mostrar la pregunta actual
def mostrar_pregunta():
    global opciones
    
    limpiar_tip()  # Limpia el botón TIP y la justificación antes de mostrar una nueva pregunta
    
    # Limpiar opciones previas
    for boton in opciones:
        boton.pack_forget()
    opciones.clear()

    if randomizar_alternativas:
        random.shuffle(preguntas[pregunta_actual]["alternativas"])  # Aleatoriza alternativas
    respuesta_seleccionada.set("")  # Restablece selección
    pregunta_data = preguntas[pregunta_actual]
    label_pregunta.configure(text=f"{pregunta_actual + 1}.- {pregunta_data['pregunta']}")
    label_preguntas_pendientes.configure(text=f"Preguntas restantes: {len(preguntas) - pregunta_actual}")
    
    # Crear nuevos RadioButtons según la cantidad de alternativas y formatear el texto
    for i, alternativa in enumerate(pregunta_data["alternativas"]):
        texto_formateado = formatear_texto(alternativa)  # Formatea el texto
        boton = ctk.CTkRadioButton(ventana, text=texto_formateado, variable=respuesta_seleccionada, value=str(i))
        boton.pack(anchor="w", padx=20, pady=2)
        opciones.append(boton)
    
    # Crear botón TIP y etiqueta de justificación en el contenedor de botones
    justificacion = pregunta_data.get("justificacion", "")
    if not justificaciones_mostradas[pregunta_actual]:
        boton_tip = ctk.CTkButton(contenedor_botones, text="TIP", command=lambda: [mostrar_justificacion(boton_tip, label_justificacion, justificacion), guardar_justificacion_mostrada()])
        boton_tip.pack(side="left", padx=5)

    contenedor_botones.pack(pady=10)

    # Mueve el botón Verificar al contenedor de botones
    #boton_verificar.pack_forget()  # Elimina cualquier posición previa del botón Verificar
    #boton_verificar.pack(in_=contenedor_botones, side="left", padx=5)

    label_justificacion.configure(text="")
    label_justificacion.pack_forget()


def guardar_justificacion_mostrada():
    justificaciones_mostradas[pregunta_actual] = True

# Función para verificar la respuesta
def verificar_respuesta():
    if not respuesta_seleccionada.get():  # Verifica si hay selección
        mostrar_advertencia()
        return
    
    global correctas
    respuesta_correcta = preguntas[pregunta_actual]["respuesta_correcta"]
    seleccion_index = int(respuesta_seleccionada.get())  # Obtiene el índice seleccionado
    seleccion_texto = preguntas[pregunta_actual]["alternativas"][seleccion_index]  # Texto de la alternativa seleccionada

    print(f"Respuesta correcta esperada: '{respuesta_correcta}'")
    print(f"Respuesta seleccionada: '{seleccion_texto}'")

    if seleccion_texto == respuesta_correcta:
        correctas += 1
        resultado = "¡Correcto!"
    else:
        resultado = f"Incorrecto. La respuesta correcta es {respuesta_correcta}."
        preguntas_incorrectas.append(preguntas[pregunta_actual])  # Agrega a incorrectas
    mostrar_resultado(resultado)

# Función para mostrar advertencia centrada si no hay respuesta
def mostrar_advertencia():
    dialogo_advertencia = Toplevel(ventana)
    dialogo_advertencia.title("Advertencia")
    Label(dialogo_advertencia, text="Debe seleccionar una respuesta antes de continuar.").pack(pady=20)
    ctk.CTkButton(dialogo_advertencia, text="Aceptar", command=dialogo_advertencia.destroy).pack(pady=10)
    dialogo_advertencia.update_idletasks()
    centrar_dialogo(dialogo_advertencia)

# Función para mostrar el resultado de la pregunta
def mostrar_resultado(mensaje):
    dialogo = Toplevel(ventana)
    dialogo.title("Resultado")
    Label(dialogo, text=mensaje).pack(pady=20)
    ctk.CTkButton(dialogo, text="Aceptar", command=lambda: [dialogo.destroy(), avanzar_pregunta()]).pack(pady=10)
    dialogo.update_idletasks()
    centrar_dialogo(dialogo)

# Función para avanzar a la siguiente pregunta
def avanzar_pregunta():
    global pregunta_actual
    pregunta_actual += 1
    if pregunta_actual < len(preguntas):  # Si hay más preguntas
        mostrar_pregunta()
    else:
        finalizar_quiz()

# Función para finalizar y mostrar el resultado final
def finalizar_quiz():
    dialogo_final = Toplevel(ventana)
    dialogo_final.title("Resultado final")
    mensaje = f"Respuestas correctas: {correctas} de {len(preguntas)}"
    
    if correctas == len(preguntas):
        mensaje += "\n¡Felicidades! Has acertado todas las respuestas."
    else:
        mensaje += "\n¿Quieres intentar nuevamente?"
    
    Label(dialogo_final, text=mensaje).pack(pady=20)
    ctk.CTkButton(dialogo_final, text="Salir", command=ventana.quit).pack(pady=10)

    # Opción para reiniciar solo con respuestas incorrectas si las hay
    if preguntas_incorrectas:
        ctk.CTkButton(dialogo_final, text="Reintentar solo con respuestas incorrectas", 
                      command=lambda: reiniciar(False)).pack(pady=10)
    dialogo_final.update_idletasks()
    centrar_dialogo(dialogo_final)

def limpiar_tip():
    label_justificacion.pack_forget()  # Oculta la etiqueta de justificación
    for widget in ventana.pack_slaves():  # Elimina el botón TIP si existe
        if isinstance(widget, ctk.CTkButton) and widget.cget("text") == "TIP":
            widget.pack_forget()


# Función para reiniciar el cuestionario
def reiniciar(todas):
    global pregunta_actual, correctas, preguntas_incorrectas, preguntas
    pregunta_actual = 0
    correctas = 0
    preguntas = preguntas_original.copy() if todas else preguntas_incorrectas.copy()
    preguntas_incorrectas = []
    justificaciones_mostradas = [False] * len(preguntas)  # Inicializa como no mostradas

    limpiar_tip()  
    # Aleatorizar preguntas si está activada la opción
    if randomizar_preguntas:
        random.shuffle(preguntas)
    
    mostrar_pregunta()

# Función para mostrar el mensaje de recomendación
def mostrar_recomendacion():
    dialogo_recomendacion = Toplevel(ventana)
    dialogo_recomendacion.title("Recomendación")
    Label(dialogo_recomendacion, text="Se recomienda reiniciar el cuestionario en File->Nuevo.").pack(pady=20)
    ctk.CTkButton(dialogo_recomendacion, text="Aceptar", command=dialogo_recomendacion.destroy).pack(pady=10)
    dialogo_recomendacion.update_idletasks()
    centrar_dialogo(dialogo_recomendacion)

# Función para alternar la opción de randomizar preguntas
def alternar_randomizar_preguntas():
    global randomizar_preguntas
    randomizar_preguntas = not randomizar_preguntas
    mostrar_recomendacion()

# Función para alternar la opción de randomizar alternativas
def alternar_randomizar_alternativas():
    global randomizar_alternativas
    randomizar_alternativas = not randomizar_alternativas
    mostrar_recomendacion()


# Preguntas, alternativas y respuestas correctas
preguntas_original = cargar_preguntas()

# Crear la ventana principal
ventana = ctk.CTk()
ventana.title("Proyecto Ejemplo")
ventana.geometry("500x450") #450 alto, debería estar en variable HEIGHT
ventana.resizable(False, False)

# Variables de control
respuesta_seleccionada = StringVar(value="")  # Vacío por defecto
pregunta_actual = 0
correctas = 0
preguntas = preguntas_original.copy()
justificaciones_mostradas = [False] * len(preguntas)  # Inicializa como no mostradas

preguntas_incorrectas = []
randomizar_preguntas = False
randomizar_alternativas = False
opciones = []  # Lista de botones de opciones

# Etiqueta para mostrar el total de preguntas pendientes
label_preguntas_pendientes = ctk.CTkLabel(ventana, text=f"Preguntas restantes: {len(preguntas)}")
label_preguntas_pendientes.pack(anchor="ne", padx=20)

# Etiqueta para mostrar la pregunta
label_pregunta = ctk.CTkLabel(ventana, text="", wraplength=300)
label_pregunta.pack(pady=10)

# Etiqueta para mostrar la justificación
label_justificacion = ctk.CTkLabel(ventana, text="", wraplength=450) #la variable HEIGHT

# Contenedor para los botones TIP y Verificar
contenedor_botones = ctk.CTkFrame(ventana)
contenedor_botones.pack(pady=5)

# Crear botón TIP, pero no lo empaques todavía
boton_tip = ctk.CTkButton(contenedor_botones, text="TIP", command=lambda: mostrar_justificacion(boton_tip, label_justificacion, ""))

# Crear botón Confirmar, pero no lo empaques todavía
boton_verificar = ctk.CTkButton(contenedor_botones, text="Confirmar", command=verificar_respuesta)

# Menú de opciones
menu = Menu(ventana)
ventana.config(menu=menu)

# Menú Archivo
menu_archivo = Menu(menu, tearoff=0)
menu.add_cascade(label="Archivo", menu=menu_archivo)
menu_archivo.add_command(label="Nuevo", command=lambda: reiniciar(True))
menu_archivo.add_command(label="Salir", command=ventana.quit)

# Menú Opciones
menu_opciones = Menu(menu, tearoff=0)
menu.add_cascade(label="Opciones", menu=menu_opciones)
menu_opciones.add_checkbutton(label="Randomizar preguntas", command=alternar_randomizar_preguntas)
menu_opciones.add_checkbutton(label="Randomizar respuestas", command=alternar_randomizar_alternativas)

label_pregunta.pack(pady=10)

# Botón para verificar la respuesta
boton_verificar = ctk.CTkButton(ventana, text="Confirmar", command=verificar_respuesta)
boton_verificar.pack(pady=10)

# Iniciar el cuestionario
if randomizar_preguntas:
    random.shuffle(preguntas)
mostrar_pregunta()

# Ejecutar la aplicación
ventana.mainloop()
