import os
from flask import Flask, render_template, request, redirect, url_for
import grpc
import cgi
from recommendations_pb2 import MovieCategory, RecommendationRequest
from recommendations_pb2_grpc import RecommendationsStub
from movie_list_pb2 import Movie, ListItem, MovieListRequest
from movie_list_pb2_grpc import ListStub


app = Flask(__name__)
app.debug = True
recommendations_host = os.getenv("RECOMMENDATIONS_HOST", "localhost")
recommendations_channel = grpc.insecure_channel(f"{recommendations_host}:50051")
categories = ['Mystery','Science Fiction','Comedy','Thriller','Action']
recommendations_client = RecommendationsStub(recommendations_channel)

list_host = os.getenv("LIST_HOST", "localhost")
list_channel = grpc.insecure_channel(f"{list_host}:50052")
list_client = ListStub(list_channel)


@app.route("/")
def render_homepage():
  recommendations_request = RecommendationRequest(user_id=1, category=MovieCategory.ALL, max_results=20)
  recommendations_response = recommendations_client.Recommend(recommendations_request)
  return render_template("homepage.html", recommendations=recommendations_response.recommendations,)

@app.route('/dropdown', methods=['GET'])
def dropdown():
    return render_template('recommendations.html', categories = categories)

@app.route('/send_data', methods=['GET','POST'])
def send_data():
    if request.method == "POST":
        searchterm = request.form['categories']
        index = categories.index(searchterm)
        recommendations_request = RecommendationRequest(user_id=1, category=index, max_results=20)
        recommendations_response = recommendations_client.Recommend(recommendations_request)
        return render_template("show_recommendations.html", recommendations=recommendations_response.recommendations, )
    else:
        return render_template("recommendations.html")


@app.route("/list")
def render_list():
      movie_list_request = MovieListRequest(user_id=1)
      movie_list_response = list_client.GetList(movie_list_request)
      return render_template("list.html", movie_list=movie_list_response.movie_list,)

@app.route("/remove-from-list/<movieid>", methods=['GET', 'POST'])
def remove_from_list(movieid):
    list_client.RemoveFromList(ListItem(user_id = 1, movie = Movie(id = int(movieid))))
    return render_list()

@app.route("/add-to-list/<movieid>/<movietitle>", methods=['GET', 'POST'])
def add_to_list(movieid, movietitle):
    list_client.AddToList(ListItem(user_id = 1, movie = Movie(id = int(movieid), title = movietitle)))
    return render_list()

if __name__ == "__main__":
    app.run()