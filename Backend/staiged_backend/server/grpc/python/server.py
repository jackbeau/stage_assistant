from concurrent import futures
import grpc
import subprocess
import sys
import json
from multiprocessing import Process, Queue, Manager
import os
import time
from threading import Thread

# Adjust the import paths
import service_pb2
import service_pb2_grpc

# Ensure the module path is correctly set
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from mqtt_controller.mqtt_controller import MQTTController
# from speech_to_line import SpeechToLine

OUTPUT_DIR = 'server/storage/pdfs/'

class ScriptService(service_pb2_grpc.ScriptServiceServicer):

    def __init__(self, settings):
        self.process = None
        self.status_queue = Queue()
        self.settings = settings

        # Initialize statuses
        self.rpc_status = "Running"
        self.speech_to_line_status = "Stopped"

    def AddMargin(self, request, context):
        file_path = request.file_path
        margin_side = request.margin_side

        result = subprocess.run(
            [sys.executable, 'server/grpc/python/add_margin.py', file_path, margin_side, OUTPUT_DIR],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            context.set_details(result.stderr)
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.AddMarginResponse()

        response = json.loads(result.stdout)
        return service_pb2.AddMarginResponse(file_path=response['file_path'])

    def PerformOCR(self, request, context):
        file_path = request.file_path

        result = subprocess.run(
            [sys.executable, 'server/grpc/python/perform_ocr.py', file_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            context.set_details(result.stderr)
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.OCRResponse()

        response = json.loads(result.stdout)
        return service_pb2.OCRResponse(text=response['text'])

    def StartSpeechToLine(self, request, context):
        if self.process and self.process.is_alive():
            return service_pb2.StartResponse(success=False)

        self.process = Process(target=self.run_speech_to_line, args=(self.status_queue, self.settings))
        self.process.start()
        status = self.status_queue.get()  # Wait for acknowledgment
        self.speech_to_line_status = status
        return service_pb2.StartResponse(success=status == "Started")

    def StopSpeechToLine(self, request, context):
        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process.join()
            self.status_queue.put("Stopped")  # Ensure stopped status is put in the queue
            status = self.status_queue.get()  # Wait for acknowledgment
            self.speech_to_line_status = status
            return service_pb2.StopResponse(success=status == "Stopped")
        return service_pb2.StopResponse(success=False)

    def run_speech_to_line(self, status_queue, settings):
        try:
            mqtt_controller = MQTTController('0.0.0.0', 1883, 'speech_to_line')
            mqtt_controller.connect()
            # speech_to_line = SpeechToLine(mqtt_controller=mqtt_controller, status_queue=status_queue, settings=settings)
            # speech_to_line.start()
        except Exception as e:
            status_queue.put("failed")

    def GetStatuses(self, request, context):
        return service_pb2.StatusResponse(
            rpc_status=self.rpc_status,
            speech_to_line_status=self.speech_to_line_status
        )
    
def serve():
    settings = json.loads(sys.argv[1])
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_ScriptServiceServicer_to_server(ScriptService(settings), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('gRPC server running on port 50051...')
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
