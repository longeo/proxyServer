# Proxy Server and Client

This Python program implements a simple proxy server that is capable of processing both
HTTP and HTTPS requests. The proxy can also block URLs and cache data. The program uses
the python socket library.

# HTTP Requests and multiple requests

A connection is established with the browser (conn) and the program waits to receive a
request. When data is received, the program creates a thread to handle the request
(proxy_thread). This allows it to deal with multiple requests at the same time. The proxy
checks that it is not a CONNECT request and then begins parsing the data to find the port
and webserver. If a port number cannot be found, the proxy uses 80 by default.
Next, a connection is established with the required webserver and port. The proxy forwards
the request onto the server and sends the data returned back to the browser.

# HTTPS REQUESTS

This proxy uses SSL tunnelling to handle secure requests. In the case where the proxy
detects that a CONNECT request has been sent, it sends a 200 OK confirmation back to the
browser. The program uses a separate parsing process for CONNECT requests. The proxy
then transfers encrypted data between the browser and the server. It is not capable of
altering this data.

# Cache

The program uses python dictionaries to cache information. The request is used as the key
and the data is the information stored. If the proxy finds that a request is stored in the
cache dictionary it simply returns the appropriate data.

# Block

After parsing, the proxy checks if the webserver address matches a url that is blocked. If so,
the proxy ends the process.
