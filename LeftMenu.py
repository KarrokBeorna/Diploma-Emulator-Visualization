from tkinter import *
from tkinter import ttk, N
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

from ScrlNotebook import ScrollableNotebook
from Params import Params
from RangeSlider import RangeSliderV


# Класс, отвечающий за левое меню с инструментами
class LeftMenu(object):

    a2 = None
    brightness_slider = None
    btn_all = None
    btn_none = None
    canvas2 = None
    classes = []
    colours = ['white', 'red', 'green', 'blue', 'yellow', 'pink',
               'cyan', 'orange', 'lightgreen', 'purple', 'coral', 'lightblue']
    contrast_slider = None
    p2 = None
    thresholds_slider = None

    @staticmethod
    def draw_left_menu():

        frame_settings = Frame(Params.root)
        frame_settings.place(relx=0, rely=0, relwidth=0.15, relheight=1)
        settings = ScrollableNotebook(frame_settings)
        settings.pack(fill=BOTH, expand=1)

        def check_classes(cl):
            if Params.mode.get() == 1:
                for c in LeftMenu.classes:
                    c.deselect()
                LeftMenu.classes[cl].select()

        def check_all(btn):
            if btn == 'All':
                for c in LeftMenu.classes:
                    c.select()
            elif btn == 'None':
                for c in LeftMenu.classes:
                    c.deselect()

        def scale_selection():
            if var_scale.get() == 0:
                if Params.scale != 'Linear':
                    Params.scale = 'Linear'
                    Params.need_update_plot = True
            elif var_scale.get() == 1:
                if Params.scale != 'Sqrt':
                    Params.scale = 'Sqrt'
                    Params.need_update_plot = True
            elif var_scale.get() == 2:
                if Params.scale != 'Log':
                    Params.scale = 'Log'
                    Params.need_update_plot = True

        def slider_changed(event):
            Params.need_update_plot = True

        def thresholds_changed(var, index, mode):
            Params.need_update_plot = True

        child1 = Frame(frame_settings)
        settings.add(child1, text='Classes')

        frame_classes = LabelFrame(child1, text='Classes')
        frame_classes.place(relx=0.2, rely=0.05, relwidth=0.6, relheight=0.5)
        frame_show = LabelFrame(frame_classes, text='Show')
        frame_show.pack(padx=5, pady=5)

        for i in range(len(LeftMenu.colours)):
            globals()['class' + str(i)] = Checkbutton(frame_show, width=7, text='Class ' + str(i),
                                                      bg=LeftMenu.colours[i], command=lambda cl=i: check_classes(cl))
            LeftMenu.classes.append(globals()['class' + str(i)])
            globals()['class' + str(i)].grid(row=i, column=0, padx=2, pady=1, sticky='w')
        check_all('All')

        LeftMenu.btn_all = Button(frame_classes, width=8, text='All', command=lambda: check_all('All'))
        LeftMenu.btn_none = Button(frame_classes, width=8, text='None', command=lambda: check_all('None'))
        LeftMenu.btn_all.pack(pady=5)
        LeftMenu.btn_none.pack(pady=5)

        child2 = Frame(frame_settings)
        settings.add(child2, text='Visualization')

        frame_scale = LabelFrame(child2, text='Scale of brightness')
        frame_brightness = LabelFrame(child2, text='Brightness')
        frame_contrast = LabelFrame(child2, text='Contrast')
        frame_bar = Frame(child2)

        frame_scale.place(relx=0.13, rely=0.03, relwidth=0.74, relheight=0.12)
        frame_brightness.place(relx=0.13, rely=0.23, relwidth=0.74, relheight=0.06)
        frame_contrast.place(relx=0.13, rely=0.36, relwidth=0.74, relheight=0.06)
        frame_bar.place(relx=0.08, rely=0.5, relwidth=0.84, relheight=0.2)

        var_scale = IntVar()

        scale0 = ttk.Radiobutton(frame_scale, variable=var_scale, value=0, command=scale_selection, text='Linear')
        scale1 = ttk.Radiobutton(frame_scale, variable=var_scale, value=1, command=scale_selection, text='Square root')
        scale2 = ttk.Radiobutton(frame_scale, variable=var_scale, value=2, command=scale_selection, text='Log')
        scale0.grid(pady=3, padx=5, row=0, column=0, sticky='w')
        scale1.grid(pady=3, padx=5, row=1, column=0, sticky='w')
        scale2.grid(pady=3, padx=5, row=2, column=0, sticky='w')

        # Яркость:
        # Увеличиваем - домножаем все значения выше 0 на некий коэф 0 <= x < 1
        # Уменьшаем - домножаем все значения выше 0 на некий коэф -1 < x <= 0
        LeftMenu.brightness_slider = ttk.Scale(frame_brightness, from_=-0.99, to=0.99, length=190, command=slider_changed)
        # Контраст:
        # Увеличиваем - все значения выше середины стремятся к максимальному значению,
        #               а все значения ниже середины стремятся к минимальному значению
        # Уменьшаем - все значения стремятся к среднему значению
        LeftMenu.contrast_slider = ttk.Scale(frame_contrast, from_=-0.99, to=0.99, length=190, command=slider_changed)
        LeftMenu.brightness_slider.pack(pady=5, padx=5)
        LeftMenu.contrast_slider.pack(pady=5, padx=5)

        # График яркости/контраста
        fig2 = Figure()
        LeftMenu.a2 = fig2.add_subplot()
        LeftMenu.p2 = sns.kdeplot(Params.bar_values, ax=LeftMenu.a2)
        fig2.subplots_adjust(left=0, right=0.99, top=1, bottom=0.01)
        LeftMenu.canvas2 = FigureCanvasTkAgg(fig2, frame_bar)
        LeftMenu.canvas2.get_tk_widget().pack(fill=BOTH, expand=1)

        child3 = Frame(frame_settings)
        settings.add(child3, text='Thresholding')
        frame_thresholds = LabelFrame(child3, text='Thresholds')
        frame_thresholds.place(relx=0.23, rely=0.05, relwidth=0.7, relheight=0.45)
        min_var_slider = DoubleVar()
        max_var_slider = DoubleVar()
        LeftMenu.thresholds_slider = RangeSliderV(
                                        frame_thresholds, (min_var_slider, max_var_slider),
                                        min_val=0, max_val=1, padY=20, Width=120, digit_precision='.3f')

        LeftMenu.thresholds_slider.pack()
        min_var_slider.trace_add(['read', 'write'], thresholds_changed)
        max_var_slider.trace_add(['read', 'write'], thresholds_changed)
