import requests
import telebot
from telebot import types
from auth_data import token

# Инициализация словаря для хранения значений фильтров
filters = {
    'region': '',
    'name': '',
    'min_salary': ''
}

def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, "Привет! Рассказать тебе о новых вакансиях на портале Работа России?")
        info_message(message)

    @bot.message_handler(commands=["help"])
    def info_message(message):
        info = """Руководство по использованию telegram-бота
        Бот предназначен для упрощенного просмотра информации о вакансиях онлайн портала

    Список команд:
    - /start - Создание чата
    - /help - Получение справки о командах

    - /filter - Просмотр фильтра вакансий (регион, название вакансии, минимальная зарплата)
    - /region - Установить регион РФ для поиска вакансий (введите число, /region 59)
    - /name - Установить название вакансии (/name менеджер)
    - /min_salary - Установить минимальную З/П (/min_salary 60000)

    - /search - Поиск вакансий по фильтру
    """
        bot.send_message(message.chat.id, info)

    @bot.message_handler(commands=["filter"])
    def filter_get(message):
        bot.send_message(message.chat.id, f"""Текущие параметры фильтра:
Регион: {filters['region'] if filters['region'] else "-"}
Название: {filters['name'] if filters['name'] else "-"}
Минимальная зарплата: {filters['min_salary'] if filters['min_salary'] else "-"}""")

    @bot.message_handler(commands=['region'])
    def region_set(message):
        filters['region'] = message.text.split()[1]
        bot.reply_to(message, f"Регион: {filters['region']}")

    @bot.message_handler(commands=['name'])
    def name_set(message):
        filters['name'] = "/s".join(message.text.split()[1:])
        bot.reply_to(message, f"Название: {filters['name']}")

    @bot.message_handler(commands=['min_salary'])
    def min_salary_set(message):
        filters['min_salary'] = message.text.split()[1]
        bot.reply_to(message, f"Минимальная З/П: {filters['min_salary']}")

    @bot.message_handler(commands=["search"])
    def search(message):
        # Используйте значения из словаря filters
        region = filters['region']
        name = filters['name']
        min_salary = filters['min_salary']

        request_str = f"http://opendata.trudvsem.ru/api/v1/vacancies" \
                      f"{f'/region/{region}' if region else ''}" \
                      f"?text={name}" \
                      f"&salary_min={min_salary}" \
                      f"&limit=10"

        try:
            # запрос
            req = requests.get(request_str)
            response = req.json()

            vacs = response["results"]['vacancies']
            t = "Вакансии по запросу:\n\n"
            for v in vacs:
                i = v['vacancy']
                t += f"<a href='{i['vac_url']}'>{i['job-name']}</a>\n"          # должность - гиперссылка
                t += f"Специализация: {i['category']['specialisation']}\n"      # специализация
                t += f"Компания: {i['company']['name']}\n"               # работадатель
                t += f"Зарплата: {i['salary_min']}-{i['salary_max']} {i['currency'][1:-2]}\n"    # зарплата
                t += f"Контакты: {i['contact_list'][0]['contact_value']}\n\n"                  # контактные данные

            bot.send_message(message.chat.id, t, parse_mode='html')

        except Exception as ex:
            print(ex)
            bot.send_message(
                message.chat.id,
                "Ничего не найдено"
            )


    bot.polling()


if __name__ == '__main__':
    telegram_bot(token)
