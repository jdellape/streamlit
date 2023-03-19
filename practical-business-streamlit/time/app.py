import streamlit as st
import pandas as pd
import duckdb
from datetime import time, date, timedelta

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

generate_calculation_button = st.button('Click to Calculate Business Time on Task')

if generate_calculation_button:

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
    
    #Store the dataframe from above query
    calendar_df = duckdb.sql(sql).fetchdf()

    #Pull in the test dataset of tickets
    fetch_tickets_sql = """SELECT 
                           ticket_id,
                           open_time,
                           CAST(open_time AS DATE) as open_date,
                           date_part('hour', open_time) as open_hour,
                           close_time,
                           CAST(close_time AS DATE) as close_date,
                           date_part('hour', close_time) as close_hour
                           FROM read_csv_auto('data/test_data.csv')
                        """
    ticket_table = duckdb.sql(fetch_tickets_sql).fetchdf()

    #Apply sql logic to calculate business time on task: https://docs.getdbt.com/blog/measuring-business-hours-sql-time-on-task
    business_minutes_calc_sql = """
        select tix.ticket_id,
        tix.open_time,
        tix.close_time,
        cal.date_hour,
        case
            when cal.date = CAST(tix.open_time AS DATE) AND cal.hour = date_part('hour', tix.open_time) then 60 - date_part('minute', tix.open_time)
            when cal.date = CAST(tix.close_time AS DATE) AND cal.hour = date_part('hour', tix.close_time) then date_part('minute', tix.close_time)
        else 60
        end as minutes_on_task_by_business_hour
        from ticket_table as tix
        inner join calendar_df as cal on ((cal.date_hour >= tix.open_time OR (cal.date = tix.open_date and cal.hour = tix.open_hour))
                                        and (cal.date_hour <= tix.close_time))
        where cal.is_business_hour = true 
        order by tix.ticket_id, cal.date_hour asc
    """
    rows_by_business_hours = duckdb.sql(business_minutes_calc_sql).fetchdf()
    aggregation = duckdb.sql("""SELECT ticket_id, 
                             sum(minutes_on_task_by_business_hour) as business_minutes_on_task,
                             round(sum(minutes_on_task_by_business_hour) / 60, 1) as business_hours_on_task
                             from rows_by_business_hours 
                             GROUP BY ticket_id
                             """).fetchdf()
    st.header("Results")
    st.subheader("Business Minutes on Task by Ticket")
    st.dataframe(aggregation)
    st.subheader("Calculation Details")
    st.dataframe(rows_by_business_hours)

