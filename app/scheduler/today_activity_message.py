from database.repositories import getUsersTodayActivity, changeErrorUserStatus
from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode



async def sendTodayActivity(bot: Bot):
    # Получаем словарь пользователей и их незавершенных привычек/задач
    users_activity_dict = await getUsersTodayActivity()
    
    counter = 0
    error_counter = 0
    
    for tg_id, activity in users_activity_dict.items():
        habits = activity.get("habits", [])
        tasks = activity.get("tasks", [])
        
        # Формируем текст сообщения
        message_parts = []
        
        if habits:
            habit_list = "\n".join([f"▫️ <b>{habit.name}</b>" for habit in habits])
            message_parts.append(f"🔥 Habits to complete:\n{habit_list}")
        
        if tasks:
            task_list = "\n".join([f"▪️ <b>{task.task}</b>" for task in tasks])
            message_parts.append(f"🎯 Tasks to complete:\n{task_list}")
        
        # Если нет ни привычек, ни задач, пропускаем пользователя
        if not message_parts:
            continue
        
        # Объединяем все части сообщения
        message_text = "\n\n".join(message_parts)
        
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
    
    print(f"\n\n\n\nУтром напоминания отправлены {counter} юзерам\n\nОшибки у {error_counter} юзеров\n\n\n\n")



def schedulerTodayActivity(scheduler, bot: Bot):
    try:
        scheduler.add_job(sendTodayActivity, "cron", hour = 8, minute = 0, args = [bot])
    except Exception as e:
        print(e)