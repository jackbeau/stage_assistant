import json
from multiprocessing import Process
import subprocess
import sys
from gui.app import App
from async_tkinter_loop import async_mainloop

def start_python_grpc_server(settings):
    subprocess.run([sys.executable, 'server/grpc/python/server.py', json.dumps(settings)])

def start_node_graphql_server():
    subprocess.run(['node', 'server/server.js'])

if __name__ == "__main__":
    # Load settings from settings.json
    with open('settings.json', 'r') as f:
        settings = json.load(f)

    # Start the Python gRPC server
    grpc_process = Process(target=start_python_grpc_server, args=(settings,))
    grpc_process.start()

    # Start the Node.js GraphQL server
    graphql_process = Process(target=start_node_graphql_server)
    graphql_process.start()

    # Start Tkinter UI
    app = App()
    async_mainloop(app)

    # If the app is closed, stop the servers
    grpc_process.terminate()
    graphql_process.terminate()
    quit()
