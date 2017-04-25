
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

#**************************** Cache file set up *******************************
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

#***************************** OMDB function set up ***************************

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
#Also adding the official twitter handle of each movie
logan_dict = data_list[0]
logan_dict["twitter_handle"] = "WolverineMovie" 
split_dict = data_list[2]
split_dict["twitter_handle"] = "splitmovie"
get_out_dict = data_list[1]
get_out_dict["twitter_handle"] = "GetOutMovie"

movie_dicts = [logan_dict, split_dict, get_out_dict]

#************************* Constructing Movie Class ****************************

#define a class movie that has at least 3 instance variable and 2 methods
#info needed for each movie: title, director, imdb score, top actor, twitter handle.
class Movie(object):
	def __init__(self, title, director, imdb, actor, twitter):
		self.title = title
		self.director = director
		self.imdb = imdb
		self.top_actor = actor
		self.twitter = twitter
	def get_users(self): #gets user info for each movie
		if self.twitter in CACHE_DICTION:
			self.user = CACHE_DICTION[self.twitter]
		else:
			user = api.get_user(self.twitter)
			self.user = user
			CACHE_DICTION[self.twitter] = self.user
			f = open(CACHE_FNAME, 'w')
			f.write(json.dumps(CACHE_DICTION))
			f.close()
		return self.user
	def get_user_timeline(self): #get the most recent tweet on the user's profile
		unique_identifier = "timeline_{}".format(self.twitter)
		if unique_identifier in CACHE_DICTION:
			self.timeline = CACHE_DICTION[unique_identifier]
		else:
			timeline = api.user_timeline(self.twitter)
			self.timeline = timeline
			CACHE_DICTION[unique_identifier] = self.timeline
			f = open(CACHE_FNAME, 'w')
			f.write(json.dumps(CACHE_DICTION))
			f.close()
		return self.timeline[:1]


logan = Movie(logan_dict['Title'], logan_dict['Director'], logan_dict['imdbRating'], logan_dict['Actors'].split()[0] + " " + logan_dict['Actors'].split()[1].replace(",",''), logan_dict["twitter_handle"])
split = Movie(split_dict['Title'], split_dict['Director'], split_dict['imdbRating'], split_dict['Actors'].split()[0] + " " + split_dict['Actors'].split()[1].replace(",",''), split_dict["twitter_handle"])
get_out = Movie(get_out_dict['Title'], get_out_dict['Director'], get_out_dict['imdbRating'], get_out_dict['Actors'].split()[0] + " " + get_out_dict['Actors'].split()[1].replace(",",''), get_out_dict["twitter_handle"])

movie_class_instances = [logan, split, get_out]

movie_twitters_list = [] #list of dictionaries of each movie's twitter info
for x in movie_class_instances:
	users = x.get_users()
	movie_twitters_list.append(users)

#************************ Setting up the databases *****************************
conn = sqlite3.connect("206_final_project.db")
cur = conn.cursor()

#Creating Movies database
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

statement_mov = "INSERT INTO Movies VALUES (?, ?, ?, ?, ?, ?)"
for mov in mov_db_lst:
	cur.execute(statement_mov, mov)


#Creating Users database
cur.execute('DROP TABLE IF EXISTS Users')
table_users = "CREATE TABLE IF NOT EXISTS Users (user_id TEXT PRIMARY KEY, screen_name TEXT, followers INT, num_favs INT)"
cur.execute(table_users)

user_db_lst = []
for x in movie_twitters_list:
	user_id = x['id_str']
	screen_name = x['screen_name']
	followers = x['followers_count']
	num_favs = x['favourites_count']
	db = (user_id, screen_name, followers, num_favs)
	user_db_lst.append(db)

statement_user = "INSERT INTO Users VALUES (?, ?, ?, ?)"
for user in user_db_lst:
	cur.execute(statement_user, user)

movie_timeline_list=[]
for x in movie_class_instances:
	tweets = x.get_user_timeline()
	movie_timeline_list.append(tweets)


# Creating Tweets database
cur.execute('DROP TABLE IF EXISTS Tweets')
table_tweets = "CREATE TABLE IF NOT EXISTS Tweets (tweet_id TEXT PRIMARY KEY, text TEXT, user_id TEXT, movie_title TEXT, num_favs INT, num_rts INT)"
cur.execute(table_tweets)

tweet_db_lst =[]
for x in movie_timeline_list:
	tweet_id = x[0]['id_str']
	text = x[0]['text']
	user_id = x[0]['user']['id_str']
	movie_search = x[0]['user']['name']
	num_favs = x[0]["favorite_count"]
	num_rts = x[0]["retweet_count"]
	db = (tweet_id, text, user_id, movie_search, num_favs, num_rts)
	tweet_db_lst.append(db)

statement_tweet = "INSERT INTO Tweets VALUES (?, ?, ?, ?, ?, ?)"
for tweet in tweet_db_lst:
	cur.execute(statement_tweet, tweet)


