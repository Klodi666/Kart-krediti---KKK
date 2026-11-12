#!/usr/bin/env python3
"""
Krijues Kodesh
--------------
Mjet me menu për gjenerimin e kodeve numerike, skanimin e tyre kundrejt
prefikseve të dokumentuara publikisht të emetuesve, validimin e PAN-ve me
Luhn, dhe ruajtjen/ngarkimin e grupeve të rezultateve.

Funksionon plotësisht offline. Nuk bëhen kërkesa rrjeti.
"""

import os
import random
import sys
from datetime import datetime

# --------------------------------------------------------------------------
# Konfigurimi
# --------------------------------------------------------------------------

EMRI_APLIKACIONIT = "Krijues Kodesh"
SASI_DEFAULT = 10
DOSJA_REZULTATEVE = "rezultate"

CILESIMET = {
    "shifra": 6,               # sa shifra për çdo kod
    "unike": True,             # shifrat brenda një kodi duhet të jenë të ndryshme
    "lejo_zero_fillim": True,  # lejo kode si 048291
    "rendit_shifrat": False,   # rendit shifrat në mënyrë rritëse
}

GJENERUARA = []  # grupi i rezultateve në memorie

# --------------------------------------------------------------------------
# Ndihmës
# --------------------------------------------------------------------------

def _ne_int(vlera, parazgjedhur=-1):
    try:
        return int(vlera)
    except (TypeError, ValueError):
        return parazgjedhur


# --------------------------------------------------------------------------
# Tabela publike e prefikseve IIN / BIN
# --------------------------------------------------------------------------

def marka_per_prefiks(kodi):
    """Kthen emrin e rrjetit që përputhet me shifrat fillestare të `kodi`, ose None."""
    if not kodi or not kodi.isdigit():
        return None

    plotësuar = (kodi + "000000")[:6]
    p2, p3, p4, p6 = plotësuar[:2], plotësuar[:3], plotësuar[:4], plotësuar[:6]
    i2, i3, i4, i6 = _ne_int(p2), _ne_int(p3), _ne_int(p4), _ne_int(p6)

    if p2 in ("34", "37"):
        return "American Express"
    if plotësuar[0] == "4":
        return "Visa"
    if 51 <= i2 <= 55:
        return "Mastercard"
    if 2221 <= i4 <= 2720:
        return "Mastercard"
    if p4 == "6011" or p2 == "65":
        return "Discover"
    if 644 <= i3 <= 649:
        return "Discover"
    if 622126 <= i6 <= 622925:
        return "Discover"
    if 3528 <= i4 <= 3589:
        return "JCB"
    if p2 in ("36", "38") or 300 <= i3 <= 305:
        return "Diners Club"
    if p2 == "62":
        return "UnionPay"
    return None


def filtro_te_pershtatura(kodet):
    return [k for k in kodet if marka_per_prefiks(k) is not None]


def filtro_te_papershtatura(kodet):
    return [k for k in kodet if marka_per_prefiks(k) is None]


# --------------------------------------------------------------------------
# Luhn
# --------------------------------------------------------------------------

def luhn_i_vlefshem(numri):
    if not numri or not numri.isdigit():
        return False
    totali = 0
    dyfisho = False
    for ch in reversed(numri):
        shifra = int(ch)
        if dyfisho:
            shifra *= 2
            if shifra > 9:
                shifra -= 9
        totali += shifra
        dyfisho = not dyfisho
    return totali % 10 == 0


def inspekto_pan(numri):
    pastruar = "".join(c for c in numri if c.isdigit())
    return {
        "pastruar": pastruar,
        "vetem_shifra": pastruar == numri.strip() and pastruar != "",
        "gjatesi": len(pastruar),
        "gjatesi_ok": 12 <= len(pastruar) <= 19,
        "luhn_ok": luhn_i_vlefshem(pastruar),
        "prefiks": pastruar[:6] if len(pastruar) >= 6 else None,
        "marka": marka_per_prefiks(pastruar),
    }


