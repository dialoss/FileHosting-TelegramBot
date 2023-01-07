import emoji
import telebot
from telebot import types
import datetime

import database

me_id = None  # your telegram id
token = '***'  # tg token
admin_code = "***"  # a code for database access
caption_text = '''Mathicool - это игра для желающих повысить свои навыки в устном счете. 
Ознакомьтесь с основными техниками быстрого счета в уме, а затем отточите их в бесконечном режиме!'''

bot = telebot.TeleBot(token)

feedback = types.KeyboardButton("Оставить отзыв")
feedback_check = types.KeyboardButton("Посмотреть отзывы")
download = types.KeyboardButton("Скачать игру")
back = types.KeyboardButton("Назад")
upload_game = types.KeyboardButton("Обновить игру")
upload_photos = types.KeyboardButton("Обновить скриншоты")
finish = types.KeyboardButton("Подтвердить")
keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
keyboard_markup.add(feedback, feedback_check, download)
default_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
default_markup.add(back)
admin_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
admin_markup.add(feedback_check, upload_game, upload_photos, back)
file_update_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
file_update_markup.add(finish, back)

users = dict()
db = database.DB()


@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.chat.id
    group = []
    query = db.get_photos()
    for photo in query:
        group.append(types.InputMediaPhoto(photo['file_id']))

    bot.send_media_group(user_id, group)
    bot.send_message(user_id, caption_text, reply_markup=keyboard_markup)


@bot.message_handler(content_types=['document', 'photo'])
def get_file_id(msg):
    global apk_id, photos
    user_id = msg.chat.id
    if users.get(user_id) is None:
        users[user_id] = database.User(msg.from_user.first_name + f"({msg.from_user.id})")
    cur_user = users[user_id]

    if not cur_user.admin_enter:
        return

    if cur_user.updating_photos:
        file_id = msg.photo[0].file_id
        photos.append(file_id)
    elif cur_user.updating_game:
        apk_id = msg.document.file_id


@bot.message_handler(content_types=['text'])
def handle_input(msg):
    global admin_enter, photos, apk_id
    text = msg.text
    user_id = msg.chat.id
    if users.get(user_id) is None:
        users[user_id] = database.User(msg.from_user.first_name + f"({msg.from_user.id})")

    cur_user = users[user_id]

    if text == admin_code and not cur_user.admin_enter:
        bot.send_message(user_id, "Админ панель", reply_markup=admin_markup)
        cur_user.admin_enter = True
        return

    if cur_user.admin_enter:
        splitted = text.split(' ')
        if splitted[0] == "Удалить":
            db.remove(int(splitted[1]))
        elif text == "Посмотреть отзывы":
            rows = db.all_feedback()
            if len(rows) == 0:
                bot.send_message(user_id, emoji.emojize("Нет отзывов", language="alias"))
                return
            bot.send_message(user_id, f"Всего отзывов: {len(rows)}")
            for row in rows:
                bot.send_message(user_id, f"id({row['msgid']}) " + emoji.emojize(row['name'], language='alias') + " написал(а): " + emoji.emojize(row['text'], language='alias'))
        elif text == "Обновить игру":
            cur_user.updating_game = True
            bot.send_message(user_id, "Отправьте файл", reply_markup=file_update_markup)
        elif text == "Обновить скриншоты":
            cur_user.updating_photos = True
            bot.send_message(user_id, "Отправьте скриншоты по одному", reply_markup=file_update_markup)
        elif text == "Подтвердить":
            if cur_user.updating_photos:
                if len(photos) == 0:
                    bot.send_message(user_id, "Файлы не были добавлены")
                    return
                else:
                    bot.send_message(user_id, "Скриншоты успешно обновлены")
                    db.update_photos()
            if cur_user.updating_game:
                if apk_id == "":
                    bot.send_message(user_id, "Файл не был добавлен")
                    return
                else:
                    bot.send_message(user_id, "Игра успешно обновлена")
                    db.update_game()
            cur_user.updating_photos = False
            cur_user.updating_game = False
        elif text == "Назад":
            if cur_user.updating_photos or cur_user.updating_game:
                bot.send_message(user_id, "Назад", reply_markup=admin_markup)
                cur_user.updating_photos = False
                cur_user.updating_game = False
            else:
                bot.send_message(user_id, "Назад", reply_markup=keyboard_markup)
                cur_user.admin_enter = False
        return

    if text == "Назад":
        bot.send_message(user_id, "Назад", reply_markup=keyboard_markup)
        cur_user.reset()
        return

    if text == "Посмотреть отзывы":
        if cur_user.isTyping:
            return

        rows = db.all_feedback()
        if len(rows) == 0:
            bot.send_message(user_id, emoji.emojize("Нет отзывов. Оставьте первым :winking_face:", language='alias'))
            return
        bot.send_message(user_id, f"Всего отзывов: {len(rows)}")
        for row in rows:
            bot.send_message(user_id, f"{emoji.emojize(row['name'], language='alias')} оценивает игру: {row['mark']}/5\n{emoji.emojize(row['text'], language='alias')}")

        return

    if text == "Скачать игру":
        if cur_user.isTyping:
            return
        try:
            query = db.get_apk()
            bot.send_document(user_id, query[0]['file_id'])
        except:
            bot.send_message(user_id, "Произошла ошибка")
        return

    if text == "Оставить отзыв":
        if cur_user.isTyping:
            return
        bot.send_message(user_id, "Введите Ваше имя", reply_markup=default_markup)
        cur_user.isTyping = True
        return

    if cur_user.isTyping:
        if cur_user.username == '':
            text = emoji.demojize(text, language='alias')
            cur_user.username = text
            bot.send_message(user_id, "Напишите отзыв")
            return

        if cur_user.comment == '':
            if len(text) > 200:
                text = text[:200]
            text = emoji.demojize(text, language='alias')
            cur_user.comment = text
            bot.send_message(user_id, "Оцените игру (от 1 до 5)")
            return

        if cur_user.mark == 0:
            try:
                text = int(text)
            except:
                bot.send_message(user_id, "Введите только цифру!")
                return
            text = min(text, 5)
            text = max(text, 1)

            db.add_feedback(cur_user.username, cur_user.comment, text)
            date = datetime.datetime.fromtimestamp(msg.date).strftime('%Y-%m-%d %H:%M:%S')
            name = cur_user.fullname
            bot.send_message(me_id, f"{emoji.emojize(name, language='alias')} ({text}/5) отправил сообщение {emoji.emojize(cur_user.comment, language='alias')} в {date}")
            bot.send_message(user_id, "Отзыв успешно отправлен", reply_markup=keyboard_markup)
            cur_user.reset()
            return

    bot.send_message(user_id, "Не понимаю команду")


if __name__ == '__main__':
    bot.polling(none_stop=True)