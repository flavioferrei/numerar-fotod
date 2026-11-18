[app]
title = Numerar Fotos
package.name = numerarfotos
package.domain = br.app
source.dir = .
source.include_exts = py,png,ttf
source.exclude_dirs = bin,.buildozer,.github
version = 1.0
requirements = python3,kivy==2.3.1,pillow,pyjnius,android
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png
android.presplash_color = #141A26
orientation = portrait
fullscreen = 0

android.permissions = READ_MEDIA_IMAGES, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
android.api = 34
android.minapi = 26
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True
android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 0
