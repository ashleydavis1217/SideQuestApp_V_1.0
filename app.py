
from flask import Flask, render_template, request, redirect, url_for, session
from database import get_db_connection

import requests



# Create the Flask application
app = Flask(__name__)
app.secret_key = "sidequest-demo-secret-key"

## Dummy log in
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "traveler" and password == "adventure123":
            session["logged_in"] = True
            session["username"] = username

            return redirect(url_for("home"))

        else:
            return render_template(
                "login.html",
                error="Incorrect username or password. Please try again!"
            )
    print("LOGIN TEMPLATE:", app.jinja_env.get_template("login.html").filename)

    return render_template("login.html", login_note="")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

#Help page
@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")

        connection = get_db_connection()

        if connection is None:
            return "Could not connect to the SideQuest database."

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO contact_messages
                (name, email, subject, message)
                VALUES (%s, %s, %s, %s)
                """,
                (name, email, subject, message)
            )

            connection.commit()

        finally:
            cursor.close()
            connection.close()

        return render_template(
            "contact.html",
            success=True
        )

    return render_template("contact.html")


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html", page_title="Home")


# DISCOVER PAGE
@app.route("/discover")
def discover():
    search_term = request.args.get("game", "").strip()

    connection = get_db_connection()

    if connection is None:
        return "Could not connect to the SideQuest database."

    try:
        cursor = connection.cursor(dictionary=True)

        if search_term:
            cursor.execute(
                """
                SELECT id, title, tags AS genre, description
                FROM games
                WHERE title LIKE %s
                """,
                (f"%{search_term}%",)
            )
        else:
            cursor.execute(
                """
                SELECT id, title, tags AS genre, description
                FROM games
                """
            )

        games = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template(
        "discover.html",
        page_title="Discover",
        search_term=search_term,
        games=games
    )

# MY LISTS PAGE
@app.route("/lists")
def lists():
    connection = get_db_connection()

    if connection is None:
        return "Could not connect to the SideQuest database."

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                reading_lists.id AS list_id,
                reading_lists.name AS list_name,
                books.id AS book_id,
                books.title AS book_title,
                books.author AS book_author,
                books.publication_year,
                books.cover_url,
                books.isbn_10,
                books.isbn_13,
                books.open_library_id
            FROM reading_lists
            LEFT JOIN list_books
                ON reading_lists.id = list_books.list_id
            LEFT JOIN books
                ON list_books.book_id = books.id
            ORDER BY reading_lists.id DESC, books.title
        """)

        results = cursor.fetchall()

        reading_lists = {}

        for row in results:
            list_id = row["list_id"]

            if list_id not in reading_lists:
                reading_lists[list_id] = {
                    "id": list_id,
                    "name": row["list_name"],
                    "books": []
                }

            if row["book_id"] is not None:
                reading_lists[list_id]["books"].append({
                    "id": row["book_id"],
                    "title": row["book_title"],
                    "author": row["book_author"],
                    "publication_year": row["publication_year"],
                    "cover_url": row["cover_url"],
                    "isbn_10": row["isbn_10"],
                    "isbn_13": row["isbn_13"],
                    "open_library_id": row["open_library_id"]
                })

        reading_lists = list(reading_lists.values())

    finally:
        cursor.close()
        connection.close()

    return render_template(
        "lists.html",
        reading_lists=reading_lists
    )


# INDIVIDUAL READING LIST PAGE
@app.route("/list/<int:list_id>")
def view_list(list_id):
    connection = get_db_connection()

    if connection is None:
        return "Could not connect to the SideQuest database."

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM reading_lists WHERE id = %s",
            (list_id,)
        )

        reading_list = cursor.fetchone()

        if reading_list is None:
            return "Reading list not found.", 404

        cursor.execute(
            """
            SELECT books.*
            FROM books
            INNER JOIN list_books
                ON books.id = list_books.book_id
            WHERE list_books.list_id = %s
            ORDER BY books.title
            """,
            (list_id,)
        )

        books = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template(
        "list_detail.html",
        reading_list=reading_list,
        books=books
    )


# CREATE A READING LIST
@app.route("/lists/create", methods=["POST"])
def create_list():
    list_name = request.form.get("list_name", "").strip()

    if not list_name:
        return redirect(url_for("lists"))

    connection = get_db_connection()

    if connection is None:
        return "Could not connect to the SideQuest database."

    try:
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO reading_lists (name) VALUES (%s)",
            (list_name,)
        )

        connection.commit()

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("lists"))



# RENAME A READING LIST
@app.route("/lists/<int:list_id>/rename", methods=["POST"])
def rename_list(list_id):
    new_name = request.form.get("list_name", "").strip()

    if not new_name:
        return redirect(url_for("lists"))

    connection = get_db_connection()

    if connection is None:
        return "Could not connect to the SideQuest database."

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE reading_lists
            SET name = %s
            WHERE id = %s
            """,
            (new_name, list_id)
        )

        connection.commit()

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("lists"))


# DELETE A READING LIST
@app.route("/lists/<int:list_id>/delete", methods=["POST"])
def delete_list(list_id):
    connection = get_db_connection()

    if connection is None:
        return "Could not connect to the SideQuest database."

    try:
        cursor = connection.cursor()

        # Remove the books associated with this list first.
        cursor.execute(
            "DELETE FROM list_books WHERE list_id = %s",
            (list_id,)
        )

        # Then delete the reading list.
        cursor.execute(
            "DELETE FROM reading_lists WHERE id = %s",
            (list_id,)
        )

        connection.commit()

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("lists"))


# TEST MYSQL CONNECTION
@app.route("/test-db")
def test_database():
    connection = get_db_connection()

    if connection is None:
        return "Database connection failed. Check your MySQL settings."

    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        return f"Successfully connected to MySQL! Tables: {tables}"

    finally:
        cursor.close()
        connection.close()


# RECOMMENDATIONS PAGE

@app.route("/recommendations/<int:game_id>")
def recommendations(game_id):
    connection = get_db_connection()

    if connection is None:
        return "Could not connect to the SideQuest database."

    try:
        cursor = connection.cursor(dictionary=True)

        # Get the selected game
        cursor.execute(
            "SELECT * FROM games WHERE id = %s",
            (game_id,)
        )
        game = cursor.fetchone()

        # Get all existing reading lists
        cursor.execute(
            "SELECT * FROM reading_lists ORDER BY name"
        )
        reading_lists = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    if game is None:
        return "Game not found.", 404

    # Get the game's themes
    tags = game.get("tags") or ""

    search_terms = [
        tag.strip()
        for tag in tags.split(",")
        if tag.strip()
    ]

    if not search_terms:
        search_terms = [game["title"]]

    # Search Open Library once using all themes
    books = []

    try:
        search_query = " OR ".join(search_terms)

        response = requests.get(
            "https://openlibrary.org/search.json",
            params={
                "q": search_query,
                "limit": 12,
                "fields": "title,author_name,first_publish_year,isbn,cover_i,key,subject"
            },
            timeout=10
        )

        response.raise_for_status()
        books = response.json().get("docs", [])

    except requests.RequestException as error:
        print("Open Library search error:", error)

    return render_template(
        "recommendations.html",
        game=game,
        books=books,
        reading_lists=reading_lists
    )


@app.route("/theme/<theme>")
def theme_books(theme):

    # Only allow the six themes displayed on the homepage.
    theme_searches = {
        "Fantasy": "subject:fantasy",
        "Cozy": "cozy fiction",
        "Adventure": "subject:adventure",
        "Spooky": "subject:horror",
        "Science Fiction": "science fiction",
        "Mystery": "subject:mystery"
    }

    if theme not in theme_searches:
        return "Theme not found.", 404

    books = []
    unavailable = False

    # Search Open Library for books matching the selected theme.
    try:
        response = requests.get(
            "https://openlibrary.org/search.json",
            params={
                "q": theme_searches[theme],
                "limit": 12,
                "fields": "title,author_name,first_publish_year,isbn,cover_i,key"
            },
            timeout=30
        )

        response.raise_for_status()
        books = response.json().get("docs", [])

    except requests.RequestException as error:
        print("Open Library theme search error:", error)
        unavailable = True

    # Retrieve the user's reading lists.
    reading_lists = []
    connection = get_db_connection()

    if connection is not None:
        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                "SELECT id, name FROM reading_lists ORDER BY name"
            )

            reading_lists = cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    return render_template(
        "theme_books.html",
        theme=theme,
        books=books,
        reading_lists=reading_lists,
        unavailable=unavailable
    )



# INDIVIDUAL BOOK DETAILS PAGE

@app.route("/book/<work_id>")
def book_detail(work_id):

    try:
        response = requests.get(
            f"https://openlibrary.org/works/{work_id}.json",
            timeout=30
        )

        response.raise_for_status()
        book = response.json()

        description = book.get("description", "")

        if isinstance(description, dict):
            description = description.get("value", "")

        covers = book.get("covers", [])
        cover_id = covers[0] if covers else None

        return render_template(
            "book_detail.html",
            book=book,
            description=description,
            cover_id=cover_id,
            unavailable=False
        )

    except Exception as error:
        print("BOOK DETAIL ERROR:", repr(error))

        return render_template(
            "book_detail.html",
            book={"title": "Book Details Unavailable"},
            description="We're having trouble connecting to Open Library right now. Please try again in a little while.",
            cover_id=None,
            unavailable=True
        )


# ADD A BOOK TO A READING LIST

@app.route("/lists/add-book", methods=["POST"])
def add_book_to_list():

    list_id = request.form.get("list_id")
    game_id = request.form.get("game_id")
    theme = request.form.get("theme")
    work_id = request.form.get("work_id")
    title = request.form.get("title")
    author = request.form.get("author", "")
    publication_year = request.form.get("publication_year") or None
    cover_id = request.form.get("cover_id")
    isbn = request.form.get("isbn", "")

    # A book must come from either a game or a theme page.
    if not all([list_id, work_id, title]) or not (game_id or theme):
        return "Missing information needed to save this book.", 400

    try:
        list_id = int(list_id)

        if game_id:
            game_id = int(game_id)

        if publication_year:
            publication_year = int(publication_year)

    except ValueError:
        return "Invalid list or publication information.", 400

    # Prepare the book cover URL.
    cover_url = (
        f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
        if cover_id else None
    )

    isbn_10 = isbn if len(isbn) == 10 else None
    isbn_13 = isbn if len(isbn) == 13 else None

    connection = get_db_connection()

    if connection is None:
        return "Could not connect to the SideQuest database."

    try:
        cursor = connection.cursor()

        # Save the book if it is not already in the books table.
        cursor.execute(
            """
            INSERT IGNORE INTO books
            (open_library_id, title, author, publication_year,
             cover_url, isbn_10, isbn_13)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                f"/works/{work_id}",
                title,
                author,
                publication_year,
                cover_url,
                isbn_10,
                isbn_13
            )
        )

        # Find the book's database ID.
        cursor.execute(
            "SELECT id FROM books WHERE open_library_id = %s",
            (f"/works/{work_id}",)
        )

        book = cursor.fetchone()

        if book is None:
            connection.rollback()
            return "Could not save this book.", 500

        book_id = book[0]

        # Add the book to the selected reading list.
        cursor.execute(
            """
            INSERT IGNORE INTO list_books (list_id, book_id)
            VALUES (%s, %s)
            """,
            (list_id, book_id)
        )

        # Check whether the book was already in this list.
        duplicate = cursor.rowcount == 0

        connection.commit()

    finally:
        cursor.close()
        connection.close()

    # Return the visitor to the page where they found the book.
    if theme:
        return redirect(
            url_for(
                "theme_books",
                theme=theme,
                duplicate=1 if duplicate else 0
            )
        )

    return redirect(
        url_for(
            "recommendations",
            game_id=game_id,
            duplicate=1 if duplicate else 0
        )
    )

# REMOVE A BOOK FROM A READING LIST
@app.route("/lists/<int:list_id>/remove-book/<int:book_id>", methods=["POST"])
def remove_book_from_list(list_id, book_id):

    connection = get_db_connection()

    if connection is None:
        return "Could not connect to the SideQuest database."

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM list_books
            WHERE list_id = %s AND book_id = %s
            """,
            (list_id, book_id)
        )

        connection.commit()

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("lists"))




# RUN THE APPLICATION
if __name__ == "__main__":
    app.run(debug=False)
