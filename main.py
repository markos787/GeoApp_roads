import psycopg2 as ps
import requests as rq
from tkinter import *
from tkintermapview import TkinterMapView
import math

db_params=ps.connect(
    database='postgres',
    user='postgres',
    password='***********',
    host='localhost',
    port=5433
)
cursor=db_params.cursor()

create_pracownicy='''
    CREATE TABLE IF NOT EXISTS pracownicy (
    id INT PRIMARY KEY,
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
    id INT PRIMARY KEY,
    odc_start TEXT(50),
    odc_koniec TEXT(50)
    );
'''
cursor.execute(create_prace_drogowe)
db_params.commit()


def auto_id_remonty_dodawanie():
    sql_query_1 = f"SELECT * FROM public.prace_drogowe ORDER BY id ASC;"
    cursor.execute(sql_query_1)
    query_result = cursor.fetchall()

    index=[]
    if not query_result:
        index.append('1')
    else:
        for row in query_result:
            index.append(row[0])

    return int(max(index))+1

def auto_id_remonty_aktualizacja():
    sql_query_1 = f"SELECT * FROM public.prace_drogowe ORDER BY id ASC;"
    cursor.execute(sql_query_1)
    query_result = cursor.fetchall()

    ids=[]
    for row in query_result:
        ids.append(row[0])
    for idx, id in enumerate(ids):
        sql_query_2 = f"UPDATE public.prace_drogowe SET id='{idx+1}' WHERE id='{id}';"
        cursor.execute(sql_query_2)
        db_params.commit()

def auto_id_pracownicy_dodawanie():
    sql_query_1 = f"SELECT * FROM public.pracownicy ORDER BY id ASC;"
    cursor.execute(sql_query_1)
    query_result = cursor.fetchall()

    index=[]
    if not query_result:
        index.append('1')
    else:
        for row in query_result:
            index.append(row[0])

    return int(max(index))+1

def auto_id_pracownicy_aktualizacja():
    sql_query_1 = f"SELECT * FROM public.pracownicy ORDER BY id ASC;"
    cursor.execute(sql_query_1)
    query_result = cursor.fetchall()

    ids=[]
    for row in query_result:
        ids.append(row[0])
    for idx, id in enumerate(ids):
        if idx+1==id:
            continue
        else:
            sql_query_2 = f"UPDATE public.pracownicy SET id='{idx+1}' WHERE id='{id}';"
            cursor.execute(sql_query_2)
            db_params.commit()

def get_coordinates(address):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json"}

    response = rq.get(base_url, params)
    data = response.json()
    latitude = data[0]["lat"]
    longitude = data[0]["lon"]
    return [float(latitude), float(longitude)]

