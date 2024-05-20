#used libraries

import streamlit as st
from googleapiclient.discovery import build
import mysql.connector
import pandas as pd

#ApI Key Connection 
def Api_connect():
    Api_id = "AIzaSyCi45lNiUsF2N4M2hlxIJfEGeSgxWg131Q"

    api_service_name ="youtube"
    api_version="v3"

    youtube=build(api_service_name,api_version,developerKey=Api_id)
    return youtube
youtubeConnect = Api_connect()

#get Channel informations
def get_channel_info(ChannelID):
    request = youtubeConnect.channels().list(
            part = "statistics,snippet,contentDetails",
            id= ChannelID
        )
    response=request.execute()

    for detail in response["items"]:
        channel_data=dict(channel_Name=detail["snippet"]["title"],
                    channel_Id = detail["id"],
                    subscribe_count = detail["statistics"]["subscriberCount"],
                    view_count=detail["statistics"]["viewCount"],
                    Channel_Description= detail["snippet"]["description"],
                    Playlist_Id = detail["contentDetails"]["relatedPlaylists"]["uploads"]
        )
    return channel_data

#get youtube channel videos ids
def get_videoIds(channelID):
    video_ids =[]
    playlistidresponse= youtubeConnect.channels().list(id=channelID,
        part='contentDetails').execute()

    playlistID= playlistidresponse["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    next_page_token = None
    while True:
        videoidresponse = youtubeConnect.playlistItems().list(
                                part='snippet',
                                playlistId=playlistID,maxResults=50,
                                pageToken=next_page_token).execute()
        
        for i in range(len(videoidresponse["items"])):
            video_ids.append(videoidresponse["items"][i]["snippet"]["resourceId"]["videoId"])
        next_page_token = videoidresponse.get('nextPageToken')

        if next_page_token is None:
            break
    return video_ids


#get video info from video ids list
def get_video_info(videoIds_list):
    video_Datas=[]
    for video_id in videoIds_list:
        video_info_response=youtubeConnect.videos().list(
                                                part="snippet,ContentDetails,statistics",
                                                id=video_id)
        response=video_info_response.execute()
        for video_item in response["items"]:
            video_data=dict(Channel_Name=video_item['snippet']['channelTitle'],
                            channel_Id=video_item['snippet']['channelId'],
                            video_ID=video_item['id'],
                            Video_Name= video_item['snippet']['title'],
                            Video_Description  = video_item['snippet']['description'],
                            Published_Date= video_item['snippet']['publishedAt'],
                            Tags= video_item['snippet']['title'],
                            Views= video_item['statistics']['viewCount'],
                            Likes= video_item['statistics']['likeCount'],
                            FavoriteCount=video_item['statistics']['favoriteCount'],
                            Comments= video_item['statistics']['commentCount'],
                            Thumbnail=video_item['snippet']['thumbnails']['default']['url'],
                            Duration= video_item['contentDetails']['duration'],
                            caption= video_item['contentDetails']['caption']
                            )
            video_Datas.append(video_data)
    return video_Datas

#get comment details from videoId
def get_Comment_info(videoIds_list):
    comment_datas=[]
    try:
        for video_id in videoIds_list:
            request=youtubeConnect.commentThreads().list(
                                                        part="snippet",
                                                        videoId=video_id,
                                                        maxResults=50
                                                        )
            response=request.execute()

            for comment_item in response["items"]:
                    comment_data= dict(comment_ID= comment_item["snippet"]["topLevelComment"]["id"],
                                    video_ID = comment_item["snippet"]["topLevelComment"]["snippet"]["videoId"],
                                    Comment_Text= comment_item["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                                    Comment_Author=comment_item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                                    Comment_PublishedAt= comment_item["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
                                    )
                    comment_datas.append(comment_data)
    except:
        pass
    return comment_datas


#get_playlist_details

def get_playlist_details(channel_id):
        """
    Fetches details of playlists from a specified YouTube channel.

    Parameters: channel_id (str)

    Returns:
        list(All_data): A list of dictionaries(data)"""

        next_page_token=None
        playlist_data=[]
        while True:
                request=youtubeConnect.playlists().list(
                        part='snippet,contentDetails',
                        channelId=channel_id,
                        maxResults=50,
                        pageToken=next_page_token
                )
                response=request.execute()

                for item in response['items']:
                        data=dict(Playlist_Id=item['id'],
                                Title=item['snippet']['title'],
                                Channel_Id=item['snippet']['channelId'],
                                Channel_Name=item['snippet']['channelTitle'],
                                PublishedAt=item['snippet']['publishedAt'],
                                Video_Count=item['contentDetails']['itemCount'])
                        playlist_data.append(data)

                next_page_token=response.get('nextPageToken')
                if next_page_token is None:
                        break
        return playlist_data

#Full channel info collection


def Channel_full_details(ChannelID):
    channel_details=get_channel_info(ChannelID)
    videoIds_list = get_videoIds(ChannelID)
    Playlist_Details = get_playlist_details(ChannelID)
    video_Details = get_video_info(videoIds_list)
    Comment_details= get_Comment_info(videoIds_list)
    
    return {
                "channel_details": channel_details,
                "Playlist_Details": Playlist_Details,
                "video_Details": video_Details,
                "Comment_details": Comment_details
            }


#convert into datframes

def dataframes(youtubeChannelID):
    Channel_fulldetails = Channel_full_details(youtubeChannelID)
    print("Data Collected....")

    #1 Dataframe channel table
    df_channel_details = pd.DataFrame([Channel_fulldetails["channel_details"]])

    #2 Dataframe playlist table
    df_Playlist = []
    for i in range(len(Channel_fulldetails["Playlist_Details"])):
        Channel_data= Channel_fulldetails["Playlist_Details"][i]
        df=pd.DataFrame([Channel_data])
        df_Playlist.append(df)
    df_Playlist_details = pd.concat(df_Playlist, ignore_index=True)

    #3 Dataframe video table
    df_video = []
    for i in range(len(Channel_fulldetails["video_Details"])):
        Channel_data= Channel_fulldetails["video_Details"][i]
        df=pd.DataFrame([Channel_data])
        df_video.append(df)
    df_video_details = pd.concat(df_video, ignore_index=True)

    #4 Dataframe comment table
    df_comment = []
    for i in range(len(Channel_fulldetails["Comment_details"])):
        Channel_data= Channel_fulldetails["Comment_details"][i]
        df=pd.DataFrame([Channel_data])
        df_comment.append(df)
    df_comment_details = pd.concat(df_comment, ignore_index=True)
    print("collected data to dataframe")

    return df_channel_details, df_Playlist_details, df_video_details, df_comment_details
        

 #sql connection 

def insert_Channel(df_channel_details):
     # Establishing a connection to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="YoutubeData"
    )

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    # INSERT Channel DataFrame to MYSQL
    try:
        table_create = '''CREATE TABLE IF NOT EXISTS Channeltable (
                channel_Id VARCHAR(50) PRIMARY KEY,
                channel_Name VARCHAR(255),
                subscribe_count INT,
                view_count INT,
                Channel_Description TEXT,
                Playlist_Id VARCHAR(50)
            );'''
        cursor.execute(table_create)
        #print("Channeltable created successfully.")
    except Exception as e:
        print("Error creating table:", e)

    insert_query = '''INSERT INTO Channeltable (channel_Id, channel_Name, subscribe_count, view_count, Channel_Description, Playlist_Id)
                    VALUES (%s, %s, %s, %s, %s, %s)'''

    for index, row in  df_channel_details.iterrows():
        try:
            cursor.execute(insert_query, (
                row['channel_Id'],
                row['channel_Name'],
                row['subscribe_count'],
                row['view_count'],
                row['Channel_Description'],
                row['Playlist_Id']
            ))

            # Commit changes to the database
            conn.commit()
        except Exception as e:
            conn.rollback()  # Rollback changes if there's an error
            #print("Insert Error:", e)    


def insert_playlist(df_Playlist_details):
    
    # Establishing a connection to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="YoutubeData"
    )

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()


    # INSERT playlist DataFrame to MYSQL
    try:
        table_create = '''CREATE TABLE IF NOT EXISTS playlisttable (
                channel_Id VARCHAR(255) ,
                channel_Name VARCHAR(100),
                Playlist_Id VARCHAR(255) PRIMARY KEY,
                Title VARCHAR(100),
                Video_Count INT,
                PublishedAt VARCHAR(50)
            );'''
        cursor.execute(table_create)
        #print("playlisttable created successfully.")
    except Exception as e:
        print("Error creating table:", e)

    insert_query = '''INSERT INTO playlisttable (channel_Id, channel_Name, Playlist_Id, Title, Video_Count, PublishedAt)
                    VALUES (%s, %s, %s, %s, %s, %s)'''

    for index, row in df_Playlist_details.iterrows():
        try:
            cursor.execute(insert_query, (
                    row['Channel_Id'], 
                    row['Channel_Name'], 
                    row['Playlist_Id'], 
                    row['Title'], 
                    row['Video_Count'], 
                    row['PublishedAt']
                ))

            # Commit changes to the database
            conn.commit()
        except Exception as e:
            conn.rollback()  # Rollback changes if there's an error
            #print("Insert Error:", e)
