# ===========================================================================================
# (1) Function that takes in QEP and generates equivalent pipe syntax dynamically 
# ===========================================================================================
def generate_pipe_syntax(qep): # QEP is nested JSON --> root node = outermost dictionary = processed first 
    
    # parent_operation_type: used to track the operation (e.g. aggregate/sort) done by parent
    # from_clause_printed: used to track whether a FROM clause has already been printed (handle case where both branches no filter/aggregation/sort/order)
    
    # Conditions for printing the FROM clause:
    # 1. Scan has filter condition (WHERE)
    # 2. Scan node's parent node does aggregation/sort/order 

    def process_current_qep_node(cur_node, parent_operation_type = None, from_clause_printed = False): 
        pipesyntax_output = []    # To store the pipe syntax output        
        # curnode_accumcostfrmchildren = 0     
        relations = []            

        # If cur QEP node has child plans, process them first
        # (child plans = sub operations to be completed before cur node's operation)
        # Have "Plans" keyword in QEP JSON 
        if "Plans" in cur_node:
            for child in cur_node["Plans"]:
                # childnode_totalcost, child_pipesyntax_lines, child_relations, child_from_clause_printed = process_current_qep_node(child, cur_node.get("Node Type"), from_clause_printed)
                child_pipesyntax_lines, child_relations, child_from_clause_printed = process_current_qep_node(child, cur_node.get("Node Type"), from_clause_printed)
                pipesyntax_output += child_pipesyntax_lines           
                # curnode_accumcostfrmchildren += childnode_totalcost             
                relations.extend(child_relations)          
                from_clause_printed = from_clause_printed or child_from_clause_printed      

        # Once children processed, remember to also process the current node's plan
        # curnode_pipesyntaxline, curnode_finalcost, new_relation, curnode_from_clause_printed = qepnodeinfo_to_pipesyntaxline(
        #     cur_node, curnode_accumcostfrmchildren, relations, parent_operation_type, from_clause_printed
        # )
        curnode_pipesyntaxline, new_relation, curnode_from_clause_printed = qepnodeinfo_to_pipesyntaxline(
            cur_node, relations, parent_operation_type, from_clause_printed
        )

        # If the current node has a pipe syntax output line to be added (not empty), append the line
        if curnode_pipesyntaxline != "empty":
            pipesyntax_output.append(curnode_pipesyntaxline)

        # return curnode_finalcost, pipesyntax_output, [new_relation], from_clause_printed or curnode_from_clause_printed
        return pipesyntax_output, [new_relation], from_clause_printed or curnode_from_clause_printed

    # Begin traversal from root node 
    # Return the joined pipe syntax strings (containing all lines of the pipe syntax accumulated)
    # _, pipesyntax_output, _, _ = process_current_qep_node(qep)
    pipesyntax_output, _, _ = process_current_qep_node(qep)
    return "\n".join(pipesyntax_output)



