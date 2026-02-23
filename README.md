# sciProSpace

sciProSpace is a Django-based web application designed to manage and showcase scientific projects. It enables users to create accounts, manage their profiles, and explore publicly available research projects in a structured and organized manner. The platform focuses on presenting scientific work, highlighting project details, and making research results accessible to the scientific community.

## Key Features

- Two-step registration process (account creation followed by profile completion).
- Role-based project membership with Leader and Member roles.
- Automatic linking of existing profiles when adding project members by email.
- Shared scientific organizations across multiple projects (preventing duplication).
- Custom validation logic, including:
  - Enforcement of a single Leader per project.
  - Requirement of at least one scientific identifier (ORCID ID or Scopus Author ID) in profiles.
  - Chronological validation of scientific event dates.
- Responsive user interface supporting desktop, tablet, and mobile devices.


## Project Structure

The project follows a standard Django architecture with the following main components:

*   **sciProSpace/**: The main project configuration directory.
*   **accounts/**: Handles user authentication, registration, and profile management. The registration process consists of two steps: entering an email and password, followed by completing the user profile information.
*   **projects/**: Manages the core functionality related to projects. This includes:
    *   **Overview**: General information about the project.
    *   **Members**: Management of project members and their roles (Leader, Member).
    *   **Organizations**: Management of associated scientific organizations (base and partner organizations).
    *   **Articles**: Tracking of published scientific articles presenting results obtained during the project.
    *   **Scientific Events**: Management of scientific events at which project results were presented.
    *   **Forms**: Utilization of Django forms for creating and updating project details, memberships, articles, and events.
*   **common/**: Contains shared utilities and common functionality across the application.
*   **templates/**: HTML templates for the application.
*   **static/**: Static files (CSS, images).
*   **media/**: User-uploaded content.

## Authentication

To create and manage projects, users must:
- Register an account.
- Complete their profile.
- Log in to the system.

Only authenticated users can create new projects and manage related members, scientific organizations, articles, and scientific events.
Unauthenticated users can browse publicly available projects but cannot modify content.

## Setup and Installation

### Prerequisites

*   Python 3.10 or higher (tested with Python 3.11)
*   PostgreSQL

## Tech Stack

- Django 5.2
- psycopg2
- python-dotenv

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

4. **Create PostgreSQL Database**

    Make sure PostgreSQL is running, then create a database:
    
    ```bash
    createdb your_db_name
    ```

5.  **Environment Configuration:**

    A `.env.example` file with the required environment variables is included in the project.
    Create a `.env` file in the root directory by copying it and updating the values.
    This file should contain the following credentials and configuration settings:

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

6.  **Apply Migrations and Load Initial Data:**

    ```bash
    python manage.py migrate
    python manage.py loaddata initial_data.json
    ```
    
    An `initial_data.json` fixture file is included in the project.
    It contains sample data for three scientific projects, including detailed project overviews, associated members and scientific organizations, as well as related articles and scientific events at which the project results were presented.

7.  **Run the Development Server:**
    ```bash
    python manage.py runserver
    ```

    Access the application at `http://127.0.0.1:8000/`.


---

### Project Information

This project was created by **Diana Toneva** as an exam project for the Django Basics course at SoftUni.
