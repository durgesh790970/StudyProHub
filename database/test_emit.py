import socketio
s = socketio.Client()
print('connecting...')
try:
    s.connect('http://localhost:3000')
    print('connected')
    s.emit('server_emit', {'to':'1','event':'profileUpdated','payload':{'manual':'test'}})
    print('emitted')
    s.disconnect()
    print('disconnected')
except Exception as e:
    print('error', e)
