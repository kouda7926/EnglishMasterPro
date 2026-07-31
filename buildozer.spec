[app]

title = EnglishMaster Pro
package.name = englishmasterpro
package.domain = com.englishmasterpro

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = data/*

version = 3.0.0

requirements = python3,kivy,gTTS,Pillow,sdl2,SDL2_ttf,SDL2_image,android

orientation = portrait

fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.arch = arm64-v8a

# icon
# icon.filename = %(source.dir)s/icon.png

# presplash
# presplash.filename = %(source.dir)s/presplash.png

# list of services
# services = PushService:pyservice

# chmod 755
# chmod = 755

# p4a.branch =
# p4a.local_recipes =
# p4a.recipe_dir =

# log level
log_level = 2

# warn on root
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
