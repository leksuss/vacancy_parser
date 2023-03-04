import requests
from environs import Env

from terminaltables import AsciiTable


def predict_rub_salary(salary_from, salary_to):

    if salary_from and salary_to:
        predicted_salary = (salary_from + salary_to) // 2
    elif salary_from:
        predicted_salary = int(salary_from * 1.2)
    else:
        predicted_salary = int(salary_to * 0.8)

    return predicted_salary or None


def get_salary_stat(vacancies, predict_rub_salary_func):

    vacancies_processed = 0
    sum_salaries = 0
    for vacancy in vacancies:
        salary = predict_rub_salary_func(vacancy)
        if salary:
            sum_salaries += salary
            vacancies_processed += 1
    salary_stat = {
        'vacancies_found': len(vacancies),
        'vacancies_processed': vacancies_processed,
        'avg_salary': sum_salaries // (vacancies_processed or 1),
    }

    return salary_stat


def fetch_city_id_sj(city):
    url = 'https://api.superjob.ru/2.0/towns/'

    params = {
        'keyword': city,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    found_cities = response.json()

    if found_cities.get('objects'):
        return found_cities['objects'][0]['id']

    return None


def fetch_vacancies_sj(prog_lang, city, sj_secret_key):

    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': sj_secret_key,
    }
    params = {
        'keyword': prog_lang,
        'town': fetch_city_id_sj(city),
        'catalogues': 48,
        'count': 5,
        'page': 0,
    }

    vacancies = []
    has_more_vacancies = True
    while has_more_vacancies:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        one_page_vacancies = response.json()

        has_more_vacancies = one_page_vacancies['more']
        vacancies.extend(one_page_vacancies['objects'])

        params['page'] += 1

    return vacancies


def predict_rub_salary_sj(vacancy):

    if vacancy['currency'] == 'rub':
        return predict_rub_salary(
            vacancy['payment_from'],
            vacancy['payment_to'],
        )
    return None


def get_salary_stat_sj(prog_langs, city, sj_secret_key):

    salaries_stat = {}
    for prog_lang in prog_langs:
        vacancies = fetch_vacancies_sj(prog_lang, city, sj_secret_key)
        salary_stat = get_salary_stat(vacancies, predict_rub_salary_sj)
        salaries_stat[prog_lang] = salary_stat

    return salaries_stat


def predict_rub_salary_hh(vacancy):

    predicted_salary = None
    if vacancy['salary'] and vacancy['salary']['currency'] == 'RUR':
        predicted_salary = predict_rub_salary(
            vacancy['salary']['from'],
            vacancy['salary']['to'],
        )
    return predicted_salary


def fetch_city_id_hh(city):

    url = 'https://api.hh.ru/suggests/areas'
    params = {
        'text': city,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    found_cities = response.json()

    if found_cities.get('items'):
        return found_cities['items'][0]['id']

    return None


def fetch_prof_role_id_hh(prof_role):

    url = 'https://api.hh.ru/suggests/professional_roles'
    params = {
        'text': prof_role,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    found_prof_roles = response.json()

    if found_prof_roles.get('items'):
        return found_prof_roles['items'][0]['id']

    return None


def fetch_vacancies_hh(prog_lang, prof_role, city):

    url = 'https://api.hh.ru/vacancies'
    params = {
        'professional_role': fetch_prof_role_id_hh(prof_role),
        'area': fetch_city_id_hh(city),
        'period': 30,
        'order_by': 'publication_time',
        'search_field': 'name',
        'text': prog_lang,
        'page': 0,
        'per_page': 100,
        # 'only_with_salary': True,
    }
    vacancies = []
    pages = 1
    while params['page'] < pages:
        response = requests.get(url, data=params)
        response.raise_for_status()
        one_page_vacancies = response.json()
        params['page'] += 1
        pages = one_page_vacancies['pages']
        vacancies.extend(one_page_vacancies['items'])

    return vacancies


def get_salary_stat_hh(prog_langs, prof_role, city):

    salaries_stat = {}
    for prog_lang in prog_langs:
        vacancies = fetch_vacancies_hh(prog_lang, prof_role, city)
        salary_stat = get_salary_stat(vacancies, predict_rub_salary_hh)
        salaries_stat[prog_lang] = salary_stat

    return salaries_stat


def draw_table(vacancies_stat, title):

    TABLE_DATA = [
        (
            'Язык программирования',
            'Вакансий найдено',
            'Вакансий обработано',
            'Средняя зарплата',
        ),
    ]

    for prog_lang, salary_stat in vacancies_stat.items():
        TABLE_DATA.append((prog_lang, *salary_stat.values()))

    table_instance = AsciiTable(TABLE_DATA, title)

    return table_instance.table


def main():

    env = Env()
    env.read_env()

    prog_langs = (
        'JavaScript',
        'Java',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'Go',
        'Scala',
        'Swift',
    )
    prof_role = 'Программист'
    city = 'Москва'
    secret_key_sj = env.str('SJ_SECRET_KEY')

    title = f'HeadHunter {city}'
    salary_stat_hh = get_salary_stat_hh(prog_langs, prof_role, city)
    stat_table_hh = draw_table(salary_stat_hh, title)
    print(stat_table_hh)

    print()

    title = f'SuperJob {city}'
    salary_stat_sj = get_salary_stat_sj(prog_langs, city, secret_key_sj)
    stat_table_sj = draw_table(salary_stat_sj, title)
    print(stat_table_sj)


if __name__ == '__main__':
    main()
