from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.types.input_file import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import random
import os
from app.l10n.l10n import Message as L10nMessage
from database.repositories import (setUser, getUserDB, changeNameDB, saveUserCharacter, getLeaderboard)
from app.states import User, Profile
from app.core.utils.name_validation import emoji_specSign, letters, compiled_patterns
from app.keyboards import (startReplyKb, profileInLineKB, avatarNavigationKB, profileSettngsKB, editAvatarKB, goToCharacterKB)
from app.core.utils.config import IMG_FOLDER, LEVEL
from PIL import Image
import io
from dataclasses import dataclass


router = Router()
router.name = 'profiles'


# Створимо кеш для файлів
IMAGE_CACHE = {}

@dataclass
class ProfileData:
    photo: BufferedInputFile
    profile_message: str



async def load_image(filepath: str) -> BufferedInputFile:
    """Завантажує зображення в пам'ять або бере з кешу"""
    if filepath not in IMAGE_CACHE:
        # Відкриваємо та оптимізуємо зображення
        with Image.open(filepath) as img:
            # Конвертуємо в RGB, якщо зображення в RGBA
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Створюємо буфер для збереження оптимізованого зображення
            buffer = io.BytesIO()
            # Зберігаємо з оптимізацією якості (quality=70 дає хороший баланс між розміром та якістю)
            img.save(buffer, format='JPEG', quality=70, optimize=True)
            content = buffer.getvalue()
            IMAGE_CACHE[filepath] = content
            
    return BufferedInputFile(IMAGE_CACHE[filepath], filename=os.path.basename(filepath))



@router.message(Profile.setName)
async def setName_handler(message: Message, state: FSMContext, language_code: str):
    new_name = message.text.strip() 
    is_valid, text = await name_validation(new_name, language_code)
    if not is_valid:
        await message.answer(text)
        
    else:
        await state.update_data(new_name = new_name)
        await state.set_state(Profile.setAvatar)
        await message.answer(L10nMessage.get_message(language_code, "characterInfo").format(user_name = new_name), 
                            reply_markup = await goToCharacterKB(language_code))
        # await setAvatar(message, state, language_code)



@router.callback_query(F.data == "goToCharacter")
async def goToCharacter(callback: CallbackQuery, state: FSMContext, language_code: str):
    await callback.message.delete()
    await setAvatar(callback.message, state, language_code)



@router.message(Profile.setAvatar)
async def setAvatar(message: Message, state: FSMContext, language_code: str):
    if not os.path.exists(IMG_FOLDER):
        print(f"Directory not found: {IMG_FOLDER}")
        await message.answer("Error: Images directory not found")
        return
        
    try:
        img_files = [f for f in os.listdir(IMG_FOLDER) if f.startswith('1_') and f.endswith('.png')]
        if not img_files:
            await message.answer("No avatars found!")
            return
        
        current_index = random.randint(0, len(img_files) - 1)
        selected_file = img_files[current_index]
        photo_path = os.path.join(IMG_FOLDER, selected_file)
        
        if not os.path.isfile(photo_path):
            print(f"File not found: {photo_path}")
            await message.answer("Error: Image file not found")
            return
        
        # Відразу зберігаємо першу картинку в стан
        await state.update_data(
            img_files=img_files,
            current_index=current_index,
            selected_img=selected_file  # Додаємо вибраний файл у стан
        )
        
        photo = await load_image(photo_path)
        character_name = selected_file.split('_', 1)[1].replace('.png', '')
        
        await message.answer_photo(
            photo=photo,
            caption=f"👾 {character_name}\n{current_index + 1} / {len(img_files)}",
            reply_markup=await avatarNavigationKB(language_code)
        )
            
    except Exception as e:
        print(f"Error in setAvatar: {e}")
        await message.answer("Error: Cannot process avatar selection")



@router.callback_query(F.data.in_(["next_img", "prev_img", "edit_next_img", "edit_prev_img"]))
async def navigate_avatar(callback: CallbackQuery, state: FSMContext, language_code: str):
    data = await state.get_data()
    img_files = data.get('img_files', [])
    current_index = data.get('current_index', 0)
    
    if "next" in callback.data:
        current_index = (current_index + 1) % len(img_files)
    else:
        current_index = (current_index - 1) % len(img_files)
    
    selected_file = img_files[current_index]
    photo_path = os.path.join(IMG_FOLDER, selected_file)
    
    # Зберігаємо поточну картинку в стан при кожній навігації
    await state.update_data(
        current_index=current_index,
        selected_img=selected_file
    )
    
    photo = await load_image(photo_path)
    character_name = selected_file.split('_', 1)[1].replace('.png', '')
    
    await callback.message.edit_media(
        media=types.InputMediaPhoto(
            media=photo,
            caption=f"👾 {character_name}\n{current_index + 1} / {len(img_files)}"
        ),
        reply_markup=await avatarNavigationKB(language_code) if "edit" not in callback.data else await editAvatarKB(language_code)
    )
    
    await callback.answer()



