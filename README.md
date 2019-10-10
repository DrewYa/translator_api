# API Яндекс.Переводчика
Модуль содержит класс для работы с и так легким в освоении API переводчика от Яндекс

Для работы требуется наличие библиотеки __request__:
```python -m pip install requests```

Также потребуется __API-ключ__, который можно бесплатно получить [```здесь```](https://yandex.ru/dev/translate/doc/dg/concepts/api-keys-docpage/)

Полную __документацию по API__ можно найти [```тут```](https://yandex.ru/dev/translate/doc/dg/concepts/about-docpage/)


Согласно лицензии Яндекс.Переводчика, под результатом перевода должен быть указан текст _Переведено сервисом "Яндекс.Перевдчик"_ со ссылкой на страницу переводчика http://translate.yandex.ru

__Подробнее__ [```вот здесь```](https://yandex.ru/dev/translate/doc/dg/concepts/design-requirements-docpage/)

Простой пример создания простого переводчика - __translate.py__ (для работы требуется записать API-ключ в key_api.txt)