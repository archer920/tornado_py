import csv

import requests
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
from requests_oauthlib import OAuth1

API_KEY = 'uu8qugbGwnJv8kKhkcwGcQVhR'
API_SECRET = 'LxkME4lwLvVdyktm1QzapcSvpche9o1bcV0syzAdiR2CFgqOMn'
TOKEN = '20014705-T4sSXbCBNUtx9eRHN5CdiEtSiDMO9os5iRqPcFHpa'
TOKEN_SECRET = '6fJGoD9zCWTa2pb39IhxXrgneKC70V5GMZubOEINaOSCa'


def read_tweets_file(path: str) -> list:
    tweets = []
    with open(path) as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            tweets.append(row)
    return tweets[1:]


def search_for_trend(trend: str) -> list:
    url = 'https://api.twitter.com/1.1/search/tweets.json?q=%{}'.format(trend)
    r = requests.get(url, auth=OAuth1(API_KEY, API_SECRET, TOKEN, TOKEN_SECRET))
    results = []
    for status in r.json()['statuses']:
        results.append((status['user']['name'], status['text']))
    return results


class RequestHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.tweets = read_tweets_file('tweets.csv')

    def data_received(self, chunk):
        pass

    def get(self):  # Code for responding to a request
        self.render('index.html', error=None, questions=self.tweets)

    def post(self):
        try:
            answers = self.parse_body_arguments()
            score = self.calc_score(answers)

            if score < .5:
                despot_tweets = search_for_trend('northkorea')
                despot_img = 'https://pbs.twimg.com/profile_images/3512389032/b6c46d92409175fe95a091a53293e264_400x400.jpeg'
            else:
                despot_tweets = search_for_trend('trump')
                despot_img = 'http://www.fullredneck.com/wp-content/uploads/2016/03/Funny-Donald-Trump-Jokes.jpg'

            self.render('score.html', score='{0:.2f}'.format(score), tweets=despot_tweets, image=despot_img)

        except tornado.web.MissingArgumentError:
            self.render('index.html', error='Please answer all questions', questions=self.tweets)

    def parse_body_arguments(self) -> list:
        answers = []
        for i in range(len(self.tweets)):
            answers.append(self.get_body_argument(str(i)))
        return answers

    def calc_score(self, answers: list) -> float:
        correct = 0
        for i in range(len(answers)):
            if answers[i] == self.tweets[i][3]:
                correct += 1
        return float(correct) / len(answers)


def start_web_server() -> None:
    PORT = 8080  # Port our application will listen to
    Application = tornado.web.Application([(r"/", RequestHandler)], debug=True)
    Application.listen(PORT)

    # Access the site using http://127.0.0.1:9999/
    # Not necessary onside Jupyter Notebook
    tornado.options.parse_command_line()
    tornado.ioloop.IOLoop.current().start()


start_web_server()
