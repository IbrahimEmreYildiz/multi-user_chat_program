import socket
import threading
from datetime import datetime  # Zaman damgası için kütüphane
import time  # zaman damgası tutmak için

clients = []  # bağlanan istemcileri tutacağım yer
nicknames = {}  # her client için kullanıcı adlarını tutmak için sözlük
message_count = 0     # Sunucunun işlediği toplam mesaj sayısı
connection_count = 0  # Toplam bağlanan istemci sayısı


# spam önlemek için mesaj limiti
RATE_LIMIT_MAX = 8          #1 kişinin gönderebileceği max mesaj sayısı (rate limit window süresince)
RATE_LIMIT_WINDOW = 5       # bu süre boyunca rate limit max sayısından fazla mesaj gelmemeli
MUTE_SECONDS = 10           # susturulma yani ceza süresi
msg_times = {}              # istemcinin bağlı olduğu soketteki mesaj zamanlarını tutan liste
muted_until = {}            # susturmanın biteceği zaman

#bu fonksiyon hangi client hangi soketle bağlı onu bulma yeri
def get_socket_by_nick(target_name): #target name soketin bağlı olduğu isim
    for s, n in nicknames.items(): # hem soketi hem de nicki döndüren method
        if n == target_name:
            return s # eşleşirse direkt soketi döndür
    return None # isimler eşleşmezse none döner

