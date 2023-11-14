import sqlite3
import os
from pathlib import Path
import pandas as pd



def create_database(data_path, database_path):
    
    # Read data into Pandas
    df = pd.read_csv(data_path)

    # Create SQLite connection
    conn = sqlite3.connect(database_path)

    # Create tables for Users, Books, and Ratings
    conn.execute('''CREATE TABLE IF NOT EXISTS Users (user_id INTEGER PRIMARY KEY)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS Books (book_id INTEGER PRIMARY KEY, title TEXT, cover_url TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS Ratings (user_id INTEGER, book_id INTEGER, user_rating INTEGER,
    avg_rating REAL, FOREIGN KEY(user_id) REFERENCES Users(user_id), 
    FOREIGN KEY(book_id) REFERENCES Books(book_id))''')

    # Add user IDs to Users table
    unique_user_ids = df['user_id'].unique()

    for user_id in unique_user_ids:
        try:
            conn.execute('INSERT INTO Users (user_id) VALUES (?)', (user_id,))
        except sqlite3.IntegrityError:
            pass
    conn.commit()

    # Add books to Books table
    unique_books = df.drop_duplicates(subset=['title', 'cover_url'])
    for _, row in unique_books.iterrows():
        try:
            conn.execute('INSERT INTO Books (title, cover_url) VALUES (?, ?)', (row['title'], row['cover_url']))
        except sqlite3.IntegrityError:
            pass
    conn.commit()

    book_id_map = pd.read_sql_query('SELECT book_id, title, cover_url FROM Books', conn)
    df = df.merge(book_id_map, on=['title', 'cover_url'])
    
    # Insert data into Ratings table
    for _, row in df.iterrows():
        try:
            conn.execute('INSERT INTO Ratings (user_id, book_id, user_rating, avg_rating) VALUES (?, ?, ?, ?)',
                         (row['user_id'], row['book_id'], row['user_rating'], row['avg_rating']))
        except sqlite3.IntegrityError:
            pass
            
    conn.commit()
    conn.close()



if __name__ == '__main__':

    data_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.pardir,
                os.pardir,
                'data',
                'interim',
                'consolidated_data.csv'
                )
            )

    database_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.pardir,
                os.pardir,
                'data',
                'processed',
                'books.db'
                )
            )

    create_database(data_path, database_path)