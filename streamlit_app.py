import streamlit as st
import datetime
import joblib
import pandas as pd

st.title('NYC Subway')
departing_station = st.selectbox('Departing station', ('Select', 'NY Penn Station', 'Grand Central', 'Jamaica',
                                                       'Long Island City', 'Hunterspoint Ave', 'Mets-Willets Point',
                                                       'Queens Village', 'Flushing Main St', 'Woodside',
                                                       'Elmont-UBS Arena',
                                                       'Bayside', 'Flatbush Avenue', 'Atlantic Terminal',
                                                       'West Side Yard',
                                                       ))
arrival_station = st.selectbox('Arriving station', ('Select', 'NY Penn Station', 'Grand Central', 'Jamaica',
                                                    'Long Island City', 'Hunterspoint Ave', 'Mets-Willets Point',
                                                    'Queens Village', 'Flushing Main St', 'Woodside',
                                                    'Elmont-UBS Arena',
                                                    'Bayside', 'Flatbush Avenue', 'Atlantic Terminal', 'West Side Yard',
                                                    ))

if departing_station and departing_station != 'Select' and arrival_station and arrival_station != 'Select':
    if departing_station == arrival_station:
        st.error(
            'Arriving and Departing stations cannot be same. Please select a different arriving or departing station')

selected_date = st.date_input("Date", value=datetime.date.today())
selected_time = st.time_input("Time", value=None)

run_model = False

if departing_station and departing_station != 'Select' and arrival_station and arrival_station != 'Select':
    st.write('Departing station:', departing_station)
    st.write('Arriving station:', arrival_station)

    if selected_date and selected_time:
        st.write("Date Time:", selected_date, selected_time)
        weekday_num = selected_date.weekday()  # 0 = Monday, 1 = Tuesday, ..., 6 = Sunday
        weekday_name = selected_date.strftime("%A")  # Full weekday name
        month_name = selected_date.strftime("%b")
        st.write('Weekday:', weekday_name, ' Month:', month_name)
        run_model = True

if run_model:
    df_incidents = pd.read_csv('df_agg_incidents.csv')
    # Load the pipeline
    pipeline = joblib.load('xgb_pipeline_new.pkl')

    depart_station = 'Atlantic Terminal'
    arrive_station = 'Jamaica'
    date_str = "2010-01-02"
    time_str = "09:30"

    date_obj = pd.to_datetime(date_str, format='%Y-%m-%d')
    month = date_obj.month
    day = date_obj.day

    time = pd.to_datetime(time_str, format='%H:%M')
    if (time.hour == 7 and time.minute >= 15) or (time.hour == 8 or time.hour == 9):
        peak_period = "AM-Peak"
    else:
        peak_period = "Off-Peak"

    df_incidents_filter = df_incidents[(df_incidents['Month'] == month) & (df_incidents['day'] == day)]

    station_borough_mapping = {
        'NY Penn Station': 'MANHATTAN',
        'Grand Central': 'MANHATTAN',
        'Jamaica': 'QUEENS',
        'Long Island City': 'QUEENS',
        'Hunterspoint Ave': 'QUEENS',
        'Mets-Willets Point': 'QUEENS',
        'Queens Village': 'QUEENS',
        'Flushing Main St': 'QUEENS',
        'Woodside': 'QUEENS',
        'Elmont-UBS Arena': 'QUEENS',
        'Bayside': 'QUEENS',
        'Flatbush Avenue': 'BROOKLYN',
        'Atlantic Terminal': 'BROOKLYN',
        'West Side Yard': 'BROOKLYN'
    }

    user_input = {
        'PRCP': df_incidents_filter['PRCP'],
        'SNOW': df_incidents_filter['SNOW'],
        'SNWD': df_incidents_filter['SNWD'],
        'TMIN': df_incidents_filter['TMIN'],
        'TMAX': df_incidents_filter['TMAX'],
        'Crash Count': df_incidents_filter['Crash Count'],
        'SHOOTING_INCIDENT_COUNT': df_incidents_filter['SHOOTING_INCIDENT_COUNT'],
        'FIRE_INCIDENT_COUNT': df_incidents_filter['FIRE_INCIDENT_COUNT'],
        'EVRNT_COUNT': df_incidents_filter['EVRNT_COUNT'],
        'DayOfWeek': df_incidents_filter['DayOfWeek'],
        'IsWeekend': df_incidents_filter['IsWeekend'],
        'Minutes Late Lag1': df_incidents_filter['Minutes Late Lag1'],
        'Minutes Late Lag7': df_incidents_filter['Minutes Late Lag7'],
        'Minutes Late Lag14': df_incidents_filter['Minutes Late Lag14'],
        'Delay Category': df_incidents_filter['Delay Category'],
        'Period': peak_period,
        'Branch': depart_station,
        'Depart Station': depart_station,
        'Arrive Station': arrive_station,
        'Depart Station Borough': station_borough_mapping[depart_station],
        'Arrive Station Borough': station_borough_mapping[arrive_station]
    }

    # Ensure that 'Branch', 'Depart Station', and 'Arrive Station' categories are consistent with training
    top_branches = ['Babylon', 'Port Washington', 'Ronkonkoma', 'Hempstead', 'Long Beach', 'Other']
    top_stations = ['Penn Station', 'Jamaica', 'Atlantic Terminal', 'Hicksville', 'Babylon', 'Other']

    user_input['Branch'] = user_input['Branch'] if user_input['Branch'] in top_branches else 'Other'
    user_input['Depart Station'] = user_input['Depart Station'] if user_input['Depart Station'] in top_stations else 'Other'
    user_input['Arrive Station'] = user_input['Arrive Station'] if user_input['Arrive Station'] in top_stations else 'Other'

    # Convert user input to DataFrame
    input_df = pd.DataFrame([user_input])
    st.write(input_df)
    # Make prediction
    y_pred = pipeline.predict(input_df)
    st.write(y_pred)
