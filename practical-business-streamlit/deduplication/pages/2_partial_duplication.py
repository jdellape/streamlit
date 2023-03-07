import streamlit as st
import pandas as pd
from collections import Counter

st.set_page_config(page_title="Partial Duplication")

uploaded_file = st.file_uploader("Choose a file (accepting .csv files only at the moment)")

def get_df_column_list(df):
    return list(df.columns)

def get_df_columns_excluding_column(df, id_column):
    col_list = list(df.columns)
    col_list.remove(id_column)
    return col_list

def get_duplicated_ids(df, id_column):
    c = Counter(list(df[id_column]))
    return {_id: count for _id, count in c.items() if count > 1} 

def get_duplication_details(df, col_name_list, id_value):
    output_ids = []
    output_values = []
    output_columns = []
    for col in col_name_list:
        values = list(pd.unique(df[col]))
        for v in values:
            output_ids.append(id_value)
            output_columns.append(col)
            output_values.append(v)
    return (output_ids, output_columns, output_values)

def get_columns_causing_duplication(df, id_column, non_id_columns, id_value):
    df_by_id = df[df[id_column]==id_value]
    cols_causing_duplication = [col for col in non_id_columns if len(pd.unique(df_by_id[col])) > 1]
    return cols_causing_duplication

def flatten_list(l):
    return [item for sublist in l for item in sublist]


if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write(df)

    id_column = st.selectbox('Choose the ID column (column whose values should never be repeated in file)', get_df_column_list(df))
    non_id_columns = get_df_columns_excluding_column(df, id_column)

    dup_id_list = list(get_duplicated_ids(df, id_column).keys())

    #print out information on what is causing duplication
    cols_causing_duplication_set = set()
    full_output_ids = []
    full_output_columns = []
    full_output_values = []
    
    for _id in dup_id_list:
        cols_causing_duplcation = get_columns_causing_duplication(df, id_column, non_id_columns, _id)
        cols_causing_duplication_set.update(cols_causing_duplcation)
        _ids, cols, vals = get_duplication_details(df[df[id_column]==_id], cols_causing_duplcation, _id)
        full_output_ids.append(_ids)
        full_output_columns.append(cols)
        full_output_values.append(vals)


    st.write(f"Columns causing partial duplication: {cols_causing_duplication_set}")

    df_duplication_details = pd.DataFrame(
        {'id': flatten_list(full_output_ids),
         'column_name':flatten_list(full_output_columns),
         'column_value':flatten_list(full_output_values)}
    )
    st.write('Full Details on Duplicated Rows:')
    st.write(df_duplication_details)