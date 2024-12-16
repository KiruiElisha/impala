import frappe

def construct_hierarchy(supervisor):
    """
    Construct organizational hierarchy recursively starting from the given supervisor.
    
    Args:
        supervisor (str): The name of the supervisor.
        
    Returns:
        list: List containing tuples of employee names and their respective payroll categories in the hierarchy.
    """
    employees = frappe.get_all("Employee", filters={"reports_to": supervisor, "status": "Active"},
                                fields=["name", "designation", "reports_to", "payroll_category"])
    hierarchy = []
    for employee in employees:
        employee_name = employee.get("name")
        payroll_category = employee.get("payroll_category")
        hierarchy.append((employee_name, payroll_category))
        hierarchy.extend(construct_hierarchy(employee_name))
    return hierarchy


def get_chart():
    """
    Retrieve data for generating an organizational chart.
    
    Returns:
        list: List containing tuples of employee names and their respective payroll categories in the hierarchy.
    """
    top_supervisors = frappe.get_all("Employee", filters={"reports_to": ""},
                                      fields=["name", "designation", "reports_to", "payroll_category"])
    
    org_hierarchy = []

    for supervisor in top_supervisors:
        supervisor_name = supervisor.get("name")
        hierarchy = construct_hierarchy(supervisor_name)
        org_hierarchy.extend(hierarchy)

    return org_hierarchy

def get_columns():
    """
    Define columns for the organizational hierarchy report.
    
    Returns:
        list: List of dictionaries representing column properties.
    """
    columns = [
        {"label": "Level One", "fieldname": "level_one", "fieldtype": "Data", "width": 100},
        {"label": "Level Two", "fieldname": "level_two", "fieldtype": "Data", "width": 150},
        {"label": "Level Three", "fieldname": "level_three", "fieldtype": "Data", "width": 150},
        {"label": "Level Four", "fieldname": "level_four", "fieldtype": "Data", "width": 150},
        {"label": "Level Five", "fieldname": "level_five", "fieldtype": "Data", "width": 150},
    ]
    
    return columns

def execute(filters=None):
    """
    Execute the organizational hierarchy report.
    
    Returns:
        dict: Dictionary containing columns and hierarchical chart data.
    """
    columns = get_columns()
    tree_data = get_chart()
    
    # Prepare rows dynamically
    hierarchical_data = []

    # Organize employees by payroll category
    categories = {
        "Top Management": [],
        "Senior Management": [],
        "Middle Management": [],
        "Junior Management": [],
        "Factory": []
    }

    for employee_info in tree_data:
        employee_name, payroll_category = employee_info
        categories[payroll_category].append(employee_name)

    # Create hierarchical structure
    max_level = max(len(employees) for employees in categories.values())
    for i in range(max_level):
        row = {}
        for j, (category, employees) in enumerate(categories.items(), start=1):
            if i < len(employees):
                row[f"level_{j}"] = employees[i]
            else:
                row[f"level_{j}"] = ""
        hierarchical_data.append(row)

    return columns, hierarchical_data

