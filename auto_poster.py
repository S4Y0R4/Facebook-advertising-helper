from poster import Poster
from custom_gui_setup import AutoPosterGUI

poster = Poster()
gui = AutoPosterGUI(poster)
poster.bind_gui(gui)
poster.start_driver()