import PySimpleGUI as sg
import os
import pickle
import csv
import datetime
from collections import namedtuple

sg.ChangeLookAndFeel("Dark")
FileIndex = namedtuple("FileIndex","modified, dirlist")

# search functions
def re_index(path='C:\\'):
    ''' index the file directory for paths that include files '''
    modified = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dirlist = [(root, files) for root, dirs, files in os.walk(path) if files]
    file_index = FileIndex(modified, dirlist)
    
    # save index results
    with open('file_index.pkl','wb') as f:
        pickle.dump(file_index, f)

    return file_index
    
def load_index():
    ''' load an existing index if exists '''
    try:
        with open('file_index.pkl','rb') as f:
            return pickle.load(f)
    except:
        return FileIndex(None, None)

def search(index, values):
    ''' search the index for the term based on the search type '''
    # search type to include: 'contains','endswith','startswith'
    term = values['_TERM_']
    modified = index.modified
    file_index = index.dirlist
    results = []
    match_cnt = 0
    total_cnt = 0

    if values['contains']:
        for (path, files) in file_index:
            for file in files:
                total_cnt +=1
                if term.lower() in file.lower():
                    result = path + "\\" + file
                    results.append(result)
                    match_cnt +=1
    elif values['startswith']:
        for (path, files) in file_index:
            for file in files:
                total_cnt +=1
                if file.lower().startswith(term.lower()):
                    result = path + "\\" + file
                    results.append(result)
                    match_cnt +=1
    elif values['endswith']:
        for (path, files) in file_index:
            for file in files:
                total_cnt +=1
                if file.lower().endswith(term.lower()):
                    result = path + "\\" + file
                    results.append(result)
                    match_cnt +=1
    else:
        print("ERROR!! Invalid search type.")
        print("Please choose from: contains, startswith, endswith\n")

    # save results to text file
    with open('search_results.txt','w') as f:
        for row in results:
            f.write(row + "\n")
    return results, total_cnt, match_cnt

def get_gui(index):
    ''' gui layout & window setup '''
    layout = [[sg.Text('Root Path:', size=(10,1)),
               sg.Input("C:\\", size=(20,1), key="_PATH_"),
               sg.Button('Re-Index', size=(8,1), key="_INDEX_"),
               sg.Text(index.modified, key="_MODIFIED_")],
              [sg.Text('Search Term:', size=(10,1)),
               sg.Input("enter search term", size=(20,1), key="_TERM_", focus=True),
               sg.Button('Search', size=(8,1), key="_SEARCH_", bind_return_key=True)],
              [sg.Radio('Contains', group_id='type', key='contains', default=True),
               sg.Radio('StartsWith', group_id='type', key='startswith'),
               sg.Radio('EndsWith', group_id='type', key='endswith')],
              [sg.Output(size=(100,30), pad=(5,10), key="_OUT_")]]
    window = sg.Window('File Search Engine').Layout(layout)
    return window, layout

def main():
    index = load_index()
    window, layout = get_gui(index)

    while True:
        event, values = window.Read()

        if event is None:
            break
        if event == "_SEARCH_":
            window.Element('_OUT_').Update(value='')
            results, total, matches = search(index, values)
            for result in results:
                print(result)

            print("\nSearch results saved in current working directory: search_results.txt")
            print("Searched {:,d} records and found {:,d} matches.".format(total, matches))
        if event == "_INDEX_":
            index = re_index(values['_PATH_'])
            window.Element('_MODIFIED_').Update(value=index.modified)
            window.Element('_OUT_').Update(value='')
            window.Element('_OUT_').Update(value='\nFile index has been updated.')

if __name__ == "__main__":
    main()            
    
        
