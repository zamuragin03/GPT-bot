# BASE COMMANDS
from .Utils import router
from .Start import router
from .PaymentProcess import router
from .Admin import admin_router

# TASKS
from .Tasks import Tasks

# MIDDLEWARES
from .Middlewares import SubscriptionMiddleware, CaptchaMiddleWare, GPTSubscriptionMiddleware,BannedMiddleware, AdminMiddleware

# GPT ROUTERS
from .CodeHelper import gpt_router
from .SolvePhotoProblem import gpt_router
from .ChartHelper import gpt_router
from .AbstractHelper import gpt_router
from .CourseWorkHelper import gpt_router
from .RewritingHelper import gpt_router
from .EssayHelper import gpt_router

# PPTX API Router
from .PPTXHelper import gpt_router

# DEFAULT MODE (должен обрабатывать запросы в самом конце)
from .DefaultMode import gpt_free_router

