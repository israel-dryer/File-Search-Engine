from collections import namedtuple
import datetime
import pickle
import os

FileIndex = namedtuple("FileIndex","modified directory")

class Crawler:
    def __init__(self):
        self.file_index = FileIndex(None, None)
        self.results = []
        self.matches = 0
        self.records = 0

    def create_new_index(self, values):
        path = values['_PATH_']
        modified = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        directory = [(root, files) for root, dirs, files in os.walk(path) if files]
        self.file_index = FileIndex(modified, directory)

        # save index to file
        with open('file_index.pkl','wb') as pkl:
            pickle.dump(self.file_index, pkl)

    def load_existing_index(self):
        try:
            with open('file_index.pkl','rb') as pkl:
                self.file_index = pickle.load(pkl)
        except:
            self.file_index = FileIndex(None, None)

    def search(self, values):
        self.matches = 0
        self.records = 0
        self.results.clear()
        term = values['_TERM_']

        for (path, files) in self.file_index.directory:
            for file in files:
                self.records +=1
                if (values['contains'] and term.lower() in file.lower() or
                    values['startswith'] and file.lower().startswith(term.lower()) or
                    values['endswith'] and file.lower().endswith(term.lower())):

                    result = path.replace('\\','/') + "/" + file
                    self.results.append(result)
                    self.matches +=1
                else:
                    continue

        # save results to text file
        with open('search_results.txt','w') as f:
            for row in self.results:
                f.write(row + "\n")       
    

            
