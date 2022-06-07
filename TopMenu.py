import socket
import struct
import time
import threading
from tkinter import *
from tkinter import filedialog as fd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from Params import Params
from MainPlot import MainPlot
from Messages import ClientMessage, ServerMessage
from LeftMenu import LeftMenu


# Класс, отвечающий за верхнюю панель меню
class TopMenu(object):

    canvas3 = None
    canvas4 = None
    disconnect = False
    energy_diff = StringVar()
    graph_axes3 = None
    graph_axes4 = None
    p3 = None
    p4 = None
    s = None
    servermenu = None
    x1_entry = None
    x2_entry = None
    y1_entry = None
    y2_entry = None
    sigma = StringVar()

    @staticmethod
    def draw_top_menu():

        # Функция открытия файла для отображения
        def open_txt(mode=0):

            file_name = fd.askopenfilename()

            try:
                # Открываем файл на чтение
                with open(file_name, 'r') as f:
                    lines = f.read().split('\n')
                    for i, line in enumerate(lines):
                        if line[:9] == 'SpaceSize':
                            Params.NUM_CHANNELS = int(line[10:])
                        elif line[:10] == 'DATA_START':
                            start_data_index = i
                            break
                    MainPlot.scrollbar.set(0, 0.2)
                    if mode == 0:
                        Params.init()
                        for line in lines[start_data_index + 1:-1]:
                            if len(line.split('\t')) != 1:
                                frame, channel, _, power = line.split('\t')
                            else:
                                frame, channel, _, power = line.split('    ')
                            Params.time_frame = int(frame)
                            Params.data[int(channel)][Params.time_frame % Params.NUM_FRAMES] = float(power)
                            Params.need_update_plot = True
                    else:
                        Params.comparison = True
                        Params.reference_config_data = np.zeros((Params.NUM_CHANNELS, Params.NUM_FRAMES))
                        Params.rcd_slice = np.zeros((Params.NUM_CHANNELS, 200))
                        for line in lines[start_data_index + 1:-1]:
                            if len(line.split('\t')) != 1:
                                frame, channel, _, power = line.split('\t')
                            else:
                                frame, channel, _, power = line.split('    ')
                            Params.reference_config_data[int(channel)][int(frame) % Params.NUM_FRAMES] = float(power)
                        Params.need_update_plot = True
                        Params.first_comparison = True
                Params.manual_shift = True
            except Exception:
                pass

        # Функция создания нового диалогового окна с параметрами подключения к серверу
        def connect_wndw():
            connect_window = Toplevel(Params.root)
            connect_window.title('Server connection')
            connect_window.resizable(0, 0)
            connect_window.wm_attributes('-topmost', 1)

            ip_label = Label(connect_window, text='IP address:')
            port_label = Label(connect_window, text='Port:')
            packet_label = Label(connect_window, text='Packet size:')

            ip_label.grid(row=0, column=0, sticky="w")
            port_label.grid(row=1, column=0, sticky="w")
            packet_label.grid(row=2, column=0, sticky="w")

            ip_entry = Entry(connect_window)
            port_entry = Entry(connect_window)
            packet_entry = Entry(connect_window)

            ip_entry.insert(0, 'localhost')
            port_entry.insert(0, '8080')
            packet_entry.insert(0, str(Params.PACKET_SIZE))
            packet_entry.configure(state=DISABLED)

            ip_entry.grid(row=0, column=1, padx=5, pady=5)
            port_entry.grid(row=1, column=1, padx=5, pady=5)
            packet_entry.grid(row=2, column=1, padx=5, pady=5)

            connect_btn = Button(connect_window, text='Connect',
                                 command=lambda info=(ip_entry, port_entry, packet_entry, connect_window): connect(info))
            connect_btn.grid(row=3, column=1, padx=5, pady=5, sticky="e")

        # # Функция создания нового диалогового окна для ввода диапазона принимаемых каналов
        # def channel_wndw():
        #     channel_window = Toplevel(Params.root)
        #     channel_window.title('Channel range')
        #     channel_window.resizable(0, 0)
        #     channel_window.wm_attributes('-topmost', 1)
        #
        #     ch_range1 = Label(channel_window, text='Start channel:')
        #     ch_range2 = Label(channel_window, text='Last channel:')
        #     ch_range1.grid(row=0, column=0, sticky="w")
        #     ch_range2.grid(row=1, column=0, sticky="w")
        #
        #     ch_entry1 = Entry(channel_window)
        #     ch_entry2 = Entry(channel_window)
        #     ch_entry1.insert(0, '0')
        #     ch_entry2.insert(0, str(Params.NUM_CHANNELS-1))
        #     ch_entry1.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        #     ch_entry2.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        #
        #     ch_btn = Button(channel_window, text='Request Data Frames', command=lambda: request_data_frames(channel_window))
        #     ch_btn.grid(row=2, column=1, padx=5, pady=5, sticky="e")

        # Функция подключения к серверу
        def connect(info):
            ip = info[0].get()
            port = int(info[1].get())
            Params.PACKET_SIZE = int(info[2].get())
            info[3].destroy()
            try:
                TopMenu.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                TopMenu.s.connect((ip, port))
                thread1 = threading.Thread(target=Client.receiver)
                thread1.start()
                TopMenu.servermenu.entryconfig(4, state=NORMAL)
                TopMenu.servermenu.entryconfig(6, state=NORMAL)
                MainPlot.scrollbar.set(0, 0.2)
                TopMenu.disconnect = False
                TopMenu.s.send(ClientMessage.PAKOSAM_CLIENT_REQUEST_METADATA.value.to_bytes(1, 'little'))
            except Exception:
                pass

        # Функция остановки вычислений
        def stop_processing():
            TopMenu.s.send(ClientMessage.PAKOSAM_CLIENT_STOP_PROCESSING.value.to_bytes(1, 'little'))

        # Функция отключения от сервера
        def disconnect():
            try:
                TopMenu.s.send(ClientMessage.PAKOSAM_CLIENT_DISCONNECT.value.to_bytes(1, 'little'))
            except Exception:
                pass
            try:
                TopMenu.s.close()
                TopMenu.s.shutdown()
            except Exception:
                pass

            TopMenu.servermenu.entryconfig(2, state=DISABLED)
            TopMenu.servermenu.entryconfig(4, state=DISABLED)
            TopMenu.servermenu.entryconfig(6, state=DISABLED)

        # Функция остановки сервера
        def stop_server():
            TopMenu.s.send(ClientMessage.PAKOSAM_CLIENT_STOP_SERVER.value.to_bytes(1, 'little'))
            disconnect()

        def mode_selection():
            if Params.mode.get() == 0:
                for c in LeftMenu.classes:
                    c.select()
                LeftMenu.btn_all.configure(state=NORMAL)
                LeftMenu.btn_none.configure(state=NORMAL)
            elif Params.mode.get() == 1:
                for c in LeftMenu.classes:
                    c.deselect()
                LeftMenu.classes[0].select()
                LeftMenu.btn_all.configure(state=DISABLED)
                LeftMenu.btn_none.configure(state=DISABLED)

        def comparison():
            comparison_window = Toplevel(Params.root)
            comparison_window.title('Comparison config')
            comparison_window.resizable(0, 0)
            comparison_window.wm_attributes('-topmost', 1)
            w = Params.root.winfo_screenwidth()
            h = Params.root.winfo_screenheight()
            comparison_window.geometry(f'{int(w * 0.85)}x{int(h * 0.845)}+279-54')

            def close_window():
                Params.comparison = False
                Params.reference_config_data = np.zeros(1)
                Params.rcd_slice = np.zeros(1)
                comparison_window.destroy()

            comparison_window.protocol("WM_DELETE_WINDOW", close_window)

            frame_plot_reference = Frame(comparison_window)
            frame_plot_initial = Frame(comparison_window)

            frame_plot_reference.place(relx=0, rely=0.05, relwidth=0.5, relheight=0.95)
            frame_plot_initial.place(relx=0.5, rely=0.05, relwidth=0.5, relheight=0.95)

            fig3 = Figure()
            TopMenu.graph_axes3 = fig3.add_subplot()
            fig3.subplots_adjust(left=0.07, right=0.96, top=0.95, bottom=0.07)
            TopMenu.p3 = TopMenu.graph_axes3.imshow(Params.data, aspect='auto', cmap=Params.cmap, origin="lower", extent=(0, 2, 0, 2))
            TopMenu.canvas3 = FigureCanvasTkAgg(fig3, frame_plot_initial)
            TopMenu.canvas3.get_tk_widget().pack(fill=BOTH, expand=1)

            fig4 = Figure()
            TopMenu.graph_axes4 = fig4.add_subplot()
            fig4.subplots_adjust(left=0.07, right=0.96, top=0.95, bottom=0.07)
            TopMenu.p4 = TopMenu.graph_axes4.imshow(Params.data, aspect='auto', cmap=Params.cmap, origin="lower", extent=(0, 2, 0, 2))
            TopMenu.canvas4 = FigureCanvasTkAgg(fig4, frame_plot_reference)
            TopMenu.canvas4.get_tk_widget().pack(fill=BOTH, expand=1)

            TopMenu.energy_diff.set('Energy difference: 0.0; 0.0%')
            energy_label = Label(comparison_window, textvariable=TopMenu.energy_diff)
            energy_label.place(relx=0.7, rely=0, relwidth=0.2, relheight=0.05)
            TopMenu.sigma.set('σ: 0.0')
            sigma_label = Label(comparison_window, textvariable=TopMenu.sigma)
            sigma_label.place(relx=0.55, rely=0, relwidth=0.15, relheight=0.05)
            config_btn = Button(comparison_window, text='Open reference config', command=lambda: open_txt(1))
            config_btn.place(relx=0.01, rely=0.0125, relwidth=0.09, relheight=0.025)

            x1_label = Label(comparison_window, text='Time Frame:')
            x1_label.place(relx=0.15, rely=0.0125, relwidth=0.06, relheight=0.025)
            x2_label = Label(comparison_window, text='-')
            x2_label.place(relx=0.24, rely=0.0125, relwidth=0.01, relheight=0.025)
            y1_label = Label(comparison_window, text='Channel:')
            y1_label.place(relx=0.3, rely=0.0125, relwidth=0.05, relheight=0.025)
            y2_label = Label(comparison_window, text='-')
            y2_label.place(relx=0.38, rely=0.0125, relwidth=0.01, relheight=0.025)

            local_left, local_right = MainPlot.scrollbar.get()
            TopMenu.x1_entry = Entry(comparison_window)
            TopMenu.x2_entry = Entry(comparison_window)
            TopMenu.x1_entry.insert(0, f'{int(local_left * 1000)}')
            TopMenu.x2_entry.insert(0, f'{int(local_left * 1000 + 200)}')
            TopMenu.y1_entry = Entry(comparison_window)
            TopMenu.y2_entry = Entry(comparison_window)
            TopMenu.y1_entry.insert(0, '0')
            TopMenu.y2_entry.insert(0, f'{Params.NUM_CHANNELS}')
            TopMenu.x1_entry.place(relx=0.21, rely=0.0125, relwidth=0.03, relheight=0.025)
            TopMenu.x2_entry.place(relx=0.25, rely=0.0125, relwidth=0.03, relheight=0.025)
            TopMenu.y1_entry.place(relx=0.35, rely=0.0125, relwidth=0.03, relheight=0.025)
            TopMenu.y2_entry.place(relx=0.39, rely=0.0125, relwidth=0.03, relheight=0.025)


        def changed_viewmenu():
            mainmenu.entryconfigure(5, label=Params.view_var.get())

        mainmenu = Menu(Params.root)
        Params.root.config(menu=mainmenu)

        filemenu = Menu(mainmenu, tearoff=0)
        filemenu.add_command(label='Open .txt file', command=lambda: open_txt(0))
        filemenu.add_separator()
        filemenu.add_command(label='Save as Image')

        TopMenu.servermenu = Menu(mainmenu, tearoff=0)
        TopMenu.servermenu.add_command(label='Connect to...', command=connect_wndw)
        TopMenu.servermenu.add_separator()
        TopMenu.servermenu.add_command(label='Stop Processing', command=stop_processing, state=DISABLED)
        TopMenu.servermenu.add_separator()
        TopMenu.servermenu.add_command(label='Disconnect...', command=disconnect, state=DISABLED)
        TopMenu.servermenu.add_separator()
        TopMenu.servermenu.add_command(label='Stop Server', command=stop_server, state=DISABLED)

        modemenu = Menu(mainmenu, tearoff=0)
        modemenu.add_radiobutton(label='Viewer', value=0, variable=Params.mode, command=mode_selection)
        modemenu.add_radiobutton(label='Selector', value=1, variable=Params.mode, command=mode_selection)

        comparisonmenu = Menu(mainmenu, tearoff=0)
        comparisonmenu.add_command(label='Comparison configs', command=comparison)

        OptionList = ['0 - No ouput map', '1 - Smoothed normalized QSG', '2 - QSG scores', '3 - Noise energy',
                      '4 - Corrected SNR', '5 - Intensity of spatial fading (Inverse channel gain)', '6 - Detected events',
                      '7 - Event recognition', '8 - Dynamic clusters of event', '9 - Tracks of target', '10 - Carrier energy']

        Params.view_var.set(OptionList[4])

        viewmenu = Menu(mainmenu, tearoff=0)
        for item in OptionList:
            viewmenu.add_radiobutton(value=item, label=item, variable=Params.view_var, command=changed_viewmenu)

        mainmenu.add_cascade(label='File', menu=filemenu)
        mainmenu.add_cascade(label='Server', menu=TopMenu.servermenu)
        mainmenu.add_cascade(label='Mode', menu=modemenu)
        mainmenu.add_cascade(label='Comparison', menu=comparisonmenu)
        mainmenu.add_cascade(label=OptionList[4], menu=viewmenu)


