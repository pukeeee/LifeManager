from database.repositories import resetHabit


async def resetTodayHabits():
    habitsCount, usersCount = await resetHabit()
    print(f"\n\n\n\nИзменено {habitsCount} привычек у {usersCount} пользователей.\n\n\n\n")


def schedulerResetHabits(scheduler):
    try:
        scheduler.add_job(resetTodayHabits, "cron", hour = 1, minute = 0)
    except Exception as e:
        print(e)