conn.commit()
# conn.close()

#******************** Database Queries and Data Processing *****************************
#Make a query to the data base to get the top billed actor for each of the three movies
cur.execute("SELECT top_billed FROM Movies")
top_billed_actors = [x[0] for x in cur.fetchall()] #using list comprehension to clean up database queries


cur.execute("SELECT Tweets.num_favs, Users.followers FROM Tweets INNER JOIN Users ON Users.user_id = Tweets.user_id")
favs_tup_list = cur.fetchall()
favs_ratio_list = []

cur.execute("SELECT screen_name FROM Users")
screen_name_list = [x[0] for x in cur.fetchall()]


cur.execute("SELECT title from Movies")
titles = [x[0] for x in cur.fetchall()]


cur.execute("SELECT text from Tweets")
tweet_text = [x[0] for x in cur.fetchall()]

cur.execute("SELECT imdb From Movies")
imdb_scores = [x[0] for x in cur.fetchall()]
conn.close()

dog = 0
score_dict = {}
for x in titles:
	score_dict[x] = imdb_scores[dog]
	dog+= 1
#sorting with a key parameter to sort movies by imdb score
items = score_dict.items()
sorted_dict = sorted(items, key = lambda x: x[1], reverse = True)


cat = 0
followers_dict = {}
for x in titles:
	followers_dict[x] = favs_tup_list[cat][1]
	cat+= 1
items2 = followers_dict.items()
sorted_followers = sorted(items2, key = lambda x: x[1], reverse = True)
print (sorted_followers)

#*************************** Writing output file ****************************
content = "206 Final project output \n\nThis text file consists of information about three movies, the twitter accounts associated with those movies, and the most recent tweet of each movie's Twitter account.\n\n"
dog = 0
for x in movie_dicts:
	content+= "Movie #{}:".format(str(dog+1))
	content+= " " + titles[dog]
	content+=", starring actor "+top_billed_actors[dog]+"\n"
	content+="{} received an imdb score of ".format(titles[dog]) + str(imdb_scores[dog])+".\n"
	content+="The Movie's official twitter account " + "@"+screen_name_list[dog] + " has " + str(favs_tup_list[dog][1]) + " followers." +"\n"
	content+="The most recent tweet on this account reads: " +tweet_text[dog] + "\n"
	content+="This tweet received " + str(favs_tup_list[dog][0]) + " favorites." + "\n"
	content+="Followers to imdb score ratio: " + str(favs_tup_list[dog][1])+"/"+str(imdb_scores[dog])+" = "+ str(favs_tup_list[dog][1]/imdb_scores[dog])[:7]
	content+= "\n\n"
	dog += 1
content+="Miscellaneous info: " +'\n'
content+= "Movies sorted by imdb score: " + str(sorted_dict)+ "\n"
content+= "Movies sorted by number of followeres: " + str(sorted_followers)
f = open("final_output.txt", "w")
f.write(content)
f.close()



#**************************** Put your tests here ******************************
class Test_Functions(unittest.TestCase):
	def test_1(self): #testing the RequestUrl function returns a url string
		base_url = "http://www.omdbapi.com/?"
		params = omdb_params
		url = RequestUrl(base_url, params = omdb_params)
		self.assertEqual(type(url), type('hi'))
	def test_2(self): #testing that CACHE_DICTION is a dictionary
		self.assertEqual(type(CACHE_DICTION), type({}))
	def test_3(self): #testing that there is one dictionary for each movie
		self.assertEqual(len(movie_dicts), 3)
	def test_4(self): #testing that get_movie_info funtion returns a dictionary of data
		info = get_movie_info(base_url, omdb_params)
		self.assertEqual(type(info), type({}))

class Test_Class(unittest.TestCase):
	def test_5(self): #testing that get_users method returns the correct twitter handle
		handle = logan.get_users()
		self.assertEqual(handle["screen_name"], "WolverineMovie")
	def test_6(self): #testing that get_user_timeline method returns the correct screen name
		time = split.get_user_timeline()
		self.assertEqual(time[0]["user"]["name"], "Split")
	def test_7(self): #testing that get_user_timeline method returns only one status
		timeline = split.get_user_timeline()
		self.assertEqual(len(timeline), 1)
		
class Test_db(unittest.TestCase):
	def test_8(self): #testing that the Movies database has data in it
		conn = sqlite3.connect('206_final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Movies')
		num = cur.fetchall()
		self.assertEqual(len(num) > 0, True)
	def test_9(self): #testing that the Movies database has movie titles in the correct place
		conn = sqlite3.connect('206_final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT title FROM Movies')
		title = cur.fetchall()
		self.assertTrue("Logan" in title[0])

# # Remember to invoke your tests so they will run! (Recommend using the verbosity=2 argument.)

if __name__ == "__main__":
	unittest.main(verbosity=2)