def logowanie(event=None):

    haslo=logowanie_entry.get()
    if haslo=='Geoinfa123':

        def remonty():

            def center_widgets_remonty(event=None):
                window_width = root_remonty_all.winfo_width()
                frame_height=root_remonty.winfo_height()

                root_remonty.place(x=window_width // 2, y=frame_height/2, anchor='center')

            def pokaz_wszystko_remont():
                listbox_remonty.delete(0, END)
                sql_query_1 = f"SELECT * FROM public.prace_drogowe ORDER BY id ASC;"
                cursor.execute(sql_query_1)
                query_result = cursor.fetchall()
                for idx, row in enumerate(query_result):
                    listbox_remonty.insert(idx, f'Odcinek {row[1]} - {row[2]}')

                auto_id_remonty_aktualizacja()

            def dodaj_remont():
                poczatek_remontu=entry_remonty_odc_start.get()
                koniec_remontu=entry_remonty_odc_koniec.get()

                sql_query_1 = f"INSERT INTO public.prace_drogowe(id, odc_start, odc_koniec) VALUES ('{auto_id_remonty_dodawanie()}', '{poczatek_remontu}', '{koniec_remontu}');"
                cursor.execute(sql_query_1)
                db_params.commit()

                entry_remonty_odc_start.delete(0, END)
                entry_remonty_odc_koniec.delete(0, END)

                pokaz_wszystko_remont()

            def edytuj_remont():
                sql_query_1 = f"SELECT * FROM public.prace_drogowe ORDER BY id ASC;"
                cursor.execute(sql_query_1)
                query_result = cursor.fetchall()

                i=listbox_remonty.index(ACTIVE)

                entry_remonty_odc_start.delete(0, END)
                entry_remonty_odc_koniec.delete(0, END)

                entry_remonty_odc_start.insert(0, query_result[i][1])
                entry_remonty_odc_koniec.insert(0, query_result[i][2])

                button_remonty_dodaj_remont.config(text='Zapisz zmiany', command=lambda: aktualizuj_remont(i))

            def aktualizuj_remont(i):
                sql_query_1 = f"SELECT * FROM public.prace_drogowe ORDER BY id ASC;"
                cursor.execute(sql_query_1)
                query_result = cursor.fetchall()

                start=entry_remonty_odc_start.get()
                koniec=entry_remonty_odc_koniec.get()

                sql_query_2 = f"UPDATE public.prace_drogowe SET odc_start='{start}',odc_koniec='{koniec}' WHERE odc_start='{query_result[i][1]}' and odc_koniec='{query_result[i][2]}';"
                cursor.execute(sql_query_2)
                db_params.commit()

                button_remonty_dodaj_remont.config(text='Dodaj remont', command=dodaj_remont)

                entry_remonty_odc_start.delete(0, END)
                entry_remonty_odc_koniec.delete(0, END)

                pokaz_wszystko_remont()

            def usun_remont():
                i = listbox_remonty.index(ACTIVE)

                sql_query_1 = f"DELETE FROM public.prace_drogowe WHERE id='{i+1}';"
                cursor.execute(sql_query_1)
                db_params.commit()

                pokaz_wszystko_remont()

            def pokaz_remont():
                sql_query_1 = f"SELECT * FROM public.prace_drogowe ORDER BY id ASC;"
                cursor.execute(sql_query_1)
                query_result = cursor.fetchall()

                i = listbox_remonty.index(ACTIVE)

                sql_query_2 = f"SELECT * FROM public.pracownicy WHERE odc_start='{query_result[i][1]}' and odc_koniec='{query_result[i][2]}' ORDER BY id ASC;"
                cursor.execute(sql_query_2)
                query_result_2 = cursor.fetchall()

                start=query_result[i][1]
                koniec=query_result[i][2]
                wsp_srodka=f'{round((float(get_coordinates(start)[0])+float(get_coordinates(koniec)[0]))/2,4)}\n {round((float(get_coordinates(start)[1])+float(get_coordinates(koniec)[1]))/2,4)}'
                liczba_pracownikow=len(query_result_2)

                label_remonty_odc_start_szczegoly_wartosc.config(text=start)
                label_remonty_odc_koniec_szczegoly_wartosc.config(text=koniec)
                label_remonty_srodek_szczegoly_wartosc.config(text=wsp_srodka)
                label_remonty_liczba_szczegoly_wartosc.config(text=liczba_pracownikow)

            root_remonty_all = Toplevel(root_choice)
            root_remonty_all.title('Utrudnienia drogowe')
            szer = 670
            wys = 360
            root_remonty_all.geometry(f'{szer}x{wys}')
            root_remonty_all.bind('<Configure>', center_widgets_remonty)

            root_remonty=Frame(root_remonty_all)
            root_remonty.grid(row=0, column=0)

            ramka_remonty_start = Frame(root_remonty)
            ramka_remonty_lista = Frame(root_remonty)
            ramka_remonty_formularz = Frame(root_remonty)
            ramka_remonty_szczegoly = Frame(root_remonty)

            ramka_remonty_start.grid(row=0, column=0, columnspan=2)
            ramka_remonty_lista.grid(row=1, column=0)
            ramka_remonty_formularz.grid(row=1, column=1)
            ramka_remonty_szczegoly.grid(row=2, column=0, columnspan=2)

            # ---------------------------------------
            # ramka remonty_start
            # ---------------------------------------
            label_remonty_lista = Label(ramka_remonty_start, text='Lista remontów drogowych', font=('Arial', 12, 'bold'))
            button_pokaz_liste = Button(ramka_remonty_start, text='Pokaż wszystko', command=pokaz_wszystko_remont)

            label_remonty_lista.grid(row=0, column=0, padx=(szer / 2 - label_remonty_lista.winfo_reqwidth() / 2), pady=(10, 0))
            button_pokaz_liste.grid(row=1, column=0)

            # ---------------------------------------
            # ramka remonty_lista
            # ---------------------------------------
            listbox_remonty = Listbox(ramka_remonty_lista, width=50)
            button_remonty_pokaz_szczegoly = Button(ramka_remonty_lista, text='Pokaż dane remontu', command=pokaz_remont)
            button_remonty_usun = Button(ramka_remonty_lista, text='Usuń remont', command=usun_remont)
            button_remonty_edytuj = Button(ramka_remonty_lista, text='Edytuj remont', command=edytuj_remont)

            listbox_remonty.grid(row=1, column=0, columnspan=3, pady=(10, 0))
            button_remonty_pokaz_szczegoly.grid(row=2, column=0)
            button_remonty_usun.grid(row=2, column=1)
            button_remonty_edytuj.grid(row=2, column=2)

            # ---------------------------------------
            # ramka remonty_formularz
            # ---------------------------------------
            label_remonty_nowy_obiekt = Label(ramka_remonty_formularz, text='Formularz edycji i dodawania:',
                                              font=('Arial', 10))
            label_remonty_odc_start = Label(ramka_remonty_formularz, text='Początek remontu')
            label_remonty_odc_koniec = Label(ramka_remonty_formularz, text='Koniec remontu')

            entry_remonty_odc_start = Entry(ramka_remonty_formularz)
            entry_remonty_odc_koniec = Entry(ramka_remonty_formularz)

            label_remonty_nowy_obiekt.grid(row=0, column=0, columnspan=2)
            label_remonty_odc_start.grid(row=1, column=0, sticky=W)
            label_remonty_odc_koniec.grid(row=2, column=0, sticky=W)

            entry_remonty_odc_start.grid(row=1, column=1, sticky=W)
            entry_remonty_odc_koniec.grid(row=2, column=1, sticky=W)

            button_remonty_dodaj_remont = Button(ramka_remonty_formularz, text='Dodaj remont', command=dodaj_remont)
            button_remonty_dodaj_remont.grid(row=3, column=0, columnspan=2)

            # ---------------------------------------
            # ramka remonty_szczegoly
            # ---------------------------------------
            label_remonty_opis_obiektu = Label(ramka_remonty_szczegoly, text='Szczegóły remontu:', font=('Arial', 10))
            label_remonty_odc_start_szczegoly = Label(ramka_remonty_szczegoly, text='Punkt początkowy')
            label_remonty_odc_start_szczegoly_wartosc = Label(ramka_remonty_szczegoly, text='...', width=20)

            label_remonty_odc_koniec_szczegoly = Label(ramka_remonty_szczegoly, text='Punkt końcowy')
            label_remonty_odc_koniec_szczegoly_wartosc = Label(ramka_remonty_szczegoly, text='...', width=20)

            label_remonty_srodek_szczegoly = Label(ramka_remonty_szczegoly, text='Współrzędne środka')
            label_remonty_srodek_szczegoly_wartosc = Label(ramka_remonty_szczegoly, text='...', width=20)

            label_remonty_liczba_szczegoly = Label(ramka_remonty_szczegoly, text='Liczba pracowników')
            label_remonty_liczba_szczegoly_wartosc = Label(ramka_remonty_szczegoly, text='...', width=20)

            label_remonty_opis_obiektu.grid(row=0, column=0, columnspan=8, pady=10)

            label_remonty_odc_start_szczegoly.grid(row=1, column=0)
            label_remonty_odc_start_szczegoly_wartosc.grid(row=2, column=0)

            label_remonty_odc_koniec_szczegoly.grid(row=1, column=1)
            label_remonty_odc_koniec_szczegoly_wartosc.grid(row=2, column=1)

            label_remonty_srodek_szczegoly.grid(row=1, column=2)
            label_remonty_srodek_szczegoly_wartosc.grid(row=2, column=2)

            label_remonty_liczba_szczegoly.grid(row=1, column=3)
            label_remonty_liczba_szczegoly_wartosc.grid(row=2, column=3)

            root_remonty_all.mainloop()


        def pracownicy():

            def center_widgets_pracownicy(event=None):
                window_width = root_pracownicy_all.winfo_width()
                frame_height=root_pracownicy.winfo_height()

                root_pracownicy.place(x=window_width // 2, y=frame_height/2, anchor='center')

            def pokaz_wszystko_pracownicy():
                radiobutton_all.select()
                listbox_pracownicy.delete(0, END)
                sql_query_1 = f"SELECT * FROM public.pracownicy ORDER BY id ASC;"
                cursor.execute(sql_query_1)
                query_result = cursor.fetchall()
                for idx, row in enumerate(query_result):
                    listbox_pracownicy.insert(idx, f'Pracownik {row[1]} {row[2]}' )

            def pokaz_autoid_pracownicy():
                pokaz_wszystko_pracownicy()
                auto_id_pracownicy_aktualizacja()

            def pokaz_zaznaczone_pracownicy():
                if var.get()==1:
                    pokaz_wszystko_pracownicy()
                elif var.get()==2:
                    odc_start=entry_start_odc_start.get()
                    odc_koniec=entry_start_odc_koniec.get()

                    listbox_pracownicy.delete(0, END)
                    sql_query_1 = f"SELECT * FROM public.pracownicy WHERE odc_start='{odc_start}' and odc_koniec='{odc_koniec}' ORDER BY id ASC;"
                    cursor.execute(sql_query_1)
                    query_result = cursor.fetchall()
                    for idx, row in enumerate(query_result):
                        listbox_pracownicy.insert(idx, f'Pracownik {row[1]} {row[2]}')

            def dodaj_pracownika():
                imie=entry_pracownicy_imie.get()
                nazwisko=entry_pracownicy_nazwisko.get()
                zamieszkanie=entry_pracownicy_zamieszkanie.get()
                poczatek_remontu=entry_pracownicy_odc_start.get()
                koniec_remontu=entry_pracownicy_odc_koniec.get()

                sql_query_1 = f"INSERT INTO public.pracownicy(id, imie, nazwisko, zamieszkanie, odc_start, odc_koniec) VALUES ('{auto_id_pracownicy_dodawanie()}', '{imie}', '{nazwisko}', '{zamieszkanie}', '{poczatek_remontu}', '{koniec_remontu}');"
                cursor.execute(sql_query_1)
                db_params.commit()

                entry_pracownicy_imie.delete(0, END)
                entry_pracownicy_nazwisko.delete(0, END)
                entry_pracownicy_zamieszkanie.delete(0, END)
                entry_pracownicy_odc_start.delete(0, END)
                entry_pracownicy_odc_koniec.delete(0, END)

                pokaz_zaznaczone_pracownicy()

            def edytuj_pracownika():
                i=listbox_pracownicy.index(ACTIVE)

                entry_pracownicy_imie.delete(0, END)
                entry_pracownicy_nazwisko.delete(0, END)
                entry_pracownicy_zamieszkanie.delete(0, END)
                entry_pracownicy_odc_start.delete(0, END)
                entry_pracownicy_odc_koniec.delete(0, END)

                if var.get() == 1:
                    sql_query_1 = f"SELECT * FROM public.pracownicy ORDER BY id ASC;"
                    cursor.execute(sql_query_1)
                    query_result = cursor.fetchall()

                elif var.get()==2:
                    odc_start=entry_start_odc_start.get()
                    odc_koniec=entry_start_odc_koniec.get()

                    sql_query_1 = f"SELECT * FROM public.pracownicy WHERE odc_start='{odc_start}' and odc_koniec='{odc_koniec}' ORDER BY id ASC;"
                    cursor.execute(sql_query_1)
                    query_result = cursor.fetchall()

                entry_pracownicy_imie.insert(0, query_result[i][1])
                entry_pracownicy_nazwisko.insert(0, query_result[i][2])
                entry_pracownicy_zamieszkanie.insert(0, query_result[i][3])
                entry_pracownicy_odc_start.insert(0, query_result[i][4])
                entry_pracownicy_odc_koniec.insert(0, query_result[i][5])

                button_pracownicy_dodaj_pracownika.config(text='Zapisz zmiany', command=lambda: aktualizuj_pracownika(i))

            def aktualizuj_pracownika(i):
                if var.get() == 1:
                    sql_query_1 = f"SELECT * FROM public.pracownicy ORDER BY id ASC;"
                    cursor.execute(sql_query_1)
                    query_result = cursor.fetchall()

                elif var.get()==2:
                    odc_start=entry_start_odc_start.get()
                    odc_koniec=entry_start_odc_koniec.get()

                    sql_query_1 = f"SELECT * FROM public.pracownicy WHERE odc_start='{odc_start}' and odc_koniec='{odc_koniec}' ORDER BY id ASC;"
                    cursor.execute(sql_query_1)
                    query_result = cursor.fetchall()

                imie=entry_pracownicy_imie.get()
                nazwisko=entry_pracownicy_nazwisko.get()
                zamieszkanie=entry_pracownicy_zamieszkanie.get()
                poczatek_remontu=entry_pracownicy_odc_start.get()
                koniec_remontu=entry_pracownicy_odc_koniec.get()

                sql_query_2 = f"SELECT * FROM public.pracownicy WHERE imie='{query_result[i][1]}' and nazwisko='{query_result[i][2]}' and zamieszkanie='{query_result[i][3]}' and odc_start='{query_result[i][4]}' and odc_koniec='{query_result[i][5]}' ORDER BY id ASC;"
                cursor.execute(sql_query_2)
                query_result_2 = cursor.fetchall()

                sql_query_3 = f"UPDATE public.pracownicy SET imie='{imie}', nazwisko='{nazwisko}', zamieszkanie='{zamieszkanie}', odc_start='{poczatek_remontu}',odc_koniec='{koniec_remontu}' WHERE imie='{query_result_2[0][1]}' and nazwisko='{query_result_2[0][2]}' and zamieszkanie='{query_result_2[0][3]}' and odc_start='{query_result_2[0][4]}' and odc_koniec='{query_result_2[0][5]}';"
                cursor.execute(sql_query_3)
                db_params.commit()

                button_pracownicy_dodaj_pracownika.config(text='Dodaj pracownika', command=dodaj_pracownika)

                entry_pracownicy_imie.delete(0, END)
                entry_pracownicy_nazwisko.delete(0, END)
                entry_pracownicy_zamieszkanie.delete(0, END)
                entry_pracownicy_odc_start.delete(0, END)
                entry_pracownicy_odc_koniec.delete(0, END)

                pokaz_zaznaczone_pracownicy()

            def usun_pracownika():
                i = listbox_pracownicy.index(ACTIVE)

                if var.get() == 1:
                    sql_query_1 = f"DELETE FROM public.pracownicy WHERE id='{i+1}';"
                    cursor.execute(sql_query_1)
                    db_params.commit()

                elif var.get() == 2:
                    start = entry_start_odc_start.get()
                    koniec = entry_start_odc_koniec.get()

                    sql_query_1 = f"SELECT * FROM public.pracownicy WHERE odc_start='{start}' and odc_koniec='{koniec}' ORDER BY id ASC;"
                    cursor.execute(sql_query_1)
                    query_result = cursor.fetchall()

                    for temp_idx, row in enumerate(query_result):
                        row=row+(temp_idx+1,)
                        if row[6]==i+1:
                            id_to_remove=row[0]

                    sql_query_2 = f"DELETE FROM public.pracownicy WHERE id='{id_to_remove}';"
                    cursor.execute(sql_query_2)
                    db_params.commit()

                pokaz_zaznaczone_pracownicy()

            def pokaz_pracownika():
                if var.get()==1:
                    sql_query_1 = f"SELECT * FROM public.pracownicy ORDER BY id ASC;"
                    cursor.execute(sql_query_1)
                    query_result = cursor.fetchall()

                elif var.get()==2:
                    start = entry_start_odc_start.get()
                    koniec = entry_start_odc_koniec.get()

                    sql_query_1 = f"SELECT * FROM public.pracownicy WHERE odc_start='{start}' and odc_koniec='{koniec}' ORDER BY id ASC;"
                    cursor.execute(sql_query_1)
                    query_result = cursor.fetchall()

                i = listbox_pracownicy.index(ACTIVE)

                imie=query_result[i][1]
                nazwisko=query_result[i][2]
                zamieszkanie=query_result[i][3]
                start=query_result[i][4]
                koniec=query_result[i][5]

                label_pracownicy_imie_szczegoly_wartosc.config(text=imie)
                label_pracownicy_nazwisko_szczegoly_wartosc.config(text=nazwisko)
                label_pracownicy_zamieszkanie_szczegoly_wartosc.config(text=zamieszkanie)
                label_pracownicy_odc_start_szczegoly_wartosc.config(text=start)
                label_pracownicy_odc_koniec_szczegoly_wartosc.config(text=koniec)

            root_pracownicy_all = Toplevel(root_choice)
            root_pracownicy_all.title('Utrudnienia drogowe')
            szer = 690
            wys = 490
            root_pracownicy_all.geometry(f'{szer}x{wys}')
            root_pracownicy_all.bind('<Configure>', center_widgets_pracownicy)

            root_pracownicy=Frame(root_pracownicy_all)
            root_pracownicy.grid(row=0, column=0)

            ramka_pracownicy_start = Frame(root_pracownicy)
            ramka_pracownicy_lista = Frame(root_pracownicy)
            ramka_pracownicy_formularz = Frame(root_pracownicy)
            ramka_pracownicy_szczegoly = Frame(root_pracownicy)

            ramka_pracownicy_start.grid(row=0, column=0, columnspan=2)
            ramka_pracownicy_lista.grid(row=1, column=0)
            ramka_pracownicy_formularz.grid(row=1, column=1)
            ramka_pracownicy_szczegoly.grid(row=2, column=0, columnspan=2)

            # ---------------------------------------
            # ramka pracownicy_start
            # ---------------------------------------
            label_pracownicy_lista = Label(ramka_pracownicy_start, text='Lista pracowników remontów drogowych', font=('Arial', 12, 'bold'))
            button_pracownicy_pokaz_liste = Button(ramka_pracownicy_start, text='Pokaż wszystko', command=pokaz_autoid_pracownicy)
            label_pracownicy_wybor = Label(ramka_pracownicy_start, text='Wybierz formułę wyświetlania pracowników')
            var = IntVar()
            radiobutton_all = Radiobutton(ramka_pracownicy_start, text='Wszyscy pracownicy', variable=var, value=1)
            radiobutton_some = Radiobutton(ramka_pracownicy_start, text='Pracownicy z danego odcinka (początek - koniec)', variable=var, value=2)
            entry_start_odc_start = Entry(ramka_pracownicy_start)
            label_start_myslnik = Label(ramka_pracownicy_start, text=' - ')
            entry_start_odc_koniec = Entry(ramka_pracownicy_start)
            button_pracownicy_pokaz_wybrane = Button(ramka_pracownicy_start, text='Pokaż zaznaczone', command=pokaz_zaznaczone_pracownicy)

            label_pracownicy_lista.grid(row=0, column=0, columnspan=3, padx=(szer / 2 - label_pracownicy_lista.winfo_reqwidth() / 2), pady=(10, 0))
            button_pracownicy_pokaz_liste.grid(row=1, column=0, columnspan=3)
            label_pracownicy_wybor.grid(row=2, column=0, pady=(10, 0), columnspan=3)
            radiobutton_all.grid(row=3, column=0, columnspan=3)
            radiobutton_some.grid(row=4, column=0, columnspan=3)
            entry_start_odc_start.grid(row=5, column=0, sticky=E)
            label_start_myslnik.grid(row=5, column=1)
            entry_start_odc_koniec.grid(row=5, column=2, sticky=W)
            button_pracownicy_pokaz_wybrane.grid(row=6, column=0, columnspan=3)

            # ---------------------------------------
            # ramka pracownicy_lista
            # ---------------------------------------
            listbox_pracownicy = Listbox(ramka_pracownicy_lista, width=50)
            button_pracownicy_pokaz_szczegoly = Button(ramka_pracownicy_lista, text='Pokaż dane pracownika', command=pokaz_pracownika)
            button_pracownicy_usun = Button(ramka_pracownicy_lista, text='Usuń pracownika', command=usun_pracownika)
            button_pracownicy_edytuj = Button(ramka_pracownicy_lista, text='Edytuj pracownika', command=edytuj_pracownika)

            listbox_pracownicy.grid(row=0, column=0, columnspan=3, pady=(10, 0))
            button_pracownicy_pokaz_szczegoly.grid(row=1, column=0)
            button_pracownicy_usun.grid(row=1, column=1)
            button_pracownicy_edytuj.grid(row=1, column=2)

            # ---------------------------------------
            # ramka pracownicy_formularz
            # ---------------------------------------
            label_pracownicy_nowy_obiekt = Label(ramka_pracownicy_formularz, text='Formularz edycji i dodawania:', font=('Arial', 10))
            label_pracownicy_imie = Label(ramka_pracownicy_formularz, text='Imię')
            label_pracownicy_nazwisko = Label(ramka_pracownicy_formularz, text='Nazwisko')
            label_pracownicy_zamieszkanie = Label(ramka_pracownicy_formularz, text='Zamieszkały/a')
            label_pracownicy_odc_start = Label(ramka_pracownicy_formularz, text='Początek remontu')
            label_pracownicy_odc_koniec = Label(ramka_pracownicy_formularz, text='Koniec remontu')

            entry_pracownicy_imie = Entry(ramka_pracownicy_formularz)
            entry_pracownicy_nazwisko = Entry(ramka_pracownicy_formularz)
            entry_pracownicy_zamieszkanie = Entry(ramka_pracownicy_formularz)
            entry_pracownicy_odc_start = Entry(ramka_pracownicy_formularz)
            entry_pracownicy_odc_koniec = Entry(ramka_pracownicy_formularz)

            label_pracownicy_nowy_obiekt.grid(row=0, column=0, columnspan=2)
            label_pracownicy_imie.grid(row=1, column=0, sticky=W)
            label_pracownicy_nazwisko.grid(row=2, column=0, sticky=W)
            label_pracownicy_zamieszkanie.grid(row=3, column=0, sticky=W)
            label_pracownicy_odc_start.grid(row=4, column=0, sticky=W)
            label_pracownicy_odc_koniec.grid(row=5, column=0, sticky=W)

            entry_pracownicy_imie.grid(row=1, column=1, sticky=W)
            entry_pracownicy_nazwisko.grid(row=2, column=1, sticky=W)
            entry_pracownicy_zamieszkanie.grid(row=3, column=1, sticky=W)
            entry_pracownicy_odc_start.grid(row=4, column=1, sticky=W)
            entry_pracownicy_odc_koniec.grid(row=5, column=1, sticky=W)

            button_pracownicy_dodaj_pracownika = Button(ramka_pracownicy_formularz, text='Dodaj pracownika', command=dodaj_pracownika)
            button_pracownicy_dodaj_pracownika.grid(row=6, column=0, columnspan=2)

            # ---------------------------------------
            # ramka pracownicy_szczegoly
            # ---------------------------------------
            label_pracownicy_opis_obiektu = Label(ramka_pracownicy_szczegoly, text='Szczegóły pracowników:', font=('Arial', 10))
            label_pracownicy_imie_szczegoly = Label(ramka_pracownicy_szczegoly, text='Imię')
            label_pracownicy_imie_szczegoly_wartosc = Label(ramka_pracownicy_szczegoly, text='...', width=20)

            label_pracownicy_nazwisko_szczegoly = Label(ramka_pracownicy_szczegoly, text='Nazwisko')
            label_pracownicy_nazwisko_szczegoly_wartosc = Label(ramka_pracownicy_szczegoly, text='...', width=20)

            label_pracownicy_zamieszkanie_szczegoly = Label(ramka_pracownicy_szczegoly, text='Zamieszkały/a')
            label_pracownicy_zamieszkanie_szczegoly_wartosc = Label(ramka_pracownicy_szczegoly, text='...', width=20)

            label_pracownicy_odc_start_szczegoly = Label(ramka_pracownicy_szczegoly, text='Punkt początkowy')
            label_pracownicy_odc_start_szczegoly_wartosc = Label(ramka_pracownicy_szczegoly, text='...', width=20)

            label_pracownicy_odc_koniec_szczegoly = Label(ramka_pracownicy_szczegoly, text='Punkt końcowy')
            label_pracownicy_odc_koniec_szczegoly_wartosc = Label(ramka_pracownicy_szczegoly, text='...', width=20)

            label_pracownicy_opis_obiektu.grid(row=0, column=0, columnspan=5, pady=10)

            label_pracownicy_imie_szczegoly.grid(row=1, column=0)
            label_pracownicy_imie_szczegoly_wartosc.grid(row=2, column=0)

            label_pracownicy_nazwisko_szczegoly.grid(row=1, column=1)
            label_pracownicy_nazwisko_szczegoly_wartosc.grid(row=2, column=1)

            label_pracownicy_zamieszkanie_szczegoly.grid(row=1, column=2)
            label_pracownicy_zamieszkanie_szczegoly_wartosc.grid(row=2, column=2)

            label_pracownicy_odc_start_szczegoly.grid(row=1, column=3)
            label_pracownicy_odc_start_szczegoly_wartosc.grid(row=2, column=3)

            label_pracownicy_odc_koniec_szczegoly.grid(row=1, column=4)
            label_pracownicy_odc_koniec_szczegoly_wartosc.grid(row=2, column=4)

            root_pracownicy.mainloop()


        def mapa():

            def center_widgets_mapa(event=None):
                window_width = root_mapa_all.winfo_width()
                frame_height=root_mapa.winfo_height()

                root_mapa.place(x=window_width // 2, y=frame_height/2, anchor='center')

            def center_map_remonty(lista:list):
                lats=[]
                lons=[]

                for tuple_of_pairs in lista:
                    for pair in tuple_of_pairs:
                        lats.append(pair[0])
                        lons.append(pair[1])

                min_lat = min(lat for lat in lats)
                max_lat = max(lat for lat in lats)
                min_lon = min(lon for lon in lons)
                max_lon = max(lon for lon in lons)

                center_lat = (float(min_lat) + float(max_lat)) / 2
                center_lon = (float(min_lon) + float(max_lon)) / 2

                return (center_lat, center_lon)

            def extent_zoom_remonty(lista:list):
                lats=[]
                lons=[]

                for tuple_of_pairs in lista:
                    for pair in tuple_of_pairs:
                        lats.append(pair[0])
                        lons.append(pair[1])

                min_lat = min(lat for lat in lats)
                max_lat = max(lat for lat in lats)
                min_lon = min(lon for lon in lons)
                max_lon = max(lon for lon in lons)

                extent_width=float(max_lat) - float(min_lat)
                extent_height=float(max_lon) - float(min_lon)

                extent_width_zoom=math.log(extent_width / 1155) / (-0.716)
                extent_height_zoom=math.log(extent_height / 260) / (-0.69)

                if extent_height_zoom<extent_width_zoom:
                    return int(round(extent_height_zoom,0))
                else:
                    return int(round(extent_width_zoom,0))

            def center_map_pracownicy(lista: list):
                lats = []
                lons = []

                for pair in lista:
                    lats.append(pair[0])
                    lons.append(pair[1])

                min_lat = min(lat for lat in lats)
                max_lat = max(lat for lat in lats)
                min_lon = min(lon for lon in lons)
                max_lon = max(lon for lon in lons)

                center_lat = (float(min_lat) + float(max_lat)) / 2
                center_lon = (float(min_lon) + float(max_lon)) / 2

                return (center_lat, center_lon)

            def extent_zoom_pracownicy(lista: list):
                lats = []
                lons = []

                for pair in lista:
                    lats.append(pair[0])
                    lons.append(pair[1])

                min_lat = min(lat for lat in lats)
                max_lat = max(lat for lat in lats)
                min_lon = min(lon for lon in lons)
                max_lon = max(lon for lon in lons)

                extent_width = float(max_lat) - float(min_lat)
                extent_height = float(max_lon) - float(min_lon)

                extent_width_zoom = math.log(extent_width / 1155) / (-0.716)
                extent_height_zoom = math.log(extent_height / 260) / (-0.69)

                if extent_height_zoom < extent_width_zoom:
                    return int(round(extent_height_zoom, 0))
                else:
                    return int(round(extent_width_zoom, 0))

            def mapa_odcinki():
                sql_query_1 = f"SELECT * FROM public.prace_drogowe ORDER BY id ASC;"
                cursor.execute(sql_query_1)
                query_result = cursor.fetchall()

                tuples_coords_for_map=[]
                for row in query_result:
                    start=get_coordinates(row[1])
                    koniec=get_coordinates(row[2])
                    odc_coords=(start, koniec)
                    tuples_coords_for_map.append(odc_coords)

                mapa = TkinterMapView(ramka_mapa, width=700, height=300, corner_radius=0)
                mapa.set_position(center_map_remonty(tuples_coords_for_map)[0], center_map_remonty(tuples_coords_for_map)[1])
                mapa.set_zoom(extent_zoom_remonty(tuples_coords_for_map))
                mapa.grid(row=7, column=0, columnspan=3, pady=(10,0))

                tuples_coords = []
                for row in query_result:
                    start=get_coordinates(row[1])
                    koniec=get_coordinates(row[2])
                    odc_coords=(start, koniec)
                    tuples_coords.append(odc_coords)
                    marker_1=mapa.set_marker(start[0], start[1], text=f'{row[1]}\n', font=('Arial', 10, 'bold'), text_color='black')
                    marker_2=mapa.set_marker(koniec[0], koniec[1], text=f'{row[2]}\n', font=('Arial', 10, 'bold'), text_color='black')
                    mapa.set_path([marker_1.position, marker_2.position], color='red', width=4)

            def mapa_pracowicy():
                sql_query_1 = f"SELECT * FROM public.pracownicy ORDER BY id ASC;"
                cursor.execute(sql_query_1)
                query_result = cursor.fetchall()

                coords_for_map=[]
                for row in query_result:
                    zamieszkanie=get_coordinates(row[3])
                    coords_for_map.append(zamieszkanie)

                mapa = TkinterMapView(ramka_mapa, width=700, height=300, corner_radius=0)
                mapa.set_position(center_map_pracownicy(coords_for_map)[0], center_map_pracownicy(coords_for_map)[1])
                mapa.set_zoom(extent_zoom_pracownicy(coords_for_map))
                mapa.grid(row=7, column=0, columnspan=3, pady=(10,0))

                for row in query_result:
                    zamieszkanie=get_coordinates(row[3])
                    mapa.set_marker(zamieszkanie[0], zamieszkanie[1], text=f'{row[1]} {row[2]}', font=('Arial', 8), text_color='black')

            def mapa_pracowicy_z_odcinka():
                start=entry_mapa_odc_start.get()
                koniec=entry_mapa_odc_koniec.get()

                sql_query_1 = f"SELECT * FROM public.pracownicy WHERE odc_start='{start}' and odc_koniec='{koniec}' ORDER BY id ASC;"
                cursor.execute(sql_query_1)
                query_result = cursor.fetchall()

                coords_for_map=[]
                for row in query_result:
                    zamieszkanie=get_coordinates(row[3])
                    coords_for_map.append(zamieszkanie)

                mapa = TkinterMapView(ramka_mapa, width=700, height=300, corner_radius=0)
                mapa.set_position(center_map_pracownicy(coords_for_map)[0], center_map_pracownicy(coords_for_map)[1])
                mapa.set_zoom(extent_zoom_pracownicy(coords_for_map))
                mapa.grid(row=7, column=0, columnspan=3, pady=(10,0))

                for row in query_result:
                    zamieszkanie=get_coordinates(row[3])
                    mapa.set_marker(zamieszkanie[0], zamieszkanie[1], text=f'{row[1]} {row[2]}', font=('Arial', 8), text_color='black')

            root_mapa_all = Toplevel(root_choice)
            root_mapa_all.title('Utrudnienia drogowe')
            szer = 800
            wys = 600
            root_mapa_all.geometry(f'{szer}x{wys}')
            root_mapa_all.bind('<Configure>', center_widgets_mapa)

            root_mapa=Frame(root_mapa_all)
            root_mapa.grid(row=0, column=0)

            ramka_mapa = Frame(root_mapa)
            ramka_mapa.grid(row=0, column=3, columnspan=2)

            # ---------------------------------------
            # ramka mapa
            # ---------------------------------------
            label_mapa_start = Label(ramka_mapa, text='Portal mapowy', font=('Arial', 12, 'bold'))
            label_mapa_wybor = Label(ramka_mapa, text='Wybierz mapę do wyświetlenia:')
            label_mapa_remonty = Label(ramka_mapa, text='Mapa wszystkich remontowanych odcinków')
            button_mapa_remonty = Button(ramka_mapa, text='Wyświetl', command=mapa_odcinki)
            label_mapa_pracownicy = Label(ramka_mapa, text='Mapa wszystkich pracowników')
            button_mapa_pracownicy = Button(ramka_mapa, text='Wyświetl', command=mapa_pracowicy)
            label_mapa_pracownicy_remontu = Label(ramka_mapa, text='Mapa pracowników wybranego remontowanego odcinka')
            label_mapa_odc_start = Label(ramka_mapa, text='Start')
            entry_mapa_odc_start = Entry(ramka_mapa)
            label_mapa_odc_koniec = Label(ramka_mapa, text='Koniec')
            entry_mapa_odc_koniec = Entry(ramka_mapa)
            button_mapa_pracownicy_remontu = Button(ramka_mapa, text='Wyświetl', command=mapa_pracowicy_z_odcinka)

            label_mapa_start.grid(row=0, column=0, columnspan=3, pady=(10, 0))
            label_mapa_wybor.grid(row=1, column=0, columnspan=3)
            label_mapa_remonty.grid(row=2, column=0, sticky=W)
            button_mapa_remonty.grid(row=2, column=1, sticky=E)
            label_mapa_pracownicy.grid(row=3, column=0, sticky=W)
            button_mapa_pracownicy.grid(row=3, column=1, sticky=E)
            label_mapa_pracownicy_remontu.grid(row=4, column=0, sticky=W)
            label_mapa_odc_start.grid(row=5, column=0, sticky=W)
            entry_mapa_odc_start.grid(row=5, column=0, padx=50, sticky=W)
            label_mapa_odc_koniec.grid(row=6, column=0, sticky=W)
            entry_mapa_odc_koniec.grid(row=6, column=0, padx=50, sticky=W)
            button_mapa_pracownicy_remontu.grid(row=6, column=1, sticky=E)

            root_mapa.mainloop()

        def center_widgets_choice(event=None):
            window_width = root_choice.winfo_width()
            frame_height = ramka_wybor.winfo_height()

            ramka_wybor.place(x=window_width // 2, y=frame_height / 2, anchor='center')

        root_pass.withdraw()

        root_choice=Toplevel()
        root_choice.title('Wybór funkcjonalności')
        root_choice.geometry('270x110')

        root_choice.bind('<Configure>', center_widgets_choice)

        ramka_wybor=Frame(root_choice)
        ramka_wybor.grid(row=0, column=0)

        label_wybor_opcje=Label(ramka_wybor,text='Wybierz funkcjonalność do uruchomienia')
        label_wybor_remonty=Label(ramka_wybor, text='Lista remontowanych odcinków')
        label_wybor_pracownicy=Label(ramka_wybor, text='Lista pracowników remontów')
        label_wybor_mapa=Label(ramka_wybor, text='Portal mapowy')
        button_wybor_remonty=Button(ramka_wybor,text='Wybierz', command=remonty)
        button_wybor_pracownicy=Button(ramka_wybor,text='Wybierz', command=pracownicy)
        button_wybor_mapa=Button(ramka_wybor,text='Wybierz', command=mapa)

        label_wybor_opcje.grid(row=0, column=0, columnspan=2)
        label_wybor_remonty.grid(row=1, column=0, sticky=W)
        label_wybor_pracownicy.grid(row=2, column=0, sticky=W)
        label_wybor_mapa.grid(row=3, column=0, sticky=W)
        button_wybor_remonty.grid(row=1, column=1, sticky=E)
        button_wybor_pracownicy.grid(row=2, column=1, sticky=E)
        button_wybor_mapa.grid(row=3, column=1, sticky=E)

        root_choice.mainloop()

    else:
        wrong_label=Label(ramka_logowanie,text='Błędne hasło, spróbuj jeszcze raz')
        wrong_label.grid(row=2, column=0, columnspan=2, padx=3)
        logowanie_entry.delete(0, END)
        logowanie_entry.focus()


def center_widgets_pass(event=None):
    window_width = root_pass.winfo_width()
    frame_height = ramka_logowanie.winfo_height()

    ramka_logowanie.place(x=window_width // 2, y=frame_height / 2, anchor='center')

root_pass=Tk()
root_pass.title('Utrudnienia drogowe - logowanie')
root_pass.geometry('195x70')

root_pass.bind('<Configure>', center_widgets_pass)

ramka_logowanie=Frame(root_pass)
ramka_logowanie.grid(row=0, column=0)

logowanie_napis=Label(ramka_logowanie, text='Podaj hasło dostępu')
logowanie_entry=Entry(ramka_logowanie, width=20, show='•')
logowanie_entry.bind('<Return>', logowanie)
logowanie_button=Button(ramka_logowanie, text='Enter', command=logowanie)

logowanie_napis.grid(row=0, column=0, columnspan=2)
logowanie_entry.grid(row=1, column=0, padx=(3,0))
logowanie_button.grid(row=1, column=1, columnspan=2)

root_pass.mainloop()