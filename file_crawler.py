import os
import pickle
from collections import namedtuple

def welcome():
    os.system('cls')
    print('''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Welcome to FILE CRAWLER
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Use the map() function to create a directory map of all files on your computer.
Use the search() function to search for a term.

The search term accepts two parameters ( term, type )

The type of search can be one of the following, but defaults to 0:

    0 contains (a search that finds all words containing the search term)
    1 starts (a search that finds all words starting with the search term)
    2 ends (a search that finds all words starting with the search term)

Happy searching!!\n''')
    map_dirs()
    get_choice()

def get_choice():
    choice = int(input("\nEnter a choice: (1) search (2) exit: "))

    if choice == 1:
        search()
    else:
        print("\nThank you for searching. Have a nice day.\n")
        exit()

# create a script that will index my storage and search for files

index = []
saved_index = '{}\\index.pkl'.format(os.getcwd())

def map_dirs():
    r'''
    Run this function to create a map of files and paths. Empty directories will not be included
    in the file index in order to speed up searches.

    The user will be asked for a path name. If the path does not exists, then the map will be
    rejected. A valid naming convention should be used such as --> C:\users\

    Make sure that you include forward or back-slashes in your path name in order to get valid
    path mapping.
    
    '''
    global index, saved_index
    
    # ask user for root path to index
    path = input("\nINDEX PATH: ")

    def run_search():
        for root, dirs, files in os.walk(path):
            if files:
                index.append([root, files])
            else:
                continue
                
    if os.path.exists(path):
        if os.path.exists(saved_index):
            print()
            print("\nWORKING DIRECTORY: " + os.getcwd())
            choice = input("\nThere is an existing index. Use existing index? (Y/N): ")
            if choice.lower()=='y':
                with open(saved_index, 'rb') as f:
                    index = pickle.load(f)
                print("Index loaded.\n")
            else:
                print("\nCreating new index...")
                run_search()
                with open(saved_index, 'wb') as f:
                    pickle.dump(index, f)
                print("Done.\n")
        else:
            print("\nCreating new index...")
            run_search()
            with open(saved_index, 'wb') as f:
                pickle.dump(index, f)
            print("Done.\n")
    else:
        print("\nERROR!! Path does not exist!\n")
        get_choice()
          
def search():
    '''
    Find all files that contain the search term. You can perform different types of searches which
    are indicated by:
        0 contains (a search that finds all words containing the search term)
        1 starts (a search that finds all words starting with the search term)
        2 ends (a search that finds all words starting with the search term)
    '''
    global index
    results = []
    result_cnt = 0
    file_cnt = 0

    term = input("\nWhat do you want to search for? ")
    search_type = int(input("\nWhat type of search? (0=contains, 1=starts, 2=ends): "))

    if search_type == 0:
        for root, files in index:
            for file in files:
                if term.lower() in file.lower():
                     results.append(['{}\\{}'.format(root, file)])
                     result_cnt += 1
                     file_cnt += 1
                else:
                    file_cnt += 1
                    continue
    elif search_type == 1:
        for root, files in index:
            for file in files:
                if file.lower().startswith(term.lower()):
                     results.append(['{}\\{}'.format(root, file)])
                     result_cnt += 1
                     file_cnt += 1
                else:
                    file_cnt += 1
                    continue
    elif search_type == 2:
        for root, files in index:
            for file in files:
                if file.lower().endswith(term.lower()):
                     results.append('{}\\{}'.format(root, file))
                     result_cnt += 1
                     file_cnt += 1
                else:
                    file_cnt += 1
                    continue
    else:
        print("\nNot a valid type. 0=contains 1=starts 2=ends")

    print("-"*50)
    print("{:,d} matches found in {:,d} files searched.".format(result_cnt, file_cnt))
    print("-"*50)
    for result in results:
        print(result)

    with open('search_results.txt','w') as f:
        for result in results:
            f.write(result[0] + "\n")
    print("\nResults have been saved to: {}".format(os.getcwd() + "\\search_results.txt"))
    get_choice()

if __name__=='__main__':
    welcome()
    map()
