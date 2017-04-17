###### INSTRUCTIONS ###### 

# An outline for preparing your final project assignment is in this file.

# Below, throughout this file, you should put comments that explain exactly what you should do for each step of your project. You should specify variable names and processes to use. For example, "Use dictionary accumulation with the list you just created to create a dictionary called tag_counts, where the keys represent tags on flickr photos and the values represent frequency of times those tags occur in the list."

# You can use second person ("You should...") or first person ("I will...") or whatever is comfortable for you, as long as you are clear about what should be done.

# Some parts of the code should already be filled in when you turn this in:
# - At least 1 function which gets and caches data from 1 of your data sources, and an invocation of each of those functions to show that they work 
# - Tests at the end of your file that accord with those instructions (will test that you completed those instructions correctly!)
# - Code that creates a database file and tables as your project plan explains, such that your program can be run over and over again without error and without duplicate rows in your tables.
# - At least enough code to load data into 1 of your dtabase tables (this should accord with your instructions/tests)

######### END INSTRUCTIONS #########

# Put all import statements you need here.
import requests
import json
import pprint
import unittest
import tweepy
import twitter_info
import sqlite3
import re
import itertools
import collections
from pprint import pprint
# Begin filling in instructions....

consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

CACHE_FNAME = '206_final_project_cache.json'
try:
	cache_file = open(CACHE_FNAME, 'r')
	cache_contents = cache_file.read()
	CACHE_DICTION = json.loads(cache_contents)
	cache_file.close()
except:
	CACHE_DICTION = {}

#Write a function to get data from omdb about three movies and save the data in a separate dictionary for each movie
base_url = "http://www.omdbapi.com/?"
omdb_params = {}
omdb_params['format'] = 'json'
omdb_params['type'] = 'movie'

#Three box office hits from 2017
move_titles = ["Logan", "Get Out", "Split"] 

#omdb requests
def RequestUrl(baseurl, params = {}):
	req = requests.Request(method = 'GET', url = base_url, params = omdb_params)
	prepped = req.prepare()
	return prepped.url
data_list = []

for mov in move_titles:
	omdb_params['t'] = str(mov)
	def get_movie_info(base_url, omdb_params):
		url = RequestUrl(base_url, omdb_params)
		if url in CACHE_DICTION:
			response_text = CACHE_DICTION[url] 
		else:
			response = requests.get(base_url, params = omdb_params)
			CACHE_DICTION[url] = response.text
			response_text = response.text
			f = open(CACHE_FNAME, 'w')
			f.write(json.dumps(CACHE_DICTION))
			f.close()
		response_dict = json.loads(response_text)
		return response_dict
	movie_data = get_movie_info(base_url, omdb_params)
	data_list.append(movie_data)

#dictionary of info for each move
logan_dict = data_list[0]
split_dict = data_list[2]
get_out_dict = data_list[1]

movie_dicts = [logan_dict, split_dict, get_out_dict]

#set up database file
conn = sqlite3.connect("206_final_project.db")
cur = conn.cursor()
#Movies
cur.execute('DROP TABLE IF EXISTS Movies')
table_mov = "CREATE TABLE IF NOT EXISTS Movies (movie_id TEXT PRIMARY KEY, title TEXT, director TEXT, imdb INT, top_billed TEXT, languages TEXT)"
cur.execute(table_mov)


mov_db_lst = []
for x in movie_dicts:
	movie_id = x['imdbID']
	title = x['Title']
	director = x['Director']
	imdb = x['imdbRating']
	actor = x['Actors'].split()[0] + " " + x['Actors'].split()[1].replace(",",'')
	languages = x['Language']
	db = (movie_id, title, director, imdb, actor, languages)
	mov_db_lst.append(db)

# print(mov_db_lst)
statement_mov = "INSERT INTO Movies VALUES (?, ?, ?, ?, ?, ?)"
for mov in mov_db_lst:
	cur.execute(statement_mov, mov)

