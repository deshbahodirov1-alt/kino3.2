from aiogram.fsm.state import State, StatesGroup


class AddMovie(StatesGroup):
    waiting_for_name = State()
    waiting_for_language = State()
    waiting_for_genre = State()

class AddGroup(StatesGroup):
    waiting_for_name = State()
    waiting_for_url = State()

class UserListState(StatesGroup):

    waiting_start = State()
    waiting_end = State()

class MovieInfoState(StatesGroup):

    waiting_movie_id = State()