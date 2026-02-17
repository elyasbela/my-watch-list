from django.urls import path
from . import views
urlpatterns = [
	path('', views.index, name="list"),
	path('update_task/<str:pk>/', views.updateTask, name="update_task"),
	path('delete_task/<str:pk>/', views.deleteTask, name="delete"),
	path('add_netflix/', views.addNetflixSeries, name="add_netflix"),
	path('add_amazon/', views.addAmazonSeries, name="add_amazon"),
	path('add_appletv/', views.addAppleTVSeries, name="add_appletv"),
	path('clear/', views.clearWatchlist, name="clear_watchlist"),
]