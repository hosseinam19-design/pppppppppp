[app]
title = Dovam Samen Card
package.name = dovamsamencard
package.domain = ir.dovamsamen
source.dir = .
source.include_exts = py,png,jpg,jpeg,webp,ttf,json
source.exclude_dirs = .git,.github,.buildozer,bin,cards,__pycache__
version = 1.0.1
requirements = python3==3.12.13,kivy==2.3.0,pillow==10.4.0,arabic-reshaper==3.0.0,python-bidi==0.6.6,qrcode==8.2
orientation = landscape
fullscreen = 0
android.api = 35
android.minapi = 23
android.ndk = 28c
android.archs = arm64-v8a,armeabi-v7a
android.permissions = READ_MEDIA_IMAGES
android.allow_backup = True
android.uses_cleartext_traffic = False
android.debug_artifact = apk
icon.filename = %(source.dir)s/assets/davam_logo_transparent.png

# IMPORTANT:
# Use the stable python-for-android master branch with Python 3.12.
# The previous build accidentally used p4a develop/Python 3.14 with ndk-api 23,
# which caused preadv/pwritev compilation errors.
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
