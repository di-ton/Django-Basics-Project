# sciProSpace

sciProSpace is a Django-based web application designed to manage and showcase scientific projects. It allows users to create accounts, manage their profiles, and explore publicly available research projects in a structured and organized way. The platform focuses on presenting scientific work, highlighting project details, and making research outputs accessible to visitors.

## Project Structure

The project follows a standard Django architecture with the following main components:

*   **sciProSpace/**: The main project configuration directory.
*   **accounts/**: Handles user authentication, registration, and profile management.
*   **projects/**: Manages the core functionality related to projects. This includes:
    *   **Overview**: General information about the project.
    *   **Members**: Management of project members and their roles (Leader, Member).
    *   **Articles**: Tracking of published scientific articles presenting results obtained during the project.
    *   **Scientific Events**: Management of scientific events at which project results were presented.
    *   **Forms**: Utilization of Django forms for creating and updating project details, memberships, articles, and events.
*   **common/**: Contains shared utilities and common functionality across the application.
*   **templates/**: HTML templates for the application.
*   **static/**: Static files (CSS, images).
*   **media/**: User-uploaded content.

## Setup and Installation

### Prerequisites

*   Python 3.x
*   PostgreSQL

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd sciProSpace
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration:**
    Create a `.env` file in the root directory of the project. This file should contain the following credentials and configuration settings:

    ```env
    DJANGO_SECRET_KEY=your_secret_key_here
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=localhost
    DB_PORT=5432
    ```

    *   `DJANGO_SECRET_KEY`: A secret key for a particular Django installation.
    *   `DB_NAME`: The name of your PostgreSQL database.
    *   `DB_USER`: The username for your database.
    *   `DB_PASSWORD`: The password for your database user.
    *   `DB_HOST`: The database host (usually `localhost` or `127.0.0.1`).
    *   `DB_PORT`: The database port (default is `5432`).

5.  **Apply Migrations and Load Initial Data:**
    ```bash
    python manage.py migrate
    python manage.py loaddata initial_data.json
    ```

6.  **Run the Development Server:**
    ```bash
    python manage.py runserver
    ```

    Access the application at `http://127.0.0.1:8000/`.
