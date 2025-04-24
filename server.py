# импортируем библиотеки
from flask import Flask, request, jsonify
import logging
# библиотека, которая нам понадобится для работы с JSON 
import json
# создаем приложение 
app = Flask(__name__)
# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)
# Создадим словарь для хранения подсказок пользователя
sessionStorage = {}

@app.route('/post', methods=['POST'])
# Функция получает тело запроса и возвращает ответ.
def main():
    logging.info('Request: %r', request.json)
    # Начинаем формировать ответ, согласно документации
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    # Отправляем request.json и response в функцию handle_dialog
    handle_dialog(request.json, response)
    logging.info('Response: %r', response)
    # Преобразовываем в JSON и возвращаем
    return jsonify(response)

def handle_dialog(req, res):
    user_id = req['session']['user_id']
    
    # Если новая сессия
    if req['session']['new']:
        # Инициализируем сессию и поприветствуем пользователя
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        # Заполняем текст ответа с инструкцией по взаимодействию
        res['response']['text'] = 'Привет! Я навык "Продавец слонов". Я могу убедить вас купить слона. Просто скажите что-нибудь, и я постараюсь вас уговорить!'
        # Получим подсказки
        res['response']['buttons'] = get_suggests(user_id)
        return
    
    # Обрабатываем команды помощи
    if req['request']['original_utterance'].lower() in ['помощь', 'что ты умеешь', 'что ты умеешь?']:
        res['response']['text'] = 'Я навык "Продавец слонов". Моя задача - убедить вас купить слона! Вы можете соглашаться или отказываться, а я буду пытаться вас уговорить. Если вы согласитесь (скажете "ладно", "куплю", "хорошо" или "покупаю"), я подскажу, где можно найти слона.'
        res['response']['buttons'] = get_suggests(user_id)
        return
    
    # Обрабатываем согласие пользователя
    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо'
    ]:
        # Пользователь согласился, прощаемся.
        res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = True
        return
        
    # Если нет, то убеждаем его купить слона!
    res['response']['text'] = 'Все говорят "%s", а ты купи слона!' % (
        req['request']['original_utterance']
    )
    res['response']['buttons'] = get_suggests(user_id)

# Функция возвращает подсказки для ответа
def get_suggests(user_id):
    session = sessionStorage[user_id]
    # Выбираем две первые подсказки из массива
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]
    # Убираем первую подсказку, чтобы подсказки менялись каждый раз
    session['suggests'] = session['suggests'][1:]
    # Добавляем "Помощь" в качестве постоянной подсказки
    suggests.append({
        "title": "Что ты умеешь?",
        "hide": True
    })
    # Если осталась только одна подсказка, предлагаем подсказку со ссылкой
    if len(suggests) < 3:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })
    sessionStorage[user_id] = session
    return suggests

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
