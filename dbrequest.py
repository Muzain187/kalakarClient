import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='mysql-demo-muzain-17d0.d.aivencloud.com',
            database='defaultdb',
            user='avnadmin',
            password='AVNS_TySeJXo2gfZsbFbN5B7',
            port=25435
        )
        if connection.is_connected():
            print("Successfully connected to the database")
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def add_music(movieName, songTitle, lyrics, connection):
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            insert_query = """INSERT INTO lyric_temp_z1 (movieList, LyricList, SongTitle, Movie,Singers,Lyricst,Director, Lyric) VALUES (%s, %s, %s, %s, %s,%s,%s,%s)"""
            data = (movieName, songTitle, songTitle, movieName,"Singers:","Lyricst Name:","Music Director:", lyrics)
            cursor.execute(insert_query, data)
            connection.commit()
            print(cursor.rowcount, "Record inserted successfully into table")
    except Error as e:
        print("Error while inserting into MySQL table", e)
