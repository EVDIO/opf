import os
import pandas as pd
import numpy as np
import random
import json


def calculate_hourly_mean_consumers(input_path, output_path_active, output_path_reactive):
    # Read the input CSV file
    df_individual = pd.read_csv(input_path)

    # Convert date and time columns to datetime
    df_individual['Datetime'] = pd.to_datetime(df_individual['Date'] + ' '
                                               + df_individual['Time'],
                                                format='mixed')

    # Drop unnecessary columns
    df_individual.drop(['Voltage', 'Global_intensity', 'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3'], axis=1, inplace=True)
    df_individual.reset_index(inplace=True)

    # Convert non-numeric values to NaN
    df_individual['Global_active_power'] = pd.to_numeric(df_individual['Global_active_power'], errors='coerce')
    df_individual['Global_reactive_power'] = pd.to_numeric(df_individual['Global_reactive_power'], errors='coerce')

    # Calculate the mean values
    mean_active_power = df_individual['Global_active_power'].mean()
    mean_reactive_power = df_individual['Global_reactive_power'].mean()

    # Replace NaN values with the mean
    df_individual['Global_active_power'].fillna(mean_active_power, inplace=True)
    df_individual['Global_reactive_power'].fillna(mean_reactive_power, inplace=True)

    # Convert data types to float
    df_individual['Global_active_power'] = df_individual['Global_active_power'].astype(float)
    df_individual['Global_reactive_power'] = df_individual['Global_reactive_power'].astype(float)

    # Group by date and hour, calculate hourly mean
    df_hourly_ind = df_individual.groupby([df_individual['Date'], df_individual['Datetime'].dt.hour])[['Global_active_power', 'Global_reactive_power']].mean()
    df_hourly_ind.reset_index(inplace=True)

    # Convert hour to datetime format
    df_hourly_ind['Datetime'] = pd.to_datetime(df_hourly_ind['Date'] + ' '
                                               + df_hourly_ind['Datetime'].astype(str)
                                               + ':00:00',
                                                format='mixed')

    # Drop the "Date" column
    df_hourly_ind.drop('Date', axis=1, inplace=True)

    # Calculate mean for each hour
    mean_active = df_hourly_ind.groupby(df_hourly_ind["Datetime"].dt.hour)["Global_active_power"].mean().to_numpy()
    mean_reactive = df_hourly_ind.groupby(df_hourly_ind["Datetime"].dt.hour)["Global_reactive_power"].mean().to_numpy()

    # Save mean values to numpy arrays
    np.save(output_path_active, mean_active)
    np.save(output_path_reactive, mean_reactive)
    print("Consumer data saved!")


def calculate_mean_per_hour_pvs(input_path_pv,output_path_mean_pv,output_path_std_pv):
    pv_data = pd.read_excel(input_path_pv)

    pv_data['Timestamp'] = pd.to_datetime(pv_data['Timestamp'], format='%Y%m%d%H%M%S')
    # set the timestamp column as the dataframe index
    pv_data.set_index('Timestamp', inplace=True)
    # resample the dataframe to hourly frequency
    pv_data = pv_data.resample('1H').first()
    pv_data = pv_data.applymap(lambda x: float(x.replace(',', '') if type(x) is not int else x))
    pv_data_mean = pv_data.mean(axis=1).to_numpy()/1000 # make kWh
    pv_data_std = pv_data.std(axis=1).to_numpy()/1000 # make kWh

    np.save(output_path_mean_pv,pv_data_mean)
    np.save(output_path_std_pv,pv_data_std)
    print("PV data saved!")


def process_ev_data(input_path, output_path_start_charge, output_path_duration):
    with open(input_path, 'r') as f:
        file_contents = f.read()
        data_ev = json.loads(file_contents)

    data_ev = data_ev['_items']
    df_ev = pd.DataFrame(data_ev)

    df_ev['connectionTime'] = pd.to_datetime(df_ev['connectionTime'])
    df_ev['disconnectTime'] = pd.to_datetime(df_ev['disconnectTime'])
    df_ev['doneChargingTime'] = pd.to_datetime(df_ev['doneChargingTime'])
    df_ev['duration'] = ((df_ev['disconnectTime'] - df_ev['connectionTime']) / np.timedelta64(1, 'h')).round(decimals=0)

    start_charge_time = df_ev.groupby(df_ev['connectionTime'].dt.hour)['_id'].count().reset_index()
    sum_counts = start_charge_time['_id'].sum()
    start_charge_time['probability'] = (start_charge_time['_id'] / sum_counts)
    start_charge_time.drop('_id', axis=1, inplace=True)
    start_charge_time['cumulative_prob'] = start_charge_time['probability'].cumsum()

    Q1 = df_ev['duration'].quantile(0.25)
    Q3 = df_ev['duration'].quantile(0.75)
    IQR = Q3 - Q1
    lower_threshold = Q1 - 0.5 * IQR
    upper_threshold = Q3 + 1.5 * IQR

    mask = (df_ev['duration'] >= lower_threshold) & (df_ev['duration'] <= upper_threshold)
    df_ev = df_ev[mask]

    duration_time = df_ev.groupby(df_ev['duration'])['_id'].count().reset_index()
    sum_counts = duration_time['_id'].sum()
    duration_time['probability'] = (duration_time['_id'] / sum_counts)
    duration_time.drop('_id', axis=1, inplace=True)
    duration_time['cumulative_prob'] = duration_time['probability'].cumsum()

    start_charge_time.to_csv(output_path_start_charge, index=False)
    duration_time.to_csv(output_path_duration, index=False)
    print("EV data saved!")

if __name__ == '__main__':
    # Get the root directory path
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_data_dir = os.path.join(root_dir, '..')

    # Construct input and output paths using relative paths
    input_path_cons = os.path.join(raw_data_dir, 'data', 'raw', 'household_power_consumption.csv')
    output_path_active = os.path.join(raw_data_dir, 'data', 'interim', 'cons_act_mean.npy')
    output_path_reactive = os.path.join(raw_data_dir, 'data', 'interim', 'cons_react_mean.npy')

    calculate_hourly_mean_consumers(input_path_cons, output_path_active, output_path_reactive)

    # Construct input and output paths using relative paths
    input_path_pv = os.path.join(raw_data_dir, 'data', 'raw', 'PV_data.xlsx')
    output_path_mean_pv = os.path.join(raw_data_dir, 'data', 'interim', 'pv_mean.npy')
    output_path_std_pv = os.path.join(raw_data_dir, 'data', 'interim', 'pv_std.npy')

    calculate_mean_per_hour_pvs(input_path_pv,output_path_mean_pv,output_path_std_pv)

    # Construct input and output paths using relative paths
    input_path_ev = os.path.join(raw_data_dir, 'data', 'raw', 'acndata_sessions.json')
    output_path_start_charge = os.path.join(raw_data_dir, 'data', 'interim', 'start_charge_time.csv')
    output_path_duration = os.path.join(raw_data_dir, 'data', 'interim', 'duration_time.csv')

    process_ev_data(input_path_ev,output_path_start_charge,output_path_duration)

