import socket
import os
# http://127.0.0.1:80 or 8080


def is_get_request(data):
    """
    :param data: what client sent
    :return: url: if client sent legal stuff-param, else empty
    """
    url = None
    line0 = data.split("\r\n")[0]
    params = line0.split(' ')

    if len(params) == 3 and params[0] == 'GET' and params[2] == "HTTP/1.1":
        url = params[1]
    return url


def build_ok_response(msg, content_type=None):
    """
    :param msg: msg to return on clients screen
    :param content_type: optional, if entered "/" to msg "text/html; charset=utf-8"
    :return: msg build in header ready to send to client
    """
    res = "HTTP/1.1 200 OK\r\n"
    if content_type:
        res += f"Content-Type: {content_type}\r\n"
    res += f"Content-Length: {len(msg)}\r\n"
    res += "\r\n"
    mesg2send = res.encode() + msg

    return mesg2send


def build_return_file(file, content_type=None):
    """
    :param file: file name
    :param content_type: optional, if entered / to msg "text/html; charset=utf-8"
    :return: msg to send back to client in header
    """
    if os.path.isfile(file):
        with open(file, 'rb') as f:
            file_data = f.read()
        mesg2send = build_ok_response(file_data, content_type)
    else:
        mesg2send = build_ok_response("404 Not Found".encode())
    return mesg2send


server_soc = socket.socket()
server_soc.bind(("0.0.0.0", 80))   # 8080
server_soc.listen(3)


while True:
    client_soc, addr = server_soc.accept()
    print(f"{addr[0]} - connected")

    while True:
        try:
            data = client_soc.recv(1024).decode()
        except Exception as e:
            print(f"error in receive {str(e)}")
            break

        url = is_get_request(data)
        if not url:
            break
        print(url)

        if url == "/":
            msg2send = build_return_file("index.html", "text/html; charset=utf-8")

        elif url[1:].lower() == "server" or url[1:].lower() == "favicon.ico":
            msg2send = build_return_file("Internal Server Error 500")

        else:
            msg2send = build_return_file(url[1:])
        if not os.path.isfile(url[1:]):
            try:
                client_soc.send(msg2send)
            except Exception as e:
                print(f"error in send {str(e)}")
                break
            break

        try:
            client_soc.send(msg2send)
        except Exception as e:
            print(f"error in send {str(e)}")
            break
        break

    client_soc.close()