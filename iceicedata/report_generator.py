import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from database import get_data_for_report
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)

def generate_report(report_type, start_date, end_date, output_format, config):
    logger.info(f"Generating {report_type} report from {start_date} to {end_date}")
    df = get_data_for_report(config['database_file'], start_date, end_date)
    
    logger.info(f"DataFrame shape: {df.shape}")
    logger.info(f"DataFrame columns: {df.columns}")
    
    if df.empty:
        logger.warning("No data available for the specified date range")
        return
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    logger.info(f"Date range of data: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    if report_type == 'daily':
        generate_daily_report(df, start_date, end_date, output_format)
    elif report_type == 'weekly':
        generate_weekly_report(df, start_date, end_date, output_format)
    elif report_type == 'monthly':
        generate_monthly_report(df, start_date, end_date, output_format)

def generate_daily_report(df, start_date, end_date, output_format):
    plt.figure(figsize=(12, 6))
    if 'air_temperature' in df.columns:
        plt.plot(df['timestamp'], df['air_temperature'])
        plt.title(f"Daily Temperature Report ({start_date} to {end_date})")
        plt.xlabel("Time")
        plt.ylabel("Temperature (°C)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        filename = f"daily_temperature_report_{start_date}_to_{end_date}.png"
        plt.savefig(filename)
        logger.info(f"Daily temperature report generated: {filename}")
    else:
        logger.error("Air temperature data not found in the DataFrame")
    
    if 'relative_humidity' in df.columns:
        plt.figure(figsize=(12, 6))
        plt.plot(df['timestamp'], df['relative_humidity'])
        plt.title(f"Daily Humidity Report ({start_date} to {end_date})")
        plt.xlabel("Time")
        plt.ylabel("Relative Humidity (%)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        filename = f"daily_humidity_report_{start_date}_to_{end_date}.png"
        plt.savefig(filename)
        logger.info(f"Daily humidity report generated: {filename}")
    
    save_report(df, f"daily_report_{start_date}_to_{end_date}", output_format)

def generate_weekly_report(df, start_date, end_date, output_format):
    df_weekly = df.resample('W', on='timestamp').agg({
        'air_temperature': 'mean',
        'relative_humidity': 'mean',
        'wind_speed': 'mean'
    })
    
    plt.figure(figsize=(12, 6))
    plt.plot(df_weekly.index, df_weekly['air_temperature'])
    plt.title(f"Weekly Average Temperature Report ({start_date} to {end_date})")
    plt.xlabel("Week")
    plt.ylabel("Average Temperature (°C)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    filename = f"weekly_temperature_report_{start_date}_to_{end_date}.png"
    plt.savefig(filename)
    logger.info(f"Weekly temperature report generated: {filename}")
    
    plt.figure(figsize=(12, 6))
    plt.plot(df_weekly.index, df_weekly['relative_humidity'])
    plt.title(f"Weekly Average Humidity Report ({start_date} to {end_date})")
    plt.xlabel("Week")
    plt.ylabel("Average Relative Humidity (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    filename = f"weekly_humidity_report_{start_date}_to_{end_date}.png"
    plt.savefig(filename)
    logger.info(f"Weekly humidity report generated: {filename}")
    
    save_report(df_weekly, f"weekly_report_{start_date}_to_{end_date}", output_format)

def generate_monthly_report(df, start_date, end_date, output_format):
    df_monthly = df.resample('M', on='timestamp').agg({
        'air_temperature': ['mean', 'min', 'max'],
        'relative_humidity': 'mean',
        'wind_speed': 'mean'
    })
    
    plt.figure(figsize=(12, 6))
    plt.plot(df_monthly.index, df_monthly['air_temperature']['mean'], label='Average')
    plt.plot(df_monthly.index, df_monthly['air_temperature']['min'], label='Min')
    plt.plot(df_monthly.index, df_monthly['air_temperature']['max'], label='Max')
    plt.title(f"Monthly Temperature Report ({start_date} to {end_date})")
    plt.xlabel("Month")
    plt.ylabel("Temperature (°C)")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    filename = f"monthly_temperature_report_{start_date}_to_{end_date}.png"
    plt.savefig(filename)
    logger.info(f"Monthly temperature report generated: {filename}")
    
    plt.figure(figsize=(12, 6))
    sns.heatmap(df.pivot_table(index=df['timestamp'].dt.day, columns=df['timestamp'].dt.month, values='air_temperature', aggfunc='mean'), 
                cmap="YlOrRd", annot=True, fmt=".1f")
    plt.title(f"Monthly Temperature Heatmap ({start_date} to {end_date})")
    plt.xlabel("Month")
    plt.ylabel("Day")
    plt.tight_layout()
    filename = f"monthly_temperature_heatmap_{start_date}_to_{end_date}.png"
    plt.savefig(filename)
    logger.info(f"Monthly temperature heatmap generated: {filename}")
    
    save_report(df_monthly, f"monthly_report_{start_date}_to_{end_date}", output_format)

def save_report(df, filename, output_format):
    if output_format == 'csv':
        df.to_csv(f"{filename}.csv")
        logger.info(f"Report saved as CSV: {filename}.csv")
    elif output_format == 'html':
        df.to_html(f"{filename}.html")
        logger.info(f"Report saved as HTML: {filename}.html")
    elif output_format == 'pdf':
        # You'll need to implement PDF generation separately
        logger.warning("PDF output not yet implemented")
    else:
        logger.warning(f"Unsupported output format: {output_format}")