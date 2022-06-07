from tkinter import *
from tkinter.ttk import *


# Класс, отвечающий за слайдер с двумя ползунками
class RangeSliderV(Frame):
    LINE_COLOR = "#476b6b"
    LINE_S_COLOR = "#0a50ff"
    LINE_WIDTH = 3
    BAR_COLOR_INNER = "#5c8a8a"
    BAR_COLOR_OUTTER = "#c2d6d6"
    BAR_RADIUS = 10
    BAR_RADIUS_INNER = 5
    DIGIT_PRECISION = '.1f'  # for showing in the canvas
    FONT_SIZE = 16
    FONT_FAMILY = 'Times'
    IMAGE_ANCHOR_L = CENTER
    IMAGE_ANCHOR_U = CENTER

    def __init__(self, master, variables, Width=80, Height=400, min_val=0, max_val=1, padY=3,
                 image_anchorU=CENTER, image_anchorL=CENTER, imageL=None, imageU=None,
                 auto=True, line_width=3, bar_radius=10,
                 bar_color_inner='#5c8a8a', line_s_color="#0a50ff", bar_color_outer='#c2d6d6', line_color='#476b6b',
                 bgColor='#ffffff',
                 show_value=True, digit_precision='.1f', valueSide='LEFT', font_family='Times', font_size=16,
                 suffix=""):
        RangeSliderV.LINE_COLOR = line_color
        RangeSliderV.LINE_WIDTH = line_width
        RangeSliderV.BAR_COLOR_INNER = bar_color_inner
        RangeSliderV.BAR_COLOR_OUTTER = bar_color_outer
        RangeSliderV.BAR_RADIUS = bar_radius
        RangeSliderV.BAR_RADIUS_INNER = bar_radius - 5
        RangeSliderV.DIGIT_PRECISION = digit_precision
        RangeSliderV.FONT_SIZE = font_size
        RangeSliderV.FONT_FAMILY = font_family
        RangeSliderV.IMAGE_ANCHOR_L = image_anchorL
        RangeSliderV.IMAGE_ANCHOR_U = image_anchorU
        RangeSliderV.LINE_S_COLOR = line_s_color
        if auto:
            if imageL != None or imageU != None:
                raise Exception("Can't decide if to use auto shape or images!")
            else:
                critical1 = max(RangeSliderV.BAR_RADIUS, RangeSliderV.FONT_SIZE * 1.33 / 2)
                critical2 = 2 * (RangeSliderV.BAR_RADIUS + max(len(str(min_val)),
                                                               len(str(max_val))) * RangeSliderV.FONT_SIZE / 1.2)
                critical3 = 2 * (padY + RangeSliderV.BAR_RADIUS)
                if show_value and padY < critical1:
                    raise Exception(
                        "padY too small, handle won't be visible completely, as per given condition padY should be atleast " + str(
                            critical1 + 1) + "px.")
                if Width < critical2:
                    raise Exception(
                        "Dimensions incompatible, consider decreasing bar_radius or FONT_SIZE or consider increasing widget width, as per given conditios width should be atleast " + str(
                            critical2 + 1) + "px.")
                if Height < critical3:
                    raise Exception(
                        "Dimensions incompatible, consider decreasing bar_radius or consider increasing widget height, as per given conditios height should be atleast " + str(
                            critical3 + 1) + "px.")
                if RangeSliderV.BAR_RADIUS <= line_width:
                    raise Exception("bar_radius too small, should be minimum equal to line_width(default=3).")
                self.draw = 'auto'
        else:
            if imageL == None or imageU == None:
                raise Exception("Handle for one image missing.")
            else:
                critical1 = (imageL.height() + padY) * 2
                critical2 = imageL.width() + max(len(str(min_val)), len(str(max_val))) * RangeSliderV.FONT_SIZE / 1.2
                critical3 = max(imageU.height() / 2, RangeSliderV.FONT_SIZE * 1.33 / 2)
                if imageL.height() == imageU.height() and imageL.width() == imageU.width():
                    if critical1 < Height and critical2 < Width:
                        if show_value and padY < critical3:
                            raise Exception(
                                "padY too small, value won't be visible completely, padY mimumum expected is " + str(
                                    critical3) + "px.")
                        self.draw = 'image'
                    else:
                        raise Exception(
                            "Image dimensions not suited with widget Height and width, minimum height expected is " + str(
                                critical1) + "px and minimum width expected is " + str(critical2) + "px.")
                else:
                    raise Exception(
                        "Image dimensions incompatible, width and height of both handles should be same respectively.")
        Frame.__init__(self, master, height=Height, width=Width)
        self.pady = padY
        self.ImageL = imageL
        self.ImageU = imageU
        self.master = master
        self.init_lis = [min_val, max_val]
        self.max_val = max_val
        self.min_val = min_val
        self.show_value = show_value
        self.valueSide = valueSide
        self.H = Height
        self.W = Width
        self.canv_H = self.H
        self.canv_W = self.W
        self.suffix = suffix
        self.variables = variables
        if not show_value:
            self.slider_x = self.canv_W / 2  # y pos of the slider
        else:
            if self.valueSide == 'LEFT':
                if self.draw == 'auto':
                    self.slider_x = self.canv_W - RangeSliderV.BAR_RADIUS - 2
                elif self.draw == 'image':
                    self.slider_x = self.canv_W - self.ImageL.width() / 2 - 2
            elif self.valueSide == 'RIGHT':
                if self.draw == 'auto':
                    self.slider_x = RangeSliderV.BAR_RADIUS + 2
                else:
                    self.slider_x = self.ImageL.width() / 2 + 2
            else:
                raise Exception("valueSide can either be LEFT or RIGHT")
        self.slider_y = self.pady

        self.bars = []
        self.selected_idx = None  # current selection bar index
        for value in self.init_lis:
            pos = (value - min_val) / (max_val - min_val)
            ids = []
            bar = {"Pos": pos, "Ids": ids, "Value": value}
            self.bars.append(bar)

        self.canv = Canvas(self, height=self.canv_H, width=self.canv_W, bg=bgColor, bd=0, highlightthickness=0,
                           relief='ridge')
        self.canv.pack()
        self.canv.bind("<Motion>", self._mouseMotion)
        self.canv.bind("<B1-Motion>", self._moveBar)
        self.track = self.__addTrack(self.slider_x, self.slider_y, self.slider_x, self.canv_H - self.slider_y,
                                     self.bars[0]["Pos"], self.bars[1]["Pos"])
        tempIdx = 0
        for bar in self.bars:
            bar["Ids"] = self.__addBar(bar["Pos"], tempIdx)
            tempIdx += 1

        self.__setValues()

    def getValues(self):
        values = [bar["Value"] for bar in self.bars]
        return values

    def setValues(self, min, max):
        self.max_val = max
        self.min_val = min
        self.variables[0].set(min)
        self.variables[1].set(max)
        self.bars[0]["Value"] = min
        self.bars[1]["Value"] = max

    def updateLim(self, min, max):
        self.bars[0]["Pos"] = min
        self.bars[1]["Pos"] = max
        self.__moveBar(1, 1)

    def __setValues(self):
        values = self.getValues()
        self.variables[0].set(values[0])
        self.variables[1].set(values[1])

    def getPos(self):
        poss = [bar["Pos"] for bar in self.bars]
        return poss

    def _mouseMotion(self, event):
        x = event.x;
        y = event.y
        selection = self.__checkSelection(x, y)
        if selection[0]:
            self.canv.config(cursor="hand2")
            self.selected_idx = selection[1]
        else:
            self.canv.config(cursor="")
            self.selected_idx = None

    def _moveBar(self, event):
        x = event.x;
        y = event.y
        if self.selected_idx == None:
            return False
        pos = self.__calcPos(y)
        idx = self.selected_idx
        self.__moveBar(idx, pos)

    def __addTrack(self, startx, starty, endx, endy, posL, posU):
        rangeOutL = self.canv.create_line(startx, starty + (1 - posL) * (endy - starty), startx, endy,
                                          fill=RangeSliderV.LINE_COLOR, width=RangeSliderV.LINE_WIDTH)
        rangeS = self.canv.create_line(startx, starty + (1 - posU) * (endy - starty), startx,
                                       starty + (1 - posL) * (endy - starty), fill=RangeSliderV.LINE_S_COLOR,
                                       width=RangeSliderV.LINE_WIDTH)
        rangeOutU = self.canv.create_line(startx, starty, endx, starty + (1 - posU) * (endy - starty),
                                          fill=RangeSliderV.LINE_COLOR, width=RangeSliderV.LINE_WIDTH)
        return [rangeOutL, rangeS, rangeOutU]

    def __addTrackL(self, startx, starty, endx, endy, posL, posU):
        rangeOutL = self.canv.create_line(startx, starty + (1 - posL) * (endy - starty), startx, endy,
                                          fill=RangeSliderV.LINE_COLOR, width=RangeSliderV.LINE_WIDTH)
        rangeS = self.canv.create_line(startx, starty + (1 - posU) * (endy - starty), startx,
                                       starty + (1 - posL) * (endy - starty), fill=RangeSliderV.LINE_S_COLOR,
                                       width=RangeSliderV.LINE_WIDTH)
        # rangeOutU = self.canv.create_line(startx, starty, endx, starty+(1-posU)*(endy-starty), fill = RangeSliderV.LINE_COLOR, width = RangeSliderV.LINE_WIDTH)
        return [rangeOutL, rangeS]

    def __addTrackR(self, startx, starty, endx, endy, posL, posU):
        # rangeOutL = self.canv.create_line(startx, starty+(1-posL)*(endy-starty), startx, endy, fill = RangeSliderV.LINE_COLOR, width = RangeSliderV.LINE_WIDTH)
        rangeS = self.canv.create_line(startx, starty + (1 - posU) * (endy - starty), startx,
                                       starty + (1 - posL) * (endy - starty), fill=RangeSliderV.LINE_S_COLOR,
                                       width=RangeSliderV.LINE_WIDTH)
        rangeOutU = self.canv.create_line(startx, starty, endx, starty + (1 - posU) * (endy - starty),
                                          fill=RangeSliderV.LINE_COLOR, width=RangeSliderV.LINE_WIDTH)
        return [rangeS, rangeOutU]

    def __addBar(self, pos, tempIdx=None):
        """@ pos: position of the bar, ranged from (0,1)"""
        if pos < 0 or pos > 1:
            raise Exception("Pos error - Pos: " + str(pos))
        if self.draw == 'auto':
            R = RangeSliderV.BAR_RADIUS
            r = RangeSliderV.BAR_RADIUS_INNER
            L = self.canv_H - 2 * self.slider_y
            y = self.slider_y + (1 - pos) * L
            x = self.slider_x
            id_outer = self.canv.create_oval(x - R, y - R, x + R, y + R, fill=RangeSliderV.BAR_COLOR_OUTTER, width=2,
                                             outline="")
            id_inner = self.canv.create_oval(x - r, y - r, x + r, y + r, fill=RangeSliderV.BAR_COLOR_INNER, outline="")
            if self.show_value:
                if self.valueSide == 'LEFT':
                    x_value = x - RangeSliderV.BAR_RADIUS - RangeSliderV.FONT_SIZE / 2
                    value = pos * (self.max_val - self.min_val) + self.min_val
                    id_value = self.canv.create_text(x_value, y, anchor=E,
                                                     text=format(value, RangeSliderV.DIGIT_PRECISION) + self.suffix,
                                                     font=(RangeSliderV.FONT_FAMILY, RangeSliderV.FONT_SIZE))
                elif self.valueSide == 'RIGHT':
                    x_value = x + RangeSliderV.BAR_RADIUS + RangeSliderV.FONT_SIZE / 2
                    value = pos * (self.max_val - self.min_val) + self.min_val
                    id_value = self.canv.create_text(x_value, y, anchor=W,
                                                     text=format(value, RangeSliderV.DIGIT_PRECISION) + self.suffix,
                                                     font=(RangeSliderV.FONT_FAMILY, RangeSliderV.FONT_SIZE))
                else:
                    raise Exception("valueSide can either be LEFT or RIGHT.")
                return [id_outer, id_inner, id_value]
            else:
                return [id_outer, id_inner]
        elif self.draw == 'image':
            L = self.canv_H - 2 * self.slider_y
            y = self.slider_y + (1 - pos) * L
            x = self.slider_x
            if tempIdx == 0:
                imageH = self.canv.create_image(x, y, anchor=RangeSliderV.IMAGE_ANCHOR_L, image=self.ImageL)
            elif tempIdx == 1:
                imageH = self.canv.create_image(x, y, anchor=RangeSliderV.IMAGE_ANCHOR_U, image=self.ImageU)
            if self.show_value:
                if self.valueSide == 'LEFT':
                    x_value = x - self.ImageL.width() / 2 - RangeSliderV.FONT_SIZE / 2
                    value = pos * (self.max_val - self.min_val) + self.min_val
                    id_value = self.canv.create_text(x_value, y, anchor=E,
                                                     text=format(value, RangeSliderV.DIGIT_PRECISION) + self.suffix,
                                                     font=(RangeSliderV.FONT_FAMILY, RangeSliderV.FONT_SIZE))
                elif self.valueSide == 'RIGHT':
                    x_value = x + self.ImageL.width() / 2 + RangeSliderV.FONT_SIZE / 2
                    value = pos * (self.max_val - self.min_val) + self.min_val
                    id_value = self.canv.create_text(x_value, y, anchor=W,
                                                     text=format(value, RangeSliderV.DIGIT_PRECISION) + self.suffix,
                                                     font=(RangeSliderV.FONT_FAMILY, RangeSliderV.FONT_SIZE))
                else:
                    raise Exception("valueSide can either be LEFT or RIGHT")
                return [imageH, id_value]
            else:
                return [imageH]

    def __moveBar(self, idx, pos):
        positions = self.getPos()
        current_pos = self.bars[idx]["Pos"]
        for i in range(0, 2):
            ids = self.bars[i]["Ids"]
            for id in ids:
                self.canv.delete(id)
        for trackComponentsId in self.track[idx:idx + 2]:
            self.canv.delete(trackComponentsId)
        if idx == 0:
            otherIdx = 1
            otherPos = positions[1]
            if pos <= otherPos:
                pos = pos
            else:
                pos = current_pos
            self.track[0:2] = self.__addTrackL(self.slider_x, self.slider_y, self.slider_x, self.canv_H - self.slider_y,
                                               pos, otherPos)
        else:
            otherIdx = 0
            otherPos = positions[0]
            if pos >= otherPos:
                pos = pos
            else:
                pos = current_pos
            self.track[1:3] = self.__addTrackR(self.slider_x, self.slider_y, self.slider_x, self.canv_H - self.slider_y,
                                               otherPos, pos)

        self.bars[idx]["Ids"] = self.__addBar(pos, idx)
        self.bars[idx]["Pos"] = pos
        self.bars[idx]["Value"] = pos * (self.max_val - self.min_val) + self.min_val

        self.bars[otherIdx]["Ids"] = self.__addBar(otherPos, otherIdx)
        self.bars[otherIdx]["Pos"] = otherPos
        self.bars[otherIdx]["Value"] = otherPos * (self.max_val - self.min_val) + self.min_val

        self.__setValues()

    def __calcPos(self, y):
        """calculate position from x coordinate"""
        pos = (y - self.slider_y) / (self.canv_H - 2 * self.slider_y)
        pos = 1 - pos
        if pos < 0:
            return 0
        elif pos > 1:
            return 1
        else:
            return pos

    def __checkSelection(self, x, y):
        """
        To check if the position is inside the bounding rectangle of a Bar
        Return [True, bar_index] or [False, None]
        """
        for idx in range(len(self.bars)):
            id = self.bars[idx]["Ids"][0]
            bbox = self.canv.bbox(id)
            if bbox[0] < x and bbox[2] > x and bbox[1] < y and bbox[3] > y:
                return [True, idx]
        return [False, None]