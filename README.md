# SciProSpace

sciProSpace is a Django-based web application designed to manage and showcase scientific projects. It enables users to create accounts, manage their profiles, and explore publicly available research projects in a structured and organized manner. The platform focuses on presenting scientific work, highlighting project details, and making research results accessible to the scientific community allowing for feedback and communication among scientists.

## Live Demo

The project is deployed on Microsoft Azure and available here:
**[View the deployed project](https://sciprospace-e2ara4hphrhhb6gb.spaincentral-01.azurewebsites.net)**


## Key Features

*   **User Management & Profiles**: 
    *   Two-step registration: account creation (email/password) followed by detailed scientist profile information.
    *   Profiles include academic degree, position, affiliation, and identifiers like ORCID/Scopus IDs.
    *   Integration with **Cloudinary** for profile picture hosting.
    *   Profile moderation system with "Profile Moderators" who verify profile authenticity and either approve or ban user profiles after creation.
*   **Project Management**:
    *   Detailed project tracking including acronyms, keywords, descriptions, and funding information.
    *   Role-based membership (Leader, Member) with automatic scientist profile linking based on email.
    *   Organization management: Projects can be associated with scientific organizations (base and partner organizations).
    *   Scientific output tracking: Articles (with journal quartiles) and Scientific Events (with participations).
    *   Project moderation system with "Content Moderators" who can lock/unlock and enable/disable projects, and manage organization details.
*   **Communication & Feedback**:
    *   **Messaging System**: Internal messaging for users, supporting project-specific threads and read/unread status.
    *   **Feedback System**: Commenting system for projects with support for one level of nested replies.
*   **REST API**: Integrated **Django REST Framework** for scientific feedback (comments) and potentially other features. The REST API is implemented as an independent layer and can be accessed directly via its endpoints. The Django templates use JavaScript to consume the API, but external clients can also interact with it without relying on the frontend.
*   **Moderation**: Profile Moderators and Content Moderators are assigned via the Django admin panel.

## Project Structure

*   **sciProSpace/**: Main project configuration, settings, and URLs.
*   **accounts/**: Custom User model and ScientistProfile management. Includes managers, validators, and choices.
*   **projects/**: Manages the core functionality related to projects. This includes:
    - **Overview**: General information about the project.
    - **Members**: Management of project members and their roles (Leader, Member).
    - **Organizations**: Management of associated scientific organizations (base and partner organizations).
    - **Articles**: Tracking of published scientific articles presenting results obtained during the project.
    - **Scientific Events**: Management of scientific events at which project results were presented.
*   **messaging/**: Internal user messaging and project-related communication, including a reporting system for sending content-related issues to moderators.
*   **feedback/**: Project comments and replies, including REST API serializers and views.
*   **common/**: Shared base models (`TimeStampedModel`), context processors, and utilities.
*   **templates/**: Organized HTML templates for all applications.
*   **static/**: Static assets including responsive CSS and default images (e.g. logo, no profile picture).

## Setup and Installation

### Prerequisites

*   Python 3.11 or higher (tested on Python 3.11)
*   PostgreSQL
*   Cloudinary Account (for media storage)
*   SMTP Server (for email notifications)

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/di-ton/Django-Basics-Project.git
    cd Django-Basics-Project
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
    Create a `.env` file in the root directory (refer to `.env.example`). Required variables:

    ```env 
    # Django Settings
    DEBUG=True
    DJANGO_SECRET_KEY=your_secret_key
    ALLOWED_HOSTS=127.0.0.1,localhost
    CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
        
    # Database Configuration
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=127.0.0.1
    DB_PORT=5432
    
    # Cloudinary Settings
    CLOUDINARY_CLOUD_NAME=your_cloudinary_name
    CLOUDINARY_API_KEY=your_cloudinary_key
    CLOUDINARY_API_SECRET=your_cloudinary_secret
    
    # Email Settings
    EMAIL_HOST=your_smtp_host
    EMAIL_PORT=587
    EMAIL_HOST_USER=your_email
    EMAIL_HOST_PASSWORD=your_app_password
    EMAIL_USE_TLS=True
    DEFAULT_FROM_EMAIL=your_sender_email
    ```

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

---

### Project Information

This project was developed by **Diana Toneva** as an exam project for the Django Advanced course at SoftUni. 
