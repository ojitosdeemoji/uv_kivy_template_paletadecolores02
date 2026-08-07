"""
Analizador de Paleta de Colores - App Android
"""
import os
import io
import numpy as np
from PIL import Image
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image as KivyImage
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivy.metrics import dp
from plyer import filechooser

def rgb_a_hex(rgb):
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def kmeans_rgb(pixels, k, max_iters=20):
    k = min(k, len(pixels))
    if k == 0:
        return np.array([]), np.array([])
    idx = np.random.choice(len(pixels), k, replace=False)
    centroids = pixels[idx].astype(float)
    for _ in range(max_iters):
        distances = np.sqrt(((pixels - centroids[:, np.newaxis])**2).sum(axis=2))
        labels = np.argmin(distances, axis=0)
        new_centroids = []
        for i in range(k):
            if np.any(labels == i):
                new_centroids.append(pixels[labels == i].mean(axis=0))
            else:
                new_centroids.append(centroids[i])
        new_centroids = np.array(new_centroids)
        if np.allclose(centroids, new_centroids, atol=1):
            break
        centroids = new_centroids
    colores = centroids.astype(int)
    conteo = np.bincount(labels)
    porcentajes = (conteo / len(labels)) * 100
    idx_orden = np.argsort(porcentajes)[::-1]
    return colores[idx_orden], porcentajes[idx_orden]

def analizar_imagen(ruta, n_colores=8):
    try:
        img = Image.open(ruta).convert('RGB')
        img.thumbnail((300, 300))
        pixels = np.array(img).reshape(-1, 3)
        colores, pcts = kmeans_rgb(pixels, n_colores)
        return colores, pcts, img
    except:
        return None, None, None

class ColorBarWidget(Widget):
    def __init__(self, colores, porcentajes, **kwargs):
        super().__init__(**kwargs)
        self.colores = colores
        self.porcentajes = porcentajes
        self.bind(pos=self.redraw, size=self.redraw)
    def redraw(self, *args):
        self.canvas.clear()
        if not self.colores.any():
            return
        w = self.width
        h = self.height
        x_pos = 0
        for color, pct in zip(self.colores, self.porcentajes):
            if pct > 0:
                ancho = (pct / 100) * w
                with self.canvas:
                    Color(color[0]/255., color[1]/255., color[2]/255., 1)
                    RoundedRectangle(pos=(self.x + x_pos, self.y), size=(ancho, h), radius=[(4, 4), (4, 4), (4, 4), (4, 4)])
                x_pos += ancho

class TarjetaResultado(BoxLayout):
    def __init__(self, nombre_archivo, colores, porcentajes, img_pil, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(160)
        self.padding = dp(10)
        self.spacing = dp(10)
        from kivy.graphics.texture import Texture
        col_izq = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(120))
        lbl_nombre = Label(text=nombre_archivo[:15], font_size=dp(12), halign='center', color=(0.2,0.2,0.2,1), size_hint_y=None, height=dp(20))
        col_izq.add_widget(lbl_nombre)
        thumb = img_pil.copy()
        thumb.thumbnail((100, 100))
        data = thumb.tobytes()
        texture = Texture.create(size=thumb.size)
        texture.blit_buffer(data, colorfmt='rgb', bufferfmt='ubyte')
        texture.flip_vertical()
        img_kivy = KivyImage(texture=texture, size_hint=(1, 1), keep_ratio=True)
        col_izq.add_widget(img_kivy)
        self.add_widget(col_izq)
        col_der = BoxLayout(orientation='vertical', spacing=dp(5))
        barra = ColorBarWidget(colores, porcentajes, size_hint=(1, 0.4))
        col_der.add_widget(barra)
        txt_colores = ""
        for i, (c, p) in enumerate(zip(colores, porcentajes)):
            hex_code = rgb_a_hex(c)
            txt_colores += f"[b]{i+1}.[/b] RGB{tuple(c)}  [color={hex_code}][b]{hex_code}[/b][/color]  {p:.1f}%\n"
        lbl_info = Label(text=txt_colores, markup=True, font_size=dp(11), color=(0.1,0.1,0.1,1), halign='left', valign='top', size_hint=(1, 0.6))
        lbl_info.bind(size=lbl_info.setter('text_size'))
        col_der.add_widget(lbl_info)
        self.add_widget(col_der)

