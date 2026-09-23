import requests
import json
import time

# ELENCO DELLE TOP 5 ZONE DI RACCOLTA PER OGNUNA DELLE 8 REGIONI DEL NORD ITALIA
zone_top_nord_italia = [
    # PIEMONTE
    {"nome": "Val Sesia / Alagna", "lat": 45.85, "lon": 8.00},
    {"nome": "Valli Cuneesi / Val Vermenagna", "lat": 44.28, "lon": 7.53},
    {"nome": "Val di Susa e Chisone", "lat": 45.13, "lon": 7.05},
    {"nome": "Val Vigezzo (VCO)", "lat": 46.13, "lon": 8.50},
    {"nome": "Appennino Alessandrino", "lat": 44.68, "lon": 8.85},
    # VALLE D'AOSTA
    {"nome": "Val d'Ayas", "lat": 45.81, "lon": 7.73},
    {"nome": "Valtournenche", "lat": 45.88, "lon": 7.60},
    {"nome": "Val de Rhêmes", "lat": 45.56, "lon": 7.12},
    {"nome": "Val Veny / Courmayeur", "lat": 45.78, "lon": 6.90},
    {"nome": "Valle del Gran San Bernardo", "lat": 45.85, "lon": 7.20},
    # LOMBARDIA
    {"nome": "Valtellina / Val Masino", "lat": 46.22, "lon": 9.63},
    {"nome": "Val Camonica", "lat": 46.02, "lon": 10.33},
    {"nome": "Val Brembana", "lat": 45.96, "lon": 9.68},
    {"nome": "Val Seriana", "lat": 45.91, "lon": 9.95},
    {"nome": "Oltrepò Pavese", "lat": 44.68, "lon": 9.25},
    # TRENTINO-ALTO ADIGE
    {"nome": "Val di Fiemme / Val di Fassa", "lat": 46.28, "lon": 11.58},
    {"nome": "Val Rendena / Campiglio", "lat": 46.16, "lon": 10.76},
    {"nome": "Val di Sole e Pejo", "lat": 46.35, "lon": 10.78},
    {"nome": "Val Pusteria / Bressanone", "lat": 46.75, "lon": 11.90},
    {"nome": "Altopiano di Pinè / Lagorai", "lat": 46.13, "lon": 11.24},
    # VENETO
    {"nome": "Cadore e Ampezzano", "lat": 46.48, "lon": 12.37},
    {"nome": "Altopiano di Asiago 7 Comuni", "lat": 45.87, "lon": 11.51},
    {"nome": "Alpago e Cansiglio", "lat": 46.12, "lon": 12.40},
    {"nome": "Lessinia (VR)", "lat": 45.68, "lon": 11.02},
    {"nome": "Agordino / Val Cordevole", "lat": 46.28, "lon": 11.98},
    # FRIULI-VENEZIA GIULIA
    {"nome": "Tarvisiano e Val Canale", "lat": 46.50, "lon": 13.57},
    {"nome": "Carnia / Tolmezzo", "lat": 46.40, "lon": 12.98},
    {"nome": "Val Cellina", "lat": 46.17, "lon": 12.52},
    {"nome": "Piancavallo", "lat": 46.10, "lon": 12.51},
    {"nome": "Valli del Natisone", "lat": 46.15, "lon": 13.50},
    # LIGURIA
    {"nome": "Val d'Aveto / Monte Penna", "lat": 44.52, "lon": 9.45},
    {"nome": "Val Trebbia Ligure", "lat": 44.57, "lon": 9.18},
    {"nome": "Val Bormida (SV)", "lat": 44.35, "lon": 8.23},
    {"nome": "Val di Vara (SP)", "lat": 44.30, "lon": 9.75},
    {"nome": "Alpi Liguri / Triora", "lat": 43.99, "lon": 7.76},
    # EMILIA-ROMAGNA
    {"nome": "Val di Taro / Borgotaro", "lat": 44.48, "lon": 9.76},
    {"nome": "Val Nure e Val Trebbia", "lat": 44.60, "lon": 9.53},
    {"nome": "Appennino Reggiano / Ventasso", "lat": 44.38, "lon": 10.28},
    {"nome": "Alto Appennino Modenese", "lat": 44.18, "lon": 10.78},
    {"nome": "Appennino Bolognese / Corno alle Scale", "lat": 44.12, "lon": 10.83}
]

