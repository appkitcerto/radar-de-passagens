"""Lê os feeds RSS dos sites de promoção e grava promocoes.json.

Guarda só título, link, data e o nome do site (com crédito). Não copia o texto
das matérias: quem quiser ler a oferta abre o link no site original.
"""
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

FEEDS = [
    {"site": "Melhores Destinos", "home": "https://www.melhoresdestinos.com.br/", "url": "https://www.melhoresdestinos.com.br/feed"},
    {"site": "Passagens Imperdíveis", "home": "https://www.passagensimperdiveis.com.br/", "url": "https://www.passagensimperdiveis.com.br/feed"},
    {"site": "Pontos pra Voar", "home": "https://pontospravoar.com/", "url": "https://pontospravoar.com/feed"},
    {"site": "Passageiro de Primeira", "home": "https://passageirodeprimeira.com/", "url": "https://passageirodeprimeira.com/feed"},
    {"site": "Cartões e Viagens", "home": "https://cartoeseviagens.com.br/", "url": "https://cartoeseviagens.com.br/feed"},
]
MAX_POR_SITE = 25
UA = "RadarDePassagens/1.0 (+https://github.com/appkitcerto/radar-de-passagens)"

# Palavras que ajudam a classificar o tipo de oferta.
TIPOS = [
    ("erro", r"\berro\b|tarifa[- ]erro|error fare|bug"),
    ("milhas", r"milha|pontos|smiles|latam pass|azul fidelidade|livelo|esfera|tudoazul|transfer[êe]ncia|b[ôo]nus|clube"),
    ("internacional", r"europa|estados unidos|eua|miami|orlando|nova york|lisboa|portugal|paris|londres|madri|roma|buenos aires|santiago|chile|canc[úu]n|internaciona"),
    ("passagem", r"passage|voo|voos|ida e volta|a partir de r\$"),
]


def classificar(titulo):
    t = titulo.lower()
    return [nome for nome, rx in TIPOS if re.search(rx, t)]


def preco(titulo):
    m = re.search(r"R\$\s?([\d.]+(?:,\d{2})?)", titulo)
    if not m:
        return None
    try:
        return float(m.group(1).replace(".", "").replace(",", "."))
    except ValueError:
        return None


def data_iso(texto):
    if not texto:
        return None
    try:
        d = parsedate_to_datetime(texto.strip())
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(texto.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc).isoformat()


def ler_feed(feed):
    req = urllib.request.Request(feed["url"], headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        raiz = ET.fromstring(r.read())
    itens = []
    atom = "{http://www.w3.org/2005/Atom}"
    for it in raiz.iter("item"):
        itens.append((it.findtext("title"), it.findtext("link"), it.findtext("pubDate")))
    for it in raiz.iter(atom + "entry"):
        link = it.find(atom + "link")
        itens.append((it.findtext(atom + "title"), link.get("href") if link is not None else None,
                      it.findtext(atom + "published") or it.findtext(atom + "updated")))
    saida = []
    for titulo, link, data in itens[:MAX_POR_SITE]:
        if not titulo or not link:
            continue
        titulo = " ".join(titulo.split())
        saida.append({
            "titulo": titulo,
            "link": link.strip(),
            "data": data_iso(data),
            "site": feed["site"],
            "site_url": feed["home"],
            "tipos": classificar(titulo),
            "preco": preco(titulo),
        })
    return saida


def main():
    destino = Path(sys.argv[1] if len(sys.argv) > 1 else "promocoes.json")
    anterior = {}
    if destino.exists():
        try:
            anterior = {i["link"]: i for i in json.loads(destino.read_text("utf-8")).get("itens", [])}
        except (ValueError, KeyError):
            anterior = {}
    itens, status = [], []
    for feed in FEEDS:
        try:
            novos = ler_feed(feed)
            itens.extend(novos)
            status.append({"site": feed["site"], "ok": True, "itens": len(novos)})
        except Exception as e:  # um site fora do ar não derruba os outros
            print(f"Falha em {feed['site']}: {e}", file=sys.stderr)
            antigos = [i for i in anterior.values() if i["site"] == feed["site"]]
            itens.extend(antigos)
            status.append({"site": feed["site"], "ok": False, "itens": len(antigos)})
    vistos, unicos = set(), []
    for i in itens:
        if i["link"] not in vistos:
            vistos.add(i["link"])
            unicos.append(i)
    unicos.sort(key=lambda i: i["data"] or "", reverse=True)
    destino.write_text(json.dumps({
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
        "fontes": status,
        "itens": unicos,
    }, ensure_ascii=False, indent=1), "utf-8")
    print(f"{len(unicos)} itens gravados em {destino}")


if __name__ == "__main__":
    main()
