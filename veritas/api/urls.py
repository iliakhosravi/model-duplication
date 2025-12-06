from django.urls import path
from .views import evaluator_view

urlpatterns = [
    path('evaluator/', evaluator_view, name='evaluator'),
]
