"""Numerar Fotos — app Android (Kivy) para numerar fotos em sequência."""
import os
import threading
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform

import numerador

ANDROID = platform == "android"
RAIZ = "/storage/emulated/0" if ANDROID else os.path.expanduser("~")
SAIDA_BASE = os.path.join(RAIZ, "Pictures", "FotosNumeradas")

KV = """
#:import POSICOES numerador.POSICOES

<Rotulo@Label>:
    color: 0.75, 0.80, 0.90, 1
    font_size: '15sp'
    size_hint_y: None
    height: '26dp'
    text_size: self.width, None
    halign: 'left'

<Campo@TextInput>:
    size_hint_y: None
    height: '46dp'
    font_size: '17sp'
    multiline: False
    padding: '12dp', '12dp'
    background_color: 0.16, 0.19, 0.26, 1
    foreground_color: 1, 1, 1, 1
    cursor_color: 0.35, 0.65, 1, 1

<Escolha@Spinner>:
    size_hint_y: None
    height: '46dp'
    font_size: '16sp'
    background_normal: ''
    background_color: 0.16, 0.19, 0.26, 1
    text_size: self.width - dp(24), None
    shorten: True
    halign: 'left'

<Tela>:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 0.08, 0.10, 0.15, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        size_hint_y: None
        height: '64dp'
        padding: '18dp', '10dp'
        canvas.before:
            Color:
                rgba: 0.13, 0.42, 0.90, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: 'Numerar Fotos'
            bold: True
            font_size: '22sp'
            text_size: self.size
            halign: 'left'
            valign: 'middle'

    ScrollView:
        do_scroll_x: False
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            padding: '18dp'
            spacing: '8dp'

            Rotulo:
                text: '1. Pasta das fotos'
                bold: True
                color: 1, 1, 1, 1
            Escolha:
                id: pasta
                text: root.pasta_escolhida or 'Toque para escolher'
                values: root.pastas
                on_text: root.ao_escolher_pasta(self.text)
            Campo:
                id: caminho
                hint_text: 'ou digite o caminho da pasta'
                font_size: '14sp'
                on_text_validate: root.ao_digitar_caminho(self.text)
            Rotulo:
                text: root.info_pasta
                color: 0.45, 0.85, 0.55, 1

            Widget:
                size_hint_y: None
                height: '6dp'
            Rotulo:
                text: '2. Como numerar'
                bold: True
                color: 1, 1, 1, 1
            GridLayout:
                cols: 2
                size_hint_y: None
                height: self.minimum_height
                spacing: '10dp'
                Rotulo:
                    text: 'Prefixo do nome'
                Rotulo:
                    text: 'Começar no número'
                Campo:
                    id: prefixo
                    text: 'Foto'
                Campo:
                    id: inicio
                    text: '1'
                    input_filter: 'int'
                Rotulo:
                    text: 'Dígitos (001 = 3)'
                Rotulo:
                    text: 'Ordem'
                Campo:
                    id: digitos
                    text: '3'
                    input_filter: 'int'
                Escolha:
                    id: ordem
                    text: 'Data da foto'
                    values: ['Data da foto', 'Nome do arquivo']
            Rotulo:
                text: 'Exemplo: ' + root.exemplo(prefixo.text, inicio.text, digitos.text)
                color: 0.55, 0.70, 1, 1

            Widget:
                size_hint_y: None
                height: '6dp'
            BoxLayout:
                size_hint_y: None
                height: '46dp'
                Label:
                    text: '3. Escrever o número na foto'
                    bold: True
                    font_size: '15sp'
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
                Switch:
                    id: gravar
                    active: True
                    size_hint_x: None
                    width: '90dp'
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height if gravar.active else 0
                opacity: 1 if gravar.active else 0
                disabled: not gravar.active
                spacing: '6dp'
                Rotulo:
                    text: 'Posição do número'
                Escolha:
                    id: posicao
                    text: POSICOES[0]
                    values: POSICOES
                Rotulo:
                    text: 'Tamanho do número: %d%%' % tamanho.value
                Slider:
                    id: tamanho
                    min: 3
                    max: 20
                    step: 1
                    value: 8
                    size_hint_y: None
                    height: '40dp'

            Widget:
                size_hint_y: None
                height: '10dp'
            Button:
                text: 'Numerando...' if root.ocupado else 'NUMERAR FOTOS'
                disabled: root.ocupado or root.qtd_fotos == 0
                size_hint_y: None
                height: '58dp'
                font_size: '18sp'
                bold: True
                background_normal: ''
                background_color: (0.13, 0.42, 0.90, 1) if not self.disabled else (0.25, 0.28, 0.35, 1)
                on_release: root.iniciar()
            ProgressBar:
                max: 100
                value: root.progresso
                size_hint_y: None
                height: '20dp'
            Label:
                text: root.mensagem
                markup: True
                font_size: '15sp'
                color: 0.9, 0.92, 0.96, 1
                size_hint_y: None
                text_size: self.width, None
                height: self.texture_size[1] + dp(10)
            Label:
                text: 'As fotos originais não são alteradas. As cópias numeradas ficam em Imagens/FotosNumeradas e aparecem na Galeria.'
                font_size: '12sp'
                color: 0.55, 0.60, 0.70, 1
                size_hint_y: None
                text_size: self.width, None
                height: self.texture_size[1] + dp(10)
"""


