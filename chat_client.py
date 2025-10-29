import socket
import threading

# Sunucu bilgileri kendi pc'mde test edeceğim için local host adresini girdim
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

# klasik tcp soketi oluşturdum.
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, SERVER_PORT))  #client sunucuya bağlanır.

print("Sunucuya bağlanıldı. 'exit' yazarak çıkabilirsiniz.\n")

# sunucudan gelen mesajları sürekli dinlemesi için sonsuz döngü ama veri yoksa yani mesaj yoksa döngüden çık.
def receive_messages():
    while True:
        try:
            data = client.recv(1024)           # en fazla 1 kb veri alırım.
            if not data:
                break                          # bağlantı kapandıysa döngüden çık.
            print(data.decode("utf-8"))        # aldığımız veriyi yazdırırım ama string olarak çünkü byte şeklinde aldım veriyi.
        except:
            break                               #hata mata olursa döngüden çık.
    try:
        client.close()                          #soketi kapatma fonksiyonu.
    except:
        pass

#dinleme yaparken gelen mesajları kaçırmamak için ayrı bir thread oluşturdum bu gelen mesajlar için.
recv_thread = threading.Thread(target=receive_messages, daemon=True)
recv_thread.start()

# çok kullanıcı olduğu için nick ile ayırt edebiliriz. eğer nick girmezse boş algılarım ve kullanıcı olarak kabul ederim bu da varsayılan olarak geçer.
nickname = input("Kullanıcı adınızı yazın: ").strip()
if not nickname:
    nickname = "Kullanıcı"                      # Boş girilirse varsayılan isim.
client.send(nickname.encode("utf-8"))

#burası da clientden servera mesaj yollama yeri byte türüne çevirip öyle yollarım.
while True:
    try:
        msg = input("")                         # Yollayacağım mesaj
        client.send(msg.encode("utf-8"))
        if msg.lower().strip() == "exit":       # exit yazarsa sohbetten çıkar.
            break
    except (KeyboardInterrupt, EOFError): #keyboardinterrupt ctrl+ c ile kapat eoferror ise ctrl+ d ile kapatma anlamında
        try:
            client.send("exit".encode("utf-8")) # eğer yukarıdakileri kullanırsam exit yazmış gibi davran demek.
        except:
            pass # hata görsen de devam et
        break
    except:
        break

try:
    client.close() # soketi sonlandır.
except:
    pass

print("Bağlantı sonlandırıldı.")
