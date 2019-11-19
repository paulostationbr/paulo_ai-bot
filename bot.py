import threading
import time
from datetime import datetime

import aiml
import amanobot
import numexpr
from amanobot.exception import TelegramError
from amanobot.loop import MessageLoop
from amanobot.namedtuple import InlineKeyboardMarkup

import config

bot = amanobot.Bot(config.TOKEN)

k = aiml.Kernel()
k.learn('aiml/*.aiml')


def get_user_lang(language_code):
    if language_code.startswith('pt'):
        return 'Portuguese'
    elif language_code.startswith('en'):
        return 'English'
    elif language_code.startswith('es'):
        return 'Spanish'
    elif language_code.startswith('id'):
        return 'Indonesian'
    else:
        return 'Unknown'


def handle_thread(*args):
    t = threading.Thread(target=handle, args=args)
    t.start()


def handle(msg):
    if msg.get('text'):

        if msg['chat']['type'] == 'private':
            msg['message_id'] = None

        if msg['text'].lower() == '/start' or msg['text'].lower() == 'começar':
            bot.sendChatAction(msg['chat']['id'], 'typing')
            time.sleep(1)
            start = InlineKeyboardMarkup(inline_keyboard=[
                [dict(text='🧠 Criador', url='https://t.me/paulo_almeida')],
                [dict(text='👤 Instagram', url='https://instagr.am/paulostation')],
                [dict(text='👨🏻‍💻 Alisson', url='https://t.me/marminino')]
            ])
            bot.sendMessage(msg['chat']['id'], f'''Olá {msg["from"]["first_name"]}! Prazer em conhecê-lo 😜

Digite oi para começar a conversa comigo 😊❤''', reply_markup=start, reply_to_message_id=msg['message_id'])


        elif msg['text'].lower() == '/eu':
            bot.sendChatAction(msg['chat']['id'], 'typing')
            time.sleep(1)
            bot.sendMessage(msg['chat']['id'], '''Nome: {}
User_ID: {}
Localização: {}
Idioma: {}'''.format(msg['from']['first_name'] + (
                '\nSobrenome: ' + msg['from']['last_name'] if msg['from'].get('last_name') else ''), msg['from']['id'],
                     msg['from']['language_code'], get_user_lang(msg['from']['language_code'])),
                            reply_to_message_id=msg['message_id'])


        elif msg['text'].lower() == '/hora':
            bot.sendChatAction(msg['chat']['id'], 'typing')
            time.sleep(1)
            now = datetime.now()
            bot.sendMessage(msg['chat']['id'], f'Agora são: {now.strftime("%X")}',
                            reply_to_message_id=msg['message_id'])


        elif msg['text'].lower().startswith('/calcule '):
            bot.sendChatAction(msg['chat']['id'], 'typing')
            time.sleep(1)
            try:
                expr = numexpr.evaluate(msg['text'][9:])
            except SyntaxError:
                bot.sendMessage(msg['chat']['id'], 'Parece que tem um problema com a sua expressão matemática \n',
                                reply_to_message_id=msg['message_id'])
            else:
                if len(str(expr.item())) <= 4096:
                    bot.sendMessage(msg['chat']['id'], f'Resultado: <code>{expr}</code>', 'HTML',
                                    reply_to_message_id=msg['message_id'])
                else:
                    bot.sendMessage(msg['chat']['id'],
                                    'O resultado da conta ultrapassa o limite de caracteres que posso enviar aqui :(',
                                    reply_to_message_id=msg['message_id'])

        else:
            if msg['chat']['type'] == 'private' or msg.get('reply_to_message', dict()).get('from', dict()).get('id', dict()) == int(config.TOKEN.split(':')[0]):
                response = k.respond(msg['text'])
                if response:
                    response = response.replace('#', '\n').replace('$nome', msg['from']['first_name'])
                    bot.sendChatAction(msg['chat']['id'], 'typing')
                    time.sleep(1)
                    bot.sendMessage(msg['chat']['id'], response, reply_to_message_id=msg['message_id'],
                                    disable_web_page_preview=True)


print('Bot iniciado.')

MessageLoop(bot, handle_thread).run_forever()
