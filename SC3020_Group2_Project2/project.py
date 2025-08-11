from interface import GUI_Window
from preprocessing import db_connect_and_obtain_qep
from pipesyntax import generate_pipe_syntax

def sql_to_pipe_syntax_converter(params):
    # Take in database connection settings and input SQL query 
    # In "preprocessing.py", feed these to PostgreSQL to obtain QEP in JSON format
    qep = db_connect_and_obtain_qep(params)
    # In "pipesyntax.py", feed QEP into conversion algorithm to generate pipe syntax dynamically 
    pipe_syntax = generate_pipe_syntax(qep)
    # Returns both the QEP and the pipe syntax to the GUI for display in "QEP Text" and "Pipe Syntax" tabs
    return qep, pipe_syntax

if __name__ == "__main__":
    launchconverter = GUI_Window(sql_to_pipe_syntax_converter)
    launchconverter.mainloop()