# =====================================================================================================
# (2) Function that processes the QEP node, retrieves information, translates to pipe syntax
# =====================================================================================================
# def qepnodeinfo_to_pipesyntaxline(node, cost_accumulated_from_nodes_children , relations, parent_operation_type = None, from_clause_printed = False):
def qepnodeinfo_to_pipesyntaxline(node, relations, parent_operation_type = None, from_clause_printed = False):
    
    # For the node we are processing  
    node_type = node.get("Node Type", "") # Obtain the node type (Operation that it is performing --> E.g. Seq Scan)
    node_totalcost = float(node.get("Total Cost", 0)) # Retrieve the cost information from the current node
    
    # -------------------------------------------------------------------------------------------------------
    # (a) Base Table Scans: FROM and WHERE clauses  
    # -------------------------------------------------------------------------------------------------------
    if node_type in ["Index Only Scan", "Seq Scan", "Index Scan"]: # Scan types  
        relation_name = node.get("Relation Name", "unknown") # Table that we are performing the scan on 
        filter_condition = node.get("Filter") # Get any filter condition being applied (e.g. c_custkey > 10000)
        index_cond = node.get("Index Cond") # For index scan / index only scan (index search condition)
        recheck_cond = node.get("Recheck Cond") # For index scan / index only scan (verify index results satisfy remaining conditions)

        # When there are filter/index/recheck conditions, there will be a WHERE clause
        where_clause_conditions = []
        if filter_condition:
            where_clause_conditions.append(str(filter_condition))
        if index_cond:
            where_clause_conditions.append(f"{index_cond}")
        if recheck_cond:
            where_clause_conditions.append(f"{recheck_cond}")

        # Need to ensure that FROM <table> is printed AT LEAST ONCE and appropriately
        if where_clause_conditions or not from_clause_printed:
            # So long as there is a WHERE clause (filter condition), the "FROM"/"WHERE" for that table must be printed
            # Display the FROM <table> followed by |> WHERE <condition> in the next line
            if where_clause_conditions:
                where_block = "\n    ".join(where_clause_conditions)
                return f"FROM {relation_name}\n|> WHERE\n    {where_block} -- cost: {node_totalcost}", relation_name, True 
                # return f"FROM {relation_name}\n|> WHERE\n    {where_block} -- cost: {node_totalcost + cost_accumulated_from_nodes_children}", node_totalcost, relation_name, True 
            # No filter condition, but no FROM <table> statement has been printed yet
            else:
                # Ensure FROM is printed before operations like AGGREGATE or ORDER BY
                if parent_operation_type in ["Aggregate", "Sort", "Order"]:
                    return f"FROM {relation_name} -- cost: {node_totalcost}\n|> {node_type} -- cost: {node_totalcost}", relation_name, True
                    # return f"FROM {relation_name} -- cost: {node_totalcost+ cost_accumulated_from_nodes_children}\n|> {node_type} -- cost: {node_totalcost+ cost_accumulated_from_nodes_children}", node_totalcost, relation_name, True
                else:
                    return f"FROM {relation_name} -- cost: {node_totalcost}", relation_name, True
                    # return f"FROM {relation_name} -- cost: {node_totalcost+ cost_accumulated_from_nodes_children}", node_totalcost, relation_name, True
        
        # No filter condition, and already printed before, but if separate branch has scan operation followed by aggregate/sort/order --> still need to print a new FROM <table> for it
        else:
            # Only print "FROM" if have aggregate/sort operations
            if parent_operation_type in ["Aggregate", "Sort", "Order"]:
                return f"FROM {relation_name} -- cost: {node_totalcost}", relation_name, True
                # return f"FROM {relation_name} -- cost: {node_totalcost+ cost_accumulated_from_nodes_children}", node_totalcost, relation_name, True
            # Already printed once before + No Filter + No aggregate/sort/order --> Don't print another FROM <table> 
            else:
                # return "", node_totalcost, relation_name, from_clause_printed
                return "", relation_name, from_clause_printed

    # -------------------------------------------------------------------------------------------------------
    # (b) JOIN operations (Nested Loop, Merge Join, Hash Join)  
    # -------------------------------------------------------------------------------------------------------
    elif node_type in ["Nested Loop", "Merge Join", "Hash Join"]:
        
        # Get the join type of node (Format to all caps for pipe syntax output)
        join_type = "INNER"  # Default type
        if node.get("Join Type", "").lower() == "left":
            join_type = "LEFT"
        elif node.get("Join Type", "").lower() == "right":
            join_type = "RIGHT"
        elif node.get("Join Type", "").lower() == "full":
            join_type = "FULL"
            
        # Start building pipe syntax output line for JOIN condition
        join_pipesyntax_outputline = f"|> {join_type} JOIN"
        
        # Retrieve any join condition found in the node's information
        join_conditions = [] # Store all join conditions
        if node.get("Hash Cond"):
            join_conditions.append(node["Hash Cond"])
        if node.get("Merge Cond"):
            join_conditions.append(node["Merge Cond"])
        if node.get("Join Filter"):
            join_conditions.append(node["Join Filter"])
            
        # If the above join_conditions array is not empty, attach the join_conditions to the output pipe syntax line
        if join_conditions:
            # When there are more than 1 condtion for join --> combine with AND
            multiple_conditions_concat = " AND ".join(join_conditions)
            join_pipesyntax_outputline += f" ON {multiple_conditions_concat}"
            
        # Append cost information
        join_pipesyntax_outputline += f" -- cost: {node_totalcost}"
        
        # Name of table(s) to join
        if len(relations) >= 2:
            left_relation = relations[0]
            right_relation = relations[1]
        else:
            left_relation = relations[0] if relations else "unknown"
            right_relation = "unknown"
        
        # New name for join result (in case need to be used in later steps)
        new_relation = f"joined_{left_relation}_{right_relation}"

        # If no FROM clause has been printed up till now --> print the FROM clause first
        if not from_clause_printed:
            return f"FROM {left_relation} -- cost: {node_totalcost}\n{join_pipesyntax_outputline}", new_relation, True
            # return f"FROM {left_relation} -- cost: {node_totalcost+ cost_accumulated_from_nodes_children}\n{join_pipesyntax_outputline}", node_totalcost, new_relation, True
        
        # return join_pipesyntax_outputline, node_totalcost, new_relation, from_clause_printed
        return join_pipesyntax_outputline, new_relation, from_clause_printed

    # -------------------------------------------------------------------------------------------------------
    # (c) AGGREGATE operations 
    # -------------------------------------------------------------------------------------------------------
    elif node_type == "Aggregate":
        
        group_keys = node.get("Group Key", []) # For GROUP BY 
        strategy = node.get("Strategy", "") # Sorted/Hashed
        
        # Retrieves list of output columns or aggregate functions (sum, count etc.)
        output_cols_aggfuncs = node.get("Output", [])
        # Filters only for aggregate functions --> contains paranthesis --> count(*), sum(val) etc.
        aggregate_functions = [outputcol for outputcol in output_cols_aggfuncs if '(' in outputcol]  
        # Append all found aggregate functions (if any) into a single comma separated string 
        agg_functions_concat = ", ".join(aggregate_functions) if aggregate_functions else ""
        
        # If aggregation has GROUP BY 
        if group_keys:
            group_concat = ", ".join(group_keys)
            return f"|> AGGREGATE {agg_functions_concat} GROUP BY {group_concat} ({strategy}) -- cost: {node_totalcost}", relations[0], from_clause_printed
            # return f"|> AGGREGATE {agg_functions_concat} GROUP BY {group_concat} ({strategy}) -- cost: {node_totalcost+ cost_accumulated_from_nodes_children}", node_totalcost, relations[0], from_clause_printed
        else:
            return f"|> AGGREGATE {agg_functions_concat} -- cost: {node_totalcost}", node_totalcost, relations[0], from_clause_printed
            # return f"|> AGGREGATE {agg_functions_concat} -- cost: {node_totalcost+ cost_accumulated_from_nodes_children}", node_totalcost, relations[0], from_clause_printed

    # -------------------------------------------------------------------------------------------------------
    # (d) ORDER BY (SORT) operations 
    # -------------------------------------------------------------------------------------------------------
    elif node_type == "Sort": # Handle ORDER BY cases 
        
        sort_keys = node.get("Sort Key", []) # Column to sort by + sort order (ASC/DESC)
        
        # Handle case where there is > 1 sort col 
        sort_conds_concat = ", ".join(sort_keys) if sort_keys else "unknown" 
        
        # return f"|> ORDER BY {sort_conds_concat} -- cost: {node_totalcost+ cost_accumulated_from_nodes_children}", node_totalcost, relations[0], from_clause_printed
        return f"|> ORDER BY {sort_conds_concat} -- cost: {node_totalcost}", relations[0], from_clause_printed

    # -------------------------------------------------------------------------------------------------------
    # (e) LIMIT
    # -------------------------------------------------------------------------------------------------------
    elif node_type == "Limit":
        plan_rows = node.get("Plan Rows", "unknown") # Estimated no. of rows outputted by LIMIT (after offset)
       
        return f"|> LIMIT {plan_rows} -- cost: {node_totalcost}", relations[0], from_clause_printed


    # -------------------------------------------------------------------------------------------------------
    # (f) UNION/INTERSECT/EXCEPT
    # -------------------------------------------------------------------------------------------------------
    elif node_type == "SetOp":
        
        command = node.get("Command", "").upper()  # UNION/INTERSECT/EXCEPT
        strategy = node.get("Strategy", "")        # Hashed/Sorted
        
        # If there is a strategy (hashed/sorted) --> Format it for display
        strategy_disp = f" ({strategy})" if strategy and strategy != "Plain" else ""
        
        return f"|> {command}{strategy_disp} -- cost: {node_totalcost}", "setop_result", from_clause_printed  
        # return f"|> {command}{strategy_disp} -- cost: {node_totalcost+ cost_accumulated_from_nodes_children}", node_totalcost, "setop_result", from_clause_printed

    # -------------------------------------------------------------------------------------------------------
    # (g) TABLESAMPLE
    # -------------------------------------------------------------------------------------------------------
    elif node_type == "Sample Scan":
        relation = node.get("Relation Name", "unknown")
        return f"|> TABLESAMPLE {relation} -- cost: {node_totalcost}", relation, True
        # return f"|> TABLESAMPLE {relation} -- cost: {node_totalcost+cost_accumulated_from_nodes_children}", node_totalcost, relation, True

    # Any other unknown cases that are not handled by conversion logic
    else:
        return "empty", relations[0] if relations else "unknown", from_clause_printed
        # return "empty", node_totalcost, relations[0] if relations else "unknown", from_clause_printed

