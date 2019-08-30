import os
import json

try:
	import requests
except ImportError:
	print('please install "requests" for continue...')
	exit(1)

'''
возможные коды состояний:

-1  Ошибка подключения,
    в большинстве это ошибка requests.exceptions.ConnectionError
200	Операция выполнена успешно
401	Неправильный API-ключ
402	API-ключ заблокирован
404	Превышено суточное ограничение на объем переведенного текста
413	Превышен максимально допустимый размер текста
422	Текст не может быть переведен
501	Заданное направление перевода не поддерживается
'''

class Translator:
	'''
	Класс для работы с API Яндекс.Переводчика
	t = Translator('my api-key')
	'''
	uri = 'https://translate.yandex.net/api/v1.5/tr.json/'
	token = None

	def __init__(self, token):
		self.token = token

	@staticmethod
	def _get_request(*args, **kwargs):
		try:
			response = requests.get(*args, **kwargs)
			response.close() # нужно ли?
			return (True, json.loads(response.text))
		except requests.exceptions.RequestException: # 99% ConnectionError
			return (False, 'request exception')
		# except requests.exceptions:
		# 	return (False, 'connection error')

	@staticmethod
	def _post_request(*args, **kwargs):
		try:
			response = requests.post(*args, **kwargs)
			response.close() # нужно ли?
			return (True, json.loads(response.text))
		except requests.exceptions.RequestException:
			return (False, 'request exception')

	def get_langs(self, dirs=True, description=False, ui='ru'):
		'''
		:dirs: если True будет возвращет список пары с какой на какой язык
		возможно осуществить перевод в формате
		['az-ru', 'be-bg', ..., 'ru-en', 'en-ru', ...]
		:description: если True будет возвращен словарь описаний кодов
		языков в формате {'af': Африканский, ..., 'be': Белорусский, ...}
		:ui: язык описания/расшифровки языковых кодов в словаре :langs:
		Возвращает:
		get_langs(dirs=True) -> (code, dirs)
		get_langs(dirs=True, description=True, [ui='ru']) ->
			(200, dirs, description)
		get_langs(dirs=False, description=True, [ui='ru']) ->
			(200, description)
		В случае ошибки подключения подключения -> (-1, msg)
		Если токен/ключ недействительный -> (401, msg)
		Если токен заблокирован -> (402, msg)
		'''
		success, answer = self._get_request(self.uri+'getLangs',
							params=dict(key=self.token, ui=ui))
		if not success:
			return (-1, 'connection error')
		code = answer.get('code')
		if code:
			return (code, answer.get('message'))
		code = 200
		if dirs and description:
			return (code, answer.get('dirs'), answer.get('langs'))
		elif dirs:
			return (code, answer.get('dirs'))
		else:
			return (code, answer.get('langs'))

	def detect_lang(self, text, hint=None):
		'''
		:text: текст, язык которого нужно определить
		:hint: список предполагаемых языков текста в формате ['fr', 'en', ...]
		Возвращает код овтета и список языков текста в формате ['en']
		или код ответа и одиночный элемент
		'''
		# 200; 401 - неправильный ключ, 402-ключ заблочен, 404 - превышено
		# суточное ограничение на объем переводимого текста
		if hint:
			if type(hint) is str:
				pass
			elif len(hint) > 1:
				hint = ','.join(hint)
			else:
				hint = hint[0]
			success, answer = self._post_request(self.uri+'detect',
								params=dict(key=self.token, hint=hint),
								data=dict(text=text[:240]))
		else:
			success, answer = self._post_request(self.uri+'detect',
								params=dict(key=self.token),
								data=dict(text=text[:240]))
		if not success:
			return (-1, 'connection error')
		code = answer.get('code')
		if code == 200:
			return (code, answer.get('lang'))
		return (code, answer.get('message'))

	def translate(self, text, lang, format='plain', options=None):
		'''
		:text: текст, который требуется перевести
		:lang: языковая пара с какой на какой язык нужно перевести.
			строка в формате: 'en-ru' или 'uk-fr' или др. пара
			или кортеж в формате: ('en', 'ru')
			При :options: == 1 если в параметре :lang: указать только язык,
			на который нужно перевести текст:   'ru'
			то язык текста будет определен автоматически
		:format: формат текста может быть 'plain' - текст без разметки или
			'html' - текст в формате html
		:options: в настоящее время (v1.5 API переводчика) есть только одна
			опция, которая соответствует значению '1', которая позволяет
			включить в ответ автоматически определенный язык переводимого
			текста. Если в :lang: указана языковая пара, то указанный язык
			текста будет иметь больше приоритет, но код автоматически
			определенного языка  исходного текста будет включаться в ответ.
		Максимальный объем передаваемого текста - 10к символов.
		Возвращает:
		translate(text, lang="from-to", options=None) -> (200, <переведенный_текст>)
		translate(text, lang="from-to", options='1') ->
			(200, <переведенный_текст>, <код_авто_опр_языка>)
		translate(text, lang="to", options='1') ->
			(200, <переведенный_текст>, <код_авто_опр_языка>)
		'''
		# в содержимом запроса на перевод может быть несколько параметров text:
		# https://translate.yandex.net/api/v1.5/tr/translate?key=my_token&lang=en-ru&text=my%20text&text=text%20two&text=text%20three
		# сырой ответ:
		#'<?xml version="1.0" encoding="utf-8"?>\n
		# <Translation code="200" lang="en-ru">
		# <text>текст</text>
		# <text>текст два</text>
		# <text>текст Три</text>
		# </Translation>'

		if type(lang) is not str: # list or tuple
			lang = '-'.join(lang)
		if options:
			success, answer = self._post_request(self.uri+'translate',
							params=dict(key=self.token, lang=lang, options=options),
							data=dict(text=text))
		else:
			success, answer = self._post_request(self.uri+'translate',
							params=dict(key=self.token, lang=lang),
							data=dict(text=text))
		if not success:
			return (-1, 'connection error')
		code = answer.get('code')
		if code == 200:
			if options:
				return (code, answer['text'][0], answer.get('lang'))
			else:
				return (code, answer['text'][0])
		return (code, answer.get('message'))