#Tweets
cur.execute('DROP TABLE IF EXISTS Tweets')
table_tweets = "CREATE TABLE IF NOT EXISTS Tweets (tweet_id TEXT PRIMARY KEY, text TEXT, user_id TEXT, movie_title TEXT, num_favs INT, num_rts INT)"
cur.execute(table_tweets)

#Users
cur.execute('DROP TABLE IF EXISTS Users')
table_users = "CREATE TABLE IF NOT EXISTS Users (user_id TEXT PRIMARY KEY, screen_name TEXT, followers INT, num_favs)"
cur.execute(table_users)

conn.commit()
# conn.close()



# print("\n")
# pprint(logan_dict)

#define a class movie that ahs at least 3 instance variable and 2 methods
#info needed for each movie: title, director, imdb score, actors, languages, etc.
# class Movie(object):
# 	movies = [logan_dict, split_dict, get_out_dict]
# 	def __init__(self, title, director, imdb, actors):
# 		for x in movies:
# 			self.title = x['Title']
# 			self.director = x["Director"]
# 			self.imdb = x["imdb"]
# 			self.actors = x["actors"]
# 	def __str__(self):

#Make a query to the data base to get the top billed actor for each of the three movies
cur.execute("SELECT top_billed FROM Movies")
x = cur.fetchall()
top_billed_actors = []
for actor in x:
	a = str(actor)
	b = a.replace("(", "")
	c = b.replace(")", '')
	d = c.replace(",",'')
	e = d.replace("'", "")
	top_billed_actors.append(e)
# for x in top_billed_actors:
# 	print(x)

# Write function to get and cache data from twitter
timeline_list =[]

def get_actor_retweets(act):
	if act in CACHE_DICTION:
		print("CACHING \n")
		result = CACHE_DICTION[act]
	else:
		print("FETCHING... \n")
		result = api.user_timeline(act)
		CACHE_DICTION[act] = result
		f = open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()
	return result[:10]

accum = 0
for x in top_billed_actors:
	actor_timeline = get_actor_retweets(top_billed_actors[accum])
	timeline_list.append(actor_timeline)
	accum +=1

print(timeline_list)

# @RealHughJackman
# @JamsessionMB
# @KaluuyaDani

# for x in timeline:
# 	rts = x['retweet_count']
	


# print("\n\n\n\n")









# Put your tests here, with any edits you now need from when you turned them in with your project plan.
# class Test_Functions(unittest.TestCase):
# 	def test_1(self):
# 		tweet = get_tweet("Hello")
# 		self.assertEqual(type(tweet) = type([1,2,3]))
# 	def test_2(self):
# 		self.assertEqual(type(CACHE_DICTION), type({}))
# 	def test_3(self):
# 		movie = get_movie_info("Goodfellas")
# 		self.assertEqual(type(movie) = type({}))
# 	def test_4(self):
# 		num_mentions = get_mentions("Goodfellas")
# 		self.assertEqual(type(get_mentions) = type(12))

# class Test_Class(unittest.TestCase):
# 	def test_5(self):
# 		actors = Movie("Goodfellas")
# 		self.assertEqual(len(actors.names) > 0, True)
# 	def test_6(self):
# 		score = Movie("Goodfellas")
# 		self.assertEqual(score.imdb, 8.9)
# 	def test_7(self):
# 		dir = Movie("Goodfellas")
# 		self.assertEqual(dir.name, "Martin Scorcese")
		
# class Test_db(unittest.TestCase):
# 	def test_8(self):
# 		conn = sqlite3.connect('206_final_project.db')
# 		cur = conn.cursor()
# 		cur.execute('SELECT * FROM Tweets')
# 		num = cur.fetchall()
# 		self.assertEqual(len(num) > 0, True)

# Remember to invoke your tests so they will run! (Recommend using the verbosity=2 argument.)

# if __name__ == "__main__":
# 	unittest.main(verbosity=2)




