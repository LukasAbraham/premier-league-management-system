# Premier League Management System (PLMS)

This repository is a simplified model of a football league management system built with Django.  It was developed as part of a software testing course.

## Overview

- Web-based management system: Designed for managing Premier League clubs, players, managers, and matches.
- Simplified model: Focuses on core features like CRUD operations on player, manager, club, and match data.
- User-friendly interface: Provides visually appealing views for normal users to access and interact with information.
- Technologies: Built with the Django framework.

## Installation

1. Clone the repo:
  ```bash
  git clone https://github.com/your-username/premier-league-management-system.git
  ```
2. Create a virtual environment:
    - macOS/Linux: `python -m venv env`
    - Windows: `python -m venv env`

3. Activate the virtual environment:
    - macOS/Linux: `source env/bin/activate`
    - Windows: `env\Scripts\activate`
  
4. Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
5. Apply migrations:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```
6. Run the development server:
  ```bash
  python manage.py runserver
  ```

## Testing
- Unit tests: Utilize Django's built-in testing framework to ensure individual components function correctly.
- Automation tests: Employ Selenium WebDriver to simulate user interactions and test application behavior in a web browser.
**To run test**:
  ```bash
  python manage.py test ./path/to/the/test/cases
  ```
