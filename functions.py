import psycopg2 as ps
import requests as rq
from bs4 import BeautifulSoup
import folium

db_params=ps.connect(
    database='postgres',
    user='postgres',
    password='Geodeta102!',
    host='localhost',
    port=5433
)
cursor=db_params.cursor()

create_pracownicy='''
    CREATE TABLE IF NOT EXISTS pracownicy (
    id SERIAL PRIMARY KEY,
    imie TEXT(50),
    nazwisko TEXT(50),
    zamieszkanie TEXT(50),
    odc_start TEXT(50),
    odc_koniec TEXT(50)
    );
'''
cursor.execute(create_pracownicy)
db_params.commit()

create_prace_drogowe='''
    CREATE TABLE IF NOT EXISTS prace_drogowe (
    id SERIAL PRIMARY KEY,
    odc_start TEXT(50),
    odc_koniec TEXT(50)
    );
'''
cursor.execute(create_prace_drogowe)
db_params.commit()

def create_users_pracownicy()->None:
    imie = input('Podaj imię pracownika ')
    nazwisko = input('Podaj nazwisko pracownika ')
    zamieszkanie=input('Podaj miasto zamieszkania pracownika ')
    odc_start=input('Podaj odcinek początkowy remontu, na którym działa pracownik ')
    odc_koniec=input('Podaj odcinek końcowy remontu, na którym działa pracownik ')
    sql_query_1 = f"INSERT INTO public.pracownicy(imie, nazwisko, zamieszkanie, odc_start, odc_koniec) VALUES ('{imie}', '{nazwisko}', '{zamieszkanie}', '{odc_start}', '{odc_koniec}');"
    cursor.execute(sql_query_1)
    db_params.commit()

def delete_users_pracownicy()->None:
    nazwisko = input('Podaj nazwisko pracownika do usunięcia ')
    sql_query_1 = f"SELECT * FROM public.pracownicy WHERE nazwisko='{nazwisko}';"
    cursor.execute(sql_query_1)
    query_result=cursor.fetchall()
    print(f'znaleziono ')
    print('0: usun wszystkich znalezionycyh pracowników')
    for numerek, user_to_be_removed in enumerate(query_result):
        print(f'{numerek + 1}. {user_to_be_removed}')
    numer = int(input(f'Wybierz pracownika do usunięcia '))
    if numer == 0:
        sql_query_2 = f"DELETE FROM public.pracownicy WHERE nazwisko='{nazwisko}';"
        cursor.execute(sql_query_2)
        db_params.commit()
    else:
        sql_query_2 = f"DELETE FROM public.pracownicy WHERE nazwisko='{query_result[numer - 1][2]}';"
        cursor.execute(sql_query_2)
        db_params.commit()

def read_users_pracownicy()->None:
    sql_query_1 = f"SELECT * FROM public.pracownicy;"
    cursor.execute(sql_query_1)
    query_result=cursor.fetchall()
    for row in query_result:
        print(f'Pracownik {row[1]} {row[2]} mieszka w miejscowości {row[3]} i pracuje na odcinku {row[4]} - {row[5]}')

def update_users_pracownicy() -> None:
    nazwisko = input('Podaj nazwisko pracownika do edycji')
    sql_query_1 = f"SELECT * FROM public.pracownicy WHERE nazwisko='{nazwisko}';"
    cursor.execute(sql_query_1)
    print('Znaleziono')
    name = input('podaj nowe imie: ')
    nick = input('podaj nowe ksywe: ')
    posts =int(input('podaj liczbw postów: '))
    city= input('podaj miasto: ')
    sql_query_2 = f"UPDATE public.pracownicy SET name='{name}',nick='{nick}', posts='{posts}', city='{city}' WHERE nick='{nazwisko}';"
    cursor.execute(sql_query_2)
    db_params.commit()

def get_coordinates(city:str)->list[float,float]:
    # pobieranie strony internetowej
    adres_url=f'https://pl.wikipedia.org/wiki/{city}'

    response=rq.get(url=adres_url) #zwraca obiekt, wywołany jest status
    response_html=BeautifulSoup(response.text, 'html.parser') #zwraca tekst kodu strony internetowej, zapisany w html

    #pobieranie współrzędnych
    response_html_lat=response_html.select('.latitude')[1].text #kropka oznacza klasę, do ID odwołujemy sie przez #
    response_html_lat=float(response_html_lat.replace(',','.'))

    response_html_long=response_html.select('.longitude')[1].text #kropka oznacza klasę, do ID odwołujemy sie przez #
    response_html_long=float(response_html_long.replace(',','.'))

    return [response_html_lat,response_html_long]

def get_coordinates(address):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json"}

    response = rq.get(base_url, params)
    data = response.json()
    latitude = data[0]["lat"]
    longitude = data[0]["lon"]
    return [latitude, longitude]



#  TODO - logowanie (if, else), CRUD dla listy prac drogowych, CRUD dla listy pracowników z wszystkich miejsc gdzie są prowadzone prace drogowe, CRUD dla listy pracowników wybranym miejscu gdzie prowadzone są prace  remontowe
#  TODO - GUI - mapa wszystkich remontowanych odcinków, mapa wszystkich pracowników, mapa pracowników wybranego remontowanego odcinka
#  TODO - okodowanie wszystkich funkcjonalności
#  TODO - po wysłaniu projektu iść go obronić jak Częstochowę