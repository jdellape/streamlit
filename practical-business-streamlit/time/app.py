import streamlit as st
import pandas as pd
import duckdb
from datetime import datetime, time, date, timedelta

st.image("https://thumbs.gfycat.com/OblongImportantHowlermonkey-size_restricted.gif")

st.header("Measuring Business Time on Task")

st.subheader("Enter the Date Range for your Data")

start_date = st.date_input(
    "Enter Start Date:",
    date(2022, 1, 1))

end_date = st.date_input(
    "Enter End Date:",
    date(2023, 1, 1))

delta = end_date - start_date

#Create a list of all dates in range from start date to end date
date_list = [start_date + timedelta(days=x) for x in range(delta.days)]

#boolean for each date
is_company_holiday = [False for x in date_list]

#output an editable dataframe
df_dates = pd.DataFrame(list(zip(date_list, is_company_holiday)),
               columns =['date', 'is_company_holiday'])

st.subheader("Select your Business Holiday Dates")
edited_df = st.experimental_data_editor(df_dates)

company_holiday_dates = list(edited_df[edited_df["is_company_holiday"]==True].date)

st.subheader("Select your Business's Operating Hours")
business_hours_window = st.slider(
    "Military Time",
    value=(time(8, 00), time(20, 00)))

start, close = business_hours_window

generate_calendar_button = st.button('Click to Generate Hourly Calendar')

if generate_calendar_button:

    sql = f"""
            with t1 as (
            SELECT generate_series as date_hour,
            CAST(generate_series AS DATE) as date,
            date_part('hour', generate_series) as hour,
            CASE WHEN date_part('hour', generate_series) BETWEEN {start.hour} AND {close.hour} THEN TRUE ELSE FALSE END AS business_hour
            FROM generate_series(TIMESTAMP '{start_date}', TIMESTAMP '{end_date}', INTERVAL 60 MINUTE)
            )
            select t1.date_hour,
            t1.date,
            t1.hour,
            edited_df.is_company_holiday as is_company_holiday,
            CASE 
            when edited_df.is_company_holiday = TRUE THEN FALSE
            when t1.business_hour = FALSE THEN FALSE
            else TRUE
            END AS is_business_hour
            from t1
            left join edited_df on t1.date = edited_df.date
            order by t1.date_hour asc
            """
    
    #Write out the dataframe from above query
    st.dataframe(duckdb.sql(sql).fetchdf())

    #TODO: incorporate logic from this post: https://docs.getdbt.com/blog/measuring-business-hours-sql-time-on-task
    
    generate_calendar_button = False