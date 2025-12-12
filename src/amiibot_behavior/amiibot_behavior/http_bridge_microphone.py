#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)
node_instance = None

class HttpBridgeNode(Node):
    def __init__(self):
        super().__init__('http_to_ros_bridge')
        self.angle_publisher = self.create_publisher(Float32, '/sensors/audio_angle', 10)
        self.get_logger().info('Nodo Bridge HTTP-ROS2 iniciado. Esperando datos...')

    def publish_angle(self, angle_value):
        msg = Float32()
        msg.data = float(angle_value) 
        self.angle_publisher.publish(msg)
        self.get_logger().info(f'Publicado en ROS2: {msg.data}')

@app.route('/sensors/audio_angle', methods=['POST'])
def handle_commands():
    global node_instance
    datos = request.json
    
    if node_instance:
        angle = datos.get('angle', 0.0)
        node_instance.publish_angle(angle)
        
        print(f"Recibido desde Windows: {datos}")
        return jsonify({"status": "received", "angle": angle})
    else:
        return jsonify({"status": "error", "message": "ROS Node not active"}), 500

def run_flask_app():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def main(args=None):
    global node_instance
    rclpy.init(args=args)
    
    node_instance = HttpBridgeNode()
    
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()

    try:
        rclpy.spin(node_instance)
    except KeyboardInterrupt:
        pass
    finally:
        node_instance.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()