from database.repository import BaseRepository
from database.models import User, Statistic, Habit, Task
from sqlalchemy import select, update, delete, desc, and_, func
import time
from typing import Optional, List, Tuple, Dict
from datetime import datetime



class ProfileRepository(BaseRepository):
    async def set_user(self, tg_id: int) -> Optional[User]:
        async with self.begin():
            user = await self.session.scalar(
                select(User).where(User.tg_id == tg_id)
            )
            if not user:
                unix_time = int(time.time())
                user = User(tg_id=tg_id, start_date=unix_time)
                self.session.add(user)
            return user



    async def get_user(self, tg_id: int) -> Optional[User]:
        async with self.begin():
            return await self.session.scalar(
                select(User).where(User.tg_id == tg_id)
            )



    async def change_name(self, tg_id: int, new_name: str) -> None:
        async with self.begin():
            await self.session.execute(
                update(User)
                .where(User.tg_id == tg_id)
                .values(user_name=new_name)
            )



    async def save_character(self, tg_id: int, user_name: str, avatar: str) -> None:
        async with self.begin():
            # Прибираємо префікс, розширення .png та зайві пробіли з імені файлу
            avatar_name = avatar.split('_', 1)[1] if '_' in avatar else avatar
            avatar_name = avatar_name.strip()  # Прибираємо пробіли на початку та в кінці
            if avatar_name.endswith('.png'):
                avatar_name = avatar_name[:-4]  # Прибираємо .png з кінця рядка
            
            # Перевіряємо, чи існує користувач
            user = await self.session.scalar(
                select(User).where(User.tg_id == tg_id)
            )
            
            if user:
                # Якщо користувач існує - оновлюємо
                await self.session.execute(
                    update(User)
                    .where(User.tg_id == tg_id)
                    .values(
                        user_name=user_name,
                        avatar=avatar_name
                    )
                )
            else:
                # Якщо користувача немає - створюємо
                unix_time = int(time.time())
                new_user = User(
                    tg_id=tg_id,
                    start_date=unix_time,
                    user_name=user_name,
                    avatar=avatar_name
                )
                self.session.add(new_user)



    async def get_leaderboard(self) -> List[Tuple[str, int]]:
        async with self.begin():
            result = await self.session.execute(
                select(User.user_name, User.experience)
                .order_by(desc(User.experience))
                .limit(10)
            )
            return result.all()
    
    
    
    async def get_all_active_users(self) -> List[int]:
        async with self.begin():
            result = await self.session.execute(
                select(User.tg_id).where(User.is_active == True)
            )
            return result.scalars().all()
    
    
    
    async def get_users_with_incompleted_habits(self) -> Dict[int, List[Habit]]:
        async with self.begin():
            # Поточний день тижня (0 - понеділок, 6 - неділя)
            current_day = datetime.today().weekday()
            
            # Створюємо запит, який вибирає користувачів та їхні звички
            query = (
                select(User, Habit)
                .join(Habit, User.id == Habit.user)  # З'єднуємо User та Habit
                .where(
                    User.is_active == True,  # Тільки активні користувачі
                    Habit.status == False    # Тільки незавершені звички
                )
            )
            
            result = await self.session.execute(query)
            rows = result.all()  # Отримуємо всі рядки результату

            # Групуємо звички за користувачами
            users_habits_dict = {}
            for user, habit in rows:
                # Перевіряємо, чи актуальна звичка для поточного дня
                if len(habit.days_of_week) == 7 and habit.days_of_week[current_day] == '1':
                    if user.tg_id not in users_habits_dict:
                        users_habits_dict[user.tg_id] = []
                    users_habits_dict[user.tg_id].append(habit)

            return users_habits_dict
        
    
    
    async def get_users_today_activity(self) -> Dict[int, Dict[str, List]]:
        async with self.begin():
            # Словник для зберігання активностей користувачів
            users_activity_dict = {}

            # Поточний день тижня (0 - понеділок, 6 - неділя)
            current_day = datetime.today().weekday()

            # Запит для отримання незавершених звичок
            habits_query = (
                select(User.tg_id, Habit)
                .join(Habit, User.id == Habit.user)
                .where(
                    User.is_active == True,
                    Habit.status == False
                )
            )
            habits_result = await self.session.execute(habits_query)
            for tg_id, habit in habits_result:
                # Перевіряємо, чи актуальна звичка для поточного дня
                if len(habit.days_of_week) == 7 and habit.days_of_week[current_day] == '1':
                    if tg_id not in users_activity_dict:
                        users_activity_dict[tg_id] = {"habits": [], "tasks": []}
                    users_activity_dict[tg_id]["habits"].append(habit)

            # Запит для отримання незавершених завдань
            tasks_query = (
                select(User.tg_id, Task)
                .join(Task, User.id == Task.user)
                .where(
                    User.is_active == True,
                    Task.status == False
                )
            )
            tasks_result = await self.session.execute(tasks_query)
            for tg_id, task in tasks_result:
                if tg_id not in users_activity_dict:
                    users_activity_dict[tg_id] = {"habits": [], "tasks": []}
                users_activity_dict[tg_id]["tasks"].append(task)

            return users_activity_dict
    
    
    
    async def change_user_status(self, tg_id):
        async with self.begin():
            await self.session.execute(
                update(User)
                .where(User.tg_id == tg_id)
                .values(is_active = True)
            )



    async def change_error_user_status(self, tg_id):
        async with self.begin():
            await self.session.execute(
                update(User)
                .where(User.tg_id == tg_id)
                .values(is_active = False)
            )


################################################
"""Функції-обгортки для зворотної сумісності"""
################################################

async def setUser(tg_id: int) -> Optional[User]:
    async with ProfileRepository() as repo:
        return await repo.set_user(tg_id)



async def getUserDB(tg_id: int) -> Optional[User]:
    async with ProfileRepository() as repo:
        return await repo.get_user(tg_id)



async def changeNameDB(tg_id: int, new_name: str) -> None:
    async with ProfileRepository() as repo:
        await repo.change_name(tg_id, new_name)



async def saveUserCharacter(tg_id: int, user_name: str, avatar: str) -> None:
    async with ProfileRepository() as repo:
        await repo.save_character(tg_id, user_name, avatar)



async def getLeaderboard() -> List[Tuple[str, int]]:
    async with ProfileRepository() as repo:
        return await repo.get_leaderboard()



async def getAllActiveUsers() -> List[int]:
    async with ProfileRepository() as repo:
        return await repo.get_all_active_users()
    


async def getUsersWithIncompletedHabits() -> Dict[int, Dict[str, List]]:
    async with ProfileRepository() as repo:
        return await repo.get_users_with_incompleted_habits()



async def getUsersTodayActivity() -> Dict[int, Dict[str, List]]:
    async with ProfileRepository() as repo:
        return await repo.get_users_today_activity()



async def changeUserStatus(tg_id):
    async with ProfileRepository() as repo:
        await repo.change_user_status(tg_id)



async def changeErrorUserStatus(tg_id):
    async with ProfileRepository() as repo:
        await repo.change_error_user_status(tg_id)