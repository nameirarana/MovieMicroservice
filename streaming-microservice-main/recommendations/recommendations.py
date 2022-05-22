# recommendations/recommendations.py
from concurrent import futures
import random
import recommendations_pb2_grpc
import grpc
from recommendations_pb2 import (
  MovieCategory,
  MovieRecommendation,
  RecommendationResponse,
)
all_caterogies = [MovieCategory.MYSTERY, MovieCategory.COMEDY, MovieCategory.ACTION, MovieCategory.THRILLER, MovieCategory.SCIENCE_FICTION]

movies_by_category = {
  MovieCategory.MYSTERY: [
    MovieRecommendation(id=1, title="Enola Holmes"),
    MovieRecommendation(id=2, title="The Woman in the Window"),
    MovieRecommendation(id=3, title="The Vanished"),
  ],
  MovieCategory.SCIENCE_FICTION: [
    MovieRecommendation(id=4, title="Stowaway"),
    MovieRecommendation(id=5, title="Extinction"),
    MovieRecommendation(id=6, title="Bird Box"),
  ],
  MovieCategory.COMEDY: [
    MovieRecommendation(id=7, title="Dolittle"),
    MovieRecommendation(id=8, title="Extinct"),
    MovieRecommendation(id=9, title="Groundhog Day"),
  ],
  MovieCategory.THRILLER: [
    MovieRecommendation(id=10, title="Gerald’s Game"),
    MovieRecommendation(id=11, title="El Camino: A Breaking Bad Movie"),
    MovieRecommendation(id=12, title="Looper"),
  ],
  MovieCategory.ACTION: [
    MovieRecommendation(id=13, title="Extraction"),
    MovieRecommendation(id=14, title="The Hunger Games"),
    MovieRecommendation(id=15, title="Snowpiercer"),
  ],
  MovieCategory.ALL: [
  ]
}

class RecommendationService(
  recommendations_pb2_grpc.RecommendationsServicer):

  def Recommend(self, request, context):
    all_movies = []
    if request.category not in movies_by_category:
      context.abort(grpc.StatusCode.NOT_FOUND, "Category not found")
    if request.category == 5:
      for i in range(len(all_caterogies)):
        request.category = all_caterogies[i]
        movies_for_category = movies_by_category[request.category]
        num_results = min(request.max_results, len(movies_for_category))
        all_movies += random.sample(movies_for_category, num_results)
      movies_to_recommend = all_movies
    else:
      movies_for_category = movies_by_category[request.category]
      num_results = min(request.max_results, len(movies_for_category))
      movies_to_recommend = random.sample(movies_for_category, num_results)
    return RecommendationResponse(recommendations=movies_to_recommend)

def serve():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  recommendations_pb2_grpc.add_RecommendationsServicer_to_server(
    RecommendationService(), server
  )
  server.add_insecure_port("[::]:50051")
  server.start()
  server.wait_for_termination()

if __name__ == "__main__":
  serve()