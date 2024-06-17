# import parser object from tika
from tika import parser

def tika_read_content(filename:str):
# ***assumes file is available, no error check
    filecontent = parser.from_file(filename)
    return (filecontent['content'])

