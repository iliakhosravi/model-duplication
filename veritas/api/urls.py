from django.urls import path
from .views import evaluator_view, health_view

urlpatterns = [
    path('evaluator/', evaluator_view, name='evaluator'),
    path('health/', health_view, name='health'),
]
