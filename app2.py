
import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from io import StringIO

st.set_page_config(layout="wide")
st.sidebar.title("📊 WhatsApp Chat Analyzer")

# File upload
uploaded_file = st.sidebar.file_uploader("📁 Upload your chat file (.txt)", type="txt")

if uploaded_file is not None:
    # Try decoding with UTF-8 or fallback to ISO-8859-1
    try:
        data = uploaded_file.getvalue().decode("utf-8")
    except UnicodeDecodeError:
        data = uploaded_file.getvalue().decode("ISO-8859-1")

    # Preprocess chat
    df = preprocessor.preprocess(data)

    # Date filter (optional)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        min_date = df['date'].min().date()
        max_date = df['date'].max().date()
        start_date = st.sidebar.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
        end_date = st.sidebar.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

        df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]

    # User selection
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("👤 Analyze chat for", user_list)

    if st.sidebar.button("📈 Show Analysis"):
        # Top Stats
        st.title("📌 Top Statistics")
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Messages")
            st.title(num_messages)
        with col2:
            st.header("Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # Monthly Timeline
        st.title("🗓 Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Daily Timeline
        st.title("📅 Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Activity Map
        st.title('📌 Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # Weekly Heatmap
        st.title("🕒 Weekly Activity Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap, ax=ax)
        st.pyplot(fig)

        # Most Busy Users
        if selected_user == 'Overall':
            st.title('💬 Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            col1, col2 = st.columns(2)

            with col1:
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

        # Word Cloud
        st.title("☁️ Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis("off")
        st.pyplot(fig)

        # Most Common Words
        st.title('🗣 Most Common Words')
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1], color='skyblue')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Emoji Analysis
        st.title("😄 Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)
        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:
            if not emoji_df.empty:
                fig, ax = plt.subplots()
                ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
                st.pyplot(fig)
            else:
                st.write("No emojis found.")

        # Download cleaned data
        st.sidebar.markdown("---")
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.sidebar.download_button("📥 Download Cleaned Data", csv_data, file_name="filtered_chat.csv", mime="text/csv")
