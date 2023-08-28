import streamlit as st
import pandas as pd

class Employee:
    def __init__(self, emp_id, manager_id):
        self.emp_id = emp_id
        self.manager_id = manager_id
        
    def __str__(self): 
        return f"{self.emp_id}, {self.manager_id}" 
        

def build_hierarchy(employee_data):
    hierarchy = {}
    for employee in employee_data:
        emp_id = employee.emp_id
        manager_id = employee.manager_id

        if emp_id not in hierarchy:
            hierarchy[emp_id] = {}
        
        if manager_id is not None:
            if manager_id not in hierarchy:
                hierarchy[manager_id] = {}
            if 'subordinates' not in hierarchy[manager_id]:
                hierarchy[manager_id]['subordinates'] = []
                hierarchy[manager_id]['is_manager'] = True
            hierarchy[manager_id]['subordinates'].append(str(emp_id))
    
    return hierarchy

def find_all_reports_with_managers(hierarchy, manager_id):
    reports = []

    if manager_id in hierarchy:
        direct_reports = hierarchy[manager_id].get("subordinates", [])
        
        for report in direct_reports:
            reports.append((manager_id, report))
            reports.extend(find_all_reports_with_managers(hierarchy, report))
    
    return reports

@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')


input_file = st.file_uploader('Choose a File')

if input_file is not None:

    input_df = pd.read_csv(input_file)

    #Create employee object for each df row
    employees = [Employee(row.emp_id, row.manager_id) for row in input_df.itertuples()]

    #st.write(employees)

    hierarchy = build_hierarchy(employees)

    st.write('Raw Data')

    st.json(hierarchy, expanded=False)

    st.write("Find a Manager's Management Chain")

    #Select manager id who you want to capture all reports (direct + indirect)
    selected_manager_id = st.selectbox('Select Manager of Interest', sorted(set(list(input_df.manager_id))))

    reports_with_managers = find_all_reports_with_managers(hierarchy, str(selected_manager_id))

    output_df = pd.DataFrame(reports_with_managers, columns =['manager_id', 'emp_id'])

    st.dataframe(output_df)

    csv = convert_df(output_df)

    st.download_button(
        label='Download Above Table to csv',
        data=csv,
        file_name='management_chain.csv',
        mime='text/csv'
    )

