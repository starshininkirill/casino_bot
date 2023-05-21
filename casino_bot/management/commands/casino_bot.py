import traceback
from django.core.management.base import BaseCommand
from django.utils import timezone
from telebot import types
import telebot
from ... import models
from time import sleep


def create_after_game_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    btn_regame = types.InlineKeyboardButton(text='Крутить ещё раз!', callback_data='rebet')
    btn_rebet = types.InlineKeyboardButton(text='Поменять ставку', callback_data='game')
    btn_menu = types.InlineKeyboardButton(text='Меню', callback_data='menu')
    kb.add(btn_regame, btn_rebet, btn_menu)
    return kb


def send_start_message(bot, message, user):
    kb = types.InlineKeyboardMarkup()
    btn_game = types.InlineKeyboardButton(text='Играть', callback_data='game')
    kb.row(btn_game)
    btn_profile = types.InlineKeyboardButton(text='Мой профиль', callback_data='profile')
    btn_balance = types.InlineKeyboardButton(text='Пополнить баланс', callback_data='balance')
    kb.row(btn_profile, btn_balance)
    bot.send_message(message.chat.id, f"""
Баланс: {user.balance}
нажми "<b>играть</b>" чтобы начать
    """, reply_markup=kb, parse_mode='HTML')


def get_stage(text):
    return models.Stages.objects.filter(current_stage=f'{text}').get()


def create_position_kb():
    kb = types.InlineKeyboardMarkup(row_width=3)

    btn_1 = types.InlineKeyboardButton(callback_data='position_1', text='1')
    btn_2 = types.InlineKeyboardButton(callback_data='position_2', text='2')
    btn_3 = types.InlineKeyboardButton(callback_data='position_3', text='3')
    btn_4 = types.InlineKeyboardButton(callback_data='position_4', text='4')
    btn_5 = types.InlineKeyboardButton(callback_data='position_5', text='5')
    btn_6 = types.InlineKeyboardButton(callback_data='position_6', text='6')

    kb.add(btn_1, btn_2, btn_3, btn_4, btn_5, btn_6)

    return kb


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        bot = telebot.TeleBot("6265442848:AAHfpxNG0pEYh9GkSOXqkIk6V9RpYzUpbyQ")

        @bot.message_handler(commands=['start'])
        def start(message):
            user, created = models.User.objects.get_or_create(tg_uid=message.from_user.id)
            user.stage = 'menu'
            user.save()
            if message.from_user.username:
                user.username = message.from_user.first_name
                user.save()

