
import re
import pandas as pd

def preprocess(data):
    # Regular expression pattern for your format
    pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2})\s?(AM|PM|am|pm)? - (.*?): (.*)'
    messages = []
    dates = []
    times = []
    users = []

    for line in data.split('\n'):
        match = re.match(pattern, line)
        if match:
            date = match.group(1)
            time = match.group(2) + ' ' + (match.group(3) or 'AM')  # fallback to AM if missing
            user = match.group(4)
            message = match.group(5)
            dates.append(date)
            times.append(time)
            users.append(user)
            messages.append(message)

    # Build DataFrame
    df = pd.DataFrame({
        'date': pd.to_datetime(dates, errors='coerce'),
        'time': times,
        'user': users,
        'message': messages
    })

    # Additional features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['day_name'] = df['date'].dt.day_name()
    df['day'] = df['date'].dt.day
    df['hour'] = pd.to_datetime(df['time'], format='%I:%M %p', errors='coerce').dt.hour
    df['minute'] = pd.to_datetime(df['time'], format='%I:%M %p', errors='coerce').dt.minute
    df['period'] = df['hour'].apply(lambda x: f'{x}-{(x+1)%24}' if pd.notnull(x) else 'unknown')

    return df


