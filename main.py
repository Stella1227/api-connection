import threading
from flask import Flask, request, jsonify
import requests
from concurrent.futures import ThreadPoolExecutor
import time 
import os

class ServerService:
    def __init__(self, ui_ip='192.168.0.144', ui_port=5000, vision_ip='192.168.0.239', vision_port=5002, server_host='0.0.0.0', server_port=5003):
        
        self.app = Flask(__name__)
        
        # Configure endpoints for other services
        self.VISION_ENDPOINT = f"http://{vision_ip}:{vision_port}"
        self.UI_ENDPOINT = f"http://{ui_ip}:{ui_port}"
        
        self.server_host = server_host
        self.server_port = server_port

        self.coordinate_dict = {
            'bottle': (1, 2), 
            'shoes': (3, 4), 
            'snack': (5, 6), 
            'tissue paper': (7, 8),
            'stock' : (9, 10)
        }
        self._setup_routes()
    
    def home(self):
        print("server connected")
        try:
            response = requests.post(f"{self.VISION_ENDPOINT}/vision_connect", 
                                            json={"state": True}, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            return {"error": f"Vision error: {str(e)}"}
        try:
            response = requests.post(f"{self.UI_ENDPOINT}/UI_connect", 
                                            json={"state": True}, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            return {"error": f"UI error: {str(e)}"}
        return jsonify({"server_state": "Server connected"})

    def _setup_routes(self):
        print("Setting up routes...")
        self.app.route('/')(self.home)
        # self.app.route('/shutdown', methods=['POST'])(self.shutdown)
        self.app.route('/shutdown')(self.shutdown)
        self.app.route('/product', methods=['POST'])(self.product)
        self.app.route('/product_coordinate', methods=['POST'])(self.product_coordinate)
        self.app.route('/product_supply', methods=['POST'])(self.product_supply)
        self.app.route('/vision_connect_reply', methods=['POST'])(self.vision_connect_reply)
        self.app.route('/UI_connect_reply', methods=['POST'])(self.UI_connect_reply)
    
    def product(self):
        data = request.json
        product = data.get("product")
        print(f"input {product}")
        if not product:
            return jsonify({"error": "No product provided"}), 400
        try:
            response = requests.post(f"{self.UI_ENDPOINT}/input_product", 
                                     json={"product": product}, timeout=10)
            response.raise_for_status()
            return jsonify(response.json())
        except Exception as e:
            return jsonify({"error": f"Unknown error: {str(e)}"}), 500
    
    
    def product_supply(self):
        data = request.json
        product = data.get("product")
        if not product:
            return jsonify({"error": "No product supply provided"}), 400
        
        return jsonify({
                "received_product": product
            }), 200
    
    def vision_connect_reply(self):
        data = request.json
        state = data.get("vision_state")
        if not state:
            return jsonify({"error": "No state connected"}), 400
        
        return jsonify({
                "vision_state": state
            }), 200
    
    def UI_connect_reply(self):
        data = request.json
        state = data.get("UI_state")
        if not state:
            return jsonify({"error": "No state connected"}), 400
        
        return jsonify({
                "UI_state": state
            }), 200

    def product_coordinate(self):
        print("navigate process")
        data = request.json
        product = data.get("product")
        if not product:
            return jsonify({"error": "No product provided"}), 400
        
        state = self.navigating(product)

        def call_UI():
            print("call UI")
            try:
                response = requests.post(f"{self.UI_ENDPOINT}/navigate_success", 
                                         json={"state": state}, timeout=10)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"error": f"Navigation error: {str(e)}"}

        def call_vision():
            print("call vision")
            try:
                response = requests.post(f"{self.VISION_ENDPOINT}/check_product", 
                                         json={"state": state}, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                return {"error": f"Vision error: {str(e)}"}

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(call_UI): "UI",
                executor.submit(call_vision): "vision"
            }
            results = {}
            for future in futures:
                try:
                    results[futures[future]] = future.result()
                except Exception as e:
                    results[futures[future]] = {"error": f"Error occurred: {str(e)}"}

        return jsonify(results)

    def navigating(self, product):
        c = self.coordinate_dict[product]
        print(f"navigating to {str(c)}")
        time.sleep(5)
        return True

    def run(self):
        self.app.run(host=self.server_host, port=self.server_port, debug=True)
    
    def shutdown(self):
        print("Shutting down the server...")

        def shutdown_UI():       
            try:
                requests.post(f"{self.VISION_ENDPOINT}/vision_shutdown", 
                                            json={"state": True}, timeout=10)
            except Exception as e:
                return {"error": f"Vision shutdown error: {str(e)}"}
        def shutdown_vision():
            try:
                requests.post(f"{self.UI_ENDPOINT}/UI_shutdown", 
                                            json={"state": True}, timeout=10)
            except Exception as e:
                return {"error": f"UI shutdown error: {str(e)}"}
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(shutdown_UI): "UI",
                executor.submit(shutdown_vision): "vision"
            }
            results = {}
            for future in futures:
                try:
                    results[futures[future]] = future.result()
                except Exception as e:
                    results[futures[future]] = {"error": f"Error occurred: {str(e)}"}
        os._exit(0)


if __name__ == '__main__':
    ServerService().run()
