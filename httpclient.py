#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode response appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, header = "", body=""):
        self.code = code
        self.header = header
        self.body = body

class HTTPClient(object):
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, response):
        return int(response.split()[1])

    def get_headers(self,response):
        return response.split('\r\n\r\n')[0]

    def get_body(self, response):
        return response.split('\r\n\r\n')[1]
    
    def sendall(self, response):
        self.socket.sendall(response.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')
    """
    Purpose: to properly format a http request
    Parameters: request_type (str) - the request type (GET/POST)
                url_parse (str) - the parsed inputted url
                parameters (str) - the arguments provided for a POST request
    Return: request (str) - the formatted http request
    References: https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages
    """
    def request_handler(self, request_type, url_parse, parameters = ""):
        path = '/'
        if (url_parse.path != ''):
            path = url_parse.path
        request = request_type
        request += path
        request += ' HTTP/1.1\r\n'
        request += 'Host: ' + url_parse.hostname + '\r\n'

        if request_type == "POST ":
            request += 'Content-Type: application/x-www-form-urlencoded\r\n'
            if (parameters != None):
                request += 'Content-Length: ' + str(len(parameters)) + '\r\n'
            else:
                request += 'Content-Length: 0\r\n'
        request += 'Connection: close\r\n\r\n'
        if (parameters != None):
            request += parameters
        return request
    
    """
    Purpose: sends a GET request to a server
    Parameters: url (str) - inputted url
                args (str) - None
    Return: HTTPResponse(code, header, body) - a class that stores the HTTP response
    References: https://docs.python.org/3/library/urllib.parse.html
    """
    def GET(self, url, args=None):
        code = 500
        body = ""
        port = 80

        url_parse = urllib.parse.urlparse(url)

        if (url_parse.port != None):
            port = url_parse.port

        self.connect(url_parse.hostname, port)

        self.sendall(self.request_handler("GET ", url_parse, parameters=None))
        response = self.recvall(self.socket)

        header = self.get_headers(response)
        code = self.get_code(response)
        body = self.get_body(response)

        print(code)
        print(header)
        print(body)

        self.close()
        return HTTPResponse(code, header, body)
    
    """
    Purpose: sends a POST request to a server
    Parameters: url (str) - inputted url
                args (str) - the arguments provided for a POST request
    Return: HTTPResponse(code, header, body) - a class that stores the HTTP response
    References: https://docs.python.org/3/library/urllib.parse.html
    """
    def POST(self, url, args=None):
        code = 500
        body = ""
        parameters = None

        if (args != None):
            parameters = urllib.parse.urlencode(args)

        url_parse = urllib.parse.urlparse(url)

        self.connect(url_parse.hostname, url_parse.port)

        self.sendall(self.request_handler("POST ", url_parse, parameters))
        response = self.recvall(self.socket)

        header = self.get_headers(response)
        code = self.get_code(response)
        body = self.get_body(response)

        print(code)
        print(header)
        print(body)
        
        self.close()
        return HTTPResponse(code, header, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
