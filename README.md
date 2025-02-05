# HrBot


Used tech:
* [aiogram 3.x](https://github.com/aiogram/aiogram)
* [SQLAlchemy 2.0+](https://www.sqlalchemy.org/)
* PostgreSQL as database
* psycopg3 as database driver for SQLAlchemy
* Docker with docker-compose for deployment

## Quick Start Guide

### Setting Up Locally

#### 1. Repository Initialization
   - **Clone the Repository**

#### 2. Environment Setup
   - **Create a Virtual Environment**:
     ```bash
     python3.9 -m venv .venv
     ```
   - **Activate the Virtual Environment**:
     ```bash
     source .venv/bin/activate
     ```

#### 3. Configuration
   - **Environment Variables**:
     - Copy the example environment file:
       ```bash
       cp .env.example .env
       ```
     - _Note: The API can operate without this step, but configuring the environment variables is recommended for full functionality._

#### 4. Dependency Management
   - **Install Dependencies**:
     ```bash
     pip install -r requirements.txt
     ```

#### 6. Launching the bot
   - **Start the bot**:
     ```bash
     python bot.py
     ```


##
### Setting Up with Docker

#### 1. Repository Initialization
   - **Clone the Repository**

#### 2. Configuration
   - Follow the steps in the top 👆 to set up the `.env` file.

#### 3. Docker Container
   - **Run Bult Docker**:
     ```bash
     docker build -t <docker_container_name> .
     ```
     
#### 4.Run Docker Container
   - **Run Bult Docker**:
     ```bash
     docker run --network host --restart always -d <docker_container_name>
     ```