class PaletteApp(App):
    def build(self):
        Window.clearcolor = (0.96, 0.96, 0.96, 1)
        self.n_colores = 8
        self.fotos_seleccionadas = []
        self.resultados_imagenes = []
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        titulo = Label(text='Analizador de Paleta', font_size=dp(22), color=(0.23,0.23,0.23,1), size_hint_y=None, height=dp(50))
        root.add_widget(titulo)
        self.btn_seleccionar = Button(text='Seleccionar Fotos', background_color=(0.48,0.48,0.48,1), color=(1,1,1,1), size_hint_y=None, height=dp(50))
        self.btn_seleccionar.bind(on_press=self.seleccionar_fotos)
        root.add_widget(self.btn_seleccionar)
        self.lbl_contador = Label(text='0 fotos seleccionadas', font_size=dp(14), color=(0.4,0.4,0.4,1), size_hint_y=None, height=dp(30))
        root.add_widget(self.lbl_contador)
        self.btn_analizar = Button(text='Analizar', background_color=(0.48,0.48,0.48,1), color=(1,1,1,1), size_hint_y=None, height=dp(50))
        self.btn_analizar.bind(on_press=self.iniciar_analisis)
        root.add_widget(self.btn_analizar)
        self.scroll = ScrollView()
        self.contenedor_resultados = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        self.contenedor_resultados.bind(minimum_height=self.contenedor_resultados.setter('height'))
        self.scroll.add_widget(self.contenedor_resultados)
        root.add_widget(self.scroll)
        self.popup = None
        return root
    def seleccionar_fotos(self, instance):
        filechooser.open_file(multiple=True, on_selection=self.on_files_selected)
    def on_files_selected(self, selection):
        if selection:
            self.fotos_seleccionadas = selection
            self.lbl_contador.text = f'{len(selection)} fotos seleccionadas'
            self.lbl_contador.color = (0.1, 0.6, 0.1, 1)
            self.contenedor_resultados.clear_widgets()
            self.resultados_imagenes = []
    def iniciar_analisis(self, instance):
        if not self.fotos_seleccionadas:
            self.mostrar_popup("Error", "Primero selecciona al menos una foto.")
            return
        self.contenedor_resultados.clear_widgets()
        self.resultados_imagenes = []
        self.btn_analizar.disabled = True
        self.btn_seleccionar.disabled = True
        self.mostrar_popup_progreso()
        Clock.schedule_once(self.ejecutar_analisis, 0.1)
    def ejecutar_analisis(self, dt):
        total = len(self.fotos_seleccionadas)
        imagenes_pil = []
        for i, ruta in enumerate(self.fotos_seleccionadas):
            self.popup_content.children[0].text = f"Procesando imagen {i+1} de {total}..."
            self.popup_content.children[1].value = (i + 1) / total * 100
            colores, pcts, img_pil = analizar_imagen(ruta, self.n_colores)
            if colores is not None:
                nombre = os.path.basename(ruta)
                self.resultados_imagenes.append((nombre, colores, pcts, img_pil))
                imagenes_pil.append(img_pil)
        self.popup.dismiss()
        self.mostrar_resultados(imagenes_pil)
        self.btn_analizar.disabled = False
        self.btn_seleccionar.disabled = False
    def mostrar_resultados(self, imagenes_pil):
        contenedor = self.contenedor_resultados
        contenedor.clear_widgets()
        if not self.resultados_imagenes:
            contenedor.add_widget(Label(text="No se pudieron procesar las imágenes.", color=(0.8,0.2,0.2,1)))
            return
        if imagenes_pil:
            contenedor.add_widget(Label(text="PALETA GLOBAL", font_size=dp(16), bold=True, color=(0.2,0.2,0.2,1), size_hint_y=None, height=dp(30)))
            all_pixels = []
            for img in imagenes_pil:
                img_small = img.copy().resize((100, 100))
                all_pixels.append(np.array(img_small).reshape(-1, 3))
            all_pixels = np.vstack(all_pixels)
            colores_g, pcts_g = kmeans_rgb(all_pixels, self.n_colores)
            barra_global = ColorBarWidget(colores_g, pcts_g, size_hint=(1, 0.4))
            barra_global.height = dp(40)
            contenedor.add_widget(barra_global)
            txt_global = ""
            for i, (c, p) in enumerate(zip(colores_g, pcts_g)):
                hex_code = rgb_a_hex(c)
                txt_global += f"[b]{i+1}.[/b] RGB{tuple(c)}  [color={hex_code}][b]{hex_code}[/b][/color]  {p:.1f}%\n"
            lbl_global_info = Label(text=txt_global, markup=True, font_size=dp(12), color=(0.1,0.1,0.1,1), halign='left', valign='top', size_hint_y=None, height=dp(120))
            lbl_global_info.bind(size=lbl_global_info.setter('text_size'))
            contenedor.add_widget(lbl_global_info)
            contenedor.add_widget(Widget(size_hint_y=None, height=dp(10)))
        contenedor.add_widget(Label(text="Detalle por Foto", font_size=dp(16), bold=True, color=(0.2,0.2,0.2,1), size_hint_y=None, height=dp(30)))
        for nombre, colores, pcts, img_pil in self.resultados_imagenes:
            contenedor.add_widget(TarjetaResultado(nombre, colores, pcts, img_pil))
    def mostrar_popup_progreso(self):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        lbl = Label(text="Iniciando análisis...", color=(0.1,0.1,0.1,1))
        progress = ProgressBar(value=0, max=100)
        content.add_widget(lbl)
        content.add_widget(progress)
        self.popup_content = content
        self.popup = Popup(title='Procesando', content=content, size_hint=(0.8, 0.4))
        self.popup.open()
    def mostrar_popup(self, titulo, mensaje):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        content.add_widget(Label(text=mensaje, color=(0.1,0.1,0.1,1)))
        btn_cerrar = Button(text='OK', size_hint_y=None, height=dp(40), background_color=(0.48,0.48,0.48,1), color=(1,1,1,1))
        content.add_widget(btn_cerrar)
        popup = Popup(title=titulo, content=content, size_hint=(0.8, 0.3))
        btn_cerrar.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    PaletteApp().run()