# --------------------------------------------------------------------------
# Gjenerimi
# --------------------------------------------------------------------------

def krijo_kod(shifra=None, unike=None, lejo_zero_fillim=None, rendit_shifrat=None):
    shifra = CILESIMET["shifra"] if shifra is None else shifra
    unike = CILESIMET["unike"] if unike is None else unike
    lejo_zero_fillim = (
        CILESIMET["lejo_zero_fillim"] if lejo_zero_fillim is None else lejo_zero_fillim
    )
    rendit_shifrat = CILESIMET["rendit_shifrat"] if rendit_shifrat is None else rendit_shifrat

    if unike and shifra > 10:
        raise ValueError("Nuk mund të kërkohen më shumë se 10 shifra dhjetore unike.")

    grup = random.sample(range(10), shifra) if unike else [
        random.randint(0, 9) for _ in range(shifra)
    ]
    if not lejo_zero_fillim and grup[0] == 0:
        grup[0] = random.randint(1, 9)
    if rendit_shifrat:
        grup.sort()

    return "".join(str(s) for s in grup)


def krijo_shume(sasia, **kwargs):
    return [krijo_kod(**kwargs) for _ in range(sasia)]


# --------------------------------------------------------------------------
# Skanimi
# --------------------------------------------------------------------------

def skano_kodet(kodet):
    rezultatet = []
    for i, kodi in enumerate(kodet, start=1):
        marka = marka_per_prefiks(kodi)
        rezultatet.append({
            "indeksi": i,
            "kodi": kodi,
            "marka": marka,
            "pershtatur": marka is not None,
        })
    return rezultatet


def shfaq_skanimin(rezultatet, shfaq_te_papershtatura=True):
    for rresht in rezultatet:
        if rresht["pershtatur"]:
            print(f"[{rresht['indeksi']:>4}] {rresht['kodi']}  ->  {rresht['marka']}")
        elif shfaq_te_papershtatura:
            print(f"[{rresht['indeksi']:>4}] {rresht['kodi']}  ->  pa prefiks të dokumentuar")
    pershtatur = sum(1 for r in rezultatet if r["pershtatur"])
    totali = len(rezultatet)
    përqindje = (pershtatur / totali * 100) if totali else 0.0
    print(f"\n{pershtatur}/{totali} përputhen me një prefiks të dokumentuar ({përqindje:.1f}%).")


# --------------------------------------------------------------------------
# Ruajtja dhe ngarkimi
# --------------------------------------------------------------------------

def siguro_dosjen_e_rezultateve():
    os.makedirs(DOSJA_REZULTATEVE, exist_ok=True)
    return DOSJA_REZULTATEVE


def zgjidh_rrugen(rruga, me_kohe=False, emri_default="kodet.txt"):
    rruga = (rruga or "").strip()
    if not rruga:
        siguro_dosjen_e_rezultateve()
        rruga = os.path.join(DOSJA_REZULTATEVE, emri_default)
    if not rruga.lower().endswith(".txt"):
        rruga += ".txt"
    if me_kohe:
        baza, shtesa = os.path.splitext(rruga)
        rruga = f"{baza}_{datetime.now():%Y%m%d_%H%M%S}{shtesa}"
    return rruga


def ruaj_kodet(kodet, rruga, shto=False):
    if not kodet:
        raise ValueError("Nuk ka asgjë për të shkruar.")
    modaliteti = "a" if shto else "w"
    dosja = os.path.dirname(os.path.abspath(rruga))
    if dosja and not os.path.isdir(dosja):
        raise FileNotFoundError(f"Dosja nuk ekziston: {dosja}")
    with open(rruga, modaliteti, encoding="utf-8") as skedari:
        skedari.write("\n".join(kodet) + "\n")
    return os.path.abspath(rruga)


def ngarko_kodet(rruga):
    with open(rruga, encoding="utf-8") as skedari:
        return [rresht.strip() for rresht in skedari if rresht.strip()]


# --------------------------------------------------------------------------
# Raportimi
# --------------------------------------------------------------------------

def permbledhje_markash(kodet):
    numërimi = {}
    for kodi in kodet:
        marka = marka_per_prefiks(kodi) or "Pa përputhje"
        numërimi[marka] = numërimi.get(marka, 0) + 1
    return numërimi


def shfaq_permbledhjen(kodet):
    if not kodet:
        print("Asnjë kod i ngarkuar.")
        return
    print(f"\nPërmbledhje për {len(kodet)} kod(e):")
    for marka, sasia in sorted(permbledhje_markash(kodet).items(), key=lambda kv: -kv[1]):
        print(f"  {marka:<20} {sasia:>5}")
    gjatesite = {len(k) for k in kodet}
    print(f"  {'Gjatësi(t)':<20} {', '.join(map(str, sorted(gjatesite)))}")
    print(f"  {'Jo-numerike':<20} {sum(1 for k in kodet if not k.isdigit())}")


# --------------------------------------------------------------------------
# Rutina e përbashkët për shfaqje në terminal
# --------------------------------------------------------------------------

def _shfaq_te_filtruara(kodet, etiketa, shfaq_marken=True, thjesht=False):
    if not kodet:
        print(f"Nuk ka kode të {etiketa} në grupin aktual.")
        return

    print(f"\n=== KODET E {etiketa.upper()} ({len(kodet)}) ===\n")

    if thjesht:
        for kodi in kodet:
            print(kodi)
        print()
        return

    for i, kodi in enumerate(kodet, start=1):
        if shfaq_marken:
            marka = marka_per_prefiks(kodi)
            shtese = f"  ({marka})" if marka else ""
            print(f"[{i:>4}] {kodi}{shtese}")
        else:
            print(f"[{i:>4}] {kodi}")

    if shfaq_marken:
        print("\nNdarja:")
        for marka, sasia in sorted(permbledhje_markash(kodet).items(), key=lambda kv: -kv[1]):
            print(f"  {marka:<20} {sasia:>5}")

    perseri = input("\nShfaq si listë të thjeshtë (vetëm kode)? [p/J]: ").strip().lower()
    if perseri == "p":
        print()
        for kodi in kodet:
            print(kodi)
        print()


# --------------------------------------------------------------------------
# Rutina e përbashkët për ruajtje
# --------------------------------------------------------------------------

def _pyet_dhe_ruaj(kodet, etiketa, emri_default):
    if not kodet:
        print(f"Nuk ka kode të {etiketa} për të ruajtur.")
        return

    print(f"\n{len(kodet)} kod(e) të {etiketa} gati për ruajtje.")
    parapamje = kodet[:10]
    print("Parapamje:")
    for k in parapamje:
        marka = marka_per_prefiks(k)
        print(f"  {k}" + (f"  ({marka})" if marka else ""))
    if len(kodet) > len(parapamje):
        print(f"  ... dhe {len(kodet) - len(parapamje)} të tjera")

    rruga = input(f"Rruga e ruajtjes [{os.path.join(DOSJA_REZULTATEVE, emri_default)}]: ").strip()
    me_kohe = input("Shto vulë kohore në emrin e skedarit? [p/J]: ").strip().lower() == "p"
    shto = input("Shto në skedarin ekzistues? [p/J]: ").strip().lower() == "p"

    try:
        e_plote = ruaj_kodet(kodet, zgjidh_rrugen(rruga, me_kohe, emri_default), shto=shto)
    except (OSError, FileNotFoundError, ValueError) as gabim:
        print(f"Nuk mund të ruhej: {gabim}")
        return

    folja = "U shtuan" if shto else "U ruajtën"
    print(f"{folja} {len(kodet)} kod(e) të {etiketa} në {e_plote}")


# --------------------------------------------------------------------------
# Veprimet e menysë
# --------------------------------------------------------------------------

def vepro_gjenero():
    global GJENERUARA
    vlera = input(f"Sa kode të gjenerohen? [{SASI_DEFAULT}]: ").strip()
    sasia = _ne_int(vlera, SASI_DEFAULT)
    if sasia <= 0:
        print("Ju lutem jepni një numër pozitiv.")
        return
    try:
        GJENERUARA = krijo_shume(sasia)
    except ValueError as gabim:
        print(f"Gabim: {gabim}")
        return
    print(f"\nU gjeneruan {sasia} kod(e):")
    for kodi in GJENERUARA:
        print(kodi)


def vepro_skano():
    if not GJENERUARA:
        print("Nuk ka kode në memorie. Gjenero ose ngarko së pari.")
        return
    shfaq_te_papershtatura = input("Të shfaqen edhe kodet e papërputhura? [p/J]: ").strip().lower() != "j"
    print(f"\nPo skanohen {len(GJENERUARA)} kod(e):\n")
    shfaq_skanimin(skano_kodet(GJENERUARA), shfaq_te_papershtatura=shfaq_te_papershtatura)


def vepro_shfaq_te_pershtatura():
    _shfaq_te_filtruara(filtro_te_pershtatura(GJENERUARA), "përputhura", shfaq_marken=True)


def vepro_shfaq_te_pershtatura_thjesht():
    te_pershtatura = filtro_te_pershtatura(GJENERUARA)
    if not te_pershtatura:
        print("Nuk ka kode të përputhura në grupin aktual.")
        return
    print(f"\n=== KODET E PËRSHTATURA — THJESHT ({len(te_pershtatura)}) ===\n")
    for kodi in te_pershtatura:
        print(kodi)
    print()


def vepro_shfaq_te_papershtatura():
    _shfaq_te_filtruara(filtro_te_papershtatura(GJENERUARA), "papërputhura", shfaq_marken=False)


def vepro_shfaq_te_gjitha():
    _shfaq_te_filtruara(GJENERUARA, "të gjitha", shfaq_marken=True)


def vepro_ruaj_te_gjitha():
    _pyet_dhe_ruaj(GJENERUARA, "të gjitha", "kodet.txt")


def vepro_ruaj_te_pershtatura():
    _pyet_dhe_ruaj(filtro_te_pershtatura(GJENERUARA), "përputhura", "kodet_pershtatura.txt")


def vepro_ruaj_te_papershtatura():
    _pyet_dhe_ruaj(filtro_te_papershtatura(GJENERUARA), "papërputhura", "kodet_papershtatura.txt")


def vepro_ngarko():
    global GJENERUARA
    rruga = input("Rruga për të ngarkuar: ").strip()
    if not rruga:
        print("Nuk u dha asnjë rrugë.")
        return
    if not os.path.isfile(rruga):
        print(f"Skedari nuk u gjet: {rruga}")
        return
    try:
        te_ngarkuara = ngarko_kodet(rruga)
    except OSError as gabim:
        print(f"Nuk mund të lexohej: {gabim}")
        return
    zevendeso = input(f"Të zëvendësohet grupi aktual ({len(GJENERUARA)})? [p/J]: ").strip().lower() != "j"
    if zevendeso:
        GJENERUARA = te_ngarkuara
    else:
        GJENERUARA.extend(te_ngarkuara)
    print(f"U ngarkuan {len(te_ngarkuara)} kod(e). Në memorie: {len(GJENERUARA)}.")


def vepro_valido_pan():
    vlera = input("Jepni një numër karte për inspektim (shifra, hapësira lejohen): ").strip()
    if not vlera:
        return
    info = inspekto_pan(vlera)
    print("\nRezultati:")
    print(f"  Pastruar       : {info['pastruar'] or '(bosh)'}")
    print(f"  Gjatësi        : {info['gjatesi']} {'(ok)' if info['gjatesi_ok'] else '(jashtë intervalit)'}")
    print(f"  Luhn           : {'i vlefshëm' if info['luhn_ok'] else 'i pavlefshëm'}")
    print(f"  Prefiksi       : {info['prefiks'] or '(shumë i shkurtër)'}")
    print(f"  Marka e hamendësuar: {info['marka'] or '(e panjohur)'}")
    if info["luhn_ok"] and info["gjatesi_ok"]:
        print("  Përfundim      : strukturalisht i vlefshëm")
    else:
        print("  Përfundim      : dështon kontrollet strukturore")


def vepro_permbledhje():
    shfaq_permbledhjen(GJENERUARA)


def vepro_cilesimet():
    print("\nCilësimet aktuale:")
    for c, v in CILESIMET.items():
        print(f"  {c:<20} {v}")
    print("\nLini bosh për të mbajtur vlerën aktuale.")
    shifra = input(f"shifra [{CILESIMET['shifra']}]: ").strip()
    if shifra:
        vlera = _ne_int(shifra)
        if 1 <= vlera <= 10:
            CILESIMET["shifra"] = vlera
        else:
            print("  U injorua: shifrat duhet të jenë 1-10.")
    for celesi in ("unike", "lejo_zero_fillim", "rendit_shifrat"):
        pergjigje = input(f"{celesi} [{'p' if CILESIMET[celesi] else 'j'}]: ").strip().lower()
        if pergjigje in ("p", "j"):
            CILESIMET[celesi] = pergjigje == "p"
    print("\nCilësimet e përditësuara:")
    for c, v in CILESIMET.items():
        print(f"  {c:<20} {v}")


def vepro_pastro():
    global GJENERUARA
    GJENERUARA = []
    print("Grupi i kodeve në memorie u pastrua.")


# --------------------------------------------------------------------------
# Menyja
# --------------------------------------------------------------------------

MENYJA = """
========================================
 {app}
========================================
 SHFAQJA
  1) Gjenero kode
  2) Skano kodet për prefikse të dokumentuara
  3) Shfaq vetëm kodet E PËRSHTATURA (me marka)
  4) Shfaq vetëm kodet E PËRSHTATURA (listë e thjeshtë)
  5) Shfaq vetëm kodet E PAPËRSHTATURA
  6) Shfaq TË GJITHA kodet

 RUAJTJA
  7) Ruaj TË GJITHA kodet
  8) Ruaj vetëm kodet E PËRSHTATURA
  9) Ruaj vetëm kodet E PAPËRSHTATURA

 MJETET
 10) Ngarko kode nga skedari
 11) Valido një numër karte (Luhn)
 12) Shfaq përmbledhjen e grupit aktual
 13) Cilësimet
 14) Pastro grupin aktual
 15) Dil
========================================
""".format(app=EMRI_APLIKACIONIT)

VEPRIMET = {
    "1": vepro_gjenero,
    "2": vepro_skano,
    "3": vepro_shfaq_te_pershtatura,
    "4": vepro_shfaq_te_pershtatura_thjesht,
    "5": vepro_shfaq_te_papershtatura,
    "6": vepro_shfaq_te_gjitha,
    "7": vepro_ruaj_te_gjitha,
    "8": vepro_ruaj_te_pershtatura,
    "9": vepro_ruaj_te_papershtatura,
    "10": vepro_ngarko,
    "11": vepro_valido_pan,
    "12": vepro_permbledhje,
    "13": vepro_cilesimet,
    "14": vepro_pastro,
}


def main():
    while True:
        print(MENYJA)
        gjendja = f"{len(GJENERUARA)} kod(e) | {CILESIMET['shifra']} shifra"
        zgjedhja = input(f"[{gjendja}] Zgjidhni një opsion: ").strip()

        if zgjedhja == "15":
            print("Mirupafshim.")
            return

        trajtuesi = VEPRIMET.get(zgjedhja)
        if trajtuesi is None:
            print("Opsion i pavlefshëm. Zgjidhni 1-15.")
            continue

        try:
            trajtuesi()
        except KeyboardInterrupt:
            print("\nU anulua.")
        except Exception as gabim:
            print(f"Gabim i papritur: {gabim}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nU ndërpre.")
        sys.exit(0)