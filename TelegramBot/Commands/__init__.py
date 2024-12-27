from .Start import router
from .Admin import router
from .CodeHelper import router
from .SolvePhotoProblem import router
from .ChartHelper import router
from .AbstractHelper import router
from .CourseWorkHelper import router
from .Tasks import Tasks
from .DefaultMode import router
from .Middlewares import SubscriptionMiddleware, CaptchaMiddleWare
__all__ = ["router"]

