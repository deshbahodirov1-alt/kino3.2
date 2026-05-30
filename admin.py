from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from config import ADMIN_ID
from database import (
    load_movies,
    save_movies,
    load_groups,
    save_groups,
    load_users
)
from movie_state import (
    AddMovie,
    AddGroup,
    UserListState,
    MovieInfoState
)

router = Router()


# =========================
# KINO QO'SHISH
# =========================

@router.message(F.video | F.document)
async def get_video(message: Message, state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    if message.video:
        file_id = message.video.file_id
        file_type = "video"
    else:
        file_id = message.document.file_id
        file_type = "document"

    await state.update_data(
        video_id=file_id,
        type=file_type
    )

    await message.answer("🎬 Kino nomini kiriting:")
    await state.set_state(AddMovie.waiting_for_name)


@router.message(AddMovie.waiting_for_name)
async def get_name(message: Message, state: FSMContext):

    await state.update_data(name=message.text)

    await message.answer("🌐 Kino tilini kiriting:")

    await state.set_state(AddMovie.waiting_for_language)


@router.message(AddMovie.waiting_for_language)
async def get_language(message: Message, state: FSMContext):

    await state.update_data(language=message.text)

    await message.answer("🎭 Kino janrini kiriting:")

    await state.set_state(AddMovie.waiting_for_genre)


@router.message(AddMovie.waiting_for_genre)
async def get_genre(message: Message, state: FSMContext):

    data = await state.get_data()

    movies = load_movies()

    movie_id = str(len(movies) + 1)

    movies[movie_id] = {
        "video": data["video_id"],
        "type": data["type"],
        "name": data["name"],
        "language": data["language"],
        "genre": message.text,
        "views": 0
    }

    save_movies(movies)

    await message.answer(
        f"✅ Kino saqlandi\n🆔 Kod: {movie_id}"
    )

    await state.clear()


# =========================
# KINO TAHRIRLASH
# =========================

@router.message(F.text.startswith("edit"))
async def edit_movie(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    try:

        parts = message.text.split(maxsplit=3)

        movie_id = parts[1]
        field = parts[2].lower()
        new_value = parts[3]

        movies = load_movies()

        if movie_id not in movies:
            await message.answer("❌ Kino topilmadi.")
            return

        fields = {
            "nomi": "name",
            "til": "language",
            "janr": "genre"
        }

        if field not in fields:
            await message.answer(
                "❌ Field noto'g'ri.\n"
                "nomi / til / janr"
            )
            return

        movies[movie_id][fields[field]] = new_value

        save_movies(movies)

        await message.answer(
            "✅ Kino muvaffaqiyatli tahrirlandi."
        )

    except:

        await message.answer(
            "❌ Format noto'g'ri.\n\n"
            "Misol:\n"
            "edit 5 til rus"
        )


# =========================
# RO'YXAT
# =========================
@router.message(F.text == "📋 Ro'yhat")
async def menu_movies(
    message: Message,
    state: FSMContext
):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "🎬 Kino ID sini kiriting:"
    )

    await state.set_state(
        MovieInfoState.waiting_movie_id
    )
@router.message(MovieInfoState.waiting_movie_id)
async def movie_info(
    message: Message,
    state: FSMContext
):

    movies = load_movies()

    movie_id = message.text

    if movie_id not in movies:

        await message.answer(
            "❌ Kino topilmadi."
        )
        return

    movie = movies[movie_id]

    text = (
        f"🆔 {movie_id}\n"
        f"😁 {movie['video']}\n"
        f"🎥 {movie['name']}\n"
        f"🌐 {movie['language']}\n"
        f"🎭 {movie['genre']}\n"
        f"👁 So'ralgan soni: {movie.get('views', 0)}"
    )

    await message.answer(text)

    await state.clear()
# =========================
# GURUH QO'SHISH
# =========================

@router.message(F.text.lower() == "addgr")
async def add_group(message: Message, state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer("📝 Guruh nomini yuboring:")

    await state.set_state(AddGroup.waiting_for_name)


@router.message(AddGroup.waiting_for_name)
async def group_name(message: Message, state: FSMContext):

    await state.update_data(name=message.text)

    await message.answer("🔗 Guruh URL yuboring:")

    await state.set_state(AddGroup.waiting_for_url)


@router.message(AddGroup.waiting_for_url)
async def group_url(message: Message, state: FSMContext):

    data = await state.get_data()

    groups = load_groups()

    groups.append({
        "name": data["name"],
        "url": message.text
    })

    save_groups(groups)

    await message.answer("✅ Guruh qo'shildi.")

    await state.clear()


# =========================
# KINO O'CHIRISH
# =========================

@router.message(F.text.startswith("delete"))
async def delete_movie(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    try:

        movie_id = message.text.split()[1]

        movies = load_movies()

        if movie_id not in movies:
            await message.answer(
                "❌ Kino topilmadi."
            )
            return

        del movies[movie_id]

        save_movies(movies)

        await message.answer(
            f"✅ {movie_id} kodli kino o'chirildi."
        )

    except:

        await message.answer(
            "❌ Format noto'g'ri.\n\n"
            "Misol:\n"
            "delete 5"
        )


# =========================
# XABAR YUBORISH
# =========================

@router.message(F.text.startswith("send "))
async def send_all(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    users = load_users()

    text = message.text[5:]

    success = 0

    for user in users:

        try:

            await message.bot.send_message(
                chat_id=user["id"],
                text=text
            )

            success += 1

        except:
            pass

    await message.answer(
        f"✅ Xabar yuborildi.\n\n"
        f"👤 Yuborilgan odamlar: {success}"
    )


# =========================
# USERLAR
# =========================

# @router.message(
#     (F.text == "👥 Userlar")
# )
@router.message(F.text == "👥 Userlar")
async def users_start(
    message: Message,
    state: FSMContext
):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "📌 Qaysi raqamdan boshlansin?\n\n"
        "Masalan: 1"
    )

    await state.set_state(
        UserListState.waiting_start
    )   
@router.message(UserListState.waiting_start)
async def users_start_number(
    message: Message,
    state: FSMContext
):

    try:

        start_num = int(message.text)

        await state.update_data(
            start_num=start_num
        )

        await message.answer(
            "📌 Qaysi raqamgacha?\n\n"
            "Yoki:\n"
            "theend"
        )

        await state.set_state(
            UserListState.waiting_end
        )

    except:

        await message.answer(
            "❌ Faqat son kiriting."
        )
# =========================
# ADMIN MENU
# =========================

@router.message(F.text.lower() == "menu")
async def admin_menu(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[

            [
                KeyboardButton(text="🎬 Kino qo'shish"),
                KeyboardButton(text="📋 Ro'yhat")
            ],

            [
                KeyboardButton(text="👥 Userlar"),
                KeyboardButton(text="📢 Xabar yuborish")
            ],

            [
                KeyboardButton(text="➕ Guruh qo'shish"),
                KeyboardButton(text="🗑 Kino o'chirish")
            ],

            [
                KeyboardButton(text="📂 Guruhlar")
            ],

            [
                KeyboardButton(text="ℹ️ Admin panel ishlatish")
            ]

        ],
        resize_keyboard=True
    )

    await message.answer(
        "⚙ Admin panel",
        reply_markup=keyboard
    )


# =========================
# MENU TUGMALARI
# =========================

@router.message(F.text == "🎬 Kino qo'shish")
async def add_movie_info(message: Message):

    await message.answer(
        "🎬 Kino qo'shish uchun video yuboring."
    )


@router.message(F.text == "➕ Guruh qo'shish")
async def menu_group(message: Message, state: FSMContext):

    await add_group(message, state)


@router.message(F.text == "🗑 Kino o'chirish")
async def delete_info(message: Message):

    await message.answer(
        "❌ O'chirish uchun:\n\n"
        "delete 5"
    )


@router.message(F.text == "📢 Xabar yuborish")
async def send_info(message: Message):

    await message.answer(
        "📨 Yuborish uchun:\n\n"
        "send Salom hammaga"
    )


# =========================
# GURUHLAR
# =========================

@router.message(F.text == "📂 Guruhlar")
async def groups_menu(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    groups = load_groups()

    if not groups:

        await message.answer(
            "❌ Guruhlar yo'q."
        )
        return

    text = "📋 Guruhlar:\n\n"

    for i, group in enumerate(groups, start=1):

        text += (
            f"{i}. {group['name']}\n"
            f"🔗 {group['url']}\n\n"
        )

    text += (
        "🗑 O'chirish uchun:\n"
        "delgr 1"
    )

    await message.answer(text)


@router.message(F.text.startswith("delgr"))
async def delete_group(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    try:

        index = int(message.text.split()[1]) - 1

        groups = load_groups()

        if index < 0 or index >= len(groups):

            await message.answer(
                "❌ Guruh topilmadi."
            )
            return

        deleted_group = groups[index]["name"]

        groups.pop(index)

        save_groups(groups)

        await message.answer(
            f"✅ {deleted_group} o'chirildi."
        )

    except:

        await message.answer(
            "❌ Format noto'g'ri.\n\n"
            "Misol:\n"
            "delgr 1"
        )


# =========================
# QO'LLANMA
# =========================

@router.message(F.text == "ℹ️ Admin panel ishlatish")
async def admin_help(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    text = (
        "⚙ ADMIN PANEL QO'LLANMA\n\n"

        "🎬 Kino qo'shish:\n"
        "Video yuboring va bot savollariga javob bering.\n\n"

        "📋 Ro'yhat:\n"
        "Barcha kinolarni chiqaradi.\n\n"

        "👥 Userlar:\n"
        "Botdagi userlar ro'yhati.\n\n"

        "📢 Xabar yuborish:\n"
        "send salom\n\n"

        "➕ Guruh qo'shish:\n"
        "addgr\n\n"

        "📂 Guruhlar:\n"
        "Barcha guruhlar ro'yhati.\n\n"

        "🗑 Kino o'chirish:\n"
        "delete 5\n\n"

        "✏ Kino tahrirlash:\n"
        "edit 5 til rus\n\n"

        "🗑 Guruh o'chirish:\n"
        "delgr 1\n\n"

        "📊 Kino ko'rish soni:\n"
        "Ro'yhat ichida ko'rinadi."
    )

    await message.answer(text)

@router.message(UserListState.waiting_end)
async def users_end_number(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    start_num = data["start_num"]

    users = load_users()

    users_list = list(users)

    # theend yozsa
    if message.text.lower() == "theend":

        end_num = len(users_list)

    else:

        try:
            end_num = int(message.text)

        except:

            await message.answer(
                "❌ Son yoki theend yozing."
            )
            return

    text = ""

    for i in range(start_num - 1, min(end_num, len(users_list))):

        user = users_list[i]

        text += (
            f"{i+1}. {user['name']}\n"
            f"🆔 {user['id']}\n\n"
        )

    if not text:

        text = "❌ User topilmadi."

    # Telegram limitidan o'tmasin
    for x in range(0, len(text), 4000):

        await message.answer(
            text[x:x+4000]
        )

    await state.clear()