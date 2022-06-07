from tkinter import *

from Params import Params
from MainPlot import MainPlot
from LeftMenu import LeftMenu


# Класс, отвечающий за кнопки: "Ручное обновление", "Остановка автоматического обновления",
# "Автоматическое обновление и смещение скроллбара", "Остановка автоматического сдвига прокрутки"
class PictureBtns(object):

    # В данном классе используем self, чтобы сборщик мусора не удалял наши картинки после выполнения функции
    def __init__(self):
        self.update_image = None
        self.update_btn1 = None
        self.stop_image = None
        self.stop_btn2 = None
        self.start_image = None
        self.start_btn3 = None
        self.pause_image = None
        self.pause_btn4 = None

    def draw_picture_btns(self):

        def reset():
            Params.reset = True
            LeftMenu.brightness_slider.configure(value=0)
            LeftMenu.contrast_slider.configure(value=0)

        def start_or_stop(btn):
            if btn == 'start':
                Params.auto = True
                Params.manual_shift = False
                Params.need_update_plot = True
            else:
                Params.auto = False

        def pause_shifting():
            Params.manual_shift = True

        self.update_image = PhotoImage(file='update.png')
        self.update_btn1 = Button(MainPlot.frame_plot, image=self.update_image, borderwidth=0, command=reset)
        self.update_btn1.place(width=24, height=24)
        self.stop_image = PhotoImage(file='stop.png')
        self.stop_btn2 = Button(MainPlot.frame_plot, image=self.stop_image, borderwidth=0, command=lambda: start_or_stop('stop'))
        self.stop_btn2.place(width=24, height=24, x=24)
        self.start_image = PhotoImage(file='start.png')
        self.start_btn3 = Button(MainPlot.frame_plot, image=self.start_image, borderwidth=0, command=lambda: start_or_stop('start'))
        self.start_btn3.place(width=24, height=24, x=48)
        self.pause_image = PhotoImage(file='pause.png')
        self.pause_btn4 = Button(MainPlot.frame_plot, image=self.pause_image, borderwidth=0, command=pause_shifting)
        self.pause_btn4.place(width=24, height=24, x=72)
