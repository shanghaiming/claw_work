from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.overview, name='overview'),
    path('strategies/', views.strategy_list, name='strategy_list'),
    path('strategies/<str:strategy_name>/', views.strategy_detail, name='strategy_detail'),
    path('backtest/', views.backtest_page, name='backtest_page'),
    path('backtest/run/', views.run_backtest, name='run_backtest'),
    path('stock-selection/', views.stock_selection, name='stock_selection'),
    path('api/stocks/', views.api_stock_list, name='api_stock_list'),
    path('api/strategies/', views.api_strategy_list, name='api_strategy_list'),
    path('api/stock-kline/', views.api_stock_kline, name='api_stock_kline'),
    path('api/stock-screen/', views.api_stock_screen, name='api_stock_screen'),
]
