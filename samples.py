import random


GROUP_ID = -1002301304160
GAMEURL = "https://sofarnone.github.io/tower-blocks/"
TOKEN = "8007597630:AAGslFFrUQdxNSOKMGBRSTuI8QH4m8yqSDY"


def get_promo_code(num_chars):
    code_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    code = ""
    for i in range(0, num_chars):
        slice_start = random.randint(0, len(code_chars) - 1)
        code += code_chars[slice_start : slice_start + 1]
    return code


admin_list = set()

NEW_ADMIN = """Теперь вы администратор! Вам доступны следуюшие команды:
/clear   для сброса времени последней игры.
/check   для проверки валидности промокода"""

INTRODUCTION = """Привет!👋 Добро пожаловать!
Я — бот, который предлагает вам сыграть в увлекательную игру «Башня из блоков». 

Как играть - <b>/help</b>

"""
SUBSCRIBE = (
    "Для того, чтобы начать - необходимо подписаться на наш канал.\n@gagarin_game"
)
WINGAME = """🔥 Поздравляю, вы победили! 🔥
Вы выиграли скидку в <b>Gagarin Vape Shop</b>!
Для получения скидки предьявите данное сообщение при покупке.
И помните: дым электронный, а кашель настоящий.
\n"""
LOSEGAME = """К сожалению, вы проиграли. 😢
Но не расстраивайтесь, вы всегда можете попробовать еще раз, но только на следующий день!"""
# ЕСЛИ ПОЛЬЗОВАТЕЛЬ НАБРАЛ НЕИЗВЕСТНУЮ КОМАНДУ ИЛИ ТЕКСТ
DONTUNDERSTAND = (
    "Не понимаю, что вы хотели этим сказать.\nДля начала наберите команду <b>/start</b>"
)
# ВСТУПЛЕНИЕ В ГРУППУ
WELCOME = """🔥 Поздравляю со вступлением в группу! 🔥
Теперь вы можете наслаждаться полным функционалом нашего бота!

Чтобы начать игру, просто введите команду /start  🎮✨"""


PLAYBUTTON = "Играть 🔥"
GAMEPLAY = """
<b>Цель игры</b> — возвести башню из блоков как можно выше. С каждым новым блоком башня будет подниматься всё выше и выше.

Однако если блок не установить точно на другой блок, площадь для его размещения уменьшится. Старайтесь всегда устанавливать блоки ровно!

По завершении игры вы получите скидку на одну покупку в нашей сети. Размер скидки зависит от количества набранных очков.

Играть - <b>/start</b>
"""


def get_promo_code(num_chars):
    code_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    code = ""
    for i in range(0, num_chars):
        slice_start = random.randint(0, len(code_chars) - 1)
        code += code_chars[slice_start : slice_start + 1]
    return code


admin_list = set()
