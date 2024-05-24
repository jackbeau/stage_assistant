import logging
import time
import json
from paho.mqtt import client as mqtt_client
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes

logging.basicConfig(level=logging.INFO)

class MQTTController:
    def __init__(self, broker, port, client_id):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.subscriptions = {}

        self.client = mqtt_client.Client(client_id=self.client_id, reconnect_on_failure=True, protocol=mqtt_client.MQTTv5, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe

    def connect(self):
        properties = Properties(PacketTypes.CONNECT)
        properties.SessionExpiryInterval = 3600  # set session expiry interval
        while True:
            try:
                self.client.connect(self.broker, self.port, clean_start=False, properties=properties)
                logging.info("Connected to MQTT broker")
                for topic, callback in self.subscriptions.items():
                    self.client.subscribe(topic, qos=2)
                break  # Exit the loop if connection is successful
            except ConnectionRefusedError:
                logging.info("Connection refused. Retrying in 5 seconds...")
                time.sleep(5)
                continue  # Retry connection

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logging.info("Connected to MQTT broker")
            for topic, callback in self.subscriptions.items():
                self.client.subscribe(topic, qos=2)
        else:
            logging.info(f"Failed to connect, return code {rc}")

    def on_disconnect(self,client, userdata, disconnect_flags, reason_code, properties=None):
        logging.warning(f"Disconnected from MQTT broker with return code {rc}")

    def on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        logging.info(f"Subscribed with mid {mid}, granted QoS {granted_qos}")

    def publish(self, topic, message, retain=False):
        logging.info(f"Publishing {message} to {topic}")
        self.client.publish(topic, message, qos=0, retain=retain)

    def subscribe(self, topic, callback):
        self.client.subscribe(topic, qos=2)
        self.subscriptions[topic] = callback

    def unsubscribe(self, topic):
        self.client.unsubscribe(topic)
        if topic in self.subscriptions:
            del self.subscriptions[topic]

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        if topic in self.subscriptions:
            callback = self.subscriptions[topic]
            if callback:
                payload = msg.payload.decode()
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    pass
                callback(topic, payload)

    def disconnect(self):
        logging.info("Disconnecting from MQTT broker...")
        self.client.disconnect()

def main():
    broker = 'localhost'
    port = 1883
    client_id = "server"
    
    mqtt_controller = MQTTController(broker, port, client_id)
    mqtt_controller.connect()

    # Example subscribing to a topic with a callback
    def handle_message(topic, payload):
        print(f"Received `{payload}` from `{topic}` topic")
    mqtt_controller.subscribe("test", handle_message)

    # JSON message to be sent
    message = {
        'page_number': 35,
        'y_coordinate': 528,
        'matched_line': ' him',
        'input_line': ' mm-hmm.',
        'similarity': 80
    }

    # Start publishing messages every 500ms
    try:
        while True:
            mqtt_controller.publish("local_server/tracker/position", json.dumps(message))
            time.sleep(0.5)  # Sleep for 500ms
    except KeyboardInterrupt:
        logging.info("Stopping the MQTT publisher...")
    finally:
        mqtt_controller.disconnect()

if __name__ == '__main__':
    main()
