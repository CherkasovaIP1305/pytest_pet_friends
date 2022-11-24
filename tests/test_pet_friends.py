
from api import PetFriends
from settings import valid_email, valid_password
import os


pf = PetFriends()

def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем, что запрос всех питомцев возвращает не пустой список.
       Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
       запрашиваем список всех питомцев и проверяем что список не пустой.
       Доступное значение параметра filter - 'my_pets' либо '' """
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Пуха', animal_type='Кошка',
                                     age='9', pet_photo='images/3983.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/3984.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Пуха', animal_type='Британ', age=9):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


#Task 19.7.2

def test_create_pet_simple(name='Фаби', animal_type='Мейн кун', age='3'):
    """Проверяем возможность создания питомца без фото"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Создаем питомца
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_set_photo(pet_photo='images/3984.jpg'):
    """Проверяем возможность добавления фото"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить фото
    if len(my_pets['pets']) > 0:
        status, result = pf.set_photo(auth_key, my_pets['pets'][0]['id'], pet_photo)

        # Проверяем, что статус ответа = 200 и фото непустое
        assert status == 200
        assert result['pet_photo'] is not None
    else:
        raise Exception("There is no my pets")


def test_get_api_key_for_invalid_user(email='invalid@mail.ru', password='123456789'):
    """ Проверяем, что запрос ключа возвращает статус 403 и в результате не содержится слово key"""
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result


def test_delete_pet_another_user():
    """Проверяем возможность удаления питомца другого пользователя
    (Тест пройден успешно, но для сайта - это баг, так как удалять питамца,
    принадлежащего другому пользователю, нельзя)"""

    # Получаем ключ auth_key и запрашиваем список всех питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, all_pets = pf.get_list_of_pets(auth_key)

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = all_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, all_pets = pf.get_list_of_pets(auth_key)

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in all_pets.values()


def test_update_pet_info_another_user(name='Адидас', animal_type='кот', age=1):
    """Проверяем возможность обновления информации о питомце, принадлежащем другому пользователю
    (Тест пройден успешно, но для сайта - это баг, так как менять инфо питамца,
    принадлежащего другому пользователю, нельзя)"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, all_pets = pf.get_list_of_pets(auth_key)

    # Пробуем обновить имя, тип и возраст питомца

    status, result = pf.update_pet_info(auth_key, all_pets['pets'][0]['id'], name, animal_type, age)

    # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
    assert status == 200
    assert result['name'] == name


def test_set_photo_pet_another_user(pet_photo='images/3983.jpg'):
    """Проверяем возможность добавления фото питомцу, принадлежащему другому пользователю"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, all_pets = pf.get_list_of_pets(auth_key)

    # Пробуем обновить фото
    status, result = pf.set_photo(auth_key, all_pets['pets'][0]['id'], pet_photo)

    # Проверяем, что статус ответа = 500 и фото нет
    assert status == 500
    assert 'pet_photo' not in result


def test_get_my_pets_with_valid_key(filter=''):
    """ Проверяем, что запрос всех моих питомцев возвращает не пустой список."""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, 'my_pets')
    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_invalid_data(name='!@#$%^&', animal_type='!@#',
                                     age='два', pet_photo='images/3983.jpg'):
    """Проверяем, что можно добавить питомца с некорректными данными
    (Тест пройден успешно, но для сайта - это баг, необходимо исключить ввод невалидных значений полей"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_create_pet_simple_invalid_name(name='qwertyuiopasdfghjklxcvzbnmmnbvcxzasdfghjklpoiuytrewqasdfghjklmnbvcxzasdeqgdtevdhfjrktbvulfkghdhfygrggdsjhfgsyertywteryfgshgfysfgyeejyhgjhdsfgefgstdfsffhjfdhjfgsgdyueyehsgfhdgfsgfusygfuygygjfgsfgsyfgsgfysgfeyfyegfeyugywgfrfgdfjsdfjsgfdysuegwyegugefygfyggffgygygyfgye',
                                        animal_type='cat', age='3'):
    """Проверяем возможность в поле name ввести более 250 символов при нового питомца.
    (Тест пройден успешно, но для сайта - это баг, необходимо исключить ввод невалидных значений полей"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Создаем питомца
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