async def doneAvatar(callback: CallbackQuery, state: FSMContext, language_code: str, is_new_user: bool = False):
    """
    Загальна логіка збереження аватара
    Args:
        is_new_user: True, якщо це новий користувач, False, якщо редагування існуючого
    """
    data = await state.get_data()
    selected_img = data.get('selected_img', '')
    
    if not selected_img:
        await callback.answer("Please select an avatar first")
        return False
    
    try:
        if is_new_user:
            user_name = data.get('new_name', '')
        else:
            user = await getUserDB(callback.from_user.id)
            if not user:
                await callback.answer("Error: Profile not found")
                return False
            user_name = user.user_name
            
        await saveUserCharacter(
            tg_id=callback.from_user.id,
            user_name=user_name,
            avatar=selected_img
        )
        return True
        
    except Exception as e:
        print(f"Error saving character: {e}")
        return False



@router.callback_query(F.data == "done_img")
async def doneNewAvatar(callback: CallbackQuery, state: FSMContext, language_code: str):
    """Обробник для збереження аватара нового користувача"""
    is_saved = await doneAvatar(callback, state, language_code, is_new_user=True)
    if is_saved:
        # Видаляємо повідомлення з вибором аватара
        await callback.message.delete()
        
        # Надсилаємо вітальне повідомлення
        await callback.message.answer(
            text=L10nMessage.get_message(language_code, "characterAdded"),
            parse_mode=ParseMode.HTML
        )
        
        # Надсилаємо стартове повідомлення з клавіатурою
        await callback.message.answer(
            text=L10nMessage.get_message(language_code, "start"),
            parse_mode=ParseMode.HTML,
            reply_markup=await startReplyKb(language_code)
        )
        
        await state.clear()
        await state.set_state(User.startMenu)
    else:
        # Просто показуємо спливаюче повідомлення про помилку
        await callback.answer("Error saving character")
    
    await callback.answer()



@router.callback_query(F.data == "doneEditImg")
async def doneEditAvatar(callback: CallbackQuery, state: FSMContext, language_code: str):
    """Обробник для збереження відредагованого аватара"""
    is_saved = await doneAvatar(callback, state, language_code, is_new_user=False)
    if is_saved:
        tg_id = callback.from_user.id
        profile_data = await profileMessage(callback.message, state, language_code, tg_id)
        if profile_data:
            await callback.message.edit_media(
                media=types.InputMediaPhoto(
                    media=profile_data.photo,
                    caption=profile_data.profile_message,
                    parse_mode=ParseMode.HTML
                ),
                reply_markup=await profileInLineKB(language_code)
            )
        await state.clear()
        await state.set_state(User.startMenu)
        await callback.answer("Avatar updated successfully!✅")
    else:
        await callback.answer()



@router.callback_query(F.data == "changeName")
async def changeName(callback: CallbackQuery, state: FSMContext, language_code: str):
    await callback.message.delete()  # Удаляем сообщение с картинкой
    await callback.message.answer(
        text=L10nMessage.get_message(language_code, "changeName")
    )
    await state.set_state(Profile.changeName)



@router.message(Profile.changeName)
async def changeName(message: Message, state: FSMContext, language_code: str):
    new_name = message.text.strip() 
    is_valid, text = await name_validation(new_name, language_code)
    if not is_valid:
        await message.answer(text)
    else:
        await changeNameDB(message.from_user.id, new_name)
        await message.answer(L10nMessage.get_message(language_code, "nameChanged"))
        
        # Отримуємо та надсилаємо оновлений профіль
        profile_data = await profileMessage(message, state, language_code, message.from_user.id)
        if profile_data:
            await message.answer_photo(
                photo=profile_data.photo,
                caption=profile_data.profile_message,
                parse_mode=ParseMode.HTML,
                reply_markup=await profileInLineKB(language_code)
            )
        
        await state.clear()
        await state.set_state(User.startMenu)



async def name_validation(new_name: str, language_code: str) -> tuple[bool, str]:
    for pattern in compiled_patterns:
        if pattern.search(new_name):
            text = L10nMessage.get_message(language_code, "nameBad")
            return False, text 
    
    if len(new_name) < 3 or len(new_name) >= 15:
        text = L10nMessage.get_message(language_code, "nameLength")
        return False, text
    
    elif emoji_specSign.search(new_name):
        text = L10nMessage.get_message(language_code, "nameEmoji")
        return False, text
    
    elif not letters.match(new_name):
        text = L10nMessage.get_message(language_code, "nameLetters")
        return False, text
    
    else:
        return True, ""



