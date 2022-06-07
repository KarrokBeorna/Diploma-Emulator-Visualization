import time
import threading
import math
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.offsetbox import TextArea, AnnotationBbox

from Params import Params
from LeftMenu import LeftMenu
from MainPlot import MainPlot
from TopMenu import TopMenu


# Класс, отвечающий за обновление всех графиков: основной, яркости/контраста, сравнения
class UpdatePlot(object):

    @staticmethod
    def update():

        # Функция обновления отображения
        def modify_plot():

            Params.bar_values.clear()
            local_time_frame = Params.time_frame
            local_ts1, local_ts2 = LeftMenu.thresholds_slider.getValues()
            local_scale = Params.scale
            local_value_brightness = LeftMenu.brightness_slider.get()
            local_value_contrast = LeftMenu.contrast_slider.get()

            # Автоматический сдвиг слайдера после 199 кадра
            if local_time_frame > 199 and Params.auto and not Params.manual_shift:
                l = (local_time_frame - 199) / 1000
                MainPlot.scrollbar.set(l, l + 0.2)

            local_left, local_right = MainPlot.scrollbar.get()
            left_frame = int(local_left * 1000)
            sum_initial_data = 0.0

            # Извлечение минимального и максимального значения
            data_max = Params.data.max()
            if local_scale == 'Linear':
                nmax = data_max if data_max != 0 else 1
                nmin = Params.data.min()
            elif local_scale == 'Sqrt':
                nmax = math.sqrt(data_max) if data_max != 0 else 1
                nmin = math.sqrt(Params.data.min())
            elif local_scale == 'Log':
                nmax = math.log2(data_max + 1) if data_max != 0 else 1
                nmin = math.log2(Params.data.min() + 1)

            # Функция обновления scrollbar
            def modify_scrollbar():
                if Params.comparison:
                    sum_reference_data = 0.0
                    sigma = 0.0
                    if local_scale == 'Linear':
                        ref_max = Params.reference_config_data.max()
                    elif local_scale == 'Sqrt':
                        ref_max = math.sqrt(Params.reference_config_data.max())
                    elif local_scale == 'Log':
                        ref_max = math.log2(Params.reference_config_data.max() + 1)
                    new_data_max = Params.new_data.max()
                    if Params.first_comparison:
                        for r in range(Params.NUM_CHANNELS):
                            for c in range(Params.NUM_FRAMES):
                                new_elem = Params.reference_config_data[r][c] * new_data_max / ref_max * 8
                                Params.reference_config_data[r][c] = new_elem if new_elem < new_data_max else new_data_max
                        Params.first_comparison = False

                    Params.rcd_slice.fill(0)
                    for r in range(y1, y2):
                        for c in range(x1, x2):
                            if local_scale == 'Linear':
                                elem_reference_data = Params.reference_config_data[r][(c + Params.n) % Params.NUM_FRAMES]
                            elif local_scale == 'Sqrt':
                                elem_reference_data = math.sqrt(Params.reference_config_data[r][(c + Params.n) % Params.NUM_FRAMES])
                            elif local_scale == 'Log':
                                elem_reference_data = math.log2(Params.reference_config_data[r][(c + Params.n) % Params.NUM_FRAMES] + 1)
                            sum_reference_data += elem_reference_data
                            Params.rcd_slice[r][c - x1] = elem_reference_data
                            sigma += (Params.new_data[r][c - x1] - elem_reference_data) ** 2

                    Params.rcd_slice[0][0] = ref_max
                    f_value = abs(sum_reference_data - sum_initial_data)
                    s_value = abs(sum_reference_data - sum_initial_data) / max(sum_initial_data, sum_reference_data)
                    sigma = math.sqrt(sigma / ((x2 - x1) * (y2 - y1) - 1))
                    TopMenu.energy_diff.set(f'Energy difference: {f_value:.3f}; {s_value * 100:.3f}%')
                    TopMenu.sigma.set(f'σ: {sigma / nmax:.3f}')

                    MainPlot.scrollbar.set(x1 / 1000, x2 / 1000)
                    Params.new_data[y1][0] = nmax
                    TopMenu.p3.set_data(Params.new_data[y1:y2, :x2-x1])
                    TopMenu.p3.set_extent((x1, x2, y1, y2))

                    # Обновление осей цветовой карты
                    TopMenu.graph_axes3.set_xlim(x1, x2)
                    TopMenu.graph_axes3.set_ylim(y1, y2)

                    TopMenu.p4.set_data(Params.rcd_slice[y1:y2, :x2-x1])
                    TopMenu.p4.set_extent((x1, x2, y1, y2))

                    # Обновление осей цветовой карты
                    TopMenu.graph_axes4.set_xlim(x1, x2)
                    TopMenu.graph_axes4.set_ylim(y1, y2)

                    TopMenu.p3.autoscale()
                    TopMenu.p4.autoscale()

                    TopMenu.canvas3.draw()
                    TopMenu.canvas4.draw()

                else:
                    # Изменение границ слайдера диапазона после 999 кадра
                    if local_time_frame > 999 and Params.auto and not Params.manual_shift:
                        MainPlot.scrollbar.set(0.8, 1)

                    # Передача данных на цветовую карту и установка экстентов
                    MainPlot.p1.set_data(Params.new_data)
                    MainPlot.p1.set_extent((left_frame, left_frame + 200, 0, Params.NUM_CHANNELS))

                    # Обновление осей цветовой карты
                    MainPlot.graph_axes.set_xlim(left_frame, left_frame + 200)
                    MainPlot.graph_axes.set_ylim(0, Params.NUM_CHANNELS)

                # Обновление значения слайдера, если изменилась шкала
                if Params.previous_scale != local_scale or Params.reset or Params.old_max_element != data_max:
                    LeftMenu.thresholds_slider.setValues(nmin, nmax)
                    LeftMenu.thresholds_slider.updateLim(nmin, nmax)
                    Params.previous_scale = local_scale
                    Params.reset = False
                    Params.old_max_element = data_max

            # Так как с 1000 кадра происходит заполнение массива с самого начала,
            # то необходимо задать смещение для массива
            if local_time_frame > 999:
                Params.n = local_time_frame + 1

            # Заполнение массива исходными/из-под корня/логарифмическими данными
            if Params.view_var.get() == '4 - Corrected SNR':
                if Params.comparison:
                    x1, x2 = int(TopMenu.x1_entry.get()), int(TopMenu.x2_entry.get())
                    y1, y2 = int(TopMenu.y1_entry.get()), int(TopMenu.y2_entry.get())
                    if x2 < x1 or x2 > Params.NUM_FRAMES:
                        x1, x2 = left_frame, left_frame + 200
                    if x1 >= Params.NUM_FRAMES:
                        x1 = Params.NUM_FRAMES - 200 if Params.NUM_FRAMES - 200 >= 0 else 0
                        x2 = Params.NUM_FRAMES
                    if x2 - x1 > 200:
                        x2 = x1 + 200
                    if y2 < y1 or y1 > Params.NUM_CHANNELS:
                        y1, y2 = 0, Params.NUM_CHANNELS
                    if y2 > Params.NUM_CHANNELS:
                        y2 = Params.NUM_CHANNELS
                else:
                    y1, y2 = 0, Params.NUM_CHANNELS
                    x1, x2 = left_frame, left_frame + 200
                Params.new_data.fill(0)
                for r in range(y1, y2):
                    for c in range(x1, x2):
                        if local_scale == 'Linear':
                            temp_value = Params.data[r][(c + Params.n) % Params.NUM_FRAMES]
                        elif local_scale == 'Sqrt':
                            temp_value = math.sqrt(Params.data[r][(c + Params.n) % Params.NUM_FRAMES])
                        elif local_scale == 'Log':
                            temp_value = math.log2(Params.data[r][(c + Params.n) % Params.NUM_FRAMES] + 1)

                        if temp_value != 0:
                            if local_value_brightness >= 0:
                                with_brightness = temp_value + (nmax - temp_value) * local_value_brightness
                            else:
                                with_brightness = temp_value + (temp_value - nmin) * local_value_brightness

                            value_minus_mean = with_brightness - (nmax + nmin) / 2

                            if local_value_contrast >= 0:
                                if value_minus_mean >= 0:
                                    with_contrast = (nmax - with_brightness) * local_value_contrast
                                else:
                                    with_contrast = (nmin - with_brightness) * local_value_contrast
                            else:
                                with_contrast = (with_brightness - (nmax + nmin) / 2) * local_value_contrast

                            if local_ts1 <= with_brightness + with_contrast <= local_ts2:
                                Params.new_data[r][c - x1] = with_brightness + with_contrast
                                Params.bar_values.append(with_brightness + with_contrast)
                                sum_initial_data += with_brightness + with_contrast
                            else:
                                Params.new_data[r][c - x1] = 0
            elif Params.view_var.get() == '9 - Tracks of target':
                for r in range(Params.NUM_CHANNELS):
                    for c in range(local_time_frame - 50, local_time_frame if local_time_frame > 49 else local_time_frame + 2):
                        if local_time_frame - c > 49:
                            Params.data[r][(local_time_frame - 50 + Params.n) % Params.NUM_FRAMES] = 0
                            Params.new_data[r][c - left_frame] = 0
                        else:
                            if local_scale == 'Linear':
                                temp_value = Params.data[r][(c + Params.n) % Params.NUM_FRAMES]
                            elif local_scale == 'Sqrt':
                                temp_value = math.sqrt(Params.data[r][(c + Params.n) % Params.NUM_FRAMES])
                            elif local_scale == 'Log':
                                temp_value = math.log2(Params.data[r][(c + Params.n) % Params.NUM_FRAMES] + 1)

                            if temp_value != 0:
                                Params.new_data[r][c - left_frame] = temp_value / (1.1 ** (local_time_frame - c))
                if TopMenu.disconnect and Params.time_frame < Params.last_time_frame + 50:
                    Params.need_update_plot = True
                    Params.time_frame += 1
            Params.new_data[0][0] = nmax

            # Обновление прокрутки и слайдера среза
            modify_scrollbar()

            # Обновление шкалы и цвета
            MainPlot.canvas1.draw()
            MainPlot.p1.autoscale()
            if Params.view_var.get() == '4 - Corrected SNR':
                # Очистка осей у графика яркости/контраста
                LeftMenu.p2.cla()
                LeftMenu.p2.set_xlim(0, nmax)
                LeftMenu.p2 = sns.kdeplot(data=Params.bar_values, ax=LeftMenu.a2, warn_singular=False)
                LeftMenu.canvas2.draw()
            elif Params.view_var.get() == '9 - Tracks of target':
                delete_track = []
                for i, track in enumerate(Params.data_tracks):
                    if track[9] == 'not used':
                        if track[7] not in Params.moving_targets:
                            if track[6] > 0:
                                x_dot2 = track[0] + track[6] * 0.25
                                y_dot2 = track[1] - track[6] * 2.1 * math.sqrt(Params.NUM_CHANNELS) / 37
                                x_dot4 = track[0] - track[6] * 0.37
                                y_dot4 = track[1] - 0.07 * track[6]
                            else:
                                x_dot2 = track[0] + track[6] * 0.37
                                y_dot2 = track[1] - 0.07 * track[6]
                                x_dot4 = track[0] - track[6] * 0.25
                                y_dot4 = track[1] - track[6] * 2.1 * math.sqrt(Params.NUM_CHANNELS) / 37
                            target = Polygon([[track[0] + (-11 + 2.2 * math.log2(Params.NUM_CHANNELS)) / abs(track[6]) + 1,
                                               track[1] + np.sign(track[6]) * 0.04 * Params.NUM_CHANNELS],
                                              [x_dot2 + 1, y_dot2],
                                              [track[0] + 1, track[1]],
                                              [x_dot4 + 1, y_dot4]],
                                             edgecolor='gray',
                                             facecolor=LeftMenu.colours[int(track[8])],
                                             linewidth=1)
                            MainPlot.graph_axes.add_patch(target)
                            ab = MainPlot.graph_axes.annotate(f'{track[6]:.2f}\nid_{int(track[7])}',
                                                              (track[0] + 4, track[1]),
                                                              ha='left',
                                                              va='center',
                                                              color='white',
                                                              bbox=dict(boxstyle="round", fc="black"))
                            plt.show()
                            Params.moving_targets[int(track[7])] = [target, track, ab]

                    track[9] = 'used'
                    delete_track.append(track)
                for track in delete_track:
                    Params.data_tracks.remove(track)
            Params.ready = True

        # Функция фонового обновления графика - передаётся в один из потоков
        def update_plot():
            while True:
                time.sleep(0.1)
                if Params.auto and Params.need_update_plot and Params.ready or Params.reset and Params.ready:
                    Params.ready = False
                    Params.need_update_plot = False
                    modify_plot()

        def update_target_pos():
            while True:
                copy_arr = Params.moving_targets.copy()
                time.sleep(0.00001)
                for id_target in copy_arr:
                    target, track, ab = Params.moving_targets[id_target]
                    path = target.get_xy()
                    if 0 <= path[2][1] <= Params.NUM_CHANNELS and not TopMenu.disconnect:
                        target.set_xy([[path[0][0] + 0.01553, path[0][1] + track[6] / 20.8],
                                       [path[1][0] + 0.01553, path[1][1] + track[6] / 20.8],
                                       [path[2][0] + 0.01553, path[2][1] + track[6] / 20.8],
                                       [path[3][0] + 0.01553, path[3][1] + track[6] / 20.8]])
                        ab.set_x(path[2][0] + 4)
                        ab.set_y(path[2][1])
                        Params.need_update_plot = True
                    else:
                        target.set_visible(False)
                        ab.set_visible(False)
                        del Params.moving_targets[id_target]
        thread2 = threading.Thread(target=update_plot)
        thread2.start()

        thread3 = threading.Thread(target=update_target_pos)
        thread3.start()
