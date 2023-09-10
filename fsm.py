from aiogram.dispatcher.filters.state import State, StatesGroup



# ____PARTNER____
class MakePartner(StatesGroup):
    choose_id = State()

class DelPartner(StatesGroup):
    choose_id = State()


# ____PAID__SUB____
class UpdatePaidSubForAll(StatesGroup):
    choose_period = State()

class UpdatePaidSubForOne(StatesGroup):
    choose_id = State()
    choose_period = State()



# ____FREE__SUB____
class UpdateFreeSubForOne(StatesGroup):
    choose_id = State()
    choose_period = State()

class GiveFreeSub(StatesGroup):
    choose_id = State()
    choose_period = State()


# ____PARTNER__THINGS____
class CheckRef(StatesGroup):
    choose_id = State()


# ____PUSH__THINGS____
class PushForSubed(StatesGroup):
    input_text = State()

    