def insert_video(df_video_details):
    
    # Establishing a connection to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="YoutubeData"
    )

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()


    # INSERT video DataFrame to MYSQL
    try:
        table_create = '''CREATE TABLE IF NOT EXISTS videotable (
                channel_Id VARCHAR(255) ,
                channel_Name VARCHAR(100),
                video_ID VARCHAR(100) PRIMARY KEY,
                Video_Name VARCHAR(100),
                Video_Description TEXT,
                Published_Date VARCHAR(100),
                Tags VARCHAR(100),
                Views INT,
                Likes INT,
                FavoriteCount INT,
                Comments INT,
                Thumbnail VARCHAR(100),
                Duration VARCHAR(100),
                caption VARCHAR(100)
            );'''
        cursor.execute(table_create)
        #print("videotable created successfully.")
    except Exception as e:
        print("Error creating table:", e)

    insert_query = '''INSERT INTO videotable (channel_Id, channel_Name, video_ID, Video_Name, Video_Description, Published_Date, Tags, Views, Likes, FavoriteCount, Comments, Thumbnail, Duration, caption)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

    for index, row in df_video_details.iterrows():
        try:
            cursor.execute(insert_query, (
                    row['channel_Id'], 
                    row['Channel_Name'], 
                    row['video_ID'], 
                    row['Video_Name'], 
                    row['Video_Description'], 
                    row['Published_Date'],
                    row['Tags'],
                    row['Views'],
                    row['Likes'],
                    row['FavoriteCount'],
                    row['Comments'],
                    row['Thumbnail'],
                    row['Duration'],
                    row['caption']
                ))

            # Commit changes to the database
            conn.commit()
        except Exception as e:
            conn.rollback()  # Rollback changes if there's an error
            #print("Insert Error:", e)


def insert_comment(df_comment_details):
    
    # Establishing a connection to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="YoutubeData"
    )

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()


    # INSERT comment DataFrame to MYSQL
    try:
        table_create = '''CREATE TABLE IF NOT EXISTS commenttable (
                comment_ID VARCHAR(255) PRIMARY KEY ,
                video_ID VARCHAR(100) ,
                Comment_Text TEXT,
                Comment_Author TEXT,
                Comment_PublishedAt VARCHAR(100)
            );'''
        cursor.execute(table_create)
        #print("commenttable created successfully.")
    except Exception as e:
        print("Error creating table:", e)

    insert_query = '''INSERT INTO commenttable (comment_ID, video_ID, Comment_Text, Comment_Author, Comment_PublishedAt)
                    VALUES (%s, %s, %s, %s, %s)'''

    for index, row in df_comment_details.iterrows():
        try:
            cursor.execute(insert_query, (
                    row['comment_ID'], 
                    row['video_ID'], 
                    row['Comment_Text'], 
                    row['Comment_Author'], 
                    row['Comment_PublishedAt']
                ))

            # Commit changes to the database
            conn.commit()
        except Exception as e:
            conn.rollback()  # Rollback changes if there's an error
            #print("Insert Error:", e)


def insert_tables(df_channel_details,df_Playlist_details,df_video_details,df_comment_details):

    insert_Channel(df_channel_details)
    insert_playlist(df_Playlist_details)
    insert_video(df_video_details)
    insert_comment(df_comment_details)


def collectdata_to_sql(youtubeChannelID):

    channel_df, playlist_df, video_df, comment_df = dataframes(youtubeChannelID)
    insert_tables(channel_df, playlist_df, video_df, comment_df)
    return "Tables inserted to sql successfully"


#

def sql_to_dataframe():
    # Establishing a connection to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="YoutubeData"
    )

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    # Executing the SQL query
    query = '''SELECT * FROM channeltable'''
    cursor.execute(query)
    
    # Fetching all the rows from the result
    result = cursor.fetchall()
    
    # Getting the column names
    columns = [col[0] for col in cursor.description]
    
    # Creating DataFrame
    df = pd.DataFrame(result, columns=columns)
    
    # Closing the cursor and connection
    cursor.close()
    conn.close()
    return df

def question_1():
    # Establishing a connection to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="YoutubeData"
    )

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    # Executing the SQL query
    query = '''Select video_Name as VideoTiTle, channel_Name as ChannelName  FROM videotable'''
    cursor.execute(query)
    
    # Fetching all the rows from the result
    result = cursor.fetchall()
    
    # Getting the column names
    columns = [col[0] for col in cursor.description]
    
    # Creating DataFrame
    df = pd.DataFrame(result, columns=columns)
    
    # Closing the cursor and connection
    cursor.close()
    conn.close()
    return df

def question_2():
    # Establishing a connection to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="YoutubeData"
    )

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    # Executing the SQL query
    query = '''SELECT channel_Name as ChannelName, COUNT(video_name) AS TotalVideos
                FROM videotable
                GROUP BY ChannelName
                ORDER BY TotalVideos DESC;
