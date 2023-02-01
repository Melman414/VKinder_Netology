import os
from random import randrange
from time import time
import requests
import vk_api
from vk_api import keyboard
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from apivk import VKapi
from data_base import set_favorite, show_favorite, startBD

from dotenv import load_dotenv

load_dotenv()
token = os.environ.get('VK_TOKEN')
user_token=os.environ.get('USER_TOKEN')
dataSerchParms = {}
currentId = None

vk = vk_api.VkApi(token=token)
vkUserSerch = VKapi(user_token)
vk_upload = vk_api.VkUpload(vk)
longpoll = VkLongPoll(vk)
vkkeyboard = keyboard.VkKeyboard(one_time=False)

def send_mesage(user_id, message, keyboard=None):
  param = {
    'user_id': user_id,
    'message': message,
    'random_id': randrange(10**7)
  }
  if keyboard is not None:
    param['keyboard'] = keyboard.get_keyboard()
  vk.method('messages.send', param)


def send_photo(user_id, list_of_ids, owner_id):
  for x in list_of_ids:
    vk.method(
      'messages.send', {
        'user_id': user_id,
        'attachment': f"photo{owner_id}_{x}",
        'random_id': randrange(10**7)
      })

def main():
  print('Запуск Бота')
  startBD()
  coreBot()