lat_min, lat_max = 44.0, 46.8
lon_min, lon_max = 7.0, 13.5
step = 0.25

coords_dict = {}
for z in zone_top_nord_italia:
    coords_dict[(round(z["lat"], 2), round(z["lon"], 2))] = z["nome"]

lat = lat_min
while lat <= lat_max:
    lon = lon_min
    while lon <= lon_max:
        key = (round(lat, 2), round(lon, 2))
        if key not in coords_dict:
            coords_dict[key] = None
        lon += step
    lat += step

coords = list(coords_dict.keys())
dati_finali = []

print(f"Interrogazione Open-Meteo per {len(coords)} punti nel Nord Italia...", flush=True)

chunk_size = 25
headers = {'User-Agent': 'MappaFunghiBot/1.0'}

for i in range(0, len(coords), chunk_size):
    chunk = coords[i:i+chunk_size]
    lats = ",".join([str(c[0]) for c in chunk])
    lons = ",".join([str(c[1]) for c in chunk])
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&daily=temperature_2m_mean,precipitation_sum,wind_speed_10m_max&past_days=14&forecast_days=1&timezone=Europe%2FRome"
    
    print(f" Scaricamento blocco {i//chunk_size + 1}/{(len(coords)+chunk_size-1)//chunk_size}...", flush=True)
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            results = data if isinstance(data, list) else [data]
            
            for idx, loc_data in enumerate(results):
                if "daily" not in loc_data: 
                    continue
                    
                piogge = loc_data["daily"]["precipitation_sum"]
                temps = loc_data["daily"]["temperature_2m_mean"]
                venti = loc_data["daily"]["wind_speed_10m_max"]
                
                pioggia_14gg = sum([p for p in piogge[:-1] if p is not None])
                temp_oggi = temps[-1] if temps[-1] is not None else 15
                vento_oggi = venti[-1] if venti[-1] is not None else 5
                
                punteggio = 0
                if pioggia_14gg >= 40: 
                    punteggio += 3
                elif pioggia_14gg >= 20: 
                    punteggio += 1.5
                
                if 14 <= temp_oggi <= 22: 
                    punteggio += 2
                elif (10 <= temp_oggi < 14) or (22 < temp_oggi <= 25): 
                    punteggio += 1
                
                if vento_oggi < 15: 
                    punteggio += 1
                
                if punteggio >= 5: 
                    prob, colore, intensita = "Crescita", "#32d74b", 1.0
                elif punteggio >= 3: 
                    prob, colore, intensita = "In Incubazione", "#ffd60a", 0.55
                else: 
                    prob, colore, intensita = "Fermo", "#ff453a", 0.2
                
                c_lat, c_lon = chunk[idx][0], chunk[idx][1]
                nome_zona = coords_dict.get((c_lat, c_lon))
                
                dati_finali.append({
                    "nome": nome_zona,
                    "lat": c_lat,
                    "lon": c_lon,
                    "pioggia_14gg": round(pioggia_14gg, 1),
                    "temp_oggi": round(temp_oggi, 1),
                    "vento_oggi": round(vento_oggi, 1),
                    "probabilita": prob,
                    "colore": colore,
                    "intensita": intensita
                })
        else:
            print(f" Attenzione: HTTP {response.status_code}", flush=True)
    except Exception as e:
        print(f" Errore nel blocco {i}: {e}", flush=True)
    
    time.sleep(0.3)

with open('dati_funghi.json', 'w', encoding='utf-8') as f:
    json.dump(dati_finali, f, ensure_ascii=False, indent=4)

print(f" Fatto! {len(dati_finali)} punti salvati in dati_funghi.json", flush=True)
