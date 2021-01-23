import telebot
import langdetect
import nltk

from bot_info import token

bot = telebot.TeleBot(token)

users_texts, last_texts = {}, {}

keyboard1_names = (
    'Текст', 'Кількість символів', 'Визначити мову',
    'Кількість символів без пробілів', 'Перевести у верхній регістр',
    'Перевести у нижній регістр', 'Розділити на речення'
)
keyboard2_names = ('Повернути попередній текст', 'Продовжити')

keyboard1 = telebot.types.ReplyKeyboardMarkup(True)
keyboard1.add(*keyboard1_names)

keyboard2 = telebot.types.ReplyKeyboardMarkup(True)
keyboard2.add(*keyboard2_names)


def text_processing(text, command):
    if command == 'текст':
        return text
    elif command == 'кількість символів':
        return len(text)
    elif command == 'визначити мову':
        return langdetect.detect(text)
    elif command == 'кількість символів без пробілів':
        return len(text) - text.count(' ')
    elif command == 'перевести у верхній регістр':
        return text.upper()
    elif command == 'перевести у нижній регістр':
        return text.lower()


@bot.message_handler(commands=['start'])
def send_startmessage(message):
    text = ('\nЦе бот для обробкии текстів. '
            '\nНадішли свій текст (від 300 до 3000 символів)')
    bot.send_message(
        message.chat.id, parse_mode='Markdown',
        text=f'*Привіт, {message.from_user.first_name}.\n{text}*')


@bot.message_handler(content_types=['text'])
def send_textmessage(message):
    text = users_texts.get(message.chat.id)

    if message.text.lower() in map(str.lower, keyboard1_names):
        if text is not None:
            if message.text.lower() == 'розділити на речення':
                nltk.download('punkt')
                for sentence in nltk.sent_tokenize(text):
                    bot.send_message(message.chat.id, text=sentence)
            else:
                bot.send_message(
                    message.chat.id,
                    text=text_processing(text, message.text.lower()))

    elif message.text.lower() in map(str.lower, keyboard2_names):
        if text is not None:
            if message.text.lower() == 'повернути попередній текст':
                if message.chat.id in last_texts:
                    users_texts[message.chat.id] = last_texts[message.chat.id]
                    del last_texts[message.chat.id]

                    bot.send_message(
                        message.chat.id, text='Попередній текст повернуто.',
                        reply_markup=keyboard1)
                else:
                    bot.send_message(
                        message.chat.id, reply_markup=keyboard1,
                        text='Попередніх варіантів тексту не знайдено!')

            elif message.text.lower() == 'продовжити':
                bot.send_message(
                    message.chat.id, text='Oк.', reply_markup=keyboard1)

    else:
        if 300 <= len(message.text) <= 3000:
            bot.send_message(
                message.chat.id, reply_markup=keyboard2,
                text='Ви бажаєте надати цей текст для обробки?')

            last_texts[message.chat.id] = users_texts.get(message.chat.id)
            users_texts[message.chat.id] = message.text
        else:
            bot.send_message(
                message.chat.id,
                text='Текст повинен містити 300-3000 символів!')


bot.polling()
