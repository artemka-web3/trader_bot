from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class MakePartner(StatesGroup):
    CHOOSE_ID = State()

class ExtendSub(StatesGroup):
    CHOSE_MODE = State()
    # for one
    CHOOSE_ID = State()
    SET_EXTEND_TIME = State()
    # for multiple
    SET_DAYS = State()

class GiveFreeSub(StatesGroup):
    CHOOSE_USER = State()
    SET_TIME_FOR_SUB = State()
    
