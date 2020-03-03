from math import pi
import urllib.request
import requests
import json
import bs4 as bs
import pandas as pd
from bokeh.plotting import figure,output_file,show
from bokeh.embed import components
from bokeh.io import show,output_file
from bokeh.layouts import gridplot,row,column
from bokeh.palettes import Category20c
from bokeh.transform import cumsum
from collections import Counter
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from datetime import datetime
import calendar

class CalculationLogic:

    def __init__(self):
        pass

    def get_data_from_url(self,request,url):
        source = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(source,'lxml')
        if 'github' in url:
            descrp = [description.text for description in soup.find_all('p', class_="commit-title")]
            author = [author.text for author in soup.find_all('a', class_="commit-author")]
        elif 'gitlab' in url:
            descrp = [description.text for description in
                      soup.find_all('a', class_="commit-row-message item-title js-onboarding-commit-item")]
            author = [author.text for author in soup.find_all('a', class_="commit-author-link js-user-link")]
        elif 'bitbucket' in url:
            descrp = self.get_bitbucket_description(url)
            author = self.get_bitbucket_author(url)


        dict1 = dict(zip(descrp, author))
        dict2 = dict(Counter(dict1.values()))
        label = list(dict2.keys())
        value = list(dict2.values())
        etykiety = list(dict2.keys())
        wartosci = list(dict2.values())

        procenty = []
        for w in wartosci:
            procenty.append(w * 100 / sum(wartosci))
        slownik_procenty = dict(zip(etykiety, procenty))

        plot = figure(title='Github Effort', x_range=label, y_range=(0, 30), plot_width=1000, plot_height=400)

        plot.vbar(x=label,top=value,width=0.9)
        data = pd.Series(slownik_procenty).reset_index(name='value').rename(columns={'index': 'country'})
        data['angle'] = data['value'] / data['value'].sum() * 2 * pi

        if len(slownik_procenty) == 1:
            data['color'] = '#44e5e2'
        elif len(slownik_procenty) == 2:
            data['color'] = ['#44e5e2','#2d4a49']
        else:
            data['color'] = Category20c[len(slownik_procenty)]

        plot_pie = figure(plot_height=500,plot_width=1000, title='Pie chart', toolbar_location=None, tools='hover', x_range=(-0.5, 1.0))
        plot_pie.wedge(x=0, y=1, radius=0.35,
                       start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                       line_color="white", fill_color='color', legend_field='country', source=data)

        script, div = components(column(plot, plot_pie))

        return render(request, 'bokeh.html', {'script': script, 'div': div,"url":url})


    def show_days_of_the_week(self,request,url):
        source = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(source,'lxml')
        if 'github' in url:
            days = [date.text for date in soup.find_all("relative-time",class_="no-wrap")]
            days_of_the_week = []
            for d in days:
                days_of_the_week.append(datetime.strptime(d,"%b %d, %Y").strftime("%A"))
            days = (Counter(days_of_the_week).most_common())
            days2 = dict(days)

        elif 'gitlab' in url:
            days = [date.text for date in soup.find_all('span',class_='day')]
            commits = [commit.text for commit in soup.find_all('span',class_='commits-count')]
            clean_commits = [commit.strip('commits') for commit in commits]

            total = dict(zip(days,clean_commits))
            days2 = dict(zip(calendar.day_name,[0]*7))
            for date_str,value_str in total.items():
                days2[datetime.strptime(date_str,"%d %b, %Y").strftime("%A")] += int(value_str)



        elif 'bitbucket' in url:
            days_of_the_week = self.get_bitbucket_date(url)
            days = (Counter(days_of_the_week).most_common())
            days2 = dict(days)


        return render(request,'days.html',{'data': days2})


    def extract_github_repository(self,author):
        author_list = list(set(author))
        user_repo_url = []
        repositorys = dict()
        for a in author_list:
            user_repo_url.append('https://github.com/{}/?tab=repositories'.format(a))
            for url in user_repo_url:
                source = urllib.request.urlopen(url).read()
                soup = bs.BeautifulSoup(source, 'lxml')
                repos = [repo.get_text(strip=True) for repo in soup.find_all('div', class_='d-inline-block mb-1')]
                repositorys[a] = repos
        return repositorys

    def extract_gitlab_repository(self,author):
        author_list = list(set(author))
        user_repo_url = []
        repositorys = dict()
        for a in author_list:
            user_repo_url.append('https://gitlab.com/users/{}/projects.json'.format(a))
            for url in user_repo_url:
                print(url)
                source = urllib.request.urlopen(url).read()
                soup = bs.BeautifulSoup(json.loads(source)['html'], 'lxml')
                repos = [repo.get_text(strip=True) for repo in soup.find_all('span', class_='project-name')]
                repositorys[a] = repos
        return repositorys

    def extract_bitbucket_repository(self,author):
        author_list = list(set(author))
        user_repo_url = []
        repositorys = dict()
        repos = []
        clean_repos = []
        for a in author_list:
            user_repo_url.append('https://bitbucket.org/!api/2.0/repositories/{}?page=1&pagelen=25&sort=-updated_on&q='.format(a))
            for url in user_repo_url:
                r = requests.get(url).json()
                for i in range(0,len(r['values'])):
                    repos.append(repos.append(r['values'][i]['name']))
            for v in repos:
                if v != None:
                    clean_repos.append(v)
            repositorys[a] = clean_repos
        return repositorys

    def show_user_repo(self,request,url):
        source = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(source, 'lxml')
        if 'github' in url:
            website = 'github'
            author = [author.text for author in soup.find_all('a', class_="commit-author")]
            repositorys = self.extract_github_repository(author)
        elif 'gitlab' in url:
            website = 'gitlab'
            author = [author.text for author in soup.find_all('a', class_="commit-author-link js-user-link")]
            repositorys = self.extract_gitlab_repository(author)

        elif 'bitbucket' in url:
            website = 'bitbucket'
            fixed_url = url.strip('https://bitbucket.org/commits')
            valid_url = 'https://bitbucket.org/!api/internal/repositories/' + fixed_url + '/changesets?fields=%2B%2A.participants.approved%2C-%2A.participants.%2A&page=1&pagelen=25'
            r = requests.get(valid_url).json()
            author = []
            for i in range(0, len(r['values'])):
                author.append(r['values'][i]['author']['user']['nickname'])
            repositorys = self.extract_bitbucket_repository(author)

        return render(request,'user_repos.html',{'repositorys':repositorys,'website':website})


    def get_bitbucket_description(self,url):
        fixed_url = url.strip('https://bitbucket.org/commits')
        valid_url = 'https://bitbucket.org/!api/internal/repositories/' + fixed_url + '/changesets?fields=%2B%2A.participants.approved%2C-%2A.participants.%2A&page=1&pagelen=25'
        r = requests.get(valid_url).json()
        data = []
        for i in range(0,len(r['values'])):
            data.append(r['values'][i]['message'])
        return data

    def get_bitbucket_author(self,url):
        fixed_url = url.strip('https://bitbucket.org/commits')
        valid_url = 'https://bitbucket.org/!api/internal/repositories/' + fixed_url + '/changesets?fields=%2B%2A.participants.approved%2C-%2A.participants.%2A&page=1&pagelen=25'
        r = requests.get(valid_url).json()
        data = []
        for i in range(0,len(r['values'])):
            data.append(r['values'][i]['author']['raw'])
        return data

    def get_bitbucket_date(self,url):
        fixed_url = url.strip('https://bitbucket.org/commits')
        valid_url = 'https://bitbucket.org/!api/internal/repositories/' + fixed_url + '/changesets?fields=%2B%2A.participants.approved%2C-%2A.participants.%2A&page=1&pagelen=25'
        r = requests.get(valid_url).json()
        data = []
        for i in range(0,len(r['values'])):
            data.append(r['values'][i]['date'])
        clean_data = []
        for d in data:
            clean_data.append(d[0:10])
        days_of_the_week = []
        for c in clean_data:
            days_of_the_week.append(datetime.strptime(c, "%Y-%m-%d").strftime("%A"))
        return days_of_the_week