def coreBot():
  try:
    for event in longpoll.listen():
      if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
          request = event.text.lower()
          if request == 'привет':
            dataSerchParms[event.user_id] = vkUserSerch.get_default_param(event.user_id) 
            if vkUserSerch.get_name(event.user_id):
              send_mesage(event.user_id,
                          f'Добро пожаловать, {vkUserSerch.get_name(event.user_id)}')
              send_mesage(
                  event.user_id,
                  'Мы будем предлагать тебе кандидатов на основании твоих предпочтений.'
                  ' Изменить условия поиска можно отправив команду "Условия поиска"'
                )
              keyboard = VkKeyboard(inline=True)
              keyboard.add_button('Искать', color=VkKeyboardColor.PRIMARY)
              keyboard.add_button('Условия поиска', color=VkKeyboardColor.PRIMARY)
              send_mesage(event.user_id, 'Начинаем искать удачные совпадения?', keyboard)
            else:
              send_mesage(
                  event.user_id, 'VK временно недоступен.'
                  'Пожалуйста, попробуйте отправить запрос чуть позже.')
          elif request == 'дальше' or request == 'искать':
            if dataSerchParms[event.user_id][0] == 0:
              keyboard.add_button('Условия поиска', color=VkKeyboardColor.PRIMARY)
              send_mesage(
                event.user_id, 'Не указан пол, '
                'для корректного поиска необходимо скорректировать условия поиска.',
                keyboard)
              
            if dataSerchParms[event.user_id][2] == 0:
              keyboard.add_button('Условия поиска', color=VkKeyboardColor.PRIMARY)
              send_mesage(
                event.user_id, 'Укажите возраст,'
                ' для корректного поиска неоходимо задать условия поиска.',
                keyboard)
              
            if dataSerchParms[event.user_id][3] == 0:
              keyboard.add_button('Условия поиска', color=VkKeyboardColor.PRIMARY)
              send_mesage(
                event.user_id, 'Укажите город,'
                ' для корректного поиска неоходимо задать условия поиска.',
                keyboard)
      

            photo_param = vkUserSerch.get_photo(dataSerchParms[event.user_id], event.user_id)
            currentId = photo_param[0]
            send_photo(event.user_id, photo_param[1], photo_param[2])
            keyboard = VkKeyboard(inline=True)
            keyboard.add_button('В избранное', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button('Дальше', color=VkKeyboardColor.PRIMARY)
            send_mesage(event.user_id,
              f'{vkUserSerch.get_name(photo_param[0])}  - vk.com/id{photo_param[0]}',
              keyboard)
          elif request == 'условия поиска':
            if event.user_id not in dataSerchParms:
              dataSerchParms[event.user_id] = vkUserSerch.get_default_param(event.user_id)
            keyboard = VkKeyboard(inline=True)
            keyboard.add_button('1', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button('2', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button('3', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button('4', color=VkKeyboardColor.PRIMARY)
            send_mesage(
              event.user_id,
              'Задать условия поиска: \n1 - Пол\n2 - Статус\n3 - Возраст\n4 - Город',
              keyboard)
            vkUserSerch.clear_search_params(event.user_id)

            for event in longpoll.listen():
              if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                  request = event.text.lower()

                  if request == '1':
                    keyboard = VkKeyboard(inline=True)
                    keyboard.add_button('Девушку', color=VkKeyboardColor.NEGATIVE)
                    keyboard.add_button('Парня', color=VkKeyboardColor.PRIMARY)
                    send_mesage(event.user_id, 'Кто это будет?', keyboard)
                    for event in longpoll.listen():
                      if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                          request = event.text.lower()
                          if request == 'девушку':
                            dataSerchParms[event.user_id][0] = 1
                          else:
                            dataSerchParms[event.user_id][0] = 2
                          keyboard = VkKeyboard(inline=True)
                          keyboard.add_button('Искать', color=VkKeyboardColor.PRIMARY)
                          keyboard.add_button('Условия поиска', color=VkKeyboardColor.PRIMARY)
                          send_mesage(event.user_id, 'Сохранили условия', keyboard)
                          break
                    break

                  if request == '2':
                    keyboard = VkKeyboard(inline=True)
                    keyboard.add_button('1', color=VkKeyboardColor.SECONDARY)
                    keyboard.add_button('2', color=VkKeyboardColor.SECONDARY)
                    keyboard.add_button('3', color=VkKeyboardColor.SECONDARY)
                    keyboard.add_button('4', color=VkKeyboardColor.SECONDARY)
                    send_mesage(event.user_id, 'В каком статусе?')
                    send_mesage(event.user_id, 'Одинок(а) - 1\n Ищет пару - 2\n'
                      'В браке - 3\n Сложный момент - 4', keyboard)
                    for event in longpoll.listen():
                      if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                          request = event.text.lower()
                          if request == '1':
                            dataSerchParms[event.user_id][1] = 1
                          elif request == '2':
                            dataSerchParms[event.user_id][1] = 6
                          elif request == '3':
                            dataSerchParms[event.user_id][1] = 4
                          elif request == '4':
                            dataSerchParms[event.user_id][1] = 5
                          keyboard = VkKeyboard(inline=True)
                          keyboard.add_button('Искать', color=VkKeyboardColor.PRIMARY)
                          keyboard.add_button('Условия поиска', color=VkKeyboardColor.PRIMARY)
                          send_mesage(event.user_id, 'Сохранили условия', keyboard)
                          break
                    break

                  if request == '3':
                    send_mesage(event.user_id, 'Задайте предпочитаемый возраст')
                    for event in longpoll.listen():
                      if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                          request = event.text.lower()
                          dataSerchParms[event.user_id][2] = request
                          keyboard = VkKeyboard(inline=True)
                          keyboard.add_button('Искать', color=VkKeyboardColor.PRIMARY)
                          keyboard.add_button('Условия поиска', color=VkKeyboardColor.PRIMARY)
                          send_mesage(event.user_id, 'Сохранили условия', keyboard)
                          break
                    break

                  if request == '4':
                    send_mesage(event.user_id, 'Из какого города?')
                    for event in longpoll.listen():
                      if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                          request = event.text
                          dataSerchParms[event.user_id][3] = request
                          keyboard = VkKeyboard(inline=True)
                          keyboard.add_button('Условия поиска', color=VkKeyboardColor.PRIMARY)
                          keyboard.add_button('Искать', color=VkKeyboardColor.PRIMARY)
                  
                          send_mesage(event.user_id, 'Сохранили условия', keyboard)
                          break
                    break
          elif request == 'в избранное':
            set_favorite(currentId, event.user_id)
            keyboard = VkKeyboard(inline=True)
            keyboard.add_button('Дальше', color=VkKeyboardColor.PRIMARY)
            send_mesage(event.user_id,
                      'Пользователь добавлен в список "Избранные"', keyboard)
          elif request == 'избранное':
            user_list = show_favorite(event.user_id)
            if len(user_list) < 1:
              keyboard = VkKeyboard(inline=True)
              keyboard.add_button('Искать', color=VkKeyboardColor.PRIMARY)
              send_mesage(
                event.user_id,
                'Тут еще ни чего нет',
                keyboard)
            else:
              for user in user_list:
                send_mesage(event.user_id,
                          f'{vkUserSerch.get_name(user)}  - vk.com/id{user}')
          elif request == 'помощь' or request == 'help' or request == 'хелп':
            send_mesage(
              event.user_id,
             'Комманды для бота:\n"Условия поиска" - настроить поиск.\n"Искать" -'
              ' искать пару.\n"Избранное" - показать список избранных пользователей'
            )
          else:
            send_mesage(event.user_id, 'Искуственый интелек бота не смог распознать комманду. Попробуйте еще раз')
  except requests.exceptions.RequestException:
    time.sleep(10) 

if __name__ == '__main__':
  main()
