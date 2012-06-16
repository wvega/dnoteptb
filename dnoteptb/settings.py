# coding: utf-8
from ragendja.settings_post import settings

settings.add_app_media('combined-%(LANGUAGE_CODE)s.js',
    'dnoteptb/js/humanize.js',
    'dnoteptb/js/scripts.js',
)
settings.add_app_media('combined-%(LANGUAGE_DIR)s.css',
    'dnoteptb/css/style.css',
)