FROM python

RUN mkdir /service
COPY protobufs/ /service/protobufs/
COPY movie_list/ /service/movie_list/
WORKDIR /service/movie_list
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. \
           --grpc_python_out=. ../protobufs/movie_list.proto

EXPOSE 50052
ENTRYPOINT [ "python", "movie_list.py" ]