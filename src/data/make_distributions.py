import os
import pandas as pd
import numpy as np


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

if __name__ == '__main__':
    # Get the root directory path
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_data_dir = os.path.join(root_dir, '..')

    # Construct input and output paths using relative paths
    input_path = os.path.join(raw_data_dir, 'data', 'raw', 'household_power_consumption.csv')
    output_path_active = os.path.join(raw_data_dir, 'data', 'interim', 'cons_act_mean.npy')
    output_path_reactive = os.path.join(raw_data_dir, 'data', 'interim', 'cons_react_mean.npy')

    calculate_hourly_mean_consumers(input_path, output_path_active, output_path_reactive)