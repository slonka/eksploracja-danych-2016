#!/usr/bin/python

from neo4j.v1 import GraphDatabase, basic_auth
from collections import defaultdict
import re

#dummy list to get recommendations
input2 = [
["sheryl crow",   "every day is winding road"],
["everclear",   "santa monica"],
["sponge",   "speed racer"],
["bedlam steppenwolf",   "magic carpet ride"],
["oasis",   "champagne supernova"],
["violent femmes",   "waiting for bus"],
["starside",   "spacehog"],
["refreshements",   "banditos"],
["residents",   "mach"],
["red hot chili peppers",   "aeroplane"],

["gin blossoms",   "hey jealousy"],
["everclear",   "summerland"],
["everclear",   "i will buy you a new life"],
["blessid union of souls",   "i believe"],
["soul asylum",   "misery"],
["soul asylum",   "runaway train"],
["weezer",   "say it ain't so"],
["presidents of the united states of america",   "lump"],
["primitive radio gods;c. o'connor",   "standing outside a broken phone booth with money in my hand"],
["fuel",   "hemorrhage (in my hands)"]
]
	 

#how many top-scoring recommendations we return
threshold = 10
neo4j_login = "neo4j"
neo4j_password = "buba123"

# get artists present in both AoTM and MSD. there is about 12 000 of them. This method doesn't take collaborations into account
# return a dict mapping artist AoTM ID to their name in lowercase
def get_common_artists():
	artists = open("AoTM/artist.hash", "r").read().split('\n')[:-1]
	artists = map(lambda x: x.split('#'), artists)

	artist_dict = defaultdict(str)
	for line in artists:
	    id = line[1]
	    artist_dict[line[0]] = id
	    

	msd_artist = open("msd_artists.csv", "r").read().lower().split('\n')[:-1]

	in_both = []

	for artist in msd_artist:
	    if artist_dict[artist] != "":
	        in_both.append([artist, artist_dict[artist]])
	        

	artist_dict = defaultdict(str)
	for artist in in_both:
	    artist_dict[artist[1]] = artist[0]

	return artist_dict


# returns a dict mapping a song's AoTM ID to its title
def get_song_dict():
	songs = open("AoTM/song.hash", "r").read().split('\n')[:-1]
	songs = map(lambda x: x.split('#'), songs)

	song_dict = defaultdict(str)
	for song in songs:
	    id = song[2]
	    song_dict[id] = song[1]
	return song_dict


# returns a dict mapping an artist's AoTM ID to list of all names found for this ID
def get_artist_dict():
	artists = open("AoTM/artist.hash", "r").read().split('\n')[:-1]
	artists = map(lambda x: x.split('#'), artists)

	artist_dict = defaultdict(list)
	for line in artists:
	    id = line[1]
	    artist_dict[id].append(line[0])
	return artist_dict



# returns a list of playlists in string form, ready to be served to get_recommendations
# uses song_dict, artist_dict and common_artist to map IDs to string names
# first tries to find the artist in common_artists, then takes the first artist under given ID from artist_dict
# although we know this artist is not in MSD
def get_playlists(song_dict, artist_dict, common_artists):
	playlists = open("AoTM/aotm_list_ids.txt", "r").read().split('\n')[:-1]

	translated_playlists = []

	for line in playlists:
	    id = re.findall("#\d+#", line)
	    pairs = map(lambda x: x.split(": "), re.findall("\d+: \d+", line))
	    pairs = map(lambda x: translate_entry(x, song_dict, artist_dict, common_artists), pairs)
	    translated_playlists.append(pairs)

	return translated_playlists


def translate_entry(entry, song_dict, artist_dict, common_artists):
	if common_artists[entry[0]]!= "":
		#print "1",
		return [common_artists[entry[0]], song_dict[entry[1]]]
	else:
		#print "0",
		return [artist_dict[entry[0]][0], song_dict[entry[1]]]


# predict songs in the end of the playlist based on songs_used_to_predict first songs' recommendations
# returns the number of songs predicted sucessfully and the total number of songs in the end of the playlist
# prints is a boolean, if set to True the function prints the songs for insights
def predict_playlist(playlist, songs_used_to_predict, prints):
	if prints:
		print "\nFinding recommendations for songs:"
		for song in playlist[:songs_used_to_predict]:
			print song[0], " ", song[1]

	prediction = get_recommendations(playlist[:songs_used_to_predict])
	if prints:
		print "\nRecommendations found:"
		for song in prediction:
			print song[0], " ", song[1]

	rest = playlist[songs_used_to_predict:]
	if prints:
		print "\nRest of the playlist:"
		for song in rest:
			print song[0], " ", song[1]

	score = 0

	for real_song in rest:
		if real_song in prediction:
			score += 1

	return [score, len(playlist) - songs_used_to_predict]


# get recommendations for a list of pairs in form of [["Band1", "Title1"], ["Band2", "Title2"], ...]
# returns a list of threshold recommendations in the same format
def get_recommendations(song_list):
	driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth(neo4j_login, neo4j_password))
	session = driver.session()

	similar = defaultdict(float)

	for song in song_list:
		res = session.run("MATCH (a2:ARTIST)-[:PERFORMS]->(n2:SONG)-[w:SIMILAR_TO]-(n:SONG)<-[:PERFORMS]-(a:ARTIST)  where lower(n.title)=\"" + song[1] + 
				"\" and lower(a.name)=\"" + song[0] + "\" return n2.title AS title, a2.name AS name, w.weight as weight;")
		for r in res:
			similar[r["name"] + "\t" +  r["title"]] += r["weight"]
	
	
	sorted_similar = sorted(similar.iteritems(),key=lambda (k,v): v, reverse=True)


	session.close()
	return map(lambda x: x[0].lower().split('\t'), sorted_similar[:threshold])


if __name__ == "__main__":
	song_dict = get_song_dict()
	artist_dict = get_artist_dict()
	common_artists = get_common_artists()

	playlists = get_playlists(song_dict, artist_dict, common_artists)

	while True:
		no = int(raw_input("Please enter playlist number from 1 to 29164, Ctrl-C to exit"))
		playlist = playlists[no]
		print predict_playlist(playlist, int(len(playlist)/2), True)