# Класс, отвечающий за клиентскую часть, в которой описываются команды с сервером
class Client(object):

    # Функция приёма данных по сокету
    @staticmethod
    def receiver():

        # Открываем файл на запись
        with open(str(time.time()) + '.txt', 'w') as f:
            while True:
                try:
                    packet = TopMenu.s.recv(Params.PACKET_SIZE)
                except Exception:
                    pass
                # print(packet)

                if len(packet) > 0:

                    # Обработка пакета с метаданными
                    if int.from_bytes(packet[0:1], 'little') == ServerMessage.PAKOSAM_SERVER_SENDING_METADATA.value:
                        Params.NUM_CHANNELS = int.from_bytes(packet[1:5], 'little')
                        N_FRAMES = int.from_bytes(packet[5:9], 'little')
                        Params.init()
                        Params.manual_shift = False
                        f.write('\nHEADER_START\n')
                        f.write('version=5.1\n')
                        f.write('Mode=4\n')
                        f.write('BinaryFile=None\n')
                        f.write('TimeSize=' + str(N_FRAMES) + '\n')
                        f.write('SpaceSize=' + str(Params.NUM_CHANNELS) + '\n')
                        f.write('N_Colours=1\n')
                        f.write('HEADER_END\n')
                        f.write('DATA_START\n')
                        TopMenu.s.send(ClientMessage.PAKOSAM_CLIENT_REQUEST_SERVER_STATUS.value.to_bytes(1, 'little'))

                    # Обработка пакета со статусом сервера
                    elif int.from_bytes(packet[0:1], 'little') == ServerMessage.PAKOSAM_SERVER_SENDING_STATUS.value:
                        # server_status = int.from_bytes(packet[1:3], 'little')
                        # if server_status == 0:
                        TopMenu.s.send(ClientMessage.PAKOSAM_CLIENT_RUN_SERVER_ONLINE.value.to_bytes(1, 'little'))
                        # else:
                        #     TopMenu.servermenu.entryconfig(2, state=NORMAL)

                    # Обработка пакета с оповещением о начале обработки
                    elif int.from_bytes(packet[0:1], 'little') == ServerMessage.PAKOSAM_SERVER_STARTS_PROCESSING.value:
                        msg = ClientMessage.PAKOSAM_CLIENT_REQUEST_DATA_FRAME.value.to_bytes(1, 'little')
                        mode = 1
                        if Params.view_var.get() == '9 - Tracks of target':
                            mode = 2
                        TopMenu.s.send(msg + mode.to_bytes(4, 'little'))
                        TopMenu.servermenu.entryconfig(2, state=NORMAL)

                    # Обработка пакета с данными по текущему кадру
                    elif int.from_bytes(packet[0:1], 'little') == ServerMessage.PAKOSAM_SERVER_SENDING_DATA_FRAME.value:
                        for i in range(5, 12, 2):
                            match i:
                                case 5:
                                    Params.time_frame = int.from_bytes(packet[i - 3:i + 1], 'little')
                                    if Params.time_frame != Params.last_time_frame:
                                        Params.data[:, Params.time_frame % Params.NUM_FRAMES] = 0
                                    Params.last_time_frame = Params.time_frame
                                case 9:
                                    start_channel = int.from_bytes(packet[i - 3:i + 1], 'little')
                                case 11:
                                    N_elements = int.from_bytes(packet[i - 1:i + 1], 'little')
                        if mode == 1:
                            for i in range(15, N_elements * 4 + 15, 4):
                                [power] = struct.unpack('f', packet[i - 3:i + 1])
                                if start_channel + int((i - 15) / 4) != 0 or Params.time_frame != 0:
                                    Params.data[start_channel + int((i - 15) / 4)][Params.time_frame % Params.NUM_FRAMES] = power
                                if power != 0:
                                    f.write(f'{Params.time_frame}\t{start_channel + int((i - 15) / 4)}\t0\t{power:.6f}\n')
                        elif mode == 2:
                            for i in range(15, N_elements * 4 + 15, 32):
                                [center_in_channels, left_side, right_side, power, pos_y, velocity_x, target_id,
                                 target_class] = struct.unpack('8f', packet[i - 3:i + 29])
                                print(Params.time_frame, center_in_channels, left_side, right_side, power, pos_y,
                                      velocity_x, target_id, target_class)
                                Params.data_tracks.append([Params.time_frame, center_in_channels, left_side, right_side,
                                                           power, pos_y, velocity_x, target_id, target_class, 'not used', 0, 0])

                                for j in range(int(left_side), int(right_side + 1)):
                                    if 0 <= j < Params.NUM_CHANNELS:
                                        Params.data[j][Params.time_frame % Params.NUM_FRAMES] += \
                                            power / (1.2 ** (1/3 * abs(int(center_in_channels) - j)))

                    # Обработка пакета, информирующего о наличии нового пакета
                    elif int.from_bytes(packet[0:1], 'little') == ServerMessage.PAKOSAM_SERVER_NEW_FRAME_READY.value:
                        TopMenu.s.send(ClientMessage.PAKOSAM_CLIENT_REQUEST_DATA_FRAME.value.to_bytes(1, 'little'))

                    # Обработка пакета, информирующего об окончании текущего пакета
                    elif int.from_bytes(packet[0:1], 'little') == ServerMessage.PAKOSAM_SERVER_DATA_FRAME_END.value:
                        try:
                            TopMenu.s.send(ClientMessage.PAKOSAM_CLIENT_REQUEST_DATA_FRAME.value.to_bytes(1, 'little'))
                            Params.need_update_plot = True
                        except Exception:
                            pass

                    elif int.from_bytes(packet[0:1], 'little') == ServerMessage.PAKOSAM_SERVER_PROCESSING_STOPPED.value:
                        TopMenu.servermenu.entryconfig(2, state=DISABLED)
                        TopMenu.servermenu.entryconfig(4, state=DISABLED)
                        TopMenu.servermenu.entryconfig(6, state=DISABLED)
                        print('Server processing stopped')
                        f.write('DATA_END')
                        TopMenu.s.send(ClientMessage.PAKOSAM_CLIENT_DISCONNECT.value.to_bytes(1, 'little'))
                        TopMenu.disconnect = True
                        break

                    elif int.from_bytes(packet[0:1], 'little') == ServerMessage.PAKOSAM_SERVER_STOPPED.value:
                        TopMenu.servermenu.entryconfig(2, state=DISABLED)
                        TopMenu.servermenu.entryconfig(4, state=DISABLED)
                        TopMenu.servermenu.entryconfig(6, state=DISABLED)
                        print('Server stopped')
                        f.write('DATA_END')
                        TopMenu.s.send(ClientMessage.PAKOSAM_CLIENT_DISCONNECT.value.to_bytes(1, 'little'))
                        TopMenu.disconnect = True
                        break
