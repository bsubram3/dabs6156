import streamlit as st
import datetime
import joblib
import pandas as pd

st.title('NYC Subway Arrival Prediction')
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
debug = False

if len(st.query_params) > 0 and st.query_params["debug"] == "true":
    debug = True

if departing_station and departing_station != 'Select' and arrival_station and arrival_station != 'Select':
    if debug:
        st.write('Departing station:', departing_station)
        st.write('Arriving station:', arrival_station)

    if selected_date and selected_time:
        run_model = True
        if debug:
            st.write("Date Time:", selected_date, selected_time)
            weekday_num = selected_date.weekday()  # 0 = Monday, 1 = Tuesday, ..., 6 = Sunday
            weekday_name = selected_date.strftime("%A")  # Full weekday name
            month_name = selected_date.strftime("%b")
            st.write('Weekday:', weekday_name, ' Month:', month_name)


if run_model:
    df_incidents = pd.read_csv('df_agg_incidents.csv')
    # Load the pipeline
    pipeline = joblib.load('xgb_pipeline_new.pkl')

    depart_station = departing_station
    arrive_station = arrival_station
    date_str = selected_date
    time_str = selected_time

    date_obj = pd.to_datetime(date_str, format='%Y-%m-%d')
    month = date_obj.month
    day = date_obj.day

    time = pd.to_datetime(time_str, format='%H:%M:%S')
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
        'PRCP': df_incidents_filter['PRCP'].iloc[0],
        'SNOW': df_incidents_filter['SNOW'].iloc[0],
        'SNWD': df_incidents_filter['SNWD'].iloc[0],
        'TMIN': df_incidents_filter['TMIN'].iloc[0],
        'TMAX': df_incidents_filter['TMAX'].iloc[0],
        'Crash Count': df_incidents_filter['Crash Count'].iloc[0],
        'SHOOTING_INCIDENT_COUNT': df_incidents_filter['SHOOTING_INCIDENT_COUNT'].iloc[0],
        'FIRE_INCIDENT_COUNT': df_incidents_filter['FIRE_INCIDENT_COUNT'].iloc[0],
        'EVRNT_COUNT': df_incidents_filter['EVRNT_COUNT'].iloc[0],
        'DayOfWeek': df_incidents_filter['DayOfWeek'].iloc[0],
        'IsWeekend': df_incidents_filter['IsWeekend'].iloc[0],
        'Minutes Late Lag1': df_incidents_filter['Minutes Late Lag1'].iloc[0],
        'Minutes Late Lag7': df_incidents_filter['Minutes Late Lag7'].iloc[0],
        'Minutes Late Lag14': df_incidents_filter['Minutes Late Lag14'].iloc[0],
        'Delay Category': df_incidents_filter['Delay Category'].iloc[0],
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
    if debug:
        st.write(input_df)
    # Make prediction
    y_pred = pipeline.predict(input_df)
    predicted_value = round(y_pred[0], 2)
    if predicted_value > 0:
        st.subheader(f'{depart_station} to {arrive_station} might be :red[{predicted_value:.0f} minutes late]')
    else:
        st.subheader(f'{depart_station} to {arrive_station} might be :green[{predicted_value:.0f} minutes early]')
