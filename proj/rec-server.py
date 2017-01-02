#!/usr/bin/python

from neo4j.v1 import GraphDatabase, basic_auth
from collections import defaultdict
from flask import Flask, request, json, send_from_directory
import os

app = Flask(__name__)

# how many top-scoring recommendations we return
threshold = 10
neo4j_login = "neo4j"
neo4j_password = "buba123"


# get recommendations for a list of pairs in form of [["Band1", "Title1"], ["Band2", "Title2"], ...]
# returns a list of threshold recommendations in the same format
def get_recommendations(song_list):
  driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth(neo4j_login, neo4j_password))
  session = driver.session()

  similar = defaultdict(float)

  for song in song_list:
    query = "MATCH (a2:ARTIST)-[:PERFORMS]->(n2:SONG)-[w:SIMILAR_TO]-(n:SONG)<-[:PERFORMS]-(a:ARTIST)  where lower(n.title)=\"" + \
            song[1].lower() + "\" and lower(a.name)=\"" + song[
              0].lower() + "\" return n2.title AS title, a2.name AS name, w.weight as weight;"
    res = session.run(query)

    for r in res:
      similar[r["name"] + "\t" + r["title"]] += r["weight"]

  sorted_similar = sorted(similar.iteritems(), key=lambda (k, v): v, reverse=True)

  session.close()
  return map(lambda x: x[0].lower().split('\t'), sorted_similar[:threshold])


@app.route('/static/<path:filename>')
def front():
  root_dir = os.path.dirname(os.getcwd())
  return send_from_directory(os.path.join(root_dir, 'static'), filename)

@app.route('/', methods=['POST'])
def main():
  songs = request.form.items()  # data is empty
  print songs
  recs = get_recommendations(songs)
  response = {'recommendations': recs}
  return json.jsonify(**response)


if __name__ == "__main__":
  app.run()
