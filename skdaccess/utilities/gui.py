# The MIT License (MIT)
# Copyright (c) 2018 Massachusetts Institute of Technology
#
# Authors: Cody Rude
# This software has been created in projects supported by the US National
# Science Foundation and NASA (PI: Pankratius)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# 3rd part imports
import ipywidgets as widgets
from IPython.display import display

# Standard library imports
import configparser


class ConfigGUI(object):
    '''
    Jupyter GUI for editing ini config files with configparser

    Uses ipywidgets to edit a config file. Note that comments are not saved as
    configparser is used to read and write configuration file
    '''


    def __init__(self, filename):
        '''
        Initialize ConfigGUI Object

        @param filename: Input configuration filename
        '''
        # Location of file
        self.filename = filename


        # Create buttons for editing a sections configuration
        self.save_button = widgets.Button(description = 'Save', layout=widgets.Layout(width='34%'))
        self.save_button.on_click(self.saveConfig)

        self.add_button = widgets.Button(description = 'Add Entry',layout=widgets.Layout(width='34%'))
        self.add_button.on_click(self.addEntry)

        def deleteSection(in_button):
            '''
            Delete current section from config file

            @param in_button: Ignored
            '''
            self.setWidgetStatus(False)

            def removeCurrentSection(in_button):
                '''
                Delete current section from config file and reset GUI

                @param in_button: Ignored
                '''
                if self.conf.remove_section(self.section_name):
                    with open(self.filename, "w") as conf_handle:
                        self.conf.write(conf_handle)


                self.full_hbox.children = (self.full_hbox.children[0],)
                self.displaySectionWidgets()
                self.setWidgetStatus(True)


            def cancelDelete(in_button):
                '''
                Cancel delete request

                @param in_button: Ignored
                '''
                self.full_hbox.children[1].children = self.full_hbox.children[1].children[:-1]
                self.setWidgetStatus(True)


            confirm_button = widgets.Button(description = 'Confirm')
            confirm_button.button_style = 'danger'
            confirm_button.on_click(removeCurrentSection)

            cancel_button = widgets.Button(description = 'Cancel')
            cancel_button.button_style = 'warning'
            cancel_button.on_click(cancelDelete)


            self.full_hbox.children[1].children += (widgets.HBox([confirm_button,cancel_button]),)

        self.delete_section_button = widgets.Button(description='Delete Section', layout=widgets.Layout(width='34%'))
        self.delete_section_button.on_click(deleteSection)



        self.new_section_text = widgets.Text(value='', placeholder='New Section Name', layout=widgets.Layout(width='91%'))

        self.new_section_button = widgets.Button(description='New Section')
        self.new_section_button.style.button_color = 'limegreen'

        def createNewSection(in_button):
            '''
            Create new section

            Name for section is obtained from self.new_section_text

            @param in_button: Ignored
            '''

            if self.new_section_text.value != '':
                self.key_widget_list = []
                self.value_widget_list = []
                self.section_name = self.new_section_text.value
                self.new_section_text.value = ''

                self.addEntry(None)

        self.new_section_button.on_click(createNewSection)


        # Read in config file
        self.conf = configparser.ConfigParser()
        self.conf.read(self.filename)


        # Make lists to store widgets
        self.key_widget_list = []
        self.value_widget_list = []

        # Full HBox stores the full GUI
        self.full_hbox = widgets.HBox()

        # Populate full_hbox
        self.displaySectionWidgets()


        # Display full_hbox
        display(self.full_hbox)


    def displaySectionWidgets(self):
        '''
        Generate section buttons and display section GUI
        '''
        self.section_widgets_list = []
        for key in self.conf.sections():
            self.section_widgets_list.append(widgets.Button(description=key))
            self.section_widgets_list[-1].on_click(self.buildOptionBoxes)

        section_vbox = widgets.VBox(self.section_widgets_list + [self.new_section_text, self.new_section_button])

        self.full_hbox.children = (section_vbox,) + self.full_hbox.children[1:]


    def buildOptionBoxes(self, in_button):
        '''
        Generate widgets for editing configuration key, value pairs

        @param in_button: Button used call function. Section name is determined from button description
        '''
        self.key_widget_list = []
        self.value_widget_list = []

        self.section_name = in_button.description
        for key, value in self.conf[self.section_name].items():
            self.key_widget_list.append(widgets.Text(value=key, placeholder='Enter new key',
                                                layout=widgets.Layout(flex='2 1 auto', width='auto')))
            self.value_widget_list.append(widgets.Text(value=value, placeholder = 'Enter new Value'))

        self.displayOptionWidgets()


    def displayOptionWidgets(self):
        '''
        Display the part of the gui for editing config file
        '''

        if len(self.key_widget_list) == 0:
            self.addEntry(None)


        option_hboxes = [widgets.Label(value = self.section_name, layout=widgets.Layout(width='auto'))]

        option_hboxes += [widgets.HBox([key,value]) for key,value in zip(self.key_widget_list, self.value_widget_list)]
        option_hboxes += [widgets.HBox([self.save_button, self.add_button])]
        option_hboxes += [self.delete_section_button]

        button_vbox = widgets.VBox(option_hboxes)

        self.full_hbox.children = (self.full_hbox.children[0], button_vbox)


    def addEntry(self, in_button=None):
        '''
        Add entry for new key value pair

        @param in_button: Ignored
        '''

        self.key_widget_list.append(widgets.Text(value='', placeholder='Enter new key',
                                                 layout=widgets.Layout(flex='2 1 auto', width='auto')))
        self.value_widget_list.append(widgets.Text(value='', placeholder = 'Enter new value'))

        self.displayOptionWidgets()

    def saveConfig(self, in_button):
        '''
        Save changes to section

        @param in_button: Ignored
        '''

        if self.section_name not in self.conf:
            self.conf.add_section(self.section_name)
            self.displaySectionWidgets()

        # Add or update keys
        index_to_remove = []
        for index, (key_button, value_button) in enumerate(zip(self.key_widget_list, self.value_widget_list)):
            if key_button.value != '':
                self.conf[self.section_name][key_button.value] = value_button.value
            else:
                index_to_remove.append(index)


        for i in reversed(index_to_remove):
            del self.key_widget_list[i]
            del self.value_widget_list[i]


        # Delete unwanted keys config parser
        valid_keys = set(key.value for key in self.key_widget_list if key.value != '')
        current_keys = set(self.conf[self.section_name])

        keys_to_remove = current_keys - valid_keys

        for key in keys_to_remove:
            del self.conf[self.section_name][key]

        # Write config
        with open(self.filename, "w") as conf_handle:
            self.conf.write(conf_handle)


        self.displayOptionWidgets()


    def setWidgetStatus(self, status=True):
        '''
        Change the status of widgets in GUI

        @param status: Enable buttons (True), disable buttons (False)
        '''

        disabled = not status

        for key_widget, value_widget in zip(self.key_widget_list, self.value_widget_list):
            key_widget.disabled = disabled
            value_widget.disabled = disabled

        self.add_button.disabled = disabled
        self.save_button.disabled = disabled
        self.delete_section_button.disabled = disabled
        self.new_section_text.disabled = disabled
        self.new_section_button.disabled = disabled



        for section_widget in self.section_widgets_list:
            section_widget.disabled = disabled
