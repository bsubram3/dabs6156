import streamlit as st
import datetime

st.title('NYC Subway')
departing_station = st.selectbox( 'Departing station', ('Select','NY Penn Station', 'Grand Central', 'Jamaica',
                                                                    'Long Island City','Hunterspoint Ave','Mets-Willets Point',
                                                                    'Queens Village','Flushing Main St', 'Woodside', 'Elmont-UBS Arena',
                                                                    'Bayside','Flatbush Avenue', 'Atlantic Terminal', 'West Side Yard',
                                                                    ))
arrival_station = st.selectbox( 'Arriving station', ('Select','NY Penn Station', 'Grand Central', 'Jamaica',
                                                                    'Long Island City','Hunterspoint Ave','Mets-Willets Point',
                                                                    'Queens Village','Flushing Main St', 'Woodside', 'Elmont-UBS Arena',
                                                                    'Bayside','Flatbush Avenue', 'Atlantic Terminal', 'West Side Yard',
                                                                    ))

if departing_station and departing_station != 'Select' and arrival_station and arrival_station != 'Select':
    if departing_station == arrival_station:
        st.error('Arriving and Departing stations cannot be same. Please select a different arriving or departing station')

selected_date = st.date_input("Date", value=datetime.date.today())
selected_time = st.time_input("Time", value=None)

if departing_station and departing_station != 'Select' and arrival_station and arrival_station != 'Select':
    st.write('Departing station:', departing_station)
    st.write('Arriving station:', arrival_station)

    if selected_date and selected_time:
        st.write("Date Time:", selected_date , selected_time)
        weekday_num = selected_date.weekday()  # 0 = Monday, 1 = Tuesday, ..., 6 = Sunday
        weekday_name = selected_date.strftime("%A")  # Full weekday name
        month_name = selected_date.strftime("%b")
        st.write('Weekday:', weekday_name, ' Month:', month_name)

        st.header('Estimated delay in arrival: 20 mins')

