from collections import defaultdict
from concurrent import futures

import random
from turtle import title


import grpc

from movie_list_pb2 import (
    Movie,
    BoolValue,
    ListItem,
    MovieListResponse
)


import movie_list_pb2_grpc
import csv

list_file = open("lists.csv", "r")

csvreader = csv.reader(list_file)
list_by_user_id = defaultdict(list)
for row in csvreader:
    print(row)
    if len(row) > 0:
        list_by_user_id[int(row[0])].append(Movie(id = int(row[1]), title = row[2]))
list_file.close()

print(list_by_user_id)
def save():
    list_file = open("lists.csv", "w")
    csvwriter = csv.writer(list_file)

    for user, movies in list_by_user_id.items():
        print(user, movies)
        for movie in movies:
            csvwriter.writerow([user, movie.id, movie.title])
    list_file.close()



class MovieListService(movie_list_pb2_grpc.ListServicer):

    def GetList(self, request, context):
        if request.user_id not in list_by_user_id:
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
        
        _movie_list = list_by_user_id[request.user_id]

        return MovieListResponse(movie_list = _movie_list)

    def AddToList(self, request, context):
        if len([i for i in list_by_user_id[request.user_id] if i.id == request.movie.id]) > 0:
            context.abort(grpc.StatustCode.ALREADY_EXISTS, "Movie Already Exists")
        
        list_by_user_id[request.user_id].append(Movie(id = request.movie.id, title = request.movie.title))
        save()
        return BoolValue(value = True)
    
    def RemoveFromList(self, request, context):
        if request.user_id not in list_by_user_id:
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
        if len([i for i in list_by_user_id[request.user_id] if i.id == request.movie.id]) <= 0:
            context.abort(grpc.StatustCode.NOT_FOUND, "Movie doesn't exist")

        for i, movie in enumerate(list_by_user_id[request.user_id]):
            if movie.id == request.movie.id:
                list_by_user_id[request.user_id].pop(i)
        save()
        return BoolValue(value = True)


def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    movie_list_pb2_grpc.add_ListServicer_to_server(

        MovieListService(), server

    )

    server.add_insecure_port("[::]:50052")

    server.start()

    server.wait_for_termination()



if __name__ == "__main__":

    serve()