from flask import Flask, request, jsonify
import requests

class UIService:
    def __init__(self, server_ip='192.168.0.123', server_port=5003, 
                 ui_host='0.0.0.0', ui_port=5000):
        self.app = Flask(__name__)
        self.SERVER_ENDPOINT = f"http://{server_ip}:{server_port}"
        self.ui_host = ui_host
        self.ui_port = ui_port
        
        self._setup_routes()

    def _setup_routes(self):
        print("Setting up routes...")
        self.app.route('/')(self.home)
        self.app.route('/input_product', methods=['POST'])(self.input_product)
        self.app.route('/navigate_success', methods=['POST'])(self.navigate_success)
        self.app.route('/UI_connect', methods=['POST'])(self.UI_connect)
    
    def home(self):
        return jsonify({"message": "UI connected"})

    def input_product(self):
        print("Input product")
        data = request.json
        product = data.get("product")
        if not product:
            return jsonify({"error": "No product provided"}), 400
        try:
            response = requests.post(f"{self.SERVER_ENDPOINT}/product_coordinate", 
                                     json={"product": product}, timeout=10)
            response.raise_for_status()
            return jsonify(response.json())
        except Exception as e:
            return jsonify({"error": f"Unknown error: {str(e)}"}), 500
    
    def UI_connect(self):
        print("UI connected")
        data = request.json
        product = data.get("state")
        if not product:
            return jsonify({"error": "No state provided"}), 400
        try:
            response = requests.post(f"{self.SERVER_ENDPOINT}/UI_connect_reply", 
                                     json={"UI_state": "UI connected"}, timeout=10)
            response.raise_for_status()
            return jsonify(response.json())
        except Exception as e:
            return jsonify({"error": f"Unknown error: {str(e)}"}), 500

    def navigate_success(self):
        state = request.args.get("state")
        if not state:
            return jsonify({"error": "No state provided"}), 400

        try:
            self.show_window()
        
            return jsonify({
                "received_state": state
            }), 200
    
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error processing state: {str(e)}"}
            ), 500
    
    def show_window(self):
        print("Show pop out window")

    def run(self):
        print(f"UI Service start")
        self.app.run(host=self.ui_host, port=self.ui_port)

if __name__ == '__main__':
    UIService().run()
