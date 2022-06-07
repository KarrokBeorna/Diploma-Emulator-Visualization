from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *
import matplotlib.pyplot as plt

from Params import Params


# Класс, отвечающий за основной график с картой энергий
class MainPlot(object):

    canvas1 = None
    fig = None
    frame_plot = None
    graph_axes = None
    p1 = None
    scrollbar = None

    @staticmethod
    def draw_plot():
        MainPlot.frame_plot = Frame(Params.root)
        MainPlot.frame_plot.place(relx=0.15, rely=0, relwidth=0.85, relheight=1)
        MainPlot.fig = Figure()
        MainPlot.graph_axes = MainPlot.fig.add_subplot()
        MainPlot.fig.subplots_adjust(left=0.05, right=1.05, top=0.95, bottom=0.07)

        # Цвет можно разбить на дискретные значения cmap=plt.get_cmap('viridis', 11)
        MainPlot.p1 = MainPlot.graph_axes.imshow(Params.data, cmap=Params.cmap, aspect='auto', origin="lower", extent=(0, 2, 0, 2))
        MainPlot.canvas1 = FigureCanvasTkAgg(MainPlot.fig, MainPlot.frame_plot)
        MainPlot.canvas1.get_tk_widget().pack(fill=BOTH, expand=1)

        # Цветовая шкала
        MainPlot.fig.colorbar(MainPlot.p1)

        # Функция для прокручивания карты
        def scroll_imshow(event, mode, units=1):
            temp = (MainPlot.frame_plot.winfo_pointerx() - MainPlot.frame_plot.winfo_x()) / MainPlot.frame_plot.winfo_width()
            if 0.1 < temp < 0.9:
                MainPlot.scrollbar.set(temp - 0.1, temp + 0.1)
            elif temp >= 0.9:
                MainPlot.scrollbar.set(0.8, 1)
            elif temp <= 0.1:
                MainPlot.scrollbar.set(0, 0.2)
            Params.need_update_plot = True

        MainPlot.scrollbar = Scrollbar(MainPlot.frame_plot, orient='horizontal', command=scroll_imshow)
        MainPlot.scrollbar.place(relx=0, rely=0.98, relwidth=1, relheight=0.02)
        MainPlot.scrollbar.set(0, 0.2)

        plt.ioff()
        plt.draw()
        plt.show()
