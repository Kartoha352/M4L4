from logic import DB_Manager
from config import *
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telebot import types
import json

bot = TeleBot(TOKEN)

# Функция для генерации инлайн-клавиатуры
def gen_inline_markup(rows, data = None):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    if data == None:
        for row in rows:
            markup.add(InlineKeyboardButton(row, callback_data=row))
    else:
        for row, i in zip(rows, data):
            markup.add(InlineKeyboardButton(row, callback_data=i))
    return markup


# Функция для генерации обычной клавиатуры
def gen_markup(rows):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 1
    for row in rows:
        markup.add(KeyboardButton(row))
#    markup.add(KeyboardButton(cancel_button))
    return markup

def search_function(message, search, bot):
    if search == "Студия":
        result = manager.search_anime("Studio", message.text.lower())
        if result == []:
            text = "Я не смог найти аниме выпущенное такой студией. Попробуйте заново."
            bot.send_message(message.chat.id,text)
        else:
            text = f"Вот список первых 10 аниме которые я нашёл по твоему запросу:\nСтудия: {message.text}\n\n"
            text += "\n".join([f"{i[0]}. {i[1]}" for i in result])
            bot.send_message(message.chat.id, text)
    elif search == "Директор":
        result = manager.search_anime("staff", message.text.lower())
        if result == []:
            text = "Я не смог найти аниме с таким директором. Попробуйте заново."
            bot.send_message(message.chat.id,text)
        else:
            text = f"Вот список первых 10 аниме которые я нашёл по твоему запросу:\nДиректор: {message.text}\n\n"
            text += "\n".join([f"{i[0]}. {i[1]}" for i in result])
            bot.send_message(message.chat.id, text)

    elif search == "Теги":
        result = manager.search_anime("Tags", message.text.lower())
        if result == []:
            text = "Я не смог найти аниме с таким Тегом. Попробуйте заново."
            bot.send_message(message.chat.id,text)
        else:
            text = f"Вот список первых 10 аниме которые я нашёл по твоему запросу:\nТеги: {message.text}\n\n"
            text += "\n".join([f"{i[0]}. {i[1]}" for i in result])
            bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['start']) 
def start_command(message):
    bot.send_message(message.chat.id, """Привет! Я бот-помощник по аниме.
Помогу тебе найти любое аниме по Тегу, студии или директору!) 
""")

@bot.message_handler(commands=['search'])
def start_command(message):
    bot.send_message(message.chat.id, "Выбери по какому критерию искать аниме!",reply_markup=gen_inline_markup(("Теги","Студия", "Директор"), ("search:Теги","search:Студия","search:Директор")))


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if "search" in call.data:

        text = f"Выбранная критерия: *{call.data.split(':')[1]}*\nВведите соответствующие данные для поиска на английском."
        if "Теги" in call.data:
            text += "\nЕсли нужно, то укажите несколько Тегов через запятую."
        bot.edit_message_text(text,call.message.chat.id,call.message.id, reply_markup=None, parse_mode="Markdown")
        bot.register_next_step_handler(call.message, search_function, search=call.data.split(':')[1], bot=bot)
    elif "anime_list" in call.data:
        anime_id = call.message.text.split("\n")[2].split(" — ")[1]
        manager.add_anime_to_list(call.from_user.id, anime_id)
        bot.edit_message_reply_markup(call.message.chat.id,call.message.id, reply_markup=gen_inline_markup(("Уже в списке",)))


@bot.message_handler(commands=['info']) 
def info_command(message):
    args = message.text.split()[1:]
    if len(args) > 0:
        name = ' '.join(args)
        result = manager.search_anime("Rank", name)
        if len(result) == 0:
            result = manager.search_anime("Name", name)
        if len(result) == 0:
            bot.send_message(message.chat.id, f"Я не нашёл аниме с названием *{name}*.\nПроверьте, правильно ли вы написали название.", parse_mode="Markdown")
        elif len(result) == 1:
            result = result[0]
            text = f"Вот аниме по запросу *{name}*.\n\n"
            keys = ["Номер в системе","Название","Название в оригинале","Тип","Кол-во эпизодов","Студия","Сезон выпуска","теги","рейтинг","Год выпуска","Год заверщения","Описание","Предупреждение","Манга","Аниме","Озвучка","Сотрудники"]
            for i in zip(result,keys):
                text += "*" + i[1] + "* — " + str(i[0]) + "\n"
            if manager.anime_exists_for_user(message.from_user.id, result[0]):
                bot.send_message(message.chat.id, text, parse_mode="Markdown",reply_markup=gen_inline_markup(("Уже в списке",)))
            else:
                bot.send_message(message.chat.id, text, parse_mode="Markdown",reply_markup=gen_inline_markup(("Добавить в мой список",), ("anime_list:Добавить в мой список",)))
        else:
            text = f"Вот {'Первые ' if len(result) == 10 else ''}*{len(result)}* аниме которые я нашёл по запросу *{name}*.\n\n"
            for anime in result:
                text += f"*{anime[0]}*. `{anime[1]}`\n"
            bot.send_message(message.chat.id, text, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, f"Вы не указали название/номер аниме для поиска.", parse_mode="Markdown")

@bot.message_handler(commands=['my_list']) 
def my_list_command(message):
    anime_list = manager.get_anime_list(message.from_user.id)[0]
    anime_list = json.loads(anime_list[0])
    if len(anime_list) > 0:
        text = "Список аниме добавленных в ваш список:\n\n"
        for anime_id in anime_list:
            anime = manager.search_anime("Rank", int(anime_id))[0]
            anime_name = "`" + anime[1] + "`"
            text += f"*{anime_id}*. {anime_name}\n"

        bot.send_message(message.chat.id, text, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, f"Вы ещё не добавили аниме в свой список.", parse_mode="Markdown")


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    bot.infinity_polling()