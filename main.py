from Params import Params
from MainPlot import MainPlot
from LeftMenu import LeftMenu
from TopMenu import TopMenu
from PictureBtns import PictureBtns
from ZoomAndPan import ZoomAndPan
from UpdatePlot import UpdatePlot


if __name__ == '__main__':
    Params.root.title('Traffic monitoring')
    Params.root.state('zoomed')

    MainPlot.draw_plot()

    pic_btns = PictureBtns()
    pic_btns.draw_picture_btns()

    LeftMenu.draw_left_menu()
    TopMenu.draw_top_menu()
    ZoomAndPan.zoom_and_pan()
    UpdatePlot.update()

    Params.root.mainloop()
