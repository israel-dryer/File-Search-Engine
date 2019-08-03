from crawler_gui import *
from crawler_search import *

crawler = Crawler()
gui = Gui(crawler)

def main():

    crawler.load_existing_index()

    while True:
        event, values = gui.window.Read()

        if event is None:
            quit()
                
        if event == '_SEARCH_':
            print(event)
            gui.window.Element('_OUT_').Update(value='') # clear output
            crawler.search(values)

            for result in crawler.results:
                print(result)

            print("\nSearch results saved in current working directory: search_results.txt")
            print("Searched {:,d} records and found {:,d} matches.".format(crawler.records, crawler.matches))

        if event == "_INDEX_":
            crawler.create_new_index(values)
            gui.window.Element('_OUT_').Update(value='')
            gui.window.Element('_OUT_').Update(value='\nFile index has been updated.')
        
main()
