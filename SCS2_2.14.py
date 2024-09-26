from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import os.path
import time
import os
import shutil
import datetime
from pathlib import Path
from PIL import ImageTk, Image
import sqlite3
from configparser import ConfigParser

#ChangeLog:
#Inventory_amount zdaj bere iz SQL
#Dodano opozorilo za odsotnost database patha


ver = "v2.14"
local = "C:\\Users\\M\\Desktop\\scscout2"
# script_path = Path(__file__).parent
# local = script_path
# remote = C:\\Users\\M\\Desktop\\scscout\\Desktop-iqqp1bg\\SC programi
# database = C:\\Users\\M\\Desktop\\scscout\\remotedb
# database = \\\\192.168.50.30\\Dokumentacija\\SC programi
suf = '.txt'
suf19 = '.s19'
array = ["253isc", "303isc", "403isc-sw", "403isc-w", "imax30-300ie", "imax40-380ie", "imig250", "imig300",
         "imig400", "210sdsc", "253digit", "303digit", "403digit", 'Iskra-standard']

stm8_array = ['SYN-INVERTER-250-OCV-4', 'STM8 SYN-INVERTER-4-1-B25', 'SYN-INVERTER-300-OCV-5',
              'STM8 SYN-INVERTER-4-0-B30', 'SYN-INVERTER-400-OCV3', 'STM8 SYN-INVERTER-4-0-S4WS',
              'STM8 SYN-INVERTER-4-0-S4', 'STM8 SYN-INVERTER-4-2-T30', 'STM8 SYN-INVERTER-4-2-T4',
              'STM8 SYN-INVERTER-4-2-B25', 'STM8 SYN-INVERTER-4-2-T30', 'STM8 SYN-INVERTER-4-2-T4',
              'STM8 SYN-FCW-8899-P3-FT']

connection = None
connection_db = None

config = ConfigParser()
config.read('configfile.ini')
remote_data = config['HOST']
remote = remote_data['remote']
database_data = config['HOST']
database = database_data['database']
config_data = config['DEF']
frame_config_val = int(config_data['frame'])
var_set = int(config_data['frame'])