def handle_client(client_socket, address):
    nickname = client_socket.recv(1024).decode("utf-8").strip()  # Kullanıcıdan gelen ismi alır.

    # Aynı isim varsa sonuna sayı ekle emre, emre_2, emre_3 ....
    count = sum(1 for n in nicknames.values() if n.startswith(nickname))
    if count > 0:
        nickname = f"{nickname}_{count + 1}"

    nicknames[client_socket] = nickname  # o sırada soketteki ismi kaydeder
    print(f"{nickname} ({address}) bağlandı.")  # bağlanan client hakkında bilgi verir.
    broadcast(f"{nickname} sohbete katıldı.")  # diğer clientlara bilgi verir.

    global connection_count # bu değişken fonksiyon içi değişken olmadığı için global fonksiyonunu kullandım. yoksa hata verir local olmadığı için
    connection_count += 1 # bağlantı olduğunda 1 artır ve yazdır
    print(f"[STATS] Aktif kullanıcı: {len(clients)} | Toplam bağlantı: {connection_count}")

    log_message(f"{nickname} bağlandı ({address})")  #log dosyasına bağlananı ipsini portunu yazar.
    broadcast_user_list()  # yeni biri bağlanınca herkese bağlı olan kişileri gösterir.

 # bunlar rate limit sataçlarını başlatır.
    msg_times[client_socket] = []
    muted_until[client_socket] = 0

    while True:  # bu döngünün sebebi ise sürekli mesaj bekleyen bir server olması için.
        try:
            data = client_socket.recv(1024)  # en fazla 1kb lik veri alabilirim
            if not data:
                break  # data yollanmıyorsa yani bağlantı gittiyse sonsuz döngüyü sonlandırır.
            message = data.decode("utf-8")  # veriyi yazıya çevirir. byte->string

            # exit yazan kullanıcı sohbetten çıkar
            if message.lower().strip() == "exit":
                client_socket.send("Sohbetten çıkılıyor...\n".encode("utf-8"))
                break

            # susturulduğumda spam yapmayım diye bilgilendirme yapar
            now = time.time()
            if now < muted_until.get(client_socket, 0):
                try: # eğer mute yediysem susturulduğumun bilgisini verir
                    # ve şimdiki zamandan ban yediğim zamanı çıkararak susturmanın daha ne kadar süreceğini gösterir
                    client_socket.send(f"[UYARI] Spam nedeniyle susturuldunuz, {int(muted_until[client_socket]-now)} sn sonra tekrar deneyin.\n".encode("utf-8"))
                except:
                    pass
                continue  # mesajı işlemeyiz

            times = msg_times.get(client_socket, [])
            # eski zaman damgalarını pencere dışına at
            times = [t for t in times if now - t <= RATE_LIMIT_WINDOW] # kaydettiğim eski zaman damgalarını window sınırından çıkarıyorum örneğin 100. saniyedeyim
            # 90. saniyedeki damgayı silerim çünkü 100 -90 =10 ama benim rate limit window'um 5 sonuç 5 ten büyükleri listeden çıkarmış oluyorum.
            times.append(now)
            msg_times[client_socket] = times

            if len(times) > RATE_LIMIT_MAX:
                muted_until[client_socket] = now + MUTE_SECONDS # ne zamana kadar susturulduğunu hesaplar
                try:
                    client_socket.send(f"[UYARI] Çok hızlı mesaj yolluyorsunuz. {MUTE_SECONDS} sn susturuldunuz.\n".encode("utf-8")) #bilgilendirme
                except:
                    pass
                log_message(f"[RATE-LIMIT] {nickname} susturuldu ({MUTE_SECONDS}s)") # loglara kimin susturulduğunu işler.
                continue

            # özel mesaj yollama yeri
            if message.startswith("/msg "):
                try:
                    _, rest = message.split(" ", 1)# ilk boşlukta mesajı bölüp target nameyi yani hedef ismi bulur.
                    target_name, private_text = rest.split(" ", 1) # yani mesaj isim + mesaj şeklinde formlanır.
                except ValueError:
                    try:
                        client_socket.send("Kullanım: /msg <kullanıcı> <mesaj>\n".encode("utf-8")) # kullanım formu
                    except:
                        pass
                    continue

                target_sock = get_socket_by_nick(target_name) # eğer soketle isim eşleşmezse hata verir.
                if not target_sock:
                    try:
                        client_socket.send(f"[HATA] '{target_name}' adlı kullanıcı bulunamadı.\n".encode("utf-8"))
                    except:
                        pass
                    continue

                zaman = datetime.now().strftime("%H:%M:%S")
                priv_line_sender = f"[{zaman}] [ÖZEL] {nickname} -> {target_name}: {private_text}" #mesajı yollayan kişi mesajı bu formatta görür.
                priv_line_target = f"[{zaman}] [ÖZEL] {nickname}: {private_text}" # mesajı alan kişi bu formatta görür.
                try:
                    client_socket.send((priv_line_sender + "\n").encode("utf-8"))  # gönderen de görsün mesajın gidip gitmediğini
                    target_sock.send((priv_line_target + "\n").encode("utf-8"))    # hedef mesajı alıp almadığını görsün ve kimden olduğunu
                except:
                    pass
                log_message(f"[PRIVATE] {nickname} -> {target_name}: {private_text}") # loga özel mesajı kaydeder.
                continue  # özel mesaj olduğu için herkesin ekranına yazmaması için cont dedik

            zaman = datetime.now().strftime("%H:%M:%S")  # saat bilgisini alır
            full_message = f"[{zaman}] {nickname}: {message}"  # mesaj formatı
            global message_count # aynı şekilde local değişken olmadığı için böyle tanımlamam gerekiyor.
            message_count += 1 #mesaj sayısını 1 artır ve yazdır.
            print(f"[STATS] Toplam işlenen mesaj: {message_count}")

            print(full_message)  # terminalde görüntüler.
            broadcast(full_message)  # Mesajı herkese yollar (gönderen dahil)
            log_message(full_message)  # mesajı log dosyasına kaydeder
        except:
            break  # Bağlantı hatası vs. gibi koşullarda bağlantıyı bitirmesi için

    print(f"{nickname} ({address}) ayrıldı.")  # ayrılan veya kopan clientin adresi
    print(f"[STATS] Aktif kullanıcı: {len(clients) - 1}") # Sayaçtan 1 düşer bir client ayrıldığı için
    broadcast(f"{nickname} sohbetten ayrıldı.")  # diğer clientlara bilgi verir.
    log_message(f"{nickname} ayrıldı ({address})")  # Log dosyasına çıkış kaydı ekler.
    clients.remove(client_socket)  # O anda kopan client'i listeden çıkarmak için mesajları görmemesi adına
    del nicknames[client_socket]  # kullanıcı adını sözlükten kaldırır.
    # rate limit için kaydedilen zamanları siler çünkü çok fazla birikir silmezsem
    msg_times.pop(client_socket, None)
    muted_until.pop(client_socket, None)
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

# kullanıcı listesini gösteren fonksiyon
def broadcast_user_list():
    if not nicknames:
        return
    user_list = ", ".join(nicknames.values())  # kullanıcılar arasına virgül koyar
    message = f"Aktif kullanıcılar: [{user_list}]"
    for client in clients:
        try:
            client.send(message.encode("utf-8")) #mesajı clientlere gönderir
        except:
            pass

# log dosyasına mesajı zamanı girişi çıkışı kaydeder.
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
