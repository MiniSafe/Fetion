#coding:utf-8
import socket
def send(text):
    port=8081
    host='127.0.0.1'
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.sendto(bytes(text),(host,port))
    s.close()
