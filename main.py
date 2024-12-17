'''
Bunlar gerekli kütüphaneler, yanlarına yüklemek için gerekli prompt satırlarını ekledim.
Eğer python'u Anaconda Navigator ile kurduysanız bu promptları anaconda prompt a yazın,
kütüphaneler yüklenecektir
'''
import requests # pip install requests
from bs4 import BeautifulSoup # pip install bs4
import pyodbc #pip install pyodbc

# Bu fonksiyon incelemeleri çekmeye yarıyor.
def get_steam_reviews(app_id, num_pages=10):
    base_url = f"https://steamcommunity.com/app/{app_id}/reviews/"
    reviews = []

    for page in range(1, num_pages + 1):
        print(f"Scraping page {page}...")
        url = f"{base_url}?p={page}&browsefilter=mostrecent"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed to fetch page {page}. Status code: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        review_blocks = soup.find_all('div', class_='apphub_CardTextContent')

        for block in review_blocks:
            review_text = block.get_text(strip=True)
            reviews.append(review_text)
            
    return reviews


# Bu fonksiyon AppId'sini girdiğimiz oyunun ismini de görelim diye var.
def get_game_name(app_id):   
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get(app_id, {}).get('success', False):
            return data[app_id]['data']['name']
    return "Böyle bir oyun yok..."


game_app_id = input("İncelemelerini çekmek istediğiniz oyunun AppId'sini girin (Örneğin: 730): ")
game_name = get_game_name(game_app_id)  # Buraya incelemelerini çekmek istediğiniz oyunun app id'sini yazcanız
num_pages = int(input("Kaç sayfa inceleme çekmek istediğinizi girin: "))       # Buraya kaç sayfa inceleme çekmek istediğinizi yazcanız   
reviews = get_steam_reviews(game_app_id, num_pages)



print(f"Oyun: {game_name}")
for i, review in enumerate(reviews, start=1):
    print(f"İnceleme {i}:\n {review}\n")




def connect_to_mssql(server, database, username, password):
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password}"
    )
    return conn

# Create tables in MSSQL
def setup_database(conn):
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Game' AND xtype='U')
        CREATE TABLE Game (
            AppId INT PRIMARY KEY,
            Name NVARCHAR(255) NOT NULL
        )
    """)
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Review' AND xtype='U')
        CREATE TABLE Review (
            Id INT IDENTITY(1,1) PRIMARY KEY,
            AppId INT,
            Date DATE,
            Review NVARCHAR(MAX),
            FOREIGN KEY (AppId) REFERENCES Game(AppId)
        )
    """)
    conn.commit()

# Insert data into MSSQL database
def insert_data(conn, app_id, game_name, reviews):
    cursor = conn.cursor()

    # Insert game data
    cursor.execute("""
        IF NOT EXISTS (SELECT 1 FROM Game WHERE AppId = ?)
        INSERT INTO Game (AppId, Name) VALUES (?, ?)
    """, app_id, app_id, game_name)

    # Insert reviews
    for review in reviews:
        cursor.execute("""
            INSERT INTO Review (AppId, Date, Review) VALUES (?, ?, ?)
        """, app_id, "2024-12-11", review)

    conn.commit()

# Main logic
if __name__ == "__main__":
    server = "ENES"
    database = "reviews"
    username = "sa"
    password = "123"


    # Connect to MSSQL and insert data
    conn = connect_to_mssql(server, database, username, password)
    setup_database(conn)
    insert_data(conn, game_app_id, game_name, reviews)
    conn.close()

    print(f"Inserted {len(reviews)} reviews for the game '{game_name}' into the database.")



























