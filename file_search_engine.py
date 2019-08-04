import os
import datetime
import pickle
from collections import namedtuple
import PySimpleGUI as sg

FileIndex = namedtuple("FileIndex","modified directory")
sg.ChangeLookAndFeel("Dark")

class Gui:
    def __init__(self):
        self.layout = [[sg.Text('Search Term:', size=(10,1)),
                        sg.Input(size=(45,1), focus=True, key="TERM"),
                        sg.Radio('Contains', group_id='type', default=True, key="CONTAINS"),
                        sg.Radio('StartsWith', group_id='type', key="STARTSWITH"),
                        sg.Radio('EndsWith', group_id='type', key="ENDSWITH")],
                       [sg.Text('Root Path:', size=(10,1)),
                        sg.In('C:/', size=(45,1), key="PATH"),
                        sg.FolderBrowse(size=(10,1)),
                        sg.Button('Re-Index', size=(10,1), key="_INDEX_"),
                        sg.Button('Search', size=(10,1), bind_return_key=True, key="_SEARCH_")],
                       [sg.Output(size=(100,30))]]
        self.window = sg.Window('File Search Engine').Layout(self.layout)


class Crawler:
    def __init__(self):
        self.file_index = FileIndex(None, None)
        self.results = [] # store the search results
        self.matches = 0 # count the number of matches
        self.records = 0 # count the number of records searched

    def create_new_index(self, values):
        ''' create a new index of the root path, and save the index file '''
        root_path = values['PATH']
        modified = datetime.datetime.now().strftime("%Y-%m-%d %h:%M:%S")
        directory = [(root, files) for root, dirs, files in os.walk(root_path) if files]
        self.file_index = FileIndex(modified, directory)

        # save index to file
        with open('file_index.pkl','wb') as pkl:
            pickle.dump(self.file_index, pkl)

    def load_existing_index(self):
        ''' load an existing index into the program '''
        try:
            with open('file_index.pkl','rb') as pkl:
                self.file_index = pickle.load(pkl)
        except:
            self.file_index = FileIndex(None, None)

    def search(self, values):
        ''' search for the term based on the search type in the index
            the types of search include: contains, startswith, endswith,
            and save the search results to file '''
        self.results.clear()
        self.matches = 0
        self.records = 0
        term = values['TERM']

        # search for matches and count results
        for path, files in self.file_index.directory:
            for file in files:
                self.records +=1
                if (values['CONTAINS'] and term.lower() in file.lower() or
                    values['STARTSWITH'] and file.lower().startswith(term.lower()) or
                    values['ENDSWITH'] and file.lower().endswith(term.lower())):

                    result = path.replace('\\','/') + '/' + file
                    self.results.append(result)
                    self.matches +=1
                else:
                    continue

        # save results to file
        with open('search_results.txt','w') as f:
            for row in self.results:
                f.write(row + "\n")


def main():
    c = Crawler()
    gui = Gui()
    c.load_existing_index()

    while True:
        event, values = gui.window.Read()

        if event is None:
            break
        if event == '_INDEX_':
            c.create_new_index(values)
            print("\nNew index created.")
        if event == '_SEARCH_':
            c.search(values)

            # print the results to the output element
            print()
            for result in c.results:
                print(result)

            print("\nSearch results saved to current working directory as search_results.txt")
            print("Searched {:,d} records and found {:,d} matches.".format(c.records, c.matches))

main()

















                