class Tela(BoxLayout):
    pastas = ListProperty()
    pasta_escolhida = StringProperty("")
    info_pasta = StringProperty("")
    qtd_fotos = NumericProperty(0)
    ocupado = BooleanProperty(False)
    progresso = NumericProperty(0)
    mensagem = StringProperty("")

    def __init__(self, **kw):
        super().__init__(**kw)
        self._mapa = {}
        self._pasta_atual = ""

    # ---------- pastas ----------
    def atualizar_pastas(self):
        candidatas = []
        for base in ("DCIM", "Pictures", "Download", "Documents"):
            p = os.path.join(RAIZ, base)
            if os.path.isdir(p):
                candidatas.append(p)
                try:
                    for sub in sorted(os.listdir(p)):
                        sp = os.path.join(p, sub)
                        if os.path.isdir(sp) and not sub.startswith("."):
                            candidatas.append(sp)
                except OSError:
                    pass
        wpp = os.path.join(RAIZ, "Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images")
        if os.path.isdir(wpp):
            candidatas.append(wpp)

        self._mapa = {}
        for p in candidatas:
            n = len(numerador.listar_fotos(p))
            if n:
                rotulo = f"{os.path.relpath(p, RAIZ)}  ({n} fotos)"
                self._mapa[rotulo] = p
        self.pastas = list(self._mapa.keys())
        if not self.pastas:
            self.info_pasta = "Nenhuma pasta com fotos encontrada. Digite o caminho acima."
        # pré-seleciona a câmera
        for r in self.pastas:
            if r.startswith(os.path.join("DCIM", "Camera")):
                self.ids.pasta.text = r
                break

    def ao_escolher_pasta(self, rotulo):
        if rotulo in self._mapa:
            self._definir_pasta(self._mapa[rotulo])

    def ao_digitar_caminho(self, texto):
        texto = texto.strip()
        if texto and not os.path.isabs(texto):
            texto = os.path.join(RAIZ, texto)
        if os.path.isdir(texto):
            self._definir_pasta(texto)
        else:
            self.qtd_fotos = 0
            self.info_pasta = "Pasta não encontrada."

    def _definir_pasta(self, caminho):
        self._pasta_atual = caminho
        self.qtd_fotos = len(numerador.listar_fotos(caminho))
        self.info_pasta = f"{self.qtd_fotos} fotos encontradas"

    # ---------- utilidades ----------
    @staticmethod
    def _int(txt, padrao):
        try:
            return max(0, int(txt))
        except (TypeError, ValueError):
            return padrao

    def exemplo(self, prefixo, inicio, digitos):
        n = str(self._int(inicio, 1)).zfill(min(self._int(digitos, 3), 8))
        p = prefixo.strip()
        return f"{p}_{n}.jpg" if p else f"{n}.jpg"

    # ---------- execução ----------
    def iniciar(self):
        if self.ocupado or not self._pasta_atual:
            return
        prefixo = "".join(c for c in self.ids.prefixo.text.strip() if c not in '\\/:*?"<>|')
        opcoes = dict(
            prefixo=prefixo,
            inicio=self._int(self.ids.inicio.text, 1),
            digitos=min(self._int(self.ids.digitos.text, 3), 8),
            gravar_numero=self.ids.gravar.active,
            posicao=self.ids.posicao.text,
            tamanho_pct=int(self.ids.tamanho.value),
        )
        ordem = self.ids.ordem.text
        nome_pasta = os.path.basename(self._pasta_atual.rstrip("/")) or "fotos"
        saida = os.path.join(SAIDA_BASE, f"{nome_pasta}_{datetime.now():%Y-%m-%d_%H%M%S}")

        self.ocupado = True
        self.progresso = 0
        self.mensagem = "Organizando as fotos..."
        threading.Thread(target=self._trabalho, args=(ordem, saida, opcoes), daemon=True).start()

    def _trabalho(self, ordem, saida, opcoes):
        try:
            fotos = numerador.ordenar(numerador.listar_fotos(self._pasta_atual), ordem)
            ok, erros = numerador.numerar(fotos, saida, progresso=self._progresso_thread, **opcoes)
            escanear_galeria(ok)
            msg = f"[b]Pronto![/b] {len(ok)} fotos numeradas.\nSalvas em: {os.path.relpath(saida, RAIZ)}"
            if erros:
                msg += f"\n[color=ff8080]{len(erros)} não puderam ser processadas "
                msg += f"(ex.: {erros[0][0]}).[/color]"
        except Exception as e:
            msg = f"[color=ff8080]Erro: {e}[/color]"
        Clock.schedule_once(lambda dt: self._fim(msg))

    def _progresso_thread(self, feito, total):
        def atualizar(dt):
            self.progresso = 100 * feito / max(total, 1)
            self.mensagem = f"Numerando {feito} de {total}..."
        Clock.schedule_once(atualizar)

    def _fim(self, msg):
        self.ocupado = False
        self.progresso = 100
        self.mensagem = msg


def escanear_galeria(caminhos):
    """Avisa o Android para mostrar as novas fotos na Galeria."""
    if not ANDROID or not caminhos:
        return
    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Scanner = autoclass("android.media.MediaScannerConnection")
        Scanner.scanFile(PythonActivity.mActivity, caminhos, None, None)
    except Exception:
        pass


class NumerarFotosApp(App):
    title = "Numerar Fotos"
    icon = "icon.png"

    def build(self):
        Window.clearcolor = (0.08, 0.10, 0.15, 1)
        Builder.load_string(KV)
        self.tela = Tela()
        return self.tela

    def on_start(self):
        if ANDROID:
            from android.permissions import request_permissions
            request_permissions(
                [
                    "android.permission.READ_MEDIA_IMAGES",
                    "android.permission.READ_EXTERNAL_STORAGE",
                    "android.permission.WRITE_EXTERNAL_STORAGE",
                ],
                lambda *a: Clock.schedule_once(lambda dt: self.tela.atualizar_pastas()),
            )
        else:
            self.tela.atualizar_pastas()

    def on_resume(self):
        self.tela.atualizar_pastas()


if __name__ == "__main__":
    NumerarFotosApp().run()
