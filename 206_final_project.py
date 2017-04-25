
# All import statements you needed.
import requests
import json
import unittest
import tweepy
import twitter_info
import sqlite3
import collections
from pprint import pprint

#Twitter info file set up
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

#Cache file set up
CACHE_FNAME = '206_final_project_cache.json'
try:
	cache_file = open(CACHE_FNAME, 'r')
	cache_contents = cache_file.read()
	CACHE_DICTION = json.loads(cache_contents)
	cache_file.close()
except:
	CACHE_DICTION = {}

#OMDB url paramers set up
base_url = "http://www.omdbapi.com/?"
omdb_params = {}
omdb_params['format'] = 'json'
omdb_params['type'] = 'movie'

#Three box office hits from 2017
move_titles = ["Logan", "Get Out", "Split"] 

#This function contrsucts a OMDB url for each movie
def RequestUrl(baseurl, params = {}):
	req = requests.Request(method = 'GET', url = base_url, params = omdb_params)
	prepped = req.prepare()
	return prepped.url
data_list = []

# This function gathers the OMDB data for each movie and appends it to data_list
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

#This takes all of the data gathered from OMDB and splits it up by movie
logan_dict = data_list[0]
split_dict = data_list[2]
get_out_dict = data_list[1]

movie_dicts = [logan_dict, split_dict, get_out_dict]

#setting up the databases
conn = sqlite3.connect("206_final_project.db")
cur = conn.cursor()

#Movies database
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

#Tweets database
cur.execute('DROP TABLE IF EXISTS Tweets')
table_tweets = "CREATE TABLE IF NOT EXISTS Tweets (tweet_id TEXT PRIMARY KEY, text TEXT, user_id TEXT, movie_title TEXT, num_favs INT, num_rts INT)"
cur.execute(table_tweets)

#Users database
cur.execute('DROP TABLE IF EXISTS Users')
table_users = "CREATE TABLE IF NOT EXISTS Users (user_id TEXT PRIMARY KEY, screen_name TEXT, followers INT, num_favs)"
cur.execute(table_users)

conn.commit()
# conn.close()

# print("\n")
# pprint(logan_dict)

#define a class movie that has at least 3 instance variable and 2 methods
#info needed for each movie: title, director, imdb score, actors, languages, etc.
class Movie(object):
	def __init__(self, title, director, imdb, actor):
		self.title = title
		self.director = director
		self.imdb = imdb
		self.top_actor = actor
	def get_num_followers(self):
		unique_identifier = "tweets_{}".format(self.top_actor)
		if unique_identifier in CACHE_DICTION:
			self.followers = CACHE_DICTION[unique_identifier]
		else:
			tweets = api.search(self.top_actor)
			self.followers = tweets["followers_count"]
			self.followers = CACHE_DICTION[unique_identifier]
			f = open(CACHE_FNAME, 'w')
			f.write(json.dumps(CACHE_DICTION))
			f.close()
		return self.followers_count

logan = (logan_dict['Title'], logan_dict['Director'], logan_dict['imdbRating'], logan_dict['Actors'].split()[0] + " " + logan_dict['Actors'].split()[1].replace(",",''))
split = (split_dict['Title'], split_dict['Director'], split_dict['imdbRating'], split_dict['Actors'].split()[0] + " " + split_dict['Actors'].split()[1].replace(",",''))
get_out = (get_out_dict['Title'], get_out_dict['Director'], get_out_dict['imdbRating'], get_out_dict['Actors'].split()[0] + " " + get_out_dict['Actors'].split()[1].replace(",",''))

movie_class_info = [logan, split, get_out]
for x in movie_class_info:
	invoke = Movie(x)
	followers = invoke.get_num_followers()




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


screen_names = ["@RealHughJackman", "@JamsessionMB", "@KaluuyaDani"]
# handle_dict = {}
# handle_dict[top_billed_actors[0]] = "@RealHughJackman"
# handle_dict[top_billed_actors[1]] = "@JamsessionMB"
# handle_dict[top_billed_actors[2]] = "@KaluuyaDani"
	
# Write function to get and cache data from twitter
# searches =[]
# def get_hugh_tweets(actor):
# 	if actor in CACHE_DICTION:
# 		print("CACHING \n")
# 		result = CACHE_DICTION[actor]
# 	else:
# 		print("FETCHING... \n")
# 		result = api.search("Hugh Jackman")
# 		CACHE_DICTION[actor] = result
# 		f = open(CACHE_FNAME, 'w')
# 		f.write(json.dumps(CACHE_DICTION))
# 		f.close()
# 	return result
# hugh = get_hugh_tweets("Hugh Jackman")

# def get_daniel_tweets(actor):
# 	if actor in CACHE_DICTION:
# 		print("CACHING \n")
# 		result = CACHE_DICTION[actor]
# 	else:
# 		print("FETCHING... \n")
# 		result = api.search("Daniel Kaluuya")
# 		CACHE_DICTION[actor] = result
# 		f = open(CACHE_FNAME, 'w')
# 		f.write(json.dumps(CACHE_DICTION))
# 		f.close()
# 	return result
# daniel = get_daniel_tweets("Daniel Kaluuya")

# def get_james_tweets(actor):
# 	if actor in CACHE_DICTION:
# 		print("CACHING \n")
# 		result = CACHE_DICTION[actor]
# 	else:
# 		print("FETCHING... \n")
# 		result = api.search("James McAvoy")
# 		CACHE_DICTION[actor] = result
# 		f = open(CACHE_FNAME, 'w')
# 		f.write(json.dumps(CACHE_DICTION))
# 		f.close()
# 	return result[:1]
# james = get_james_tweets("James McAvoy")
# pprint(james)





# Put your tests here, with any edits you now need from when you turned them in with your project plan.
class Test_Functions(unittest.TestCase):
	def test_1(self):
		base_url = "http://www.omdbapi.com/?"
		params = omdb_params
		url = RequestUrl(base_url, params = omdb_params)
		self.assertEqual(type(url), type('hi'))
	def test_2(self):
		self.assertEqual(type(CACHE_DICTION), type({}))
	def test_3(self):
		self.assertEqual(len(movie_dicts), 3)
	def test_4(self):
		info = get_movie_info(base_url, omdb_params)
		self.assertEqual(type(info), type({}))

# # class Test_Class(unittest.TestCase):
# # 	def test_5(self):
# # 		actors = Movie("Goodfellas")
# # 		self.assertEqual(len(actors.names) > 0, True)
# # 	def test_6(self):
# # 		score = Movie("Goodfellas")
# # 		self.assertEqual(score.imdb, 8.9)
# # 	def test_7(self):
# # 		dir = Movie("Goodfellas")
# # 		self.assertEqual(dir.name, "Martin Scorcese")
		
class Test_db(unittest.TestCase):
	def test_8(self):
		conn = sqlite3.connect('206_final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Movies')
		num = cur.fetchall()
		self.assertEqual(len(num) > 0, True)
	def test_9(self):
		conn = sqlite3.connect('206_final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT title FROM Movies')
		title = cur.fetchall()
		self.assertTrue("Logan" in title[0])

# # Remember to invoke your tests so they will run! (Recommend using the verbosity=2 argument.)

# if __name__ == "__main__":
# 	unittest.main(verbosity=2)