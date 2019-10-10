# пример простого консольного перводчика с английского
# на русский и с русского на английский с автоматическим
# определением языка исходного текста

import requests
from translator import Translator

LANGS = {'ru': 'en', 'en': 'ru'}

with open('key_api.txt', encoding='utf-8') as f:
	APIkey = f.read()
t = Translator(APIkey)

text = None
while True:
	text = None
	while not text:
		text = input('> ').strip()
	code, to_lang = t.detect_lang(text, hint=list(LANGS))
	code, text = t.translate(text, LANGS[to_lang])
	print(text)
	print('Переведено сервисом "Яндекс.Перевдчик" http://translate.yandex.ru \n')