@router.callback_query(F.data == "changeAvatar")
async def editAvatar(callback: CallbackQuery, state: FSMContext, language_code: str):
    try:
        img_files = [f for f in os.listdir(IMG_FOLDER) if f.startswith('1_') and f.endswith('.png')]
        if not img_files:
            await callback.answer("No avatars found!")
            return
        
        current_index = random.randint(0, len(img_files) - 1)
        selected_file = img_files[current_index]
        photo_path = os.path.join(IMG_FOLDER, selected_file)
        
        # Відразу зберігаємо першу картинку в стан
        await state.update_data(
            img_files=img_files,
            current_index=current_index,
            selected_img=selected_file
        )
        
        photo = await load_image(photo_path)
        character_name = selected_file.split('_', 1)[1].replace('.png', '')
        
        await callback.message.edit_media(
            media=types.InputMediaPhoto(
                media=photo,
                caption=f"👾 {character_name}\n{current_index + 1} / {len(img_files)}"
            ),
            reply_markup=await editAvatarKB(language_code)
        )
        await state.set_state(Profile.editAvatar)
        
    except Exception as e:
        print(f"Error in editAvatar: {e}")
        await callback.answer("Error: Cannot process avatar selection")



@router.callback_query(F.data == "leaderboard")
async def leaderboardMessage(callback: CallbackQuery, state: FSMContext, language_code: str):
    leaderboard = await generateLeaderboard()
    # Надсилаємо нове повідомлення в чат
    await callback.message.answer(
        text=leaderboard,
        parse_mode=ParseMode.HTML
    )



async def generateLeaderboard():
    leaderboard = await getLeaderboard()
    message = "<b>🏆 Leaderboard 🏆</b>\n\n"
    for index, (user_name, experience) in enumerate(leaderboard, start=1):
        message += f"{index}. {user_name}: {experience} XP\n"
    return message



async def profileMessage(message: Message, state: FSMContext, language_code: str, tg_id: int):
    user = await getUserDB(tg_id)
    if not user:
        user = await setUser(tg_id)
        if not user:
            return None
    
    user_name = user.user_name
    level = (user.experience // 1000) + 1
    experience = user.experience

    # Визначаємо префікс для аватара залежно від рівня
    if level >= LEVEL[4]:
        avatar_prefix = str(LEVEL[4])
    elif level >= LEVEL[3]:
        avatar_prefix = str(LEVEL[3])
    elif level >= LEVEL[2]:
        avatar_prefix = str(LEVEL[2])
    else:
        avatar_prefix = str(LEVEL[1])

    # Отримуємо ім'я файлу аватара з БД
    db_avatar = user.avatar if user.avatar else ""
    if not db_avatar.endswith('.png'):
        db_avatar += '.png'
    
    # Формуємо шлях до файлу аватара
    avatar_filename = f"{avatar_prefix}_{db_avatar}"
    avatar_file = os.path.join(IMG_FOLDER, avatar_filename)
    
    # Якщо файл не знайдено, пробуємо використати аватар першого рівня
    if not os.path.isfile(avatar_file):
        avatar_filename = f"1_{db_avatar}"
        avatar_file = os.path.join(IMG_FOLDER, avatar_filename)
        if not os.path.isfile(avatar_file):
            return None
    
    profile_message = L10nMessage.get_message(language_code, "profile").format(
        user_name=user_name,
        userLevel=level,
        experience=experience
    )
    
    try:
        photo = await load_image(avatar_file)
        return ProfileData(photo=photo, profile_message=profile_message)
    except Exception as e:
        return None



@router.callback_query(F.data == "profileSettings")
async def profileSettings(callback: CallbackQuery, state: FSMContext, language_code: str):
    await callback.message.edit_reply_markup(
        reply_markup = await profileSettngsKB(language_code)
    )
    await callback.answer()



@router.callback_query(F.data == "backToProfile")
async def backToProfile(callback: CallbackQuery, state: FSMContext, language_code: str):
    tg_id = callback.from_user.id
    profile_data = await profileMessage(callback, state, language_code, tg_id)
    await state.set_state(User.startMenu)
    if profile_data:
        await callback.message.edit_media(
            media=types.InputMediaPhoto(
                media=profile_data.photo,
                caption=profile_data.profile_message,
                parse_mode=ParseMode.HTML
            ),
            reply_markup=await profileInLineKB(language_code)
        )

    else:
        await callback.message.answer("Error loading profile")
    await callback.answer()k.answer()