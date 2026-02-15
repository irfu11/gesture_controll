import socketio
import time

sio = socketio.Client()

@sio.event
def connect():
    print('connected to server')
    # send one gesture
    sio.emit('gesture', 'pinch')

@sio.on('action')
def on_action(data):
    print('received action from server:', data)

@sio.event
def disconnect():
    print('disconnected from server')

if __name__ == '__main__':
    try:
        sio.connect('http://127.0.0.1:5000', wait=True)
        # give some time for messages
        time.sleep(1)
    except Exception as e:
        print('connection error:', e)
    finally:
        sio.disconnect()
