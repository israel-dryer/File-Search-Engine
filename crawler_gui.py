import PySimpleGUI as sg
sg.ChangeLookAndFeel("Dark")

class Gui:
    def __init__(self, crawler):
        self.crawler = crawler
        self.layout = [[sg.Text('Search Term:', size=(10,1)),
                        sg.Input('', size=(45,1), key="_TERM_", focus=True),
                        sg.Radio('Contains', group_id='type', key='contains', default=True),
                        sg.Radio('StartsWith', group_id='type', key='startswith'),
                        sg.Radio('EndsWith', group_id='type', key='endswith')],
                       [sg.Text('Root Path:', size=(10,1)),
                        sg.In("C:/", key="_PATH_", size=(45,1)),
                        sg.FolderBrowse(target=(1,1),size=(10,1)),
                        sg.Button('Re-Index', size=(10,1), key="_INDEX_"),
                        sg.Button('Search', size=(10,1), key="_SEARCH_", bind_return_key=True)],
                       [sg.Output(size=(100,30), pad=(10,10), key="_OUT_")]]                
        self.window = sg.Window('File Search Engine').Layout(self.layout)