#             if created == True:
#                 kb = types.InlineKeyboardMarkup()
#                 btn_game = types.InlineKeyboardButton(text='Играть', callback_data='game')
#                 kb.row(btn_game)
#                 btn_profile = types.InlineKeyboardButton(text='Мой профиль', callback_data='profile')
#                 btn_balance = types.InlineKeyboardButton(text='Пополнить баланс', callback_data='balance')
#                 kb.row(btn_profile, btn_balance)
#                 bot.send_message(message.chat.id, f"""
# Приветствую тебя в моём первом телеграмм казино!\n
# Здесь можно сыграть в кости на <b>типаденьги</b>\n
# Для вызова стартового сообщения введи команду /start либо введи любой символ
#                 """, reply_markup=kb, parse_mode='HTML')
#             else:
            send_start_message(bot, message, user)

        @bot.callback_query_handler(func=lambda call: call.data == 'menu')
        def menu(call):
            user, created = models.User.objects.get_or_create(tg_uid=call.from_user.id)
            send_start_message(bot, call.message, user)

        @bot.callback_query_handler(func=lambda call: call.data == 'balance')
        def balance(call):
            user, created = models.User.objects.get_or_create(tg_uid=call.from_user.id)
            if user.stage == 'menu':
                stage = get_stage('menu 3')
                bot.send_message(call.message.chat.id, 'Введите сумму для пополнения в пределах 1000')
                bot.answer_callback_query(call.id)
                user.stage = stage.next_stage
                user.save()
            else:
                bot.answer_callback_query(call.id)

        @bot.callback_query_handler(func= lambda call: call.data == 'profile')
        def profile(call):
            user, created = models.User.objects.get_or_create(tg_uid=call.from_user.id)
            bot.send_message(call.message.chat.id, f'Привет, {user.username}\nТвой баланс: {user.balance}\nСыграно игр: {user.games_count}', parse_mode='HTML')
            bot.answer_callback_query(call.id)

        @bot.callback_query_handler(func=lambda call: call.data == 'rebet')
        def rebet(call):
            user, created = models.User.objects.get_or_create(tg_uid=call.from_user.id)
            if user.stage == 'menu':
                game = models.CubeGame.objects.get(tg_uid=user.tg_uid)
                bet = int(game.bet)
                if user.balance >= bet:
                    position = game.position
                    dice_result = bot.send_dice(call.message.chat.id)
                    bot.answer_callback_query(call.id)
                    stage = get_stage('menu 2')
                    user.stage = stage.next_stage
                    user.save()
                    sleep(3)
                    if dice_result.dice.value == position:
                        user.games_count = user.games_count + 1
                        user.balance = int(user.balance) + bet * 6
                        user.save()
                        kb = create_after_game_kb()
                        bot.send_message(call.message.chat.id,
                                         f'Вы выйграли: <b>{bet * 6}</b>\nТеперь ваш баланс: <b>{user.balance}</b>',
                                         reply_markup=kb, parse_mode='HTML')
                    else:
                        user.balance = int(user.balance) - bet
                        user.games_count = user.games_count + 1
                        user.save()
                        kb = create_after_game_kb()
                        bot.send_message(call.message.chat.id,
                                         f'Вы проиграли: <b>{bet}</b>\nТеперь ваш баланс: <b>{user.balance}</b>',
                                         reply_markup=kb, parse_mode='HTML')
                else:
                    bot.answer_callback_query(call.id)
                    bot.send_message(call.message.chat.id, f'К сожалению у вас нет денег на ещё одну такую ставку')

        @bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'game')
        def game(call):
            user, created = models.User.objects.get_or_create(tg_uid=call.from_user.id)
            if call.data == 'game':
                if user.balance <= 0:
                    bot.send_message(call.message.chat.id, 'У вас нет денег, нажмите пополнть баланс')
                    user.stage = 'menu'
                    send_start_message(bot, call.message, user)
                else:
                    stage = get_stage('menu 1')
                    if user.stage != 'game':
                        user.stage = stage.next_stage
                        user.save()
                    bot.send_message(call.message.chat.id, f'Введите ставку от 1 до {user.balance}')
                    bot.answer_callback_query(call.id)

            elif call.data == 'game 2':
                if user.stage == 'game 2':
                    game = models.CubeGame.objects.get(tg_uid=user.tg_uid)
                    bet = int(game.bet)
                    position = game.position
                    dice_result = bot.send_dice(call.message.chat.id)
                    bot.answer_callback_query(call.id)
                    stage = get_stage('menu 2')
                    user.stage = stage.next_stage
                    user.save()
                    sleep(3)
                    if dice_result.dice.value == position:
                        user.games_count = user.games_count + 1
                        user.balance = int(user.balance) + bet * 6
                        user.save()
                        kb = create_after_game_kb()
                        bot.send_message(call.message.chat.id, f'Вы выйграли: <b>{bet * 6}</b>\nТеперь ваш баланс: <b>{user.balance}</b>', reply_markup=kb, parse_mode='HTML')
                    else:
                        user.balance = int(user.balance) - bet
                        user.games_count = user.games_count + 1
                        user.save()
                        if user.balance == '0':
                            bot.send_message(call.message.chat.id, 'К сожалению у вас закончились средсва\nВведите /start чтобы пополнить деньги в меню')
                        else:
                            kb = create_after_game_kb()
                            bot.send_message(call.message.chat.id, f'Вы проиграли: <b>{bet}</b>\nТеперь ваш баланс: <b>{user.balance}</b>', reply_markup=kb, parse_mode='HTML')
                else:
                    bot.answer_callback_query(call.id)
                    bot.send_message(call.message.chat.id, 'Вы уже нажимали на эту кнопку')

        @bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'position')
        def set_position(call):
            user, created = models.User.objects.get_or_create(tg_uid=call.from_user.id)
            if user.stage == 'game 1':
                position = call.data.split("_")[1]

                bot.answer_callback_query(call.id)

                bot.send_message(call.message.chat.id, f'Вы поставили на ребро "<b>{position}</b>"', parse_mode='HTML')
                game, created = models.CubeGame.objects.update_or_create(tg_uid=user.tg_uid, defaults={'position': position})
                stage = get_stage('game 1')
                user.stage = stage.next_stage
                user.save()
                kb = types.InlineKeyboardMarkup(row_width=1)
                btn_go = types.InlineKeyboardButton(text='Начать!', callback_data='game 2')
                kb.add(btn_go)
                bot.send_message(call.message.chat.id, 'Нажмите на кнопку, чтобы начать!', reply_markup=kb)
            else:
                bot.answer_callback_query(call.id)

        @bot.message_handler(content_types=['text'])
        def text_handle(message):
            user, created = models.User.objects.get_or_create(tg_uid=message.from_user.id)
            if user.stage == 'game':
                try:
                    bet = int(message.text)
                    if bet <= 0:
                        bot.send_message(message.chat.id, 'Ставка не должна быть отрицательной')
                    else:
                        if bet > user.balance:
                            bot.send_message(message.chat.id, f'Ставка превышает ваш баланс, введите другую сумму\nВаш текущий баланс: {user.balance}')
                        else:
                            bot.send_message(message.chat.id, f'Ваша ставка "<b>{bet}</b>"', parse_mode='HTML')
                            game, created = models.CubeGame.objects.update_or_create(tg_uid=message.from_user.id, defaults={'bet': bet})

                            kb = create_position_kb()
                            bot.send_message(message.chat.id, 'Выберите ребро кубика для ставки', reply_markup=kb)

                            stage = get_stage('game')
                            user.stage = stage.next_stage
                            user.save()
                except:
                    bot.send_message(message.chat.id, 'Введите число без букв и прочих символов')

            elif user.stage == 'game 1':
                bot.send_message(message.chat.id, 'Выберите одну из кнопок')

            elif user.stage == 'balance':
                try:
                    money = int(message.text)
                    if money > 0 and money <= 1000:
                        stage = get_stage('balance')
                        user.balance = user.balance + money
                        user.stage = stage.next_stage
                        user.save()
                        bot.send_message(message.chat.id, f'Баланс успешно пополнен на: <b>{money}</b>', parse_mode='HTML')
                        send_start_message(bot, message, user)
                    else:
                        bot.send_message(message.chat.id, 'Сумма должна быть положительной и меньше 1000')
                except:
                    bot.send_message(message.chat.id, 'Введите число до 1000')

            elif user.stage == 'menu':
                send_start_message(bot, message, user)

        bot.infinity_polling()