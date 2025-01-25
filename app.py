from fastapi import FastAPI, WebSocket
import paramiko
import asyncio
import json

app = FastAPI()


class SSHConnection:
    def __init__(self, host, username, password):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(host, username=username, password=password)
        self.transport = self.client.get_transport()
        self.channel = self.transport.open_session()
        self.channel.get_pty()
        self.channel.invoke_shell()

    def send_command(self, command):
        self.channel.send(command + '\n')

    def receive_output(self):
        output = self.channel.recv(1024)
        return output.decode('utf-8')

    def close(self):
        self.channel.close()
        self.client.close()


connections = {}  # Bağlantıları saklamak için bir sözlük


@app.websocket("/ws/ssh")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Bağlantı kimliği oluştur
    connection_id = str(1)
    connections[connection_id] = SSHConnection('sdf.org', 'emrekarakaya', 'PB24Jv3zLvThvg')
    output = connections[connection_id].receive_output()
    await websocket.send_text(json.dumps({'output': output}))
    print('text gitti')
    while True:
        data = await websocket.receive_text()
        print(data)
        data = json.loads(data)  # JSON formatında veri alıyoruz
        command = data.get('command')

        if command == 'exit':
            connections[connection_id].close()
            del connections[connection_id]
            await websocket.close()
            break

        connections[connection_id].send_command(command)
        output = connections[connection_id].receive_output()
        try:
            decoded_output = output.decode('utf-8')
        except UnicodeDecodeError:
            decoded_output = output.decode('latin1', errors='ignore')  # Alternatif olarak Latin-1 kullanılıyor

        await websocket.send_text(decoded_output)

'''
#import paramiko
from fastapi import FastAPI, WebSocket
import asyncio

app = FastAPI()



@app.websocket("/ws/ssh")
async def websocket_endpoint(ws: WebSocket):
    print("WebSocket bağlantısı başlatılıyor...")
    await handle_ssh(ws)


# WebSocket ile gelen komutları SSH'ye iletmek
async def handle_ssh(ws: WebSocket):
    print(1)
    try:
        await ws.accept()  # WebSocket bağlantısı açılıyor
    except Exception as e:
        print(f"Hata oluştu: {e}")
        await ws.close()  # WebSocket bağlantısını kapat
        return

    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect('sdf.org', username='emrekarakaya', password='PB24Jv3zLvThvg')

        transport = ssh_client.get_transport()
        channel = transport.open_session()
        channel.get_pty()
        channel.invoke_shell()
        print("SSH bağlantısı kuruldu")

        while True:
            message = await ws.receive_text()  # WebSocket'ten gelen komut
            print(f"WebSocket mesajı alındı: {message}")
            if message:
                # Komutun sonuna \n ekliyoruz (Enter tuşu eklemek için)
                print("Komut SSH kanalına gönderiliyor...")
                channel.send(message + '\n')  # SSH kanalına gönderiyoruz
                print("Komut gönderildi.")

            if channel.recv_ready():
                output = channel.recv(1024)  # Çıktıyı alıyoruz
                try:
                    decoded_output = output.decode('utf-8')
                except UnicodeDecodeError:
                    decoded_output = output.decode('latin1', errors='ignore')  # Alternatif olarak Latin-1 kullanılıyor

                await ws.send_text(decoded_output)  # WebSocket'e çıktıyı gönderiyoruz

            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"SSH işlemi sırasında hata oluştu: {e}")
        await ws.close()'''