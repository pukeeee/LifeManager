from database.repositories import getUsersWithIncompletedHabits, changeErrorUserStatus
from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode



async def sendIncompletedHabits(bot: Bot):
    users_habits_dict = await getUsersWithIncompletedHabits()  # Получаем словарь пользователей и их незавершенных привычек
    
    counter = 0
    error_counter = 0
    
    for tg_id, habits in users_habits_dict.items():
        # Формируем список незавершенных привычек
        habit_list = "\n".join([f"▫️ <b>{habit.name}</b>" for habit in habits])
        message_text = f"🔥 Don't forget to do your habits today:\n\n{habit_list}"
        
        try:
            # Отправляем персонализированное сообщение
            await bot.send_message(
                chat_id=tg_id,
                text=message_text,
                parse_mode=ParseMode.HTML
            )
            counter += 1
            
        except:
            await changeErrorUserStatus(tg_id)
            error_counter += 1
    
    print(f"\n\n\n\nВечером напоминания отправлены {counter} юзерам\n\nОшибки у {error_counter} юзеров\n\n\n\n")



def schedulerIncompletedHabits(scheduler, bot: Bot):
    try:
        scheduler.add_job(sendIncompletedHabits, "cron", hour = 20, minute = 0, args = [bot])
    except Exception as e:
        print(e)