'''
    cursor.execute(query)
    
    # Fetching all the rows from the result
    result = cursor.fetchall()
    
    # Getting the column names
    columns = [col[0] for col in cursor.description]
    
    # Creating DataFrame
    df = pd.DataFrame(result, columns=columns)
    
    # Closing the cursor and connection
    cursor.close()
    conn.close()
    return df

def question_3():
    # Establishing a connection to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="YoutubeData"
    )

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    # Executing the SQL query
    query = '''SELECT Channel_Name AS ChannelName, Video_Name AS VideoTitle, Views AS Views
               FROM videotable
               WHERE Views IS NOT NULL
               ORDER BY Views DESC
               LIMIT 10;
    '''
    cursor.execute(query)
    
    # Fetching all the rows from the result
    result = cursor.fetchall()
    
    # Getting the column names
    columns = [col[0] for col in cursor.description]
    
    # Creating DataFrame
    df = pd.DataFrame(result, columns=columns)
    
    # Closing the cursor and connection
    cursor.close()
    conn.close()
    return df

def question_4():
    # Establishing a connection to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="YoutubeData"
    )

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    # Executing the SQL query
    query = '''select Video_Name AS Video_Title , comments AS Number_of_Comments from videotable where comments is not null;'''
    cursor.execute(query)
    
    # Fetching all the rows from the result
    result = cursor.fetchall()
    
    # Getting the column names
    columns = [col[0] for col in cursor.description]
    
    # Creating DataFrame
    df = pd.DataFrame(result, columns=columns)
    
    # Closing the cursor and connection
    cursor.close()
    conn.close()
    return df

def question_5():
    # Establishing a connection to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="YoutubeData"
    )
    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    # Executing the SQL query
    query = '''select channel_Name As Channel_Name , Video_Name As Video_Title  , likes AS Like_Count from videotable
                where likes is not null order by likes desc;
            '''
    cursor.execute(query)
    
    # Fetching all the rows from the result
    result = cursor.fetchall()
    
    # Getting the column names
    columns = [col[0] for col in cursor.description]
    
    # Creating DataFrame
    df = pd.DataFrame(result, columns=columns)
    
    # Closing the cursor and connection
    cursor.close()
    conn.close()
    return df


def question_6():
    # Establishing a connection to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="YoutubeData"
    )

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    # Executing the SQL query
    query = '''select Video_Name AS Video_Title, Likes As Likes_Count from videotable
                Where Likes is not null;
            '''
    cursor.execute(query)
    
    # Fetching all the rows from the result
    result = cursor.fetchall()
    
    # Getting the column names
    columns = [col[0] for col in cursor.description]
    
    # Creating DataFrame
    df = pd.DataFrame(result, columns=columns)
    
    # Closing the cursor and connection
    cursor.close()
    conn.close()
    return df


def question_7():
    # Establishing a connection to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="YoutubeData"
    )

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    # Executing the SQL query
    query = '''select channel_Name AS Channel_Name , view_count As Total_Views from channeltable;
            '''
    cursor.execute(query)
    
    # Fetching all the rows from the result
    result = cursor.fetchall()
    
    # Getting the column names
    columns = [col[0] for col in cursor.description]
    
    # Creating DataFrame
    df = pd.DataFrame(result, columns=columns)
    
    # Closing the cursor and connection
    cursor.close()
    conn.close()
    return df

def question_8():
    # Establishing a connection to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="YoutubeData"
    )

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    # Executing the SQL query
    query = '''select channel_Name As Channel_Name , Video_Name As Video_Title , Published_Date As Video_Published from videotable
               where extract(year from Published_Date)='2023'
            '''
    cursor.execute(query)
    
    # Fetching all the rows from the result
    result = cursor.fetchall()
    
    # Getting the column names
    columns = [col[0] for col in cursor.description]
    
    # Creating DataFrame
    df = pd.DataFrame(result, columns=columns)
    
    # Closing the cursor and connection
    cursor.close()
    conn.close()
    return df

def question_9():
    # Establising a connection to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="YoutubeData"
    )

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    # Executing the SQL query
    query = '''SELECT channel_Name,
          ROUND(AVG(CAST(minutes_before_M AS DECIMAL(10,0))), 0) AS Avg_Min
         FROM (SELECT channel_Name,
         CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(Duration, 'M', 1), 'PT', -1) AS DECIMAL(10,0)) AS minutes_before_M
        FROM videotable) AS subquery
         GROUP BY channel_Name;
            '''
    cursor.execute(query)
    
    # Fetching all the rows from the result
    result = cursor.fetchall()
    
    # Getting the column names
    columns = [col[0] for col in cursor.description]
    
    # Creating DataFrame
    df = pd.DataFrame(result, columns=columns)
    
    # Closing the cursor and connection
    cursor.close()
    conn.close()
    return df

def question_10():
    # Establishing a connection to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="YoutubeData"
    )

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    # Executing the SQL query
    query = '''select channel_Name As Channel_Name , Video_Name As Video_Title , Comments As Comment_Count from videotable
               where Comments is not null order by Comments desc;
            '''
    cursor.execute(query)
    
    # Fetching all the rows from the result
    result = cursor.fetchall()
    
    # Getting the column names
    columns = [col[0] for col in cursor.description]
    
    # Creating DataFrame
    df = pd.DataFrame(result, columns=columns)
    
    # Closing the cursor and connection
    cursor.close()
    conn.close()
    return df

# Streamlit part

st.title(":red[YOUTUBE DATA HARVESTING AND WAREHOUSING]")

channel_id = st.text_input("Enter the channel ID")
# Button to trigger data collection
if st.button("Collect Data"):
    if channel_id:
        collectdata_to_sql(channel_id)  # Call the function to collect data
        sqltable = sql_to_dataframe()    # Call the function to retrieve data
        if sqltable is not None:
            st.success("Data collected and added successfully!")
            channel_table_df = pd.DataFrame(sqltable)
            st.dataframe(channel_table_df)
        else:
            st.error("Failed to retrieve data from SQL")  # Handle case when data retrieval fails
    else:
        st.write("Please enter a channel ID")


question=st.selectbox("Select your question",("None",
                                              "1. Titles & Channels: List all video titles with their respective channels.",
                                              "2. Most Active Channels: Identify channels with the highest video count.",
                                              "3. Top 10 Views: Display top 10 videos with the most views and their channels.",
                                              "4. Comment Counts: Show the number of comments on each video along with their titles.",
                                              "5. Popular Likes: Highlight videos with the highest number of likes and their channels.",
                                              "6. Like Totals: Total likes for each video, alongside their titles.",
                                              "7. Channel Views: Sum up views for each channel and display their names.",
                                              "8. 2022 Publishers: List channels that posted videos in 2022.",
                                              "9. Average Video Length: Show the average duration of videos for each channel.",
                                              "10. Comment Leaders: Highlight videos with the highest comment count and their channels."))
if question == "None":
    st.write("You haven't selected any option.")
else:
    st.write("You selected:", question)

    
if question=="1. Titles & Channels: List all video titles with their respective channels.":
    query1 = question_1()
    table_df = pd.DataFrame(query1)
    st.dataframe(table_df)
    st.success("Data Retrieved Successfully!")

elif question=="2. Most Active Channels: Identify channels with the highest video count.":
    query1 = question_2()
    table_df = pd.DataFrame(query1)
    st.dataframe(table_df)
    st.success("Data Retrieved Successfully!")

elif question=="3. Top 10 Views: Display top 10 videos with the most views and their channels.":
    query1 = question_3()
    table_df = pd.DataFrame(query1)
    st.dataframe(table_df)
    st.success("Data Retrieved Successfully!")
    
elif question=="4. Comment Counts: Show the number of comments on each video along with their titles.":
    query1 = question_4()
    table_df = pd.DataFrame(query1)
    st.dataframe(table_df)
    st.success("Data Retrieved Successfully!")
    
elif question=="5. Popular Likes: Highlight videos with the highest number of likes and their channels.":
    query1 = question_5()
    table_df = pd.DataFrame(query1)
    with st.container():
        st.dataframe(table_df)
    st.success("Data Retrieved Successfully!")

elif question=="6. Like Totals: Total likes for each video, alongside their titles.":
    query1 = question_6()
    table_df = pd.DataFrame(query1)
    st.dataframe(table_df)
    st.success("Data Retrieved Successfully!")

elif question=="7. Channel Views: Sum up views for each channel and display their names.":
    query1 = question_7()
    table_df = pd.DataFrame(query1)
    st.dataframe(table_df)
    st.success("Data Retrieved Successfully!")

elif question=="8. 2022 Publishers: List channels that posted videos in 2022.":
    query1 = question_8()
    table_df = pd.DataFrame(query1)
    st.dataframe(table_df)
    st.success("Data Retrieved Successfully!")

elif question=="9. Average Video Length: Show the average duration of videos for each channel.":
    query1 = question_9()
    table_df = pd.DataFrame(query1)
    st.dataframe(table_df)
    st.success("Data Retrieved Successfully!")

elif question=="10. Comment Leaders: Highlight videos with the highest comment count and their channels.":
    query1 = question_10()
    table_df = pd.DataFrame(query1)
    st.dataframe(table_df)
    st.success("Data Retrieved Successfully!")

else:
    st.write("Empty")
    