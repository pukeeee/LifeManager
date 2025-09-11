from database.repositories import resetHabit


async def resetTodayHabits():
    habitsCount, usersCount = await resetHabit()
    print(f"Змінено {habitsCount} звичок у {usersCount} користувачів.")


def schedulerResetHabits(scheduler):
    try:
        scheduler.add_job(resetTodayHabits, "cron", hour = 1, minute = 0)
    except Exception as e:
        print(e)
