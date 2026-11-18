"""Lógica de numeração de fotos (independente da interface)."""
import os
import shutil
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont, ImageOps

EXTENSOES = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".bmp")
FONTE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonte.ttf")
POSICOES = ["Inferior direito", "Inferior esquerdo", "Superior direito", "Superior esquerdo"]


def listar_fotos(pasta):
    """Lista as fotos de uma pasta (sem subpastas)."""
    try:
        nomes = os.listdir(pasta)
    except OSError:
        return []
    fotos = []
    for n in nomes:
        caminho = os.path.join(pasta, n)
        if n.lower().endswith(EXTENSOES) and not n.startswith(".") and os.path.isfile(caminho):
            fotos.append(caminho)
    return fotos


def data_da_foto(caminho):
    """Data em que a foto foi tirada (EXIF); se não houver, data do arquivo."""
    try:
        with Image.open(caminho) as img:
            exif = img.getexif()
            valor = exif.get_ifd(0x8769).get(36867) or exif.get(306)
            if valor:
                return datetime.strptime(str(valor).strip()[:19], "%Y:%m:%d %H:%M:%S").timestamp()
    except Exception:
        pass
    return os.path.getmtime(caminho)


def ordenar(fotos, criterio):
    if criterio == "Nome do arquivo":
        return sorted(fotos, key=lambda c: os.path.basename(c).lower())
    return sorted(fotos, key=lambda c: (data_da_foto(c), os.path.basename(c).lower()))


def carimbar(origem, destino, texto, posicao, tamanho_pct):
    """Grava o número sobre a foto, num selo escuro arredondado."""
    with Image.open(origem) as img:
        img = ImageOps.exif_transpose(img)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        base = img.convert("RGBA")

    w, h = base.size
    tam_fonte = max(14, int(min(w, h) * tamanho_pct / 100))
    try:
        fonte = ImageFont.truetype(FONTE, tam_fonte)
    except OSError:
        fonte = ImageFont.load_default()

    camada = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    x0, y0, x1, y1 = d.textbbox((0, 0), texto, font=fonte)
    tw, th = x1 - x0, y1 - y0
    pad = int(tam_fonte * 0.35)
    margem = int(min(w, h) * 0.03)
    bw, bh = tw + 2 * pad, th + 2 * pad

    bx = w - bw - margem if "direito" in posicao else margem
    by = h - bh - margem if "Inferior" in posicao else margem

    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=int(pad * 0.9), fill=(0, 0, 0, 170))
    d.text((bx + pad - x0, by + pad - y0), texto, font=fonte, fill=(255, 255, 255, 255))

    final = Image.alpha_composite(base, camada)
    ext = os.path.splitext(destino)[1].lower()
    if ext in (".jpg", ".jpeg"):
        final.convert("RGB").save(destino, "JPEG", quality=95)
    elif ext == ".webp":
        final.save(destino, "WEBP", quality=95)
    else:
        final.save(destino, "PNG")


def numerar(fotos, pasta_saida, prefixo="Foto", inicio=1, digitos=3,
            gravar_numero=True, posicao=POSICOES[0], tamanho_pct=8,
            progresso=None):
    """Cria cópias numeradas em pasta_saida. Retorna (sucessos, erros)."""
    os.makedirs(pasta_saida, exist_ok=True)
    ok, erros = [], []
    total = len(fotos)
    for i, origem in enumerate(fotos):
        numero = str(inicio + i).zfill(digitos)
        ext = os.path.splitext(origem)[1].lower()
        if gravar_numero and ext in (".heic", ".bmp"):
            ext = ".jpg"  # formatos que convertemos ao carimbar
        nome = f"{prefixo}_{numero}{ext}" if prefixo else f"{numero}{ext}"
        destino = os.path.join(pasta_saida, nome)
        try:
            if gravar_numero:
                carimbar(origem, destino, numero, posicao, tamanho_pct)
            else:
                shutil.copy2(origem, destino)
            ok.append(destino)
        except Exception as e:
            erros.append((os.path.basename(origem), str(e)))
        if progresso:
            progresso(i + 1, total)
    return ok, erros
