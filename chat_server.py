import socket
import threading

clients = []  # bağlanan istemcileri tutacağım yer

def handle_client(client_socket, address):
    print(f"{address} bağlandı.") # bağlanan client hakkında bilgi verir.
    while True: # bu döngünün sebebi ise sürekli mesaj bekleyen bir server olması için.
        try:
            data = client_socket.recv(1024) #en fazla 1kb lik veri alabilirim
            if not data:
                break  # data yollanmıyorsa yani bağlantı gittiyse sonsuz döngüyü sonlandırır.
            message = data.decode("utf-8") # veriyi yazıya çevirir. byte->string
            print(f"{address} -> {message}") # Bağlanan clientin ne mesaj yolladığını gösterir.
            broadcast(message, client_socket)
        except:
            break # Bağlantı hatası vs. gibi koşullarda bağlantıyı bitirmesi için
    print(f"{address} ayrıldı.") # ayrılan veya kopan clientin adresi
    clients.remove(client_socket) # O anda kopan client'i listeden çıkarmak için mesajları görmemesi adına
    client_socket.close() # soketi kapatırız.

# Mesajı her cliente iletmek için fonksiyon tabi ki byte formunda. eğer bağlantı vs koptuysa o clienti listeden sileriz.
def broadcast(message):
    for client in clients:
            try:
                client.send(message.encode("utf-8"))
            except:
                client.close()
                clients.remove(client)
# Tcp soketi oluşturup 5000. portta çalıştırdım 0.0.0.0 adresi genelde tüm bağlantılar için kullanılır.
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5000)) #Soketi bu porta ve adrese bağlar.
    server.listen()
    print("[SERVER] Sunucu çalışıyor... 5000 portunda")
# Gelen bağlantıları kabul eder ve client listesine eklerim.
    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket, addr)) # Thread() yeni bir iş parçacığı oluşturur threading kütüphanesi içindeki bir sınıftır.
        # target ise fonksiyonumuz her çalıştığında bir thread oluşur. args ise fonksiyonun içindeki parametreler anlamına gelir.
        # daemon= True ise işlemler bitince threadi sonlandırır.
        thread.start() # threadi başlatır yani handle_client çalışır.

if __name__ == "__main__":
    start_server()
