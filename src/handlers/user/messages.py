import random
from src.create_bot import _


class Messages:
    @staticmethod
    def ask_for_locale() -> str:
        return 'Выберите язык ⤵️\n' \
               'What is your language? ⤵'

    @staticmethod
    def get_start_sticker() -> str:
        return "CAACAgIAAxkBAAI2VmTL4n1mqPBYjA4Nq849fl0AAQWpgwAC0wUAAj-VzAqfWrvSXUfHMS8E"

    @staticmethod
    def get_ru_welcome(user_name: str = 'незнакомец') -> str:
        return f'''<b>Приветствую тебя в нашей команде, {user_name}! </b> \n
Этот бот даст возможность стабильно зарабатывать каждый день на игре <b>Лаки Джет</b> 🚀🍀 \n
Все что нужно сделать, это зайти в игру и нажать кнопку ⤵️ <b>«СЛЕДУЮЩИЙ СИГНАЛ»</b> \n
Бот выдаст коэффициент, а твоя задача сделать ставку и забрать свой первый выигрыш💰'''.format(user_name=user_name)

    @staticmethod
    def get_en_welcome(user_name: str = 'незнакомец') -> str:
        return f'''<b>Welcome to our game, {user_name}!</b> \n
This bot will give you the opportunity to consistently earn every day in the game <b>Lucky Jet</b> 🚀🍀 \n
All you need to do is go into the game and use the setting ⤵️ <b>«NEXT SIGNAL»</b> \n
The bot will give you the coefficient, and your task is to make an offer and collect your first winnings💰'''.format(
            user_name=user_name)

    @staticmethod
    def get_welcome_photo() -> str:
        return 'AgACAgIAAxkBAAEB_TdkzMlMDRRexAJvbyyV2fQnqakFEAACetcxG4KmaUqOE64EzAiZUQEAAwIAA3kAAy8E'

    @staticmethod
    def get_next_signal(onewin_id: int):
        coefficient = f'{random.uniform(1.30, 2.73):.2f}'
        return _('ID: {onewin_id} \n🚀 ВЫВОДИ НА: <b>{coefficient}</b>') \
            .format(onewin_id=onewin_id, coefficient=coefficient)

    @staticmethod
    def ask_for_code_word() -> str:
        return _('🔐 Введите кодовое слово:')

    @staticmethod
    def get_code_word_incorrect():
        return _('❗<b>Вы ввели неправильное кодовое слово!</b> \nПопробуйте ещё раз:')

    @staticmethod
    def ask_for_1win_id() -> str:
        return _('Замечательно! \nТеперь введите 🆔 от вашего аккаунта 1win: ')

    @staticmethod
    def get_1win_id_incorrect_length() -> str:
        return _('❗<b>ID не может содержать букв и символов, только цифры!</b> \nПопробуйте ещё раз:')

    @staticmethod
    def get_1win_id_have_forbidden_symbols() -> str:
        return _('❗<b>ID должно иметь длину в 8 цифр</b> \nПопробуйте снова:')

    @staticmethod
    def get_before_game_start() -> str:
        return _("Перед тем как, начать ⤵️\n\n" 
                 "Минимальная сумма депозита в игре с ботом <b>500-1000₽</b> либо <b>5-15$</b> \n\n" 
                 "Если вдруг бот выдает не верные коэффициенты, скорее всего ваш аккаунт <b>не активирован</b>. \n" 
                 "Нужно сделать депозит еще раз, чтобы ваш аккаунт активировался❗")

    @staticmethod
    def get_before_start_photo() -> str:
        return 'AgACAgIAAxkBAAEB_TtkzMl5s-HsM8JstC6FO4PRc4b6SAAC3cYxG5rOaErWm2hpoDD2pQEAAwIAA3kAAy8E'
