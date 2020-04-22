from math import pi
import urllib.request
import json
from collections import Counter
from datetime import datetime
import calendar
import requests
import bs4 as bs
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import column
from bokeh.palettes import Category20c
from bokeh.models import LabelSet, ColumnDataSource
from bokeh.transform import cumsum
from django.contrib import messages
from django.shortcuts import render, redirect


class CalculationLogic:
    """class to manage data from Git Servers"""

    def __init__(self):
        pass

    def get_data_from_url(self, request, url):
        """get data from given url and create plots"""
        try:
            source = urllib.request.urlopen(url).read()
            soup = bs.BeautifulSoup(source, 'lxml')
            if 'github' in url:
                descrp = [description.text for description in soup
                          .find_all('p', class_="commit-title")]

                author = [author.text for author in soup
                          .find_all('a', class_="commit-author")]

            elif 'gitlab' in url:
                descrp = [description.text for description in soup
                          .find_all('a',
                                    class_="commit-row-message item-title js-onboarding-commit-item"
                                    )]

                author = [author.text for author in soup
                          .find_all('a', class_="commit-author-link js-user-link")]

            elif 'bitbucket' in url:
                descrp = self.get_bitbucket_description(url)
                author = self.get_bitbucket_author(url)

            dict1 = dict(zip(descrp, author))
            dict2 = dict(Counter(dict1.values()))
            label = list(dict2.keys())
            value = list(dict2.values())
            dict2_keys = list(dict2.keys())
            values = list(dict2.values())


            percentages = []
            for val in values:
                percentages.append(val * 100 / sum(values))
            percentages_dictionary = dict(zip(dict2_keys, percentages))

            plot = figure(title='Github Effort', x_range=label, y_range=(0, 30),
                          plot_width=1000, plot_height=400)

            plot.vbar(x=label, top=value, width=0.9)

            data = pd.Series(dict2).reset_index(name='value')
            data['angle'] = data['value'] / data['value'].sum() * 2 * pi

            if len(dict2) == 1:
                data['color'] = '#44e5e2'
            elif len(dict2) == 2:
                data['color'] = ['#44e5e2', '#2d4a49']
            else:
                data['color'] = Category20c[len(percentages_dictionary)]

            plot_pie = figure(plot_height=500, plot_width=1000, title='Pie chart',
                              toolbar_location=None, x_range=(-0.5, 1.0))
            plot_pie.wedge(x=0, y=1, radius=0.35,
                           start_angle=cumsum('angle', include_zero=True),
                           end_angle=cumsum('angle'),
                           line_color="white",
                           fill_color='color',
                           legend_field='index',
                           source=data)

            data['value'] = data['value'].astype(str)
            data['value'] = data['value'].str.pad(35, side='left')
            source = ColumnDataSource(data)

            labels = LabelSet(x=0, y=1, text='value', angle=cumsum('angle', include_zero=True),
                              source=source, render_mode='canvas')
            plot_pie.add_layout(labels)
            script, div = components(column(plot, plot_pie))

            return render(request, 'bokeh.html', {'script': script, 'div': div, "url": url})

        except ValueError:
            messages.error(request, 'URL not found')

        return redirect('home')

    def show_days_of_the_week(self, request, url):
        """return number of commits in every day of the week as total"""
        source = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(source, 'lxml')
        if 'github' in url:
            days = [date.text for date in soup.find_all("relative-time", class_="no-wrap")]
            days_of_the_week = []
            for day in days:
                days_of_the_week.append(datetime.strptime(day, "%b %d, %Y").strftime("%A"))
            days = (Counter(days_of_the_week).most_common())
            days2 = dict(days)

        elif 'gitlab' in url:
            days = [date.text for date in soup.find_all('span', class_='day')]
            commits = [commit.text for commit in soup.find_all('span', class_='commits-count')]
            clean_commits = [commit.strip('commits') for commit in commits]

            total = dict(zip(days, clean_commits))
            days2 = dict(zip(calendar.day_name, [0] * 7))
            for date_str, value_str in total.items():
                days2[datetime.strptime(date_str, "%d %b, %Y").strftime("%A")] += int(value_str)

        elif 'bitbucket' in url:
            days_of_the_week = self.get_bitbucket_date(url)
            days = (Counter(days_of_the_week).most_common())
            days2 = dict(days)

        return render(request, 'days.html', {'data': days2})

    @staticmethod
    def extract_github_repository(author):
        """return all repositorys for each member of project from github"""
        author_list = list(set(author))
        user_repo_url = []
        repositorys = dict()
        for authors in author_list:
            user_repo_url.append('https://github.com/{}/?tab=repositories'.format(authors))
            for url in user_repo_url:
                source = urllib.request.urlopen(url).read()
                soup = bs.BeautifulSoup(source, 'lxml')
                repos = [repo.get_text(strip=True) for repo in soup
                         .find_all('h3', class_='wb-break-all')]
                repositorys[authors] = repos
        return repositorys

    @staticmethod
    def extract_gitlab_repository(author):
        """return all repositorys for each member of project from gitlab"""
        author_list = list(set(author))
        user_repo_url = []
        repositorys = dict()
        for authors in author_list:
            user_repo_url.append('https://gitlab.com/users/{}/projects.json'.format(authors))
            for url in user_repo_url:
                print(url)
                source = urllib.request.urlopen(url).read()
                soup = bs.BeautifulSoup(json.loads(source)['html'], 'lxml')
                repos = [repo.get_text(strip=True) for repo in soup
                         .find_all('span', class_='project-name')]
                repositorys[authors] = repos
        return repositorys

    @staticmethod
    def extract_bitbucket_repository(author):
        """return all repositorys for each member of project from bitbucket"""
        author_list = list(set(author))
        user_repo_url = []
        repositorys = dict()
        repos = []
        clean_repos = []
        for authors in author_list:
            user_repo_url.append(
                'https://bitbucket.org/!api/2.0/repositories/{}'
                '?page=1&pagelen=25&sort=-updated_on&q='
                .format(authors))
            for url in user_repo_url:
                req = requests.get(url).json()
                for i in range(0, len(req['values'])):
                    repos.append(repos.append(req['values'][i]['name']))
            for value in repos:
                if value is not None:
                    clean_repos.append(value)
            repositorys[authors] = clean_repos
        return repositorys

    def show_user_repo(self, request, url):
        """method called from view, invoke to specific methods"""
        source = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(source, 'lxml')
        if 'github' in url:
            website = 'github'
            author = [author.text for author in soup
                      .find_all('a', class_="commit-author")]
            repositorys = self.extract_github_repository(author)
        elif 'gitlab' in url:
            website = 'gitlab'
            author = [author.text for author in soup
                      .find_all('a', class_="commit-author-link js-user-link")]
            repositorys = self.extract_gitlab_repository(author)

        elif 'bitbucket' in url:
            website = 'bitbucket'
            fixed_url = url.strip('https://bitbucket.org/commits')
            valid_url = 'https://bitbucket.org/!api/internal/repositories/'\
                        + fixed_url + \
                        '/changesets?fields=%2B%2A.participants.approved%2C-%2A' \
                        '.participants.%2A&page=1&pagelen=25'
            req = requests.get(valid_url).json()
            author = []
            for i in range(0, len(req['values'])):
                author.append(req['values'][i]['author']['user']['nickname'])
            repositorys = self.extract_bitbucket_repository(author)

        return render(request, 'user_repos.html', {'repositorys': repositorys, 'website': website})

    @staticmethod
    def get_bitbucket_description(url):
        """additional method to get description from BitBucket API instead of WebScraping"""
        fixed_url = url.strip('https://bitbucket.org/commits')
        valid_url = 'https://bitbucket.org/!api/internal/repositories/'\
                    + fixed_url + \
                    '/changesets?fields=%2B%2A.participants.approved%2C-%2A' \
                    '.participants.%2A&page=1&pagelen=25'
        print(valid_url)
        req = requests.get(valid_url).json()
        data = []
        for i in range(0, len(req['values'])):
            data.append(req['values'][i]['message'].strip('\n'))

        print('DANE Z GET BITBUCKET DESCRIPTION: ', data)
        return data

    @staticmethod
    def get_bitbucket_author(url):
        """additional method to get author from BitBucket API instead of WebScraping"""
        fixed_url = url.strip('https://bitbucket.org/commits')
        valid_url = 'https://bitbucket.org/!api/internal/repositories/'\
                    + fixed_url + \
                    '/changesets?fields=%2B%2A.participants.approved%2C-%2A' \
                    '.participants.%2A&page=1&pagelen=25'
        req = requests.get(valid_url).json()
        data = []
        for i in range(0, len(req['values'])):
            data.append(req['values'][i]['author']['raw'])
        return data

    @staticmethod
    def get_bitbucket_date(url):
        """additional method to get date from BitBucket API instead of WebScraping"""
        fixed_url = url.strip('https://bitbucket.org/commits')
        valid_url = 'https://bitbucket.org/!api/internal/repositories/' \
                    + fixed_url + \
                    '/changesets?fields=%2B%2A.participants.approved%2C-%2A' \
                    '.participants.%2A&page=1&pagelen=25'
        req = requests.get(valid_url).json()
        data = []
        for i in range(0, len(req['values'])):
            data.append(req['values'][i]['date'])
        clean_data = []
        for date in data:
            clean_data.append(date[0:10])
        days_of_the_week = []
        for date in clean_data:
            days_of_the_week.append(datetime.strptime(date, "%Y-%m-%d").strftime("%A"))
        return days_of_the_week
