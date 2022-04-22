import os
import platform
import subprocess
import threading
import time
from ipaddress import ip_address
from pprint import pprint

from tabulate import tabulate

result = {
    "Доступные узлы": "",
    "Недоступные узлы": "",
}  # словарь с результатами

DNULL = open(os.devnull, "w")  # заглушка, чтобы поток не выводился на экран


def check_is_ipaddress(value):
    """
    Проверка является ли введённое значение IP адресом
    :param value: присланные значения,
    :return ipv4: полученный ip адрес из переданного значения
        Exception ошибка при невозможности получения ip адреса из значения
    """
    try:
        ipv4 = ip_address(value)
    except ValueError:
        raise Exception("Некорректный ip адрес")
    return ipv4


def ping(ipv4, result, get_list):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    response = subprocess.Popen(["ping", param, "1", "-w", "1", str(ipv4)], stdout=subprocess.PIPE)
    if response.wait() == 0:
        result["Доступные узлы"] += f"{ipv4}, "
        res = f"{ipv4} - Узел доступен"
        if not get_list:  # если результаты не надо добавлять в словарь, значит отображаем
            print(res)
        return res
    else:
        result["Недоступные узлы"] += f"{ipv4}, "
        res = f"{str(ipv4)} - Узел недоступен"
        if not get_list:  # если результаты не надо добавлять в словарь, значит отображаем
            print(res)
        return res


def host_ping(hosts_list, get_list=False):
    """
    Проверка доступности хостов
    :param hosts_list: список хостов
    :param get_list: признак нужно ли отдать результат в виде словаря (для задания #3)
    :return словарь результатов проверки, если требуется
    """
    print("Начинаю проверку доступности узлов...")
    threads = []
    for host in hosts_list:  # проверяем, является ли значение ip-адресом
        try:
            ipv4 = check_is_ipaddress(host)
        except Exception as e:
            print(f"{host} - {e} воспринимаю как доменное имя")
            ipv4 = host

        thread = threading.Thread(target=ping, args=(ipv4, result, get_list), daemon=True)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    if get_list:  # если требуется вернуть словарь (для задачи №3), то возвращаем
        return result


def host_range_ping(get_list=False):
    """
    Функция запрашивает первоначальный адрес и количество адресов,
    и далее, если в последнем октете есть возможность увеличивать адрес,
    функция возвращает список возможных адресов.
    Затем проверяет доступность этих адресов с пом ф-ции host_ping()
    :param get_list:
    :return:
    """

    while True:
        start_ip = input("Введите первоначальный адрес: ")  # запрос первоначального адреса
        try:
            ipv4_start = check_is_ipaddress(start_ip)
            last_oct = int(start_ip.split(".")[3])  # смотрим чему равен последний октет
            break
        except Exception as e:
            print(e)
    while True:
        end_ip = input("Сколько адресов проверить?: ")  # Запрос на количество проверяемых адресов
        if not end_ip.isnumeric():
            print("Необходимо ввести число")
        else:
            if (last_oct + int(end_ip)) > 255 + 1:  # По условию меняется только последний октет
                print(f"Можем менять только последний октет, " f"т.е. максимальное число хостов {255 + 1 - last_oct}")
            else:
                break
    host_list = []
    [host_list.append(str(ipv4_start + x)) for x in range(int(end_ip))]  # формируем список ip
    if not get_list:  # передаём список в функцию из задания #1 для проверки
        host_ping(host_list)
    else:
        return host_ping(host_list, True)


def host_range_ping_tab():
    """
    Запрос диапазона ip адресов, проверка их доступности, вывод результатов в табличном виде
    :param
    :return:
    """
    res_dict = host_range_ping(True)  # Запрашиваем хосты, проверяем доступность, получаем словарь
    print()
    print(tabulate([res_dict], headers="keys", tablefmt="pipe", stralign="center"))


if __name__ == "__main__":
    # список проверяемых хостов
    hosts_list = [
        "192.168.8.1",
        "8.8.8.8",
        "yandex.ru",
        "google.com",
        "0.0.0.1",
        "0.0.0.2",
        "0.0.0.3",
        "0.0.0.4",
        "0.0.0.5",
        "0.0.0.6",
        "0.0.0.7",
        "0.0.0.8",
        "0.0.0.9",
        "0.0.1.0",
    ]
    start = time.time()
    host_ping(hosts_list)
    end = time.time()
    print(f"total time: {int(end - start)}")
    pprint(result)

    host_range_ping_tab()
