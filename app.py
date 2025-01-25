import paramiko
from fastapi import FastAPI, WebSocket
import asyncio

app = FastAPI()


# WebSocket ile gelen komutları SSH'ye iletmek
async def handle_ssh(ws: WebSocket):
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
        await ws.close()


@app.websocket("/ws/ssh")
async def websocket_endpoint(ws: WebSocket):
    print("WebSocket bağlantısı başlatılıyor...")
    await handle_ssh(ws)
