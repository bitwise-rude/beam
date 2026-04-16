#!/bin/python3

import sys, socket

# CONSTANTS ---
PORT = 8080
IP = "0.0.0.0"
CHUNK_SIZE = 999999

def process_arguments() -> bytes:
    if(len(sys.argv) < 2):
        print("Expected a video file to stream")
        sys.exit(1)

    with open(sys.argv[1], 'rb') as file:
        data = file.read()
    return  data

def create_connection() -> socket.socket:
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((IP,PORT))
    server.listen()

    c,a = server.accept()
    return c

video_data = process_arguments()
video_data_len = len(video_data)
with open("index.html",'r') as file:
    index_content = file.read()

while True:
    conn = create_connection()

    request = conn.recv(2048).decode()

    # first request
    if request.startswith("GET / HTTP/1.1"):
        print("GOT A BROWSER.. STARTING TO SEND..")
        response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length: {len(index_content)}\r\n\r\n{index_content}\r\n'

        conn.send(response.encode())
        conn.close()

    # request for the video (not the first but could be any)
    elif request.startswith("GET /sample.mp4"):
        range_start, range_end, *_ = request.split("Range: ")[1][6:].split("-")
        # if range_end == "\r\nConnection: keep": range_end = video_data_len 
        range_start = int(range_start)
        try:
            range_end = int(range_end)
        except ValueError:
            range_end = range_start + CHUNK_SIZE
            range_end = range_end+1 if range_end < video_data_len else video_data_len

        response = f'HTTP/1.1 206 Partial Content\r\nContent-Type: video/mp4\r\nAccept-Ranges: bytes\r\nContent-Range: bytes {range_start}-{range_end-1}/{video_data_len}\r\nContent-Length: {range_end-range_start}\r\n\r\n'.encode()
        try:
            response += video_data[range_start:range_end]
        except IndexError:
            response += video_data[range_start:]

        conn.send(response)
        conn.close()


    # print(request)

