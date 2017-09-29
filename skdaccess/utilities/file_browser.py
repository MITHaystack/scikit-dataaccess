# This code is modified from public domain code from:
# https://gist.github.com/DrDub/6efba6e522302e43d055

import os

import ipywidgets as widgets


class FileBrowser(object):
    def __init__(self):
        self.path = os.getcwd()
        self._update_files()

    def _update_files(self):
        self.files = list()
        self.dirs = list()
        if(os.path.isdir(self.path)):

            self.dirs.append('..')

            for f in os.listdir(self.path):
                ff = os.path.join(self.path, f)
                if os.path.isdir(ff):
                    self.dirs.append(f)
                else:
                    self.files.append(f)

    def widget(self):
        box = widgets.VBox()
        self._update(box)
        return box

    def _update(self, box):

        def on_click(b):
            if b.description == '..':
                self.path = os.path.split(self.path)[0]
            else:
                self.path = os.path.join(self.path, b.description)
            self._update_files()
            self._update(box)

        buttons = []

        for f in self.dirs:
            button = widgets.Button(description=f, background_color='#d0d0ff', layout=widgets.Layout(width='50%'))
            button.on_click(on_click)
            buttons.append(button)
        for f in self.files:
            button = widgets.Button(description=f, layout=widgets.Layout(width='50%'))
            button.style.button_color = 'powderblue'
            button.on_click(on_click)
            buttons.append(button)

        box.children = tuple([widgets.HTML("%s" % (self.path,))] + buttons)


# example usage:
#   f = FileBrowser()
#   f.widget()
#   <interact with widget, select a path>
# in a separate cell:
#   f.path # returns the selected path