class Scout(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        master.title('ScoutSC 2')
        master.geometry('510x420+500+500')
        master.resizable(width=False, height=False)
        master.minsize(width=510, height=420)

        self.master = master
        self.pack(fill=BOTH, expand=True)
        self.check_connection()
        self.check_connection_db()
        if frame_config_val == 0:
            self.layout_panels('gray94', 'gray94', 'gray94', 'gray94')
        elif frame_config_val == 1:
            self.layout_panels('red', 'green', 'yellow', 'blue')
        self.default_widgets()
        self.startup_check()
        self.menu_bar()
        self.slika()

    def check_connection(self):
        if os.path.exists(remote):
            global connection
            connection = True
        else:
            connection = False

    def check_connection_db(self):
        if os.path.exists(database):
            global connection_db
            connection_db = True
        else:
            connection_db = False

    def layout_panels(self, cl1, cl2, cl3, cl4):
        self.main_line_panel = Frame(self, bg=cl1, width=480, height=50)
        self.status_panel = Frame(self, bg=cl2, width=480, height=30, bd=1)#, relief=SUNKEN)
        self.left_panel = Frame(self, bg=cl3, width=80, height=280)
        self.right_panel = Frame(self, bg=cl4, width=450, height=450)

        self.main_line_panel.pack(side="top", fill='x', expand=False)
        self.status_panel.pack(side="bottom", fill='both', expand=False)
        self.left_panel.pack(side="left", fill='both', expand=False)
        self.right_panel.pack(side="right", fill='both', expand=True)

    def default_widgets(self):
        button_aparati = Button(self.main_line_panel, text='Aparati', width=10, bg='gray80', command=self.aparati)
        button_invertar = Button(self.main_line_panel, text='Skladisce', width=10, bg='gray80', command=self.invertar)
        ver_label = Label(root, text=ver)
        status = Label(self.status_panel, text=self.cstatus(), height=1, anchor=E, relief=SUNKEN)
        status_db = Label(self.status_panel, text=self.cstatus_db(), anchor=E, relief=SUNKEN)
        self.ready = Button(self.status_panel, text='Ready/Refresh', height=1, anchor=W, relief=SUNKEN, command=self.refresh)

        button_aparati.pack(side="left", anchor=N)
        button_invertar.pack(side="left", anchor=N)
        ver_label.place(relx=1.0, rely=0.0, anchor='ne')
        status.pack(anchor=NE, side="right", fill='y', expand=False)
        status_db.pack(anchor=NE, side="right", fill='y', expand=False)
        self.ready.pack(anchor=NW, side="left", fill='x', expand=True)

    def slika(self):
        img = ImageTk.PhotoImage(Image.open('scimg.png'))
        img_label = Label(self.right_panel, image=img)
        img_label.image = img
        img_label.pack(anchor=NW, expand=0, fill='none', padx=30)

    def refresh(self):
        for widget in self.status_panel.winfo_children():
            widget.destroy()
        for widget in self.main_line_panel.winfo_children():
            widget.destroy()
        for widget in self.left_panel.winfo_children():
            widget.destroy()
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        self.check_connection()
        self.check_connection_db()
        self.default_widgets()
        self.startup_check()
        self.slika()

    def menu_bar(self):
        bar_menu = Menu(root)
        root.config(menu=bar_menu)

        file_menu = Menu(bar_menu)
        bar_menu.add_cascade(label='Datoteka', menu=file_menu)
        file_menu.add_command(label='Nastavitve', command=self.file_nastavitve)
        file_menu.add_separator()
        file_menu.add_command(label='Izhod', command=self.quit)

    def file_nastavitve(self):
        for widget in Frame.winfo_children(self):
            widget.destroy()
        self.file_new_frame = Frame(self, width=480, height=360)
        self.file_new_frame.pack(fill='both', expand=True)

        frame = LabelFrame(self.file_new_frame, text='Jezik', width=300, height=50)
        frame2 = LabelFrame(self.file_new_frame, text='Orodja', width=300, height=50)
        frame3 = LabelFrame(self.file_new_frame, text='Remote direktorij', width=300, height=50)
        frame4 = LabelFrame(self.file_new_frame, text='SQL Direktorij', width=300, height=50)
        frame.pack(side="top", fill=None, anchor=NW, expand=False, padx=20, pady=5)
        frame2.pack(side="top", fill=None, anchor=NW, expand=False, padx=20, pady=5)
        frame3.pack(side="top", fill=None, anchor=NW, expand=False, padx=20, pady=5)
        frame4.pack(side="top", fill=None, anchor=NW, expand=False, padx=20, pady=5)

        drop = ttk.Combobox(frame, value='Slovenscina')
        drop.current(0)
        drop.pack()

        config.read('configfile.ini')
        con_data = config['DEF']
        frame_config_val = int(con_data['frame'])
        #global var
        var = IntVar()
        if frame_config_val == 1:
            var.set(1)
        elif frame_config_val == 0:
            var.set(0)

        def intvar():
            global var_set
            var_set = var.get()

        checkbox = Checkbutton(frame2, text='Pokazi okvirje', variable=var, command=intvar)
        checkbox.pack()

        # listbox_remote = Listbox(frame3, width=65, height=3)
        # listbox_remote.pack()
        self.select_remote = Entry(frame3, width=65)
        self.select_remote.pack()
        self.select_remote.insert(0, remote)
        # entry_remote = Entry(frame3, width=65)
        # entry_remote.pack()
        # button_add = Button(self.file_new_frame, text='Dodaj', width=5, command=self.save)
        # button_add.place(relx=0.92, rely=0.462, anchor='ne')
        # rem_data = config['HOST']
        # database_insert = db_data['database']
        # entry_db.insert(0, database_insert)

        #listbox_db = Listbox(frame4, width=50, height=3)
        #listbox_db.pack()
        self.entry_db = Entry(frame4, width=65)
        self.entry_db.pack(pady=5)
        self.entry_db.insert(0, database)
        #button_add2 = Button(self.file_new_frame, text='Dodaj', width=5, command=self.save)
        #button_add2.place(relx=0.75, rely=0.69, anchor='ne')

        button_save = Button(self.file_new_frame, text='Shrani', width=10, command=self.save)
        button_cancel = Button(self.file_new_frame, text='Preklici', width=10, command=self.cancel)
        button_save.place(relx=0.81, rely=0.9, anchor='ne')
        button_cancel.place(relx=0.98, rely=0.9, anchor='ne')

    def save(self):
        global remote
        global database
        global frame_config_val

        remote = self.select_remote.get()
        database = self.entry_db.get()

        edit = ConfigParser()
        edit.read('configfile.ini')
        change_data = edit['DEF']
        change_data['frame'] = str(var_set)
        with open('configfile.ini', 'w') as file:
            edit.write(file)

        edit2 = ConfigParser()
        edit2.read('configfile.ini')
        change_remote = edit2['HOST']
        change_remote['remote'] = remote
        with open('configfile.ini', 'w') as file:
            edit2.write(file)

        edit3 = ConfigParser()
        edit3.read('configfile.ini')
        change_remote = edit3['HOST']
        change_remote['database'] = database
        with open('configfile.ini', 'w') as file:
            edit3.write(file)

        for widget in Frame.winfo_children(self):
            widget.destroy()
        config.read('configfile.ini')
        conf_data = config['DEF']
        frame_config_val = int(conf_data['frame'])
        if frame_config_val == 0:
            self.layout_panels('gray94', 'gray94', 'gray94', 'gray94')
        elif frame_config_val == 1:
            self.layout_panels('red', 'green', 'yellow', 'blue')
        self.check_connection()
        self.check_connection_db()
        self.default_widgets()
        self.startup_check()
        self.slika()

    def cancel(self):
        global remote
        global database
        global frame_config_val

        for widget in Frame.winfo_children(self):
            widget.destroy()

        config.read('configfile.ini')
        rem_data = config['HOST']
        remote = rem_data['remote']
        datab_data = config['HOST']
        database = datab_data['database']
        conf_data = config['DEF']
        frame_config_val = int(conf_data['frame'])

        if frame_config_val == 0:
            self.layout_panels('gray94', 'gray94', 'gray94', 'gray94')
        elif frame_config_val == 1:
            self.layout_panels('red', 'green', 'yellow', 'blue')
        self.default_widgets()
        self.startup_check()
        self.slika()

    def cstatus(self):
        #check_connection()
        if connection == True:
            return 'Dok: Povezano'
        else:
            return 'Dok: Brez povezave'

    def cstatus_db(self):
        #check_connection()
        if connection_db == True:
            return 'DB: Povezano'
        else:
            return 'DB: Brez povezave'

    def startup_check(self):
            if connection == True:
                for i in array:
                    self.scout_modtime_startup(i)
            # print(" ")
            # scout_modtime_startup_dir()
            # for k in array:
            #     update_offline(k)
            # print(" ")

    def scout_modtime_startup(self, ime):
        mod_time = os.path.getmtime(os.path.join(remote, ime))
        local_time = time.ctime(mod_time)
        with open(os.path.join(local, 'storedtime', ime + suf)) as file:
            stored_time = file.read()
            file.close()
        if stored_time != local_time:
            self.ready.pack_forget()
            self.spremembe = Button(self.status_panel, text=f'SPREMEMBE!  Aparat: {ime}', fg="red",
                                    relief=SUNKEN, height=1, anchor=W, command=lambda: self.read(ime))
            self.spremembe.pack(anchor=NW, side="left", fill='x', expand=True)

        elif stored_time == local_time:
            for s_array in stm8_array:
                if os.path.exists(os.path.join(remote, ime, s_array + suf19)):
                    mod_time_stm8 = os.path.getmtime(os.path.join(remote, ime, s_array + suf19))
                    local_time_stm8 = time.ctime(mod_time_stm8)
                    with open(os.path.join(local, 'storedtime', s_array + suf)) as file:
                        stored_time = file.read()
                        file.close()
                    if stored_time != local_time_stm8:
                        self.ready.pack_forget() #mozen crash, ce na enkrat spremeni vec razlicnih stm8 fajlov..
                        #..brez sprozitve modtime mape. Resitev je try.
                        self.spremembe = Button(self.status_panel, text=f'SPREMEMBE!  Aparat: {ime}', fg="red",
                                                relief=SUNKEN, height=1, anchor=W, command=lambda: self.read(ime))
                        self.spremembe.pack(anchor=NW, side="left", fill='x', expand=True)

    def aparati(self):
        for widget in self.main_line_panel.winfo_children():
            widget.destroy()
        for widget in self.left_panel.winfo_children():
            widget.destroy()
        for widget in self.right_panel.winfo_children():
            widget.destroy()

        self.slika()

        button_aparati = Button(self.main_line_panel, text='Aparati', width=10, bg='gray80', relief=SUNKEN, state=DISABLED)
        button_invertar = Button(self.main_line_panel, text='Skladisce', width=10, bg='gray80', command=self.invertar)
        button_aparati.pack(side="left", anchor=N)
        button_invertar.pack(side="left", anchor=N)

        space = Label(self.left_panel, text=' ')
        button_sturmer = Button(self.left_panel, text='Sturmer', width=10, command=self.sturmer)
        button_techno = Button(self.left_panel, text='Technolit', width=10, command=self.techno)
        button_iskra = Button(self.left_panel, text='Iskra', width=10, command=self.iskra)

        space.grid(row=0, column=0)
        button_sturmer.grid(row=1, column=0, pady=1)
        button_techno.grid(row=2, column=0, pady=1)
        button_iskra.grid(row=3, column=0, pady=1)

    def sturmer(self):
        for widget in self.left_panel.winfo_children():
            widget.destroy()

        space2 = Label(self.left_panel, text=' ')
        button_253 = Button(self.left_panel, text='253 iSC', width=10, command=lambda: self.read('253isc'))
        button_303 = Button(self.left_panel, text='303 iSC', width=10, command=lambda: self.read('303isc'))
        button_403w = Button(self.left_panel, text='403 iSC-w', width=10, command=lambda: self.read('403isc-w'))
        button_403ws = Button(self.left_panel, text='403 iSC-sw', width=10, command=lambda: self.read('403isc-sw'))
        button_253tft = Button(self.left_panel, text='253 Digital', width=10, command=lambda: self.read('253digit'))
        button_303tft = Button(self.left_panel, text='303 Digital', width=10, command=lambda: self.read('303digit'))
        button_403tft = Button(self.left_panel, text='403 Digital', width=10, command=lambda: self.read('403digit'))
        button_back = Button(self.left_panel, text='<< Nazaj', width=10, command=self.clear_left_panel)
        space = Label(self.left_panel)
        space2.grid(row=0, column=0)
        button_253.grid(row=1, column=0, pady=1)
        button_303.grid(row=2, column=0, pady=1)
        button_403w.grid(row=3, column=0, pady=1)
        button_403ws.grid(row=4, column=0, pady=1)
        button_253tft.grid(row=5, column=0, pady=1)
        button_303tft.grid(row=6, column=0, pady=1)
        button_403tft.grid(row=7, column=0, pady=1)
        space.grid(row=8, column=0)
        button_back.grid(row=9, column=0, pady=1)

    def techno(self):
        for widget in self.left_panel.winfo_children():
            widget.destroy()

        space2 = Label(self.left_panel, text=' ')
        button_imax30 = Button(self.left_panel, text='imax30', width=10, command=lambda: self.read('imax30-300ie'))
        button_imax40 = Button(self.left_panel, text='imax40', width=10, command=lambda: self.read('imax40-380ie'))
        button_300IE = Button(self.left_panel, text='300IE', width=10, command=lambda: self.read('imax30-300ie'))
        button_380IE = Button(self.left_panel, text='380IE', width=10, command=lambda: self.read('imax40-380ie'))
        button_210SC = Button(self.left_panel, text='210SDSC', width=10, command=lambda: self.read('210sdsc'))
        button_back = Button(self.left_panel, text='<< Nazaj', width=10, command=self.clear_left_panel)
        space = Label(self.left_panel)
        space2.grid(row=0, column=0)
        button_imax30.grid(row=1, column=0)
        button_imax40.grid(row=2, column=0)
        button_300IE.grid(row=3, column=0)
        button_380IE.grid(row=4, column=0)
        button_210SC.grid(row=5, column=0)
        space.grid(row=6, column=0)
        button_back.grid(row=7, column=0, pady=1)

    def iskra(self):
        for widget in self.left_panel.winfo_children():
            widget.destroy()

        space2 = Label(self.left_panel, text=' ')
        button_250 = Button(self.left_panel, text='imig250', width=10, command=lambda: self.read('imig250'))
        button_300 = Button(self.left_panel, text='imig300', width=10, command=lambda: self.read('imig300'))
        button_400 = Button(self.left_panel, text='imig400', width=10, command=lambda: self.read('imig400'))
        button_iskra = Button(self.left_panel, text='Iskra', width=10, command=lambda: self.read('Iskra-standard'))
        button_back = Button(self.left_panel, text='<< Nazaj', width=10, command=self.clear_left_panel)
        space = Label(self.left_panel)
        space2.grid(row=0, column=0)
        button_250.grid(row=1, column=0)
        button_300.grid(row=2, column=0)
        button_400.grid(row=3, column=0)
        button_iskra.grid(row=4, column=0)
        space.grid(row=5, column=0)
        button_back.grid(row=6, column=0)

    def read(self, ime):
        for widget in self.right_panel.winfo_children():
            widget.destroy()

        #self.startup_check()

        frame = LabelFrame(self.right_panel, text='Verzija programa', width=300, height=50)
        frame2 = LabelFrame(self.right_panel, text='Zadnja sprememba', width=300, height=50)
        frame.pack(side="top", fill=None, anchor=NW, expand=False, padx=30, pady=(25,5))
        frame2.pack(side="top", fill=None, anchor=NW, expand=False, padx=30, pady=5)
        label_verzija = Label(frame, text=self.find_version(ime))
        label_posodobitev = Label(frame2, text=self.time_file(ime))
        label_verzija.pack(anchor=NW, side="left", fill=None, expand=False)
        label_posodobitev.pack(anchor=NW, side="left", fill=None, expand=False)

        #self.scout_fetch(ime)
        if self.scout_fetch(ime):
            self.spremembe_read = Label(self.right_panel, fg="red", text=f'Sprememba  {ime}!')
            self.spremembe_read.pack(side="top", fill='none', anchor=NW, expand=False, padx=20, pady=5)

            self.button_prenesi = Button(self.right_panel, text='Prenesi', width=10, command=lambda: self.prenos(ime))
            self.button_prenesi.pack(side="top", fill='none', anchor=NW, expand=False, padx=40, pady=5)

            #self.startup_check()

    def prenos(self, ime):
        mod_time = os.path.getmtime((os.path.join(remote, ime)))
        local_time = time.ctime(mod_time)
        d = datetime.datetime.now()
        timestamp = "_%04d-%02d-%02d_%02d-%02d" % (d.year, d.month, d.day, d.hour, d.minute)
        backupfile = ime + str(timestamp)
        shutil.copytree(os.path.join(local, "SCscoutSTM8", ime), (os.path.join(local, "backup", backupfile)))
        shutil.rmtree(os.path.join(local, "SCscoutSTM8", ime))  # Zbrise mapo v clientu!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        shutil.copytree(os.path.join(remote, ime), (os.path.join(local, "SCscoutSTM8", ime)))

        with open(os.path.join(local, "storedtime", ime + suf), "w") as file_stored:
            file_stored.write(str(local_time))
            file_stored.close()

        self.button_prenesi.pack_forget()
        self.spremembe_read.pack_forget()

        for widget in self.status_panel.winfo_children():
            widget.destroy()
        self.ready = Button(self.status_panel, text='Ready/Refresh', height=1, anchor=W, relief=SUNKEN, command=self.refresh)
        self.ready.pack(anchor=NW, side="left", fill='x', expand=True)
        self.startup_check()
        status = Label(self.status_panel, text=self.cstatus(), anchor=E, relief=SUNKEN)
        status_db = Label(self.status_panel, text=self.cstatus_db(), anchor=E, relief=SUNKEN)
        status.pack(anchor=NE, side="right", fill='y', expand=False)
        status_db.pack(anchor=NE, side="right", fill='y', expand=False)

        potrditev = Label(self.right_panel, fg="red", text='Posodobljeno!')
        potrditev.pack(side="top", fill='none', anchor=NW, expand=False, padx=20, pady=5)

    def scout_fetch(self, ime):
        if connection == True:
            mod_time = os.path.getmtime((os.path.join(remote, ime)))
            local_time = time.ctime(mod_time)
            with open(os.path.join(local, "storedtime", ime + suf)) as file:
                stored_time = file.read()
                file.close()

            if stored_time != local_time:
                return True

    def clear_left_panel(self):
        for widget in self.left_panel.winfo_children():
            widget.destroy()
        self.aparati()

    def find_version(self, ime):
        if connection == True:
            with open(os.path.join(remote, ime, ime + suf)) as file:  # online
                return file.read()
                # file.close()
                # time_file(ime)
                # Ascout_modtime_startup(ime)
        else:
            with open(os.path.join(local, "offline", ime + suf)) as file:  # offline
                return file.read() + '  (Offline)'

    def time_file(self, ime):
        if connection == True:
            modification_time = os.path.getmtime(os.path.join(remote, ime))
            local_time = time.ctime(modification_time)
            return local_time
        else:
            modification_time = os.path.getmtime(os.path.join(local, "offline", ime + suf))
            local_time = time.ctime(modification_time)
            return local_time + '  (Offline)'

    def invertar(self):
        if connection_db:
            for widget in self.main_line_panel.winfo_children():
                widget.destroy()
            for widget in self.left_panel.winfo_children():
                widget.destroy()
            for widget in self.right_panel.winfo_children():
                widget.destroy()

            self.slika()
            self.sql_db()

            button_aparati = Button(self.main_line_panel, text='Aparati', width=10, bg='gray80', command=self.aparati)
            button_invertar = Button(self.main_line_panel, text='Skladisce', width=10, bg='gray80', relief=SUNKEN, state=DISABLED)

            button_aparati.pack(side="left")
            button_invertar.pack(side="left")

            space2 = Label(self.left_panel, text=' ')
            button_dodaj = Button(self.left_panel, text='Dodaj', width=10, command=self.dodaj)
            button_izdaj = Button(self.left_panel, text='Izdaj', width=10, command=self.izdaj)
            button_stanje = Button(self.left_panel, text='Stanje', width=10, command=self.stanje)
            button_arhiv = Button(self.left_panel, text='Arhiv', width=10, command=self.zgodovina)

            space2.grid(row=0, column=0)
            button_dodaj.grid(row=1, column=0, pady=1)
            button_izdaj.grid(row=2, column=0, pady=1)
            button_stanje.grid(row=3, column=0, pady=1)
            button_arhiv.grid(row=4, column=0, pady=1)
        else:
            messagebox.showwarning('Opozorilo', 'Ni povezave: Tehnologija PC')

    def sql_db(self):
        connect = sqlite3.connect(os.path.join(database, 'skladisceSCOOP.db'))
        c = connect.cursor()

        try:
            c.execute("""CREATE TABLE zgodovina (
                    namen text,
                    delta number,
                    datum text,
                    stanje number
            )


            """)
        except sqlite3.OperationalError:
            pass

        connect.commit()
        connect.close()

    def dodaj(self):
        for widget in self.right_panel.winfo_children():
            widget.destroy()

        frame = LabelFrame(self.right_panel, text='Dodaj zalogo SC', width=300, height=50, padx=15, pady=10)
        frame.grid(row=0, column=0, padx=30, pady=20)

        namen_label = Label(frame, text='Opis')
        namen_label.grid(row=0, column=0)
        kolicina_label = Label(frame, text='Kolicina')
        kolicina_label.grid(row=1, column=0)
        datum_label = Label(frame, text='Datum')
        datum_label.grid(row=2, column=0)

        self.namen = Entry(frame, width=20)
        self.namen.grid(row=0, column=1, padx=20)
        self.kolicina = ttk.Spinbox(frame, from_=1, to=600, width=8)
        self.kolicina.grid(row=1, column=1, padx=(20, 0), sticky='w')
        self.datum = Entry(frame, width=20)
        self.datum.grid(row=2, column=1)
        button_dodaj = Button(frame, text='Dodaj', width=10, command=self.submit1)
        button_dodaj.grid(row=3, column=0, columnspan=2, pady=10, padx=10, ipadx=10)

        d = datetime.datetime.now()
        timestamp = "%02d.%02d.%04d" % (d.day, d.month, d.year)
        self.datum.insert(0, timestamp)

    def izdaj(self):
        for widget in self.right_panel.winfo_children():
            widget.destroy()

        frame = LabelFrame(self.right_panel, text='Izdaj zalogo SC', width=300, height=50, padx=15, pady=10)
        frame.grid(row=0, column=0, padx=30, pady=20)

        namen_label = Label(frame, text='Opis')
        namen_label.grid(row=0, column=0)
        kolicina_label = Label(frame, text='Kolicina')
        kolicina_label.grid(row=1, column=0)
        datum_label = Label(frame, text='Datum')
        datum_label.grid(row=2, column=0)

        self.namen = Entry(frame, width=20)
        self.namen.grid(row=0, column=1, padx=20)
        self.kolicina = ttk.Spinbox(frame, from_=1, to=600, width=8)
        self.kolicina.grid(row=1, column=1, padx=(20, 0), sticky='w')
        self.datum = Entry(frame, width=20)
        self.datum.grid(row=2, column=1, padx=20)
        button_izdaj = Button(frame, text='Izdaj', width=10, command=self.submit2)
        button_izdaj.grid(row=3, column=0, columnspan=2, pady=10, padx=10, ipadx=10)

        d = datetime.datetime.now()
        timestamp = "%02d.%02d.%04d" % (d.day, d.month, d.year)
        self.datum.insert(0, timestamp)

    def stanje(self):
        for widget in self.right_panel.winfo_children():
            widget.destroy()

        frame = LabelFrame(self.right_panel, text='Zaloga SC kartic', width=300, height=50, padx=15, pady=10)
        label_zaloga = Label(frame, text=self.inventory_amount())
        frame.pack(side="top", fill=None, anchor=NW, expand=False, padx=30, pady=20)
        label_zaloga.pack(anchor=NW, side="left", fill=None, expand=False)

    def inventory_amount(self):
        connect = sqlite3.connect(os.path.join(database, 'skladisceSCOOP.db'))
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM zgodovina')

        records = cursor.fetchall()
        temp_list = []
        for record in records:
            temp_list.append(int(record[1]))

        connect.commit()
        connect.close()

        return sum(temp_list)


    def zgodovina(self):
        for widget in self.right_panel.winfo_children():
            widget.destroy()

        connect = sqlite3.connect(os.path.join(database, 'skladisceSCOOP.db'))
        cursor = connect.cursor()

        cursor.execute('SELECT * FROM zgodovina')
        records = cursor.fetchall()

        scrollbar = Scrollbar(self.right_panel)
        scrollbar.pack(side="right", fill="y")

        table = ttk.Treeview(self.right_panel, columns=('opis', 'kolicina', 'datum', 'stanje'),
                             show='headings', yscrollcommand=scrollbar.set)
        scrollbar.config(command=table.yview)
        table.heading('opis', text='Opis')
        table.column('opis', minwidth=0, width=90)
        table.heading('kolicina', text='Kolicina')
        table.column('kolicina', minwidth=0, width=90)
        table.heading('datum', text='Datum')
        table.column('datum', minwidth=0, width=90)
        table.heading('stanje', text='Stanje')
        table.column('stanje', minwidth=0, width=90)
        table.pack(fill = 'both', expand=True)

        for record in records:
            opis = str(record[0])
            kolicina = str(record[1])
            datum = str(record[2])
            stanje = str(record[3])
            data = (opis, kolicina, datum, stanje)
            table.insert(parent='', index=END, values=data)

        table.yview_moveto(1)


        connect.commit()
        connect.close()

    def submit1(self):
        connect = sqlite3.connect(os.path.join(database, 'skladisceSCOOP.db'))
        c = connect.cursor()

        # with open(os.path.join(local, 'inventory', 'inventory_amount.txt'), 'r') as file:
        #     amount = file.read()
        #     new_amount = int(amount) + int(self.kolicina.get().strip())
        #     with open(os.path.join(local, 'inventory', 'inventory_amount.txt'), 'w') as file1:
        #         file1.write(str(new_amount))
        new_amount = self.inventory_amount() + int(self.kolicina.get().strip())

        c.execute('INSERT INTO zgodovina VALUES (:namen, :delta, :datum, :stanje)',
                  {
                      'namen': self.namen.get(),
                      'delta': self.kolicina.get(),
                      'datum': self.datum.get(),
                      'stanje': new_amount
                  })
        connect.commit()
        connect.close()

        dodano_label = Label(self.right_panel, text=f'Dodano {self.kolicina.get()} kom.')
        dodano_label.grid(row=1, column=0)#, padx=15, pady=10)

        self.namen.delete(0, END)
        self.kolicina.delete(0, END)


    def submit2(self):
        connect = sqlite3.connect(os.path.join(database, 'skladisceSCOOP.db'))
        c = connect.cursor()

        # with open(os.path.join(local, 'inventory', 'inventory_amount.txt'), 'r') as file:
        #     amount = file.read()
        #     new_amount = int(amount) - int(self.kolicina.get())
        #     with open(os.path.join(local, 'inventory', 'inventory_amount.txt'), 'w') as file1:
        #         file1.write(str(new_amount))
        new_amount = self.inventory_amount() - int(self.kolicina.get().strip())

        c.execute('INSERT INTO zgodovina VALUES (:namen, :delta, :datum, :stanje)',
                  {
                      'namen': self.namen.get(),
                      'delta': '-' + self.kolicina.get(),
                      'datum': self.datum.get(),
                      'stanje': new_amount
                  })
        connect.commit()
        connect.close()

        izdano_label = Label(self.right_panel, text=f'Izdano {self.kolicina.get()} kom.')
        izdano_label.grid(row=1, column=0)  # , padx=15, pady=10)
        self.namen.delete(0, END)
        self.kolicina.delete(0, END)


root = Tk()
app = Scout(master=root)
app.mainloop()
