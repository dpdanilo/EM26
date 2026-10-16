#!/usr/bin/env python3
"""
convert.py — troca só o layout: pega os dados do index.html publicado e coloca
no template.html novo, sem refazer o pipeline. Usado pelo GitHub Actions (atualizar.yml).

Uso:  python convert.py [--template template.html] [--atual index.html] [--saida index.html]
"""
import argparse
import re
import sys
from datetime import datetime, timedelta, timezone

PADRAO = re.compile(r'(<script id="dados" type="application/json">)(.*?)(</script>)', re.S)


def agora():
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("America/Sao_Paulo"))
    except Exception:
        return datetime.now(timezone(timedelta(hours=-3)))


def extrair(html):
    achados = PADRAO.findall(html)
    if len(achados) != 1:
        sys.exit(f"ERRO: esperava 1 bloco <script id=\"dados\"> no index.html atual, achei {len(achados)}.")
    dados = achados[0][1].strip()
    if dados == "__DATA__" or not dados.startswith("{"):
        sys.exit("ERRO: o index.html atual não tem dados (parece ser o template). Gere-o com build_dashboard.py.")
    return dados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default="template.html")
    ap.add_argument("--atual", default="index.html")
    ap.add_argument("--saida", default="index.html")
    a = ap.parse_args()
    with open(a.atual, encoding="utf-8") as f:
        dados = extrair(f.read())
    with open(a.template, encoding="utf-8") as f:
        tpl = f.read()
    for marca in ("__DATA__", "__BUILD__"):
        if tpl.count(marca) != 1:
            sys.exit(f"ERRO: o template deve ter {marca} exatamente uma vez.")
    # os dados já vêm escapados do index.html; a troca é literal (sem regex) para não mexer neles
    html = tpl.replace("__BUILD__", agora().strftime("%d/%m/%Y %H:%M")).replace("__DATA__", dados)
    with open(a.saida, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"OK: {a.saida} atualizado com o layout de {a.template} ({len(dados) / 1e6:.1f} MB de dados)")


if __name__ == "__main__":
    main()
