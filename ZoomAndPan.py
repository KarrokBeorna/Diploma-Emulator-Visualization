from mpl_interactions import panhandler, zoom_factory

from Params import Params
from MainPlot import MainPlot


# Класс, отвечающий за приближение/отдаление графика и его перемещение при помощи ПКМ
class ZoomAndPan(object):

    pan_handler = None

    @staticmethod
    def zoom_and_pan():

        # Функция центрирования графика
        def on_double_click(event):
            if event.dblclick:
                local_left, local_right = MainPlot.scrollbar.get()
                left_frame = int(local_left * 1000)
                MainPlot.graph_axes.set_xlim(left_frame, left_frame + 200)
                MainPlot.graph_axes.set_ylim(0, Params.NUM_CHANNELS)
                Params.need_update_plot = True

        # Перетаскивание, Двойной щелчок
        ZoomAndPan.pan_handler = panhandler(MainPlot.fig)
        MainPlot.fig.canvas.mpl_connect('button_press_event', on_double_click)
        zoom_factory(MainPlot.graph_axes, 1.1)
