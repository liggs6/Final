## Your name: Brian Liggio
## The option you've chosen:

# Put import statements you expect to need here!
import requests
import json
import pprint
import unittest
import tweepy
import twitter_info
import sqlite3
import re
from pprint import pprint

CACHE_FNAME = '206_final_project_cache.json'
try:
	cache_file = open(CACHE_FNAME, 'r')
	cache_contents = cache_file.read()
	CACHE_DICTION = json.loads(cache_contents)
	cache_file.close()
except:
	CACHE_DICTION = {}




# Write your test cases here.
class Test_Functions(unittest.TestCase):
	def test_1(self):
		tweet = get_tweet("Hello")
		self.assertEqual(type(tweet) = type([1,2,3]))
	def test_2(self):
		self.assertEqual(type(CACHE_DICTION), type({}))
	def test_3(self):
		movie = get_movie_info("Goodfellas")
		self.assertEqual(type(movie) = type({}))
	def test_4(self):
		num_mentions = get_mentions("Goodfellas")
		self.assertEqual(type(get_mentions) = type(12))

class Test_Class(unittest.TestCase):
	def test_5(self):
		actors = Movie("Goodfellas")
		self.assertEqual(len(actors.names) > 0, True)
	def test_6(self):
		score = Movie("Goodfellas")
		self.assertEqual(score.imdb, 8.9)
	def test_7(self):
		dir = Movie("Goodfellas")
		self.assertEqual(dir.name, "Martin Scorcese")
		
class Test_db(unittest.TestCase):
	def test_8(self):
		conn = sqlite3.connect('206_final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets')
		num = cur.fetchall()
		self.assertEqual(len(num) > 0, True)



## Remember to invoke all your tests...