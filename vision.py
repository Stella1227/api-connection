from flask import Flask, request, jsonify
import requests
import time
import os

class VisionService:
    def __init__(self, server_ip='192.168.0.123', server_port=5003, vision_host='0.0.0.0', vision_port=5002):
        self.app = Flask(__name__)
        self.SERVER_ENDPOINT = f"http://{server_ip}:{server_port}"
        self.vision_host = vision_host
        self.vision_port = vision_port

        self._setup_routes()
    
    def _setup_routes(self):
        self.app.route('/')(self.home)
        self.app.route('/check_product', methods=['POST'])(self.check_product)
        self.app.route('/vision_connect', methods=['POST'])(self.vision_connect)
        self.app.route('/vision_shutdown', methods=['POST'])(self.vision_shutdown)
    
    def home(self):
        return jsonify({"message": "Vision connected"}), 400
    
    def check_product(self):
        data = request.json
        state = data.get("state")
        if not state:
            return jsonify({"error": "No state provided"}), 400
        product = self.check()

        try:
            response = requests.post(f"{self.SERVER_ENDPOINT}/product_supply", json={"product":product}, timeout = 10)
            response.raise_for_status()
            return jsonify(response.json())
        except requests.RequestException as e:
            return jsonify({"error": f"check_product error: {str(e)}"}), 500
    
    def vision_connect(self):
        print("vision connected")
        data = request.json
        state = data.get("state")
        if not state:
            return jsonify({"error": "No state provided"}), 400

        try:
            response = requests.post(f"{self.SERVER_ENDPOINT}/vision_connect_reply", json={"vision_state":"Vision connected"}, timeout = 10)
            response.raise_for_status()
            return jsonify(response.json())
        except requests.RequestException as e:
            return jsonify({"error": f"check_product error: {str(e)}"}), 500
    
    def check(self):
        print("checking product...")
        time.sleep(2)
        product = "snack"
        return product
    
    def run(self):
        print("vision service start")
        self.app.run(host=self.vision_host, port = self.vision_port, debug=True)
    
    def vision_shutdown(self):
        print("Shutting down the vision service...")
        data = request.json
        state = data.get("state")
        if not state:
            return jsonify({"error": "No state provided"}), 400
        os._exit(0)


if __name__ == '__main__':
    VisionService().run()
