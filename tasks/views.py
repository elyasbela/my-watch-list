import json
import urllib.request
import urllib.parse

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from .forms import *


# Create your views here.
def index(request):
	tasks = Task.objects.all()

	form = TaskForm()

	if request.method == 'POST':
		form = TaskForm(request.POST)
		if form.is_valid():
			#adds to the database if valid
			form.save()
		return redirect('/')

	context= {'tasks':tasks,'form':form}
	return render(request, 'tasks/list.html',context)

def updateTask(request,pk):
	task = Task.objects.get(id=pk)
	form = TaskForm(instance=task)

	if request.method == "POST":
		form = TaskForm(request.POST,instance=task)
		if form.is_valid():
			form.save()
			return redirect('/')


	context = {'form':form}
	return render(request, 'tasks/update_task.html',context)

def deleteTask(request,pk):
	item = Task.objects.get(id=pk)

	if request.method == "POST":
		item.delete()
		return redirect('/')

	context = {'item':item}
	return render(request, 'tasks/delete.html', context)


def _fetch_tmdb_page(provider_id, page):
	"""Récupère une page de résultats TMDB pour un fournisseur donné."""
	params = {
		'sort_by': 'vote_average.desc',
		'vote_count.gte': '200',
		'page': str(page),
		'language': 'fr-FR',
		'with_watch_providers': str(provider_id),
		'watch_region': 'FR',
	}
	url = 'https://api.themoviedb.org/3/discover/tv?' + urllib.parse.urlencode(params)
	req = urllib.request.Request(url, headers={
		'Authorization': f'Bearer {settings.TMDB_BEARER_TOKEN}',
		'Accept': 'application/json',
	})
	with urllib.request.urlopen(req) as response:
		data = json.loads(response.read())
	return data.get('results', []), data.get('total_pages', 1)


def _fetch_new_series(provider_id, count=10):
	"""Pagine l'API TMDB jusqu'à obtenir `count` séries absentes de la watchlist."""
	existing_tmdb_ids = set(
		Task.objects.filter(tmdb_id__isnull=False).values_list('tmdb_id', flat=True)
	)
	new_series = []
	page = 1

	while len(new_series) < count:
		results, total_pages = _fetch_tmdb_page(provider_id, page)
		if not results:
			break
		for s in results:
			if s['id'] not in existing_tmdb_ids:
				new_series.append(s)
				if len(new_series) >= count:
					break
		if page >= total_pages:
			break
		page += 1

	return new_series[:count]


def addNetflixSeries(request):
	if request.method == 'POST':
		series = _fetch_new_series(provider_id=8)
		for s in series:
			title = s.get('name', s.get('original_name', 'Série inconnue'))
			Task.objects.create(title=f"[Netflix] {title}", tmdb_id=s['id'])
	return redirect('/')


def addAmazonSeries(request):
	if request.method == 'POST':
		series = _fetch_new_series(provider_id=119)
		for s in series:
			title = s.get('name', s.get('original_name', 'Série inconnue'))
			Task.objects.create(title=f"[Amazon Prime] {title}", tmdb_id=s['id'])
	return redirect('/')


def addAppleTVSeries(request):
	if request.method == 'POST':
		series = _fetch_new_series(provider_id=350)
		for s in series:
			title = s.get('name', s.get('original_name', 'Série inconnue'))
			Task.objects.create(title=f"[Apple TV+] {title}", tmdb_id=s['id'])
	return redirect('/')


def clearWatchlist(request):
	if request.method == 'POST':
		Task.objects.all().delete()
	return redirect('/')