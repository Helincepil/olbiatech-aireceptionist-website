// DOM Elemanlari
const mesajFormu = document.getElementById("mesajFormu");
const mesajInput = document.getElementById("mesajInput");
const mesajAlani = document.getElementById("mesajAlani");
const yazmaGostergesi = document.getElementById("yazmaGostergesi");
const gonderButonu = document.getElementById("gonderButonu");

// Sohbet gecmisi - API'ye gonderilecek mesajlar
const sohbetGecmisi = [];

// Mesaj gonder
mesajFormu.addEventListener("submit", async (e) => {
  e.preventDefault();

  const mesaj = mesajInput.value.trim();
  if (!mesaj) return;

  // Kullanici mesajini ekrana ekle
  mesajEkle(mesaj, "kullanici");
  mesajInput.value = "";

  // Gecmise ekle
  sohbetGecmisi.push({ role: "user", content: mesaj });

  // Butonu devre disi birak
  gonderButonu.disabled = true;
  yazmaGostergesiGoster(true);

  try {
    // Backend'e istek gonder
    const yanit = await fetch("/api/sohbet", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mesajlar: sohbetGecmisi }),
    });

    if (!yanit.ok) {
      const hata = await yanit.json();
      throw new Error(hata.hata || "A server error occurred");
    }

    const veri = await yanit.json();
    const botCevabi = veri.cevap;

    // Bot cevabini ekrana ekle
    mesajEkle(botCevabi, "bot");

    // Gecmise ekle
    sohbetGecmisi.push({ role: "assistant", content: botCevabi });
  } catch (hata) {
    // Hata mesaji goster
    mesajEkle("An error occurred: " + hata.message, "hata");
    // Hatali mesaji gecmisten cikar
    sohbetGecmisi.pop();
  } finally {
    gonderButonu.disabled = false;
    yazmaGostergesiGoster(false);
    mesajInput.focus();
  }
});

// Ekrana mesaj ekle
function mesajEkle(metin, tip) {
  const mesajDiv = document.createElement("div");
  mesajDiv.classList.add("mesaj");

  if (tip === "kullanici") {
    mesajDiv.classList.add("kullanici-mesaji");
  } else if (tip === "bot") {
    mesajDiv.classList.add("bot-mesaji");
  } else if (tip === "hata") {
    mesajDiv.classList.add("bot-mesaji", "hata-mesaji");
  }

  const balonDiv = document.createElement("div");
  balonDiv.classList.add("mesaj-baloncugu");
  balonDiv.textContent = metin;

  mesajDiv.appendChild(balonDiv);
  mesajAlani.appendChild(mesajDiv);

  // En alta kaydir
  mesajAlani.scrollTop = mesajAlani.scrollHeight;
}

// Yazma gostergesi
function yazmaGostergesiGoster(goster) {
  yazmaGostergesi.style.display = goster ? "block" : "none";
  if (goster) {
    mesajAlani.scrollTop = mesajAlani.scrollHeight;
  }
}
