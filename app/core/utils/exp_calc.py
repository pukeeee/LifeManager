from .config import TASK_BASE_EXP
from .config import HABIT_BASE_EXP


async def taskExpCalc(complexity):
    complexityR = await complexityRatio(complexity)
    
    taskExp = complexityR * TASK_BASE_EXP
    return taskExp



async def habitExpCalc(complexity, days):
    complexityR = await complexityRatio(complexity)
    
    habitExp = complexityR * HABIT_BASE_EXP * days
    return habitExp



async def complexityRatio(complexity):
    ratios = {
        "🟩": 1,
        "🟨": 1.5,
        "🟪": 2,
        "🟥": 2.5
    }
    return ratios.get(complexity, 1)