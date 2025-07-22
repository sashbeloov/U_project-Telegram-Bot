import json
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from decouple import config
from geopy import Nominatim

# local modules
import keyboard as kb
from state import *
from db import *


TOKEN = config('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()



with open("data.json", "r", encoding="utf-8") as file:
    translations = json.load(file)

def get_text(lang, category, key):
    return translations.get(lang, {}).get(category, {}).get(key, f"[{key}]")


save_lang = {"🇺🇸 eng":"eng","🇺🇿 uz":"uz","🇷🇺 ru":"ru"}
lang_from_db = {"eng":"🇺🇸 eng","uz":"🇺🇿 uz","ru":"🇷🇺 ru"}

# db tables
create_table()
create_bookings_table()
create_table_users()


@router.message(F.text.startswith("/start"))
async def start(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if check_user_language(user_id):
        await state.update_data(language=lang_from_db[check_user_language(user_id)])
        lang = lang_from_db[check_user_language(user_id)]
        await message.answer(text=get_text(lang, 'message_text', 'menu'), reply_markup=kb.menu(lang))
        await state.set_state(statuslar.customer_menu_checked)
    else:
        status, lang = get_user_status_and_language(user_id)
        if lang is not None:
            lang = lang_from_db[lang]
            if status:
                await bot.send_message(chat_id=user_id, text=get_text(lang, 'message_text', 'menu'),reply_markup=kb.registered_master(lang))
                await state.set_state(statuslar.registered_master_menu)
            else:
                await message.answer(text=get_text(lang, 'message_text', 'check_admin_message'),
                                     reply_markup=kb.waited_confirmation(lang))
                await state.set_state(statuslar.jarayonda_menu)

        else:
            await message.answer(text=translations['start'], reply_markup=kb.start_key(),parse_mode='HTML')
            await state.set_state(statuslar.language)


@router.message(statuslar.language)
async def customer_or_master(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text in {"🇺🇸 eng":"🇺🇸 eng","🇺🇿 uz":"🇺🇿 uz","🇷🇺 ru":"🇷🇺 ru",}:
        await state.update_data(language=message.text)
        data = await state.get_data()
        lang = data['language']
        await bot.send_message(chat_id=user_id,text=get_text(lang, 'message_text', 'master_type'), reply_markup=kb.customer_or_master(lang))
        await state.set_state(statuslar.customer_or_master)



# /////////////////////// ------------- SHU YERDA USTANI YOKI MIJOZNI RO'YHATDAN O'TISH BOSHQARILADI --------- \\\\\\\\\\\\\\\\\\\\\\\\\\ #
@router.message(statuslar.customer_or_master)
async def customer_or_master_register(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    lang = data['language']
    if message.text == get_text(lang, "buttons", "master"):
        await bot.send_message(chat_id=user_id,text=get_text(lang, 'message_text', 'name'), reply_markup=ReplyKeyboardRemove())
        await state.set_state(statuslar.master_name)
    if message.text == get_text(lang, "buttons", "customer"):
        await message.answer(text=get_text(lang, 'message_text', 'contact'), reply_markup=kb.phone_key(lang))
        await state.set_state(statuslar.mijoza_contact)





@router.message(statuslar.mijoza_contact)
async def mijoza_contact(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        if message.contact:
            await bot.send_message(chat_id=user_id, text=get_text(lang, 'message_text', 'name'),reply_markup=ReplyKeyboardRemove())
            await state.update_data(phone=message.contact.phone_number)
            await state.set_state(statuslar.customer_name)
        else:
            text = message.text
            if message.text.startswith("+998") and len(text) == 13 and text[1:].isdigit():
                await bot.send_message(chat_id=user_id, text=get_text(lang, 'message_text', 'name'),reply_markup=ReplyKeyboardRemove())
                await state.update_data(phone=message.text)
                await state.set_state(statuslar.customer_name)
            else:
                await message.answer(text=get_text(lang, 'message_text', 'error_phone'),reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        print(f"Error:{e}")



@router.message(statuslar.customer_name)
async def customer_name(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        correct_name = True
        for i in message.text:
            if not i.isalpha():
                correct_name = False
                break
        if correct_name:
            msg_text = (
                f"{get_text(lang, 'message_text', 'confirmation_or_rejected')}\n"
                f"{get_text(lang, 'message_text', 'phone')} {data["phone"]}\n"
                f"{get_text(lang, 'message_text', 'name')} {message.text}"
            )

            await state.update_data(name=message.text)
            await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.conf(lang))
            await state.set_state(statuslar.check_conf_customer)

        if not correct_name:
            await message.answer(text=get_text(lang, 'message_text', 'error_name'))
    except Exception as e:
        print(f"Error:{e}")


# ************************
@router.message(statuslar.check_conf_customer)
async def check_conf_customer(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        if message.text == get_text(lang, "buttons", "confirm"):
            if save_user(user_id, data["name"],data["phone"],save_lang[lang]):
                await message.answer(text=get_text(lang, 'message_text', 'menu'), reply_markup=kb.menu(lang))
                await state.set_state(statuslar.customer_menu_checked)

        if message.text == get_text(lang, "buttons", "rejected"):
            await bot.send_message(chat_id=user_id, text=get_text(lang, 'message_text', 'master_type'), reply_markup=kb.customer_or_master(lang))
            await state.set_state(statuslar.customer_or_master)

    except Exception as e:
        print(f"Error:{e}")



# customer menuuuuu
@router.message(statuslar.customer_menu_checked)
async def customer_menu_checked(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        if message.text == get_text(lang, "buttons", "change_info"):
            await message.answer(text=get_text(lang, 'message_text', 'select_change_info'), reply_markup=kb.change_info(lang))
            await state.set_state(statuslar.change_info_check)

        elif message.text == get_text(lang, "buttons", ""):
            pass
        elif message.text == get_text(lang, "buttons", ""):
            pass
    except Exception as e:
        print(f"Error:{e}")



# tilni o'zgartirishni oxirida to'g'irliman
@router.message(statuslar.change_info_check)
async def change_info_check(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']

        if message.text == get_text(lang, "buttons", "back"):
            await message.answer(text=get_text(lang, 'message_text', 'menu'), reply_markup=kb.menu(lang))
            await state.set_state(statuslar.customer_menu_checked)

        elif message.text == get_text(lang, "buttons", "change_lang"):
            await message.answer(text=get_text(lang, 'message_text', 'change_lang'), reply_markup=kb.change_lang(lang))
            await state.set_state(statuslar.update_customer_lang)

        elif message.text == get_text(lang, "buttons", "change_name"):
            await message.answer(text=get_text(lang, 'message_text', 'update_name'), reply_markup=kb.back(lang))
            await state.set_state(statuslar.update_name)

        elif message.text == get_text(lang, "buttons", "change_phone"):
            await message.answer(text=get_text(lang, 'message_text', 'update_phone'), reply_markup=kb.back(lang))
            await state.set_state(statuslar.update_phone_customer)

    except Exception as e:
            print(f"Error:{e}")




@router.message(statuslar.update_customer_lang)
async def update_customer_lang(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        if message.text == get_text(lang, "buttons", "back"):
            await message.answer(text=get_text(lang, 'message_text', 'select_change_info'),reply_markup=kb.change_info(lang))
            await state.set_state(statuslar.change_info_check)

        if message.text == get_text(lang, "buttons", "eng"):
            update_user_field(user_id,"language",save_lang[message.text])
            await message.answer(text=get_text(lang, 'message_text', 'updated_customer_info'),reply_markup=kb.change_info(lang))
            await state.set_state(statuslar.change_info_check)

        if message.text == get_text(lang, "buttons", "uz"):
            update_user_field(user_id, "language", save_lang[message.text])
            await message.answer(text=get_text(lang, 'message_text', 'updated_customer_info'), reply_markup=kb.change_info(lang))
            await state.set_state(statuslar.change_info_check)

        if message.text == get_text(lang, "buttons", "ru"):
            update_user_field(user_id, "language", save_lang[message.text])
            await message.answer(text=get_text(lang, 'message_text', 'updated_customer_info'),reply_markup=kb.change_info(lang))
            await state.set_state(statuslar.change_info_check)


    except Exception as e:
            print(f"Error:{e}")




@router.message(statuslar.update_name)
async def update_name(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        text = message.text
        if message.text == get_text(lang, "buttons", "back"):
            await message.answer(text=get_text(lang, 'message_text', 'select_change_info'),reply_markup=kb.change_info(lang))
            await state.set_state(statuslar.change_info_check)
        else:
            correct_name = True
            for i in message.text:
                if not i.isalpha():
                    correct_name = False
                    break
            if correct_name:
                update_user_field(user_id,"name",message.text)
                await message.answer(text=get_text(lang, 'message_text', 'updated_customer_info'), reply_markup=kb.change_info(lang))
                await state.set_state(statuslar.change_info_check)
            if not correct_name:
                await message.answer(text=get_text(lang, 'message_text', 'error_name'))

    except Exception as e:
            print(f"Error:{e}")



@router.message(statuslar.update_phone_customer)
async def update_phone_customer(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        text = message.text
        if message.text == get_text(lang, "buttons", "back"):
            await message.answer(text=get_text(lang, 'message_text', 'select_change_info'),reply_markup=kb.change_info(lang))
            await state.set_state(statuslar.change_info_check)
        elif message.text.startswith("+998") and len(text) == 13 and text[1:].isdigit():
            update_user_field(user_id, "phone", message.text)
            await message.answer(text=get_text(lang, 'message_text', 'updated_customer_info'), reply_markup=kb.change_info(lang))
            await state.set_state(statuslar.change_info_check)
        else:
            await message.answer(text=get_text(lang, 'message_text', 'error_phone'), reply_markup=ReplyKeyboardRemove())

    except Exception as e:
        print(f"Error:{e}")






@router.message(statuslar.master_name)
async def master_name(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        correct_name = True
        for i in message.text:
            if not i.isalpha():
                correct_name = False
                break
        if correct_name:
            await state.update_data(name=message.text.strip())
            await message.answer(text=get_text(lang, 'message_text', 'contact'), reply_markup=kb.phone_key(lang))
            await state.set_state(statuslar.master_phone)
        if not correct_name:
            await message.answer(text=get_text(lang, 'message_text', 'error_name'))
    except Exception as e:
        print(f"Error:{e}")




@router.message(statuslar.master_phone)
async def master_phone(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        if message.contact:
            await message.answer(text=get_text(lang, 'message_text', 'master_workspace_name'), reply_markup=kb.skip_message(lang))
            await state.update_data(phone=message.contact.phone_number)
            await state.set_state(statuslar.ustaxona_nomi)
        else:
            text = message.text
            if message.text.startswith("+998") and len(text) == 13 and text[1:].isdigit():
                await message.answer(text=get_text(lang, 'message_text', 'master_workspace_name'), reply_markup=kb.skip_message(lang))
                await state.update_data(phone=message.text)
                await state.set_state(statuslar.ustaxona_nomi)
            else:
                await message.answer(text=get_text(lang, 'message_text', 'error_phone'), reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        print(f"Error:{e}")


@router.message(statuslar.ustaxona_nomi)
async def ustaxona_nomi(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        if message.text not in {"⏭\uFE0F O'tkazib yuborish","⏭\uFE0F Skip","⏭\uFE0F Пропустить"}:
            await state.update_data(ustaxona_nomi=message.text)
            await message.answer(text=get_text(lang, 'message_text', 'moljal'), reply_markup=kb.skip_message(lang))
            await state.set_state(statuslar.moljal)

        if message.text in {"⏭\uFE0F O'tkazib yuborish","⏭\uFE0F Skip","⏭\uFE0F Пропустить"}:
            await state.update_data(ustaxona_nomi="—")
            await message.answer(text=get_text(lang, 'message_text', 'moljal'), reply_markup=kb.skip_message(lang))
            await state.set_state(statuslar.moljal)

    except Exception as e:
        print(f"Error:{e}")



@router.message(statuslar.moljal)
async def moljal(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        if message.text not in {"⏭\uFE0F O'tkazib yuborish","⏭\uFE0F Skip","⏭\uFE0F Пропустить"}:
            await state.update_data(moljal=message.text)
            await message.answer(text=get_text(lang, 'message_text', 'send_location'), reply_markup=kb.location(lang))
            await state.set_state(statuslar.location)

        elif message.text in {"⏭\uFE0F O'tkazib yuborish","⏭\uFE0F Skip","⏭\uFE0F Пропустить"}:
            await state.update_data(moljal="—")
            await message.answer(text=get_text(lang, 'message_text', 'send_location'), reply_markup=kb.location(lang))
            await state.set_state(statuslar.location)
    except Exception as e:
        print(f"Error:{e}")



@router.message(statuslar.location)
async def location(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        if message.location:
            await state.update_data(loc={"latitude":message.location.latitude,
                                              "longitude":message.location.longitude})
            await message.answer(text=get_text(lang, 'message_text', 'work_time'), reply_markup=ReplyKeyboardRemove())
            await state.set_state(statuslar.working_time)
        else:
            await message.answer(text=get_text(lang, 'message_text', 'error_send_location'), reply_markup=ReplyKeyboardRemove())

    except Exception as e:
        print(f"Error:{e}")




@router.message(statuslar.working_time)
async def working_time(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        text = message.text
        if "-" in text and ":" in text and text.split("-")[0][0].isdigit() and text.split("-")[1][0].isdigit():
            await state.update_data(hours=message.text)
            await message.answer(text=get_text(lang, 'message_text', 'approximately_working_time'), reply_markup=ReplyKeyboardRemove())
            await state.set_state(statuslar.min_and_confirmation)

        else:
            await message.answer(text=get_text(lang, 'message_text', 'error_work_time'), reply_markup=ReplyKeyboardRemove())

    except Exception as e:
        print(f"Error:{e}")



@router.message(statuslar.min_and_confirmation)
async def min_and_confirmation(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        text = message.text
        if text.isdigit():
            await state.update_data(min=message.text)
            latitude,longitude = data["loc"]["latitude"],data["loc"]["longitude"]
            geolocator = Nominatim(user_agent="geo_bot")
            address_info = geolocator.reverse((latitude, longitude), exactly_one=True)

            if address_info:
                address = address_info.address
            else:
                address = f"{get_text(lang, 'message_text', 'nolocation')}\n"

            msg_text = (
                f"{get_text(lang, 'message_text', 'confirmation_or_rejected')}\n"
                f"{get_text(lang, 'message_text', 'name')} {data['name']}\n"
                f"{get_text(lang, 'message_text', 'phone')} {data['phone']}\n"
                f"{get_text(lang, 'message_text', 'conf_workspace')} {data['ustaxona_nomi']}\n"
                f"{get_text(lang, 'message_text', 'conf_moljal')} {data['moljal']}\n"
                f"{get_text(lang, 'message_text', 'conf_location')}{address}\n"
                f"{get_text(lang, 'message_text', 'conf_working_time')} {data['hours']}\n"
                f"{get_text(lang, 'message_text', 'conf_working_min')} {message.text} min\n"
            )

            await state.update_data(address=address)
            await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.conf(lang))
            await state.set_state(statuslar.confirmation_or_rejected)

        else:
            await message.answer(text=get_text(lang, 'message_text', 'error_work_min'),
                                 reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        print(f"Error:{e}")



@router.message(statuslar.confirmation_or_rejected)
async def confirmation_or_rejected(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    status,lang = get_user_status_and_language(user_id)
    lang = lang_from_db[lang]
    if message.text == get_text(lang, "buttons", "confirm"):
        await message.answer(text=get_text(lang, 'message_text', 'check_admin_message'),reply_markup=kb.waited_confirmation(lang))
        insert_master(user_id, data['name'], data['phone'], data['ustaxona_nomi'], data['moljal'], data['address'], data['hours'], data['min'], save_lang[lang])

        msg_text = (
            f"{get_text(lang, 'message_text', 'new_user_register')}\n"
            f"{get_text(lang, 'message_text', 'name')} {data['name']}\n"
            f"{get_text(lang, 'message_text', 'phone')} {data['phone']}\n"
            f"{get_text(lang, 'message_text', 'conf_workspace')} {data['ustaxona_nomi']}\n"
            f"{get_text(lang, 'message_text', 'conf_moljal')} {data['moljal']}\n"
            f"{get_text(lang, 'message_text', 'conf_location')}{data['address']}\n"
            f"{get_text(lang, 'message_text', 'conf_working_time')} {data['hours']}\n"
            f"{get_text(lang, 'message_text', 'conf_working_min')} {data['min']} min\n"
            f"{get_text(lang, 'message_text', 'tg_id')} {user_id}\n"
            f"{get_text(lang, 'message_text', 'til')} {lang}\n"
        )
        await bot.send_message(chat_id=921347523, text=msg_text, reply_markup=kb.conf_new_user(lang,user_id))
        await state.set_state(statuslar.jarayonda_menu)


    if message.text == get_text(lang, "buttons", "rejected"):
        await bot.send_message(chat_id=user_id,text=get_text(lang, 'message_text', 'master_type'), reply_markup=kb.customer_or_master(lang))
        await state.set_state(statuslar.customer_or_master)



@router.message(statuslar.jarayonda_menu)
async def jarayonda_menu_check(message: Message, state: FSMContext):
    user_id = message.from_user.id
    status, lang_code = get_user_status_and_language(user_id)
    lang = lang_from_db[lang_code]

    if message.text == get_text(lang, "buttons", "conf_admin"):
        data = get_master_data(user_id)  # <-- Bazadan olamiz
        if not data:
            await message.answer("❌ Ma'lumotlar topilmadi.")
            return

        msg_text = (
            f"{get_text(lang, 'message_text', 'new_user_register')}\n"
            f"{get_text(lang, 'message_text', 'name')} {data['name']}\n"
            f"{get_text(lang, 'message_text', 'phone')} {data['phone']}\n"
            f"{get_text(lang, 'message_text', 'conf_workspace')} {data['ustaxona_nomi']}\n"
            f"{get_text(lang, 'message_text', 'conf_moljal')} {data['moljal']}\n"
            f"{get_text(lang, 'message_text', 'conf_location')}{data['address']}\n"
            f"{get_text(lang, 'message_text', 'conf_working_time')} {data['hours']}\n"
            f"{get_text(lang, 'message_text', 'conf_working_min')} {data['min']} min\n"
            f"{get_text(lang, 'message_text', 'tg_id')} {user_id}\n"
            f"{get_text(lang, 'message_text', 'til')} {lang}\n"
        )

        await bot.send_message(chat_id=921347523, text=msg_text, reply_markup=kb.conf_new_user(lang, user_id))
        await message.answer(text=get_text(lang, 'message_text', 'check_admin_message'), reply_markup=kb.waited_confirmation(lang))

    if message.text == get_text(lang, "buttons", "contact_with_admin"):
        await message.answer("✉️ Savolingizni yozing. Admin bilan bog'lanasiz.")
        await state.set_state(statuslar.contact_with_admin_message)



@router.message(statuslar.contact_with_admin_message)
async def send_to_admin(message: Message, state: FSMContext):
    user_id = message.from_user.id
    status, lang_code = get_user_status_and_language(user_id)
    lang = lang_from_db[lang_code]
    print(lang)
    msg = f"📩 Yangi xabar:\n\n👤 ID: {user_id}\n✉️ Xabar: {message.text}"
    await bot.send_message(chat_id=921347523, text=msg)

    await message.answer(text=get_text(lang, 'message_text', 'admin_contacted_successfully'))
    print(get_text(lang, 'message_text', 'admin_contacted_successfully'))
    await state.set_state(statuslar.jarayonda_menu)



@router.message(F.chat.id == 921347523)
async def admin_to_master(message: Message):
    if message.reply_to_message and message.reply_to_message.text:
        lines = message.reply_to_message.text.split("\n")
        user_id_line = next((l for l in lines if "ID:" in l or "Tg_id:" in l), None)

        if user_id_line:
            try:
                user_id = int(user_id_line.split(":")[1].strip())
                lang_code = get_user_language(user_id)
                lang_code = lang_code if lang_code in lang_from_db else 'uz'

                header = get_text(lang_code, "message_text", "admin_reply_header") or "📬 Admindan xabar:\n\n"
                await bot.send_message(chat_id=user_id, text=f"{header}{message.text}")
                await message.answer("✅ Xabar foydalanuvchiga yuborildi.")
            except Exception as e:
                await message.answer(f"❌ Xatolik: {e}")
        else:
            await message.answer("❗️ Reply qilingan xabarda foydalanuvchi ID topilmadi.")
    else:
        await message.answer("❗️ Iltimos, foydalanuvchi xabari ustiga reply qiling.")






from aiogram.types import CallbackQuery
from db import update_status

@router.callback_query(F.data.startswith(("approve", "reject")))
async def admin_confirm_user(callback: CallbackQuery, state: FSMContext):
    try:
        action, user_id = callback.data.split(":")
        user_id = int(user_id)
        lang = lang_from_db[get_user_language(user_id)]

        if action == "approve":
            update_status(user_id, True)
            await callback.answer("✅ Tasdiqlandi!")
            await callback.message.edit_text(callback.message.text + "\n✅ Admin tasdiqladi.")
            # Userni yangi menuga yuboramiz
            await callback.bot.send_message(chat_id=user_id, text=get_text(lang, 'message_text', 'master_type'),reply_markup=kb.registered_master(lang))
            await state.set_state(statuslar.registered_master_menu)


        elif action == "reject":
            update_status(user_id, False)
            await callback.message.edit_text(callback.message.text + "\n❌ Admin rad etdi.")
            # Userni bosh menyuga yuboramiz
            await bot.send_message(chat_id=user_id, text=get_text(lang, 'message_text', 'master_type'),reply_markup=kb.customer_or_master(lang))
            await state.set_state(statuslar.customer_or_master)


    except Exception as e:
        print(f"Callback error: {e}")




@router.message(statuslar.registered_master_menu)
async def rating_master(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        lang = lang_from_db[get_user_language(user_id)]
        await state.update_data(language=lang)
        if message.text == get_text(lang, "buttons", "rating"):
            if get_master_rating(user_id):
                msg_text = (
                    f"{get_text(lang, 'message_text', 'your_rating')}{get_master_rating(user_id)}"
                )
                await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.registered_master(lang))

            else:
                await message.answer(text=get_text(lang, 'message_text', 'no_rating'), reply_markup=kb.registered_master(lang))

        elif message.text == get_text(lang, "buttons", "mijozlar"):
            if get_all_customer_bookings(user_id):
                msg_text = (
                    f"{get_text(lang, 'message_text', 'all_brons')}{get_all_customer_bookings(user_id)}"
                )
                await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.registered_master(lang))
            else:
                await message.answer(text=get_text(lang, 'message_text', 'no_bron'),reply_markup=kb.registered_master(lang))

        elif message.text == get_text(lang, "buttons", "change_info_master"):
            await message.answer(text=get_text(lang, 'message_text', 'select_change_info'),reply_markup=kb.select_change_info(lang))
            await state.set_state(statuslar.select_change_info)
        elif message.text == get_text(lang, "buttons", "vaqt"):
            await message.answer(text=get_text(lang, "message_text", "sana"), reply_markup=kb.generate_date_keyboard())
            await message.answer(text=get_text(lang, "message_text", "sana_simple"), reply_markup=kb.back(lang))
            await state.set_state(statuslar.sana)

    except Exception as e:
        print(f"Error:{e}")



@router.message(statuslar.sana)
async def handle_back_or_invalid(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    lang = data['language']

    if message.text == get_text(lang, "buttons", "back"):
        await message.answer("⬅ Asosiy menuga qaytdingiz.", reply_markup=kb.registered_master(lang))
        await state.set_state(statuslar.registered_master_menu)



from datetime import datetime, timedelta
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

def generate_time_slots_keyboard(user_id):
    try:
        master_data = get_master_data(user_id)  # Sizda bor funksiya
        if not master_data:
            return None

        work_hours = master_data.get("hours")  # Masalan: "09:00-21:00"
        interval = int(master_data.get("min"))  # Masalan: 30

        if not work_hours or not interval:
            return None

        start_time_str, end_time_str = work_hours.split("-")
        start_time = datetime.strptime(start_time_str, "%H:%M")
        end_time = datetime.strptime(end_time_str, "%H:%M")

        kb = InlineKeyboardBuilder()
        current_time = start_time
        while current_time < end_time:
            time_str = current_time.strftime("%H:%M")
            kb.add(InlineKeyboardButton(text=time_str, callback_data=f"time:{time_str}"))
            current_time += timedelta(minutes=interval)

        kb.adjust(3)  # Har qatorda 3 ta tugma
        return kb.as_markup()

    except Exception as e:
        print(f"Xato (generate_time_slots_keyboard): {e}")
        return None


@router.callback_query(F.data.startswith("date:"))
async def handle_date_selection(callback: CallbackQuery, state: FSMContext):
    selected_date = callback.data.split(":")[1]  # Masalan, 22.07.2025
    await state.update_data(selected_date=selected_date)

    user_id = callback.from_user.id  # Master ID
    times_keyboard = generate_time_slots_keyboard(user_id)

    if times_keyboard:
        await callback.message.edit_text(
            text=f"📅 Tanlangan sana: {selected_date}\nEndi vaqtni tanlang:",
            reply_markup=times_keyboard
        )
    else:
        await callback.message.edit_text("❌ Vaqtlar topilmadi.")







@router.message(statuslar.select_change_info)
async def select_change_info(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']

        field_map = {
            get_text(lang, "buttons", "change_name_master"): "name",
            get_text(lang, "buttons", "change_phone_master"): "phone",
            get_text(lang, "buttons", "change_manzil_master"): "address",
            get_text(lang, "buttons", "change_moljal_master"): "moljal",
            get_text(lang, "buttons", "change_lokatsiya_master"): "ustaxona_nomi",
            get_text(lang, "buttons", "change_working_tim_master"): "hours",
            get_text(lang, "buttons", "change_working_min_master"): "min",
        }

        selected = field_map.get(message.text)
        if selected:
            await state.update_data(field=selected)
            await message.answer(text=get_text(lang, "message_text", "enter_new_value"))
            await state.set_state(statuslar.update_value)
        else:
            await message.answer(get_text(lang, "message_text", "not_found"))
    except Exception as e:
        print(f"Error in select_change_info: {e}")



@router.message(statuslar.update_value)
async def update_master_field(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        field = data['field']
        new_value = message.text.strip()

        # Ixtiyoriy validatsiya
        if field == "phone" and not new_value.startswith("+998"):
            await message.answer(get_text(lang, "message_text", "invalid_phone"))
            return

        # Yangilash
        success = update_master_info(user_id, **{field: new_value})
        if success:
            await message.answer(get_text(lang, "message_text", "update_success"), reply_markup=kb.registered_master(lang))
            await state.set_state(statuslar.registered_master_menu)
        else:
            await message.answer(get_text(lang, "message_text", "update_failed"))
    except Exception as e:
        print(f"Error in update_master_field: {e}")









