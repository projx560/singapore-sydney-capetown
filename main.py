from flask import Flask, request, jsonify
import requests
import socket
import asyncio
import json
import datetime

app = Flask(__name__)

def map_tcp_udp_error(error):
    if error.errno == socket.errno.ECONNREFUSED:
        return 'REFUSED'
    elif error.errno == socket.errno.ETIMEDOUT:
        return 'TIMED OUT'
    elif error.errno == socket.errno.EHOSTUNREACH:
        return 'HOST IS UNREACHABLE'
    elif error.errno == socket.errno.ENOTFOUND:
        return 'HOST NOT FOUND'
    elif error.errno == socket.errno.ECONNRESET:
        return 'RESET BY PEER'
    else:
        return f'Unknown error occurred: {error.strerror}'

@app.route('/http', methods=['GET'])
def http_check():
    url = request.args.get('url')
    if not url:
        return jsonify({
            'status': 'failure',
            'error': 'Missing required parameter: url',
            'dateChecked': datetime.datetime.now().isoformat()
        })

    if not url.startswith(('http://', 'https://')):
        host, port = (url.split(':') + [80])[:2]
        protocol = 'https' if port == '443' else 'http'
        formatted_url = f'{protocol}://{host}:{port}'
    else:
        formatted_url = url

    start = datetime.datetime.now()

    try:
        response = requests.get(formatted_url)
        response_time = (datetime.datetime.now() - start).total_seconds() * 1000
        status = 'success' if response.status_code < 400 else 'failure'
        return jsonify({
            'status': status,
            'url': formatted_url,
            'responseCode': response.status_code,
            'responseStatus': response.reason,
            'title': response.text.split('<title>')[1].split('</title>')[0] if '<title>' in response.text else 'No Title',
            'responseTime': f'{response_time:.2f}ms',
            'dateChecked': datetime.datetime.now().isoformat()
        })
    except requests.RequestException as e:
        return jsonify({
            'status': 'failure',
            'url': formatted_url,
            'error': f'{e.response.status_code if e.response else 500} - {e.response.reason if e.response else "Unknown Error"}',
            'dateChecked': datetime.datetime.now().isoformat()
        })

@app.route('/tcp', methods=['GET'])
def tcp_check():
    host = request.args.get('host')
    port = request.args.get('port', 80)
    if not host:
        return jsonify({
            'status': 'failure',
            'error': 'Missing required parameter: host',
            'dateChecked': datetime.datetime.now().isoformat()
        })

    try:
        with socket.create_connection((host, int(port)), timeout=5):
            return jsonify({
                'status': 'success',
                'host': host,
                'port': port,
                'message': f'Connection to {host}:{port} successful',
                'dateChecked': datetime.datetime.now().isoformat()
            })
    except socket.error as e:
        return jsonify({
            'status': 'failure',
            'host': host,
            'port': port,
            'error': map_tcp_udp_error(e),
            'dateChecked': datetime.datetime.now().isoformat()
        })
    except socket.timeout:
        return jsonify({
            'status': 'failure',
            'host': host,
            'port': port,
            'error': 'TIMED OUT',
            'dateChecked': datetime.datetime.now().isoformat()
        })

@app.route('/udp', methods=['GET'])
def udp_check():
    host = request.args.get('host')
    port = request.args.get('port', 80)
    if not host:
        return jsonify({
            'status': 'failure',
            'error': 'Missing required parameter: host',
            'dateChecked': datetime.datetime.now().isoformat()
        })

    message = b'ping'

    async def send_udp_message():
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, lambda: socket.socket(socket.AF_INET, socket.SOCK_DGRAM).sendto(message, (host, int(port))))
            return {
                'status': 'success',
                'host': host,
                'port': port,
                'message': f'UDP message sent to {host}:{port} successfully',
                'dateChecked': datetime.datetime.now().isoformat()
            }
        except socket.error as e:
            return {
                'status': 'failure',
                'host': host,
                'port': port,
                'error': map_tcp_udp_error(e),
                'dateChecked': datetime.datetime.now().isoformat()
            }

    result = asyncio.run(send_udp_message())
    return jsonify(result)

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({
        'status': 'failure',
        'error': str(e),
        'dateChecked': datetime.datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

    