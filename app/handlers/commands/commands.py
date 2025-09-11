from aiogram import Router, F
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
from app.l10n.l10n import Message as L10nMessage
from database.repositories import (getUserDB, resetHabit, changeUserStatus
)
from app.states import User, Profile, Admin
from app.keyboards import (startReplyKb, adminKb
)


# import logging
# logging.basicConfig(level=logging.INFO)

router = Router()
router.name = 'commands'



@router.message(CommandStart())
async def startCommand(message: Message, language_code: str, state: FSMContext):
    user = await getUserDB(message.from_user.id)
    
    if user and user.user_name and user.avatar:  # Проверяем что пользователь полностью настроен
        await message.answer(
            text=L10nMessage.get_message(language_code, "start"),
            parse_mode=ParseMode.HTML,
            reply_markup=await startReplyKb(language_code)
        )
        await changeUserStatus(message.from_user.id)
        await state.set_state(User.startMenu)
        
    else:
        # Для нового пользователя или если не заполнены данные
        await state.set_state(Profile.setName)
        await message.answer(
            text=L10nMessage.get_message(language_code, "newCharacter"),
            parse_mode=ParseMode.HTML
        )



@router.message(Command("donate"))
async def donateComand(message: Message, command: CommandObject, language_code: str):
    if command.args is None or not command.args.isdigit() or not 1 <= int(command.args) <= 2500:
        await message.answer(L10nMessage.get_message(language_code, "donate"), parse_mode=ParseMode.HTML)
        return
    
    amount = int(command.args)
    prices = [LabeledPrice(label="XTR", amount=amount)]
    await message.answer_invoice(
        title=L10nMessage.get_message(language_code, "invoiceTitle"),
        description=L10nMessage.get_message(language_code, "invoiceDescription"),
        prices=prices,
        provider_token="",
        payload=f"{amount}_stars",
        currency="XTR"
    )



@router.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)



@router.message(F.successful_payment)
async def on_successfull_payment(message: Message, language_code: str):
    # await message.answer(message.successful_payment.telegram_payment_charge_id)
    await message.answer(L10nMessage.get_message(language_code, "donateTy"),message_effect_id="5159385139981059251")



@router.message(Command("reset_habits"))
async def reset_habits(message: Message):
    if message.from_user.id == 514373294:
        await resetHabit()
        await message.answer("✅ Привычки успешно сброшены!")
        
    else:
        await message.answer("No no no no buddy\nWrong way") 



@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer("support: @tg_support03")


@router.message(Command("info"))
async def info_message(message: Message, state: FSMContext, language_code: str):
    current_state = await state.get_state()

    if current_state == User.todo.state:
        await message.answer(L10nMessage.get_message(language_code, "taskTrackerInfo"))
    elif current_state == User.startMenu.state:
        await message.answer(L10nMessage.get_message(language_code, "homeInfo"))
    elif current_state == User.habits.state:
        await message.answer(L10nMessage.get_message(language_code, "habitTrackerInfo"))



@router.message(Command("admin"))
async def admin_command(message: Message, state: FSMContext):
    if message.from_user.id == 514373294:
        await state.set_state(Admin.admin)
        await message.answer("Admin panel", reply_markup = await adminKb())
    else:
        pass