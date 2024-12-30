import re
import pandas as pd

def preprocess(data):
    # Define the pattern to split messages
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][Mm]\s-\s'

    # Extract messages and dates using the pattern
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Check if messages and dates match in length
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert message_date to datetime with the correct format string
    df['message_date'] = pd.to_datetime(df['message_date'], format='%m/%d/%y, %I:%M %p - ')

    # Rename the column
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Initialize empty lists for users and messages
    users = []
    msgs = []  # Renaming to avoid conflict with the original messages variable

    # Process the user and message parts
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name exists
            users.append(entry[1])
            msgs.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            msgs.append(entry[0])

    df['user'] = users
    df['message'] = msgs
    df.drop(columns=['user_message'], inplace=True)

    # Add additional date and time-related columns
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Add a 'period' column for hourly intervals
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df
