import streamlit as st
import pandas as pd
import recordlinkage

#Initial push is testing to see if I can recreate results from practical business python with dynamic user input
st.set_page_config(page_title="Duplication - Fuzzy Record Linkage")

st.write('Reference: https://pbpython.com/record-linking.html')
#Link to notebook: https://nbviewer.org/github/chris1610/pbpython/blob/master/notebooks/Record-Linking-Fuzzy-Matching.ipynb

def get_df_column_list(df):
    return list(df.columns)

hospital_dupes = pd.read_csv(
    'https://github.com/chris1610/pbpython/raw/master/data/hospital_account_dupes.csv',
    index_col='Account_Num')

df_columns = get_df_column_list(hospital_dupes)

#get user input for relevant columns to inspect
selected_neighbourhood_col = st.selectbox('Choose column to define neighborhood', df_columns, 
                                          help='https://recordlinkage.readthedocs.io/en/latest/ref-index.html#recordlinkage.index.SortedNeighbourhood')

selected_comparison_fields = st.multiselect(
    'Choose columns to compare rows',
    df_columns,
    help='https://recordlinkage.readthedocs.io/en/latest/ref-compare.html')

#allow user entry of more details for selected_comparison_fields
selected_params_dicts = [{'col':field, 'threshold': st.number_input(f"{field} Confidence Threshold: ", min_value=0.00, max_value=1.00, value=0.80, step=0.05, key=field)} for field in selected_comparison_fields]
   
#code which should not be executed until button click
activation_button = st.button('Click to Find Fuzzy Duplications')
if activation_button:
    #Initialize the indexer
    dupe_indexer = recordlinkage.Index()

    #Begin finding pairs to compare based on selected neighborhood
    dupe_indexer.sortedneighbourhood(left_on=selected_neighbourhood_col)
    dupe_candidate_links = dupe_indexer.index(hospital_dupes)

    #initialize comparison
    compare_dupes = recordlinkage.Compare()
    #create comparisons based on user selected cols to compare
    for params in selected_params_dicts:
        compare_dupes.string(params['col'], params['col'], threshold=params['threshold'], label=params['col'])
    #create duplication features
    dupe_features = compare_dupes.compute(dupe_candidate_links, hospital_dupes)
    dupe_features.sum(axis=1).value_counts().sort_index(ascending=False)

    #create potential_dupes df based upon dup_features sum above
    potential_dupes = dupe_features[dupe_features.sum(axis=1) > 2].reset_index()
    potential_dupes['Score'] = potential_dupes.loc[:, selected_params_dicts[0]['col']:selected_params_dicts[-1]['col']].sum(axis=1)

    potential_dupes.sort_values(by=['Score'], ascending=True)

    # Take a look at some of the potential duplicates
    st.write(potential_dupes.head())

    #stop procedure
    activation_button = False
