import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter.scrolledtext as scrolledtext
from tkinter import messagebox
from PIL import Image, ImageTk
from graphviz import Digraph
import io
import json

class GUI_Window(ttk.Window):
    
    # Initialise pop-up window 
    def __init__(self, sql_to_pipe_syntax_converter):
        super().__init__(themename="cyborg")
        self.title("SC3020 Group 2: SQL to Pipe Syntax Converter")
        self.geometry("1200x900")
        self.sql_to_pipe_syntax_converter = sql_to_pipe_syntax_converter
        self.create_GUI_elements()

    # ===============================================================================================
    # create_GUI_elements: To create the UI elements in the pop-up GUI window 
    # ===============================================================================================
    def create_GUI_elements(self):
        
        # ===============================================================================================
        # GUI Segment 1: PostgreSQL login and connection panel
        # ===============================================================================================

        postgres_login_panel = ttk.Labelframe(self, text="PostgreSQL Login and Connection Settings: ")
        postgres_login_panel.pack(fill="x", padx=10, pady=5)

        # To get user input for "Host" value
        ttk.Label(postgres_login_panel, text="Host:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.host_val = ttk.Entry(postgres_login_panel, width=20)
        self.host_val.grid(row=0, column=1, padx=5, pady=2)
        self.host_val.insert(0, "localhost") # Default value

        # To get user input for "Port" value
        ttk.Label(postgres_login_panel, text="Port:").grid(row=0, column=2, sticky="e", padx=5, pady=2)
        self.port_val = ttk.Entry(postgres_login_panel, width=10)
        self.port_val.grid(row=0, column=3, padx=5, pady=2)
        self.port_val.insert(0, "5432") # Default value

        # To get user input for "Database" value
        ttk.Label(postgres_login_panel, text="Database:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.db_name_val = ttk.Entry(postgres_login_panel, width=20)
        self.db_name_val.grid(row=1, column=1, padx=5, pady=2)
        self.db_name_val.insert(0, "TPC-H") # Default value

        ttk.Label(postgres_login_panel, text="User:").grid(row=1, column=2, sticky="e", padx=5, pady=2)
        self.user_val = ttk.Entry(postgres_login_panel, width=20)
        self.user_val.grid(row=1, column=3, padx=5, pady=2)
        self.user_val.insert(0, "postgres") # Default value

        ttk.Label(postgres_login_panel, text="Password:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.pw_val = ttk.Entry(postgres_login_panel, show="*", width=20)
        self.pw_val.grid(row=2, column=1, padx=5, pady=2)
        self.pw_val.insert(0, "123456") # Default value

        # ===============================================================================================
        # GUI Segment 2: Box to input SQL query (that you want to convert to pipe syntax)
        # ===============================================================================================
        input_sqlquery_panel = ttk.Labelframe(self, text="Input SQL Query to convert: ")
        input_sqlquery_panel.pack(fill="both", expand=True, padx=10, pady=5)

        self.input_sqlquery_text = scrolledtext.ScrolledText(input_sqlquery_panel, height=8)
        self.input_sqlquery_text.pack(fill="both", expand=True, padx=5, pady=5)
        # Default query example from the project description (change if not using same TPC-H dataset)
        self.input_sqlquery_text.insert("end",
            "SELECT c_count, count(*) AS custdist FROM (SELECT c_custkey, count(o_orderkey) FROM customer "
            "LEFT OUTER JOIN orders ON c_custkey = o_custkey AND o_comment NOT LIKE '%unusual%packages%' "
            "GROUP BY c_custkey) as c_orders (c_custkey, c_count) GROUP BY c_count ORDER BY custdist DESC, c_count DESC;")


        # ===============================================================================================
        # GUI Segment 3: Button to exectue SQL query and run EXPLAIN ANALYSE
        # ===============================================================================================
        # Button to start SQL --> Pipe syntax conversion (generate QEP, plot QEP visualisation graph, display converted pipe syntax)
        execute_convert_button = ttk.Button(self, text="Execute SQL Query for Pipe Syntax Conversion", command=self.execute_run_sql_generate_pipesyntax)
        execute_convert_button.pack(pady=5)

        # ===============================================================================================
        # GUI Segment 4: Button to exectue SQL query and run EXPLAIN ANALYSE
        # ===============================================================================================
        multitab_output_display_panels = ttk.Notebook(self)
        multitab_output_display_panels.pack(fill="both", expand=True, padx=10, pady=5)

        self.pipesyntax_tab = ttk.Frame(multitab_output_display_panels)
        self.qeptext_tab = ttk.Frame(multitab_output_display_panels)
        self.qepgraph_tab = ttk.Frame(multitab_output_display_panels)
        
        # -------------------------------------------------------------------------------------------------------
        # (1) First tab: Tab that contains the output in pipe syntax format 
        # -------------------------------------------------------------------------------------------------------
        multitab_output_display_panels.add(self.pipesyntax_tab, text="Pipe Syntax Query")
        self.pipesyntax_tab_text = scrolledtext.ScrolledText(self.pipesyntax_tab)
        self.pipesyntax_tab_text.pack(fill="both", expand=True, padx=5, pady=5)

        # -------------------------------------------------------------------------------------------------------
        # (2) Second tab: Tab that contains the query execution plan generated by PostgreSQL (for reference)
        # -------------------------------------------------------------------------------------------------------
        multitab_output_display_panels.add(self.qeptext_tab, text="Query Execution Plan (QEP Text)")
        self.qeptext_tab_text = scrolledtext.ScrolledText(self.qeptext_tab)
        self.qeptext_tab_text.pack(fill="both", expand=True, padx=5, pady=5)

        # -------------------------------------------------------------------------------------------------------
        # (3) Third tab: Tab that contains the QEP in graph format (for clearer reference)
        # -------------------------------------------------------------------------------------------------------
        multitab_output_display_panels.add(self.qepgraph_tab, text="QEP Graph (Visual)")
        self.qepgraph_tab_panel = ttk.Frame(self.qepgraph_tab)
        self.qepgraph_tab_panel.pack(fill="both", expand=True)

        self.qepgraph_canvas = ttk.Canvas(self.qepgraph_tab_panel, bg="#1e1e1e")
        self.qepgraph_canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.qepgraph_tab_panel, orient="vertical", command=self.qepgraph_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.qepgraph_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.qepgraph_img_container = ttk.Frame(self.qepgraph_canvas)
        self.canvas_window = self.qepgraph_canvas.create_window((0, 0), window=self.qepgraph_img_container, anchor="n")

        self.qepgraph_img_widget = ttk.Label(self.qepgraph_img_container)
        self.qepgraph_img_widget.pack(padx=20, pady=20)

        # Ensure scrollable area updates size according to changing sizes of the canvas
        def on_configure(event):
            self.qepgraph_canvas.configure(scrollregion=self.qepgraph_canvas.bbox("all"))
            canvas_width = event.width
            self.qepgraph_canvas.itemconfig(self.canvas_window, width=canvas_width)
        self.qepgraph_canvas.bind("<Configure>", on_configure)


    # ==========================================================================================================================
    # Function that calls connection to database, execution of SQL query to obtain query plan, and generation of pipe syntax
    # ==========================================================================================================================
    def execute_run_sql_generate_pipesyntax(self):  
        
        # -------------------------------------------------------------------------------------------------------
        # Retrieve user input to GUI for passing to PostgreSQL for generation of QEP
        # -------------------------------------------------------------------------------------------------------
        user_input_retrieved = {
            "host": self.host_val.get(),
            "port": self.port_val.get(),
            "database": self.db_name_val.get(),
            "user": self.user_val.get(),
            "password": self.pw_val.get(),
            "query": self.input_sqlquery_text.get("1.0", "end").strip()
        }
        
        
        try:
            # -------------------------------------------------------------------------------------------------------
            # Convert and retrieve QEP and Pipe syntax using DB connection user inputs and input SQL query
            # -------------------------------------------------------------------------------------------------------
            qep, pipe_syntax_output = self.sql_to_pipe_syntax_converter(user_input_retrieved)
            
            # -------------------------------------------------------------------------------------------------------
            # Clear existing pipe syntax output. Then, display new pipe syntax output to the GUI pipe syntax tab
            # -------------------------------------------------------------------------------------------------------
            self.pipesyntax_tab_text.delete("1.0", "end")
            self.pipesyntax_tab_text.insert("end", pipe_syntax_output)

            # -------------------------------------------------------------------------------------------------------
            # Clear existing QEP text output. Then, display new QEP JSON to the GUI QEP text tab
            # -------------------------------------------------------------------------------------------------------
            self.qeptext_tab_text.delete("1.0", "end")
            self.qeptext_tab_text.insert("end", json.dumps(qep, indent=2))

            # -------------------------------------------------------------------------------------------------------
            # Clear existing QEP text output. Then, display new QEP JSON to the GUI QEP text tab
            # -------------------------------------------------------------------------------------------------------
            dot_format_qepgraph = self.generate_qep_graph(qep) # Generate graph in DOT format by processing the QEP
            png_qepgraph = dot_format_qepgraph.pipe(format='png') # Render graph to PNG img (in mem)
            qep_imgobj = Image.open(io.BytesIO(png_qepgraph)).resize((1000, 1000), Image.LANCZOS) # Load img frm mem and resize for display
            
            self.qep_image = ImageTk.PhotoImage(qep_imgobj) # Convert img for Tkinter format
            self.qepgraph_img_widget.configure(image=self.qep_image) # Display img on img widget for QEP graph
            self.qepgraph_img_widget.image = self.qep_image # Keep img ref
        
        # Display any error directly on GUI interface to inform user
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")

    # ==========================================================================================================================
    # Function to recursively traverse QEP Json to produce graph of QEP (for clearer representation)
    # ==========================================================================================================================
    def generate_qep_graph(self, qep, dot_graph_obj = None, parent = None, node_counter = [0]):
        
        # Create new Digraph object if it has yet to exist
        if dot_graph_obj is None:
            dot_graph_obj = Digraph()
        
        # Generate unique node ID for current node using node counter
        unique_node_id = f"node{node_counter[0]}"
        node_counter[0] += 1 # Increment node counter 

        # Retrieve node (operation) type information for labelling of graph node 
        node_operation_type = qep.get("Node Type", "Unknown")
        node_operation_details = [] # Apart from node operation type, track other useful info may be available

        # Add necessary/available details to the graph node when available
        for info in ["Relation Name", "Join Type", "Filter", "Actual Rows"]:
            if info in qep:
                node_operation_details.append(f"{info}: {qep[info]}")

        # Add node to graph with operation type info and other details
        dot_graph_obj.node(unique_node_id, node_operation_type + "\n" + "\n".join(node_operation_details))

        # If current node has parent: Draw edge to connect parent to cur node
        if parent:
            dot_graph_obj.edge(parent, unique_node_id)

        # Recursively call function for child plans (identified by keyword "Plans")
        for child in qep.get("Plans", []):
            self.generate_qep_graph(child, dot_graph_obj, unique_node_id, node_counter)
            # Current node unique id passed as parent id for this child node --> used for edge connection later

        return dot_graph_obj