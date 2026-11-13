# 🐉 SideQuest 
༺𓆩༒︎𓆪༻

**Find your next great adventure.**

SideQuest is a web application that helps users discover books based on their favorite video games, explore books by theme, and organize their discoveries into personalized reading lists.

The project combines video game discovery with book recommendations to help users find their next great read.

## Features

- **Game Discovery:** Browse and search video games.
- **Book Recommendations:** Discover books related to the themes and genres of video games.
- **Theme-Based Discovery:** Explore book collections in categories such as Fantasy, Cozy, Adventure, Spooky, Science Fiction, and Mystery.
- **Book Details:** View additional information about individual books.
- **Reading Lists:** Create personalized reading lists to organize books.
- **List Management:** Rename, delete, and search reading lists.
- **Save and Remove Books:** Add books to reading lists and remove them whenever you want.
- **Contact Page:** Submit messages through the Contact Us form.

## Technologies Used

- Python
- Flask
- MySQL
- HTML
- CSS
- JavaScript
- Open Library API
- NES.css
- Google Fonts

## Installation and Setup

### Requirements

Before running SideQuest, make sure you have installed:

- Python
- MySQL Server
- MySQL Workbench
- Visual Studio Code

### 1. Clone or Download the Project

Download the SideQuest project and open its folder in Visual Studio Code.

### 2. Create a Virtual Environment

Open the VS Code terminal and run:

```bash
python -m venv .venv
```

Activate the virtual environment on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Set Up the Database

Open MySQL Workbench and connect to your local MySQL server.

Create the database:

```sql
CREATE DATABASE sidequest;
```

Make sure the following tables are created:

- `games`
- `books`
- `reading_lists`
- `list_books`
- `contact_messages`

The application uses these tables to store game information, books, reading lists, saved books, and contact messages.

### 5. Configure the Database Connection

Open `database.py` and make sure the MySQL connection settings match your local MySQL installation.

Do not share or upload your database password publicly.

### 6. Run the Application

In the VS Code terminal, make sure your virtual environment is activated and run:

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

## Demo Login

SideQuest currently uses a demonstration login.

- **Username:** `traveler`
- **Password:** `adventure123`

## Project Structure

```text
SideQuest/
│
├── app.py
├── database.py
├── requirements.txt
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── discover.html
│   ├── recommendations.html
│   ├── book_detail.html
│   ├── theme_books.html
│   ├── lists.html
│   ├── list_detail.html
│   └── contact.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── images/
│       └── logo.png
│
└── README.md
```

## APIs and Resources

- **Open Library:** Used to retrieve book information and cover images.
- **NES.css:** Provides retro-inspired pixel styling.
- **Google Fonts:** Provides the Press Start 2P font used throughout the application.
- **EmojiDB:** Used as a resource for finding emojis used throughout the SideQuest interface. https://emojidb.org/

## Project Goals

SideQuest was created to make discovering books fun, interactive, and accessible. It gives users different ways to explore recommendations, provides flexibility in organizing books, and encourages users to discover stories that match their interests.

The interface also incorporates usability principles designed to support different user preferences and approaches to exploring information.

---

**Made with 💜 for curious adventurers.**
