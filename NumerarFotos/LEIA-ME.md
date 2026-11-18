# Numerar Fotos — app Android em Python (Kivy)

Numera fotos em sequência no Samsung S23 (ou outro Android 8+).

## O que o app faz
- Escolhe uma pasta (Câmera, Capturas de tela, Downloads, WhatsApp, etc.)
- Ordena por **data em que a foto foi tirada** ou por **nome do arquivo**
- Cria cópias com nomes em sequência: `Foto_001.jpg`, `Foto_002.jpg`…
  (prefixo, número inicial e quantidade de dígitos ajustáveis)
- Opcional: **escreve o número sobre a foto** (canto e tamanho ajustáveis)
- As originais **não são alteradas**. As cópias ficam em
  `Imagens/FotosNumeradas/<pasta>_<data>` e aparecem na Galeria.

## Como gerar o APK (grátis, sem instalar nada no PC)
1. Crie uma conta em https://github.com (se não tiver).
2. Clique em **New repository** → nome `numerar-fotos` → **Public** → Create.
3. Na página do repositório, clique em **uploading an existing file** e
   arraste **todo o conteúdo** desta pasta (inclusive a pasta `.github`).
   > Dica: no Windows/Mac a pasta `.github` pode estar oculta. Se o upload
   > não levar ela, crie pelo site: **Add file → Create new file**, nome
   > `.github/workflows/gerar-apk.yml` e cole o conteúdo do arquivo.
4. Clique em **Commit changes**. A compilação começa sozinha
   (aba **Actions**). Leva ~15–25 min na primeira vez.
5. Quando ficar verde ✅, abra **Releases** (lado direito da página do
   repositório) **no celular** e toque em `NumerarFotos.apk`.

## Instalar no S23
1. Abra o APK baixado (Meus Arquivos → Downloads).
2. Se aparecer aviso, toque em **Configurações → Permitir desta fonte**.
   O Play Protect pode avisar que o app é desconhecido: toque em
   **Mais detalhes → Instalar mesmo assim**.
3. Abra **Numerar Fotos** e permita o acesso às fotos.

## Compilar no próprio PC (alternativa, Linux/WSL)
```
pip install buildozer "cython<3.1"
buildozer android debug     # APK sai em bin/
```

## Arquivos
- `main.py` – interface (Kivy)
- `numerador.py` – lógica de ordenar, renomear e carimbar (Pillow)
- `buildozer.spec` – configuração do Android
- `icon.png`, `presplash.png`, `fonte.ttf` – ícone, abertura e fonte do número
- `.github/workflows/gerar-apk.yml` – receita que gera o APK no GitHub
