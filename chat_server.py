import socket
import threading
from datetime import datetime  # Zaman damgası için kütüphane

clients = []  # bağlanan istemcileri tutacağım yer
nicknames = {}  # her client için kullanıcı adlarını tutmak için sözlük

def handle_client(client_socket, address):
    nickname = client_socket.recv(1024).decode("utf-8").strip()  # Kullanıcıdan gelen ismi alır.

    # Aynı isim varsa sonuna sayı ekle emre, emre_1, emre_2 ....
    count = sum(1 for n in nicknames.values() if n.startswith(nickname))
    if count > 0:
        nickname = f"{nickname}_{count + 1}"

    nicknames[client_socket] = nickname  # client_socket’e ait kullanıcı adını kaydeder.
    print(f"{nickname} ({address}) bağlandı.")  # bağlanan client hakkında bilgi verir.
    broadcast(f"{nickname} sohbete katıldı.")  # diğer clientlara bilgi verir.

    log_message(f"{nickname} bağlandı ({address})")  # Log dosyasına giriş kaydı ekler.
    broadcast_user_list()  # Yeni kişi bağlanınca herkese aktif kullanıcı listesini gönderir.

    while True:  # bu döngünün sebebi ise sürekli mesaj bekleyen bir server olması için.
        try:
            data = client_socket.recv(1024)  # en fazla 1kb lik veri alabilirim
            if not data:
                break  # data yollanmıyorsa yani bağlantı gittiyse sonsuz döngüyü sonlandırır.
            message = data.decode("utf-8")  # veriyi yazıya çevirir. byte->string

            # --- Kullanıcı "exit" yazarak sohbetten çıkabilir ---
            if message.lower().strip() == "exit":
                client_socket.send("Sohbetten çıkılıyor...\n".encode("utf-8"))
                break

            zaman = datetime.now().strftime("%H:%M:%S")  # anlık saat-dakika-saniye bilgisini alır.
            full_message = f"[{zaman}] {nickname}: {message}"  # zaman + isim + mesaj şeklinde birleştirir.
            print(full_message)  # terminalde görüntüler.
            broadcast(full_message)  # Mesajı herkese yollar (artık gönderen dahil)
            log_message(full_message)  # Log dosyasına mesajı ekler.
        except:
            break  # Bağlantı hatası vs. gibi koşullarda bağlantıyı bitirmesi için

    print(f"{nickname} ({address}) ayrıldı.")  # ayrılan veya kopan clientin adresi
    broadcast(f"{nickname} sohbetten ayrıldı.")  # diğer clientlara bilgi verir.
    log_message(f"{nickname} ayrıldı ({address})")  # Log dosyasına çıkış kaydı ekler.
    clients.remove(client_socket)  # O anda kopan client'i listeden çıkarmak için mesajları görmemesi adına
    del nicknames[client_socket]  # kullanıcı adını sözlükten kaldırır.
    broadcast_user_list()  # Ayrılan kişiden sonra güncel kullanıcı listesini gönderir.
    client_socket.close()  # soketi kapatırız.

# Mesajı her cliente iletmek için fonksiyon. eğer bağlantı vs koptuysa o clienti listeden sileriz.
def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode("utf-8"))  # mesajı byte’a çevirip yollar.
        except:
            client.close()
            clients.remove(client)

# --- Yeni Fonksiyon: Kullanıcı listesini herkese gönderir ---
def broadcast_user_list():
    if not nicknames:
        return
    user_list = ", ".join(nicknames.values())  # tüm kullanıcı adlarını virgülle ayırır.
    message = f"Aktif kullanıcılar: [{user_list}]"
    for client in clients:
        try:
            client.send(message.encode("utf-8"))
        except:
            pass

# Log dosyasına mesaj, giriş ve çıkışları kaydeder.
def log_message(text):
    with open("server_log.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n")

# Tcp soketi oluşturup 5000. portta çalıştırdım 0.0.0.0 adresi genelde tüm bağlantılar için kullanılır.
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5000))  # Soketi bu porta ve adrese bağlar.
    server.listen()
    print("[SERVER] Sunucu çalışıyor... 5000 portunda")

    # Gelen bağlantıları kabul eder ve client listesine eklerim.
    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))  # Thread() yeni bir iş parçacığı oluşturur threading kütüphanesi içindeki bir sınıftır.
        # target ise fonksiyonumuz her çalıştığında bir thread oluşur. args ise fonksiyonun içindeki parametreler anlamına gelir.
        # daemon=True ise işlemler bitince threadi sonlandırır.
        thread.start()  # threadi başlatır yani handle_client çalışır.

if __name__ == "__main__":
    start_server()
