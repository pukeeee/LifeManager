# LifeManagerBot 🧠✨

This is a multifunctional Telegram bot designed to enhance personal productivity through gamification. It helps users manage tasks, track habits, and develop their virtual character.

[Читати українською](README_urk.md)

## 🚀 Key Features

- **Task Tracker**: Create, edit, delete, and mark tasks as complete.
- **Habit Tracker**: Form useful habits, set a weekly schedule, and track your progress.
- **Gamification**: Earn experience points (XP) for completing tasks and habits.
- **Character Development**: Level up your character, unlocking new avatars.
- **User Profile**: View your progress, statistics, and change your name or avatar.
- **Leaderboard**: Compete with other users for a top spot.
- **Subscription Check**: The bot can require a channel subscription for full functionality.
- **Admin Panel**: Ability to broadcast messages to all active users.
- **Multilingual**: Supports Ukrainian and English languages.

## 🛠️ Tech Stack

- **Language**: Python 3.12
- **Bot Framework**: Aiogram 3
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **State Storage (FSM)**: Redis
- **Containerization**: Docker and Docker Compose
- **Task Scheduler**: APScheduler

## ⚙️ Installation and Launch

### Prerequisites
- Installed [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/).

### 1. Clone the repository
```bash
git clone <URL-of-your-repository>
cd LifeManagerBot
```

### 2. Environment Setup

Create a `.env` file in the project's root directory with the following content:

```env
# Your Telegram bot token from @BotFather
TOKEN=YOUR_TELEGRAM_BOT_TOKEN

# Your Telegram channel ID (e.g., @my_channel)
# The bot must be an administrator in this channel for the subscription check to work
CHANNEL=@your_channel
```

### 3. Telegram Channel Setup

For the subscription check feature to work correctly:
1. Create a public or private Telegram channel.
2. Add your bot to this channel.
3. Promote the bot to an **administrator** in the channel. Granting any permission (e.g., "Add Members") is sufficient for it to get the list of members.
4. Specify the channel ID (e.g., `@my_channel`) in the `CHANNEL` variable in your `.env` file.

### 4. Launching the project

After setting up the `.env` file, run the following command in the terminal:

```bash
docker-compose up --build -d
```
This command will automatically build the Docker images, launch the bot, database, and Redis containers, and create the necessary tables in the database.

## 🤖 Bot Usage

- **/start**: Starts the bot, creates a character (for new users), or opens the main menu.
- **/help**: Shows the support contact.
- **/info**: Provides information about the current section (tasks, habits, or main menu).
- **/admin**: Opens the admin panel (available only for the admin ID).
- **/donate**: Information about supporting the project.
