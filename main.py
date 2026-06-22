from kivy.uix.gridlayout import GridLayout
import math
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse
from kivy.core.window import Window

# Fenstergröße für PC-Test an Smartphone-Format anpassen
Window.size = (400, 700)

class SwipeSpielfeld(Widget):
    def __init__(self, app_instanz, **kwargs):
        super(SwipeSpielfeld, self).__init__(**kwargs)
        self.app = app_instanz
        self.buchstaben_positionen = []  # Speichert [(x, y, "A"), ...]
        self.aktive_auswahl = []         # Speichert Indizes der aktuell gewischten Buchstaben
        self.aktuelle_maus_pos = None
        self.bind(size=self.aktualisiere_spielfeld, pos=self.aktualisiere_spielfeld)

    def aktualisiere_spielfeld(self, *args):
        """Berechnet die kreisförmige Anordnung der Buchstaben neu."""
        self.buchstaben_positionen = []
        self.aktive_auswahl = []
        self.aktuelle_maus_pos = None
        
        if not self.app.levels:
            return

        aktuelles_level = self.app.levels[self.app.aktuelles_level_index]
        buchstaben = aktuelles_level["buchstaben"]
        anzahl = len(buchstaben)
        
        # Mittelpunkt und Radius des Buchstaben-Kreises bestimmen
        mitte_x = self.center_x
        mitte_y = self.center_y
        radius = min(self.width, self.height) * 0.35
        
        for i, b in enumerate(buchstaben):
            # Winkel berechnen für gleichmäßige Verteilung im Kreis
            winkel = (2 * math.pi / anzahl) * i - (math.pi / 2)
            bx = mitte_x + radius * math.cos(winkel)
            by = mitte_y + radius * math.sin(winkel)
            self.buchstaben_positionen.append((bx, by, b))
            
        self.zeichne_alles()

    def zeichne_alles(self):
        """Übernimmt das komplette Rendering der Kreise, Linien und Buchstaben."""
        self.canvas.clear()
        with self.canvas:
            # 1. Gezogene Verbindungslinien zeichnen
            if self.aktive_auswahl:
                Color(0.9, 0.6, 0.1, 0.8)  # Orangefarbene Linie
                punkte = []
                for idx in self.aktive_auswahl:
                    punkte.extend([self.buchstaben_positionen[idx][0], self.buchstaben_positionen[idx][1]])
                if self.aktuelle_maus_pos and len(punkte) >= 2:
                    punkte.extend([self.aktuelle_maus_pos[0], self.aktuelle_maus_pos[1]])
                Line(points=punkte, width=5, joint='round', cap='round')

            # 2. Die Buchstaben-Kreise zeichnen
            for i, (bx, by, b) in enumerate(self.buchstaben_positionen):
                if i in self.aktive_auswahl:
                    Color(0.2, 0.8, 0.2, 1)  # Grün wenn ausgewählt
                else:
                    Color(0.2, 0.6, 1, 1)    # Blau im Normalzustand
                
                kreis_radius = 35
                Ellipse(pos=(bx - kreis_radius, by - kreis_radius), size=(kreis_radius * 2, kreis_radius * 2))
                
                # Buchstaben-Text per Label-Rendering auf Canvas bringen ist komplex,
                # daher nutzen wir hier das Canvas-Zeichnen und aktualisieren parallel das obere Textfeld.

    def _get_getroffener_buchstabe(self, touch_pos):
        """Prüft, ob der Finger nah genug an einem Buchstaben ist (Kollisionsabfrage)."""
        for i, (bx, by, b) in enumerate(self.buchstaben_positionen):
            distanz = math.sqrt((touch_pos[0] - bx)**2 + (touch_pos[1] - by)**2)
            if distanz < 40:  # Toleranzradius für die Berührung
                return i
        return None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            idx = self._get_getroffener_buchstabe(touch.pos)
            if idx is not None:
                self.aktive_auswahl = [idx]
                self.aktuelle_maus_pos = touch.pos
                self.app.aktualisiere_wisch_text(self.buchstaben_positionen[idx][2])
                self.zeichne_alles()
                return True
        return super(SwipeSpielfeld, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.aktive_auswahl:
            self.aktuelle_maus_pos = touch.pos
            idx = self._get_getroffener_buchstabe(touch.pos)
            
            # Wenn ein neuer Buchstabe getroffen wurde, der noch nicht in der Kette ist
            if idx is not None and idx not in self.aktive_auswahl:
                self.aktive_auswahl.append(idx)
                # Aktualisiere das Textfeld oben im Spiel
                wort = "".join([self.buchstaben_positionen[i][2] for i in self.aktive_auswahl])
                self.app.aktualisiere_wisch_text(wort)
                
            self.zeichne_alles()
            return True
        return super(SwipeSpielfeld, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.aktive_auswahl:
            # Wort aus der Kette zusammenbauen
            wort = "".join([self.buchstaben_positionen[i][2] for i in self.aktive_auswahl])
            self.app.wort_pruefen(wort)
            
            # Wisch-Pfad zurücksetzen
            self.aktive_auswahl = []
            self.aktuelle_maus_pos = None
            self.zeichne_alles()
            return True
        return super(SwipeSpielfeld, self).on_touch_up(touch)

class WortGuruApp(App):
    def build(self):
        # 1. Level-Datenbank definieren
        self.levels = [
            {"buchstaben": ["A", "B", "E", "N", "D"], "loesungen": ["ABEND", "BAND", "DEN", "RAD", "AN"]},
            {"buchstaben": ["S", "P", "I", "E", "L"], "loesungen": ["SPIEL", "EIP", "SEIL", "LIPPS", "LIES"]},
            {"buchstaben": ["R", "E", "I", "S", "E", "N"], "loesungen": ["REISEN", "REISE", "EINES", "REIS", "SEIN", "EINS", "NIE", "EIS"]},
            {"buchstaben": ["G", "A", "R", "T", "E", "N"], "loesungen": ["GARTEN", "GRATEN", "AGERN", "RAGTE", "SARG", "GERN", "ART", "TAG"]},
            {"buchstaben": ["S", "P", "E", "I", "S", "E"], "loesungen": ["SPEISE", "SPEIS", "PIESE", "PESS", "SEE", "EIS", "PASS"]},
            {"buchstaben": ["T", "R", "A", "U", "B", "E"], "loesungen": ["TRAUBE", "TAUBE", "BRAUT", "RAUBE", "BART", "RAUB", "TAUB", "MUT"]},
            {"buchstaben": ["B", "L", "U", "M", "E"], "loesungen": ["BLUME", "BLUM", "BULL", "LUME", "BUM", "MUT", "LUB"]},
            {"buchstaben": ["F", "R", "E", "U", "D", "E"], "loesungen": ["FREUDE", "FREUD", "RUFE", "ERDE", "REDE", "RUF", "DER", "RUD"]},
            {"buchstaben": ["K", "E", "R", "Z", "E"], "loesungen": ["KERZE", "ERZE", "KREZ", "ECK", "ERZ", "REH"]},
            {"buchstaben": ["S", "T", "R", "A", "N", "D"], "loesungen": ["STRAND", "SAND", "RAD", "ART", "DART", "RANT"]},
            {"buchstaben": ["W", "I", "N", "T", "E", "R"], "loesungen": ["WINTER", "WIRT", "REIN", "WEIN", "NITE", "WER", "WEN"]},
            {"buchstaben": ["S", "O", "M", "M", "E", "R"], "loesungen": ["SOMMER", "MOOS", "ROME", "EMOR", "OOM", "MEM"]},
            {"buchstaben": ["S", "O", "N", "N", "E"], "loesungen": ["SONNE", "NEON", "NONS", "SON", "NEN", "ONE"]},
            {"buchstaben": ["S", "T", "E", "R", "N"], "loesungen": ["STERN", "ERNST", "REST", "NEST", "ERST", "DEN"]},
            {"buchstaben": ["W", "O", "L", "K", "E"], "loesungen": ["WOLKE", "WELK", "WOLK", "ELK", "LEK", "WOK"]},
            {"buchstaben": ["R", "E", "G", "E", "N"], "loesungen": ["REGEN", "GERNE", "REGE", "ENGE", "GERN", "GEN"]},
            {"buchstaben": ["S", "C", "H", "N", "E", "E"], "loesungen": ["SCHNEE", "SEHN", "ECHT", "SEE", "EHE", "NEH"]},
            {"buchstaben": ["P", "F", "L", "A", "N", "Z", "E"], "loesungen": ["PFLANZE", "LANZE", "PFALZ", "PLAN", "ALPEN", "ELF", "ZAN"]},
            {"buchstaben": ["F", "E", "N", "S", "T", "E", "R"], "loesungen": ["FENSTER", "FERN", "FEST", "ERST", "NEST", "SENF", "TEER"]},
            {"buchstaben": ["K", "U", "E", "C", "H", "E"], "loesungen": ["KUECHE", "KUECH", "ECHE", "KUE", "ECH", "EUH"]},
            {"buchstaben": ["Z", "I", "M", "M", "E", "R"], "loesungen": ["ZIMMER", "REIZ", "ZIER", "REIM", "IMMER", "MIR"]},
            {"buchstaben": ["M", "E", "S", "S", "E", "R"], "loesungen": ["MESSER", "MESSE", "MEER", "REIS", "ERST", "SEE"]},
            {"buchstaben": ["G", "A", "B", "E", "L"], "loesungen": ["GABEL", "ALGE", "BALG", "EGAL", "GELB", "LAB"]},
            {"buchstaben": ["L", "O", "E", "F", "F", "E", "L"], "loesungen": ["LOEFFEL", "LOEFF", "FELL", "ELF", "LOE", "OFF"]},
            {"buchstaben": ["T", "E", "L", "L", "E", "R"], "loesungen": ["TELLER", "TELL", "ELLER", "LEER", "TEER", "REEL"]},
            {"buchstaben": ["F", "L", "A", "S", "C", "H", "E"], "loesungen": ["FLASCHE", "LACHS", "SCHAF", "FALSCH", "CHEF", "FELS"]},
            {"buchstaben": ["W", "A", "S", "S", "E", "R"], "loesungen": ["WASSER", "RASSE", "WASSER", "RASS", "ASS", "WER"]},
            {"buchstaben": ["K", "A", "F", "F", "E", "E"], "loesungen": ["KAFFEE", "KAFF", "AFFE", "KAF", "EFF", "AEE"]},
            {"buchstaben": ["K", "U", "C", "H", "E", "N"], "loesungen": ["KUCHEN", "KUCH", "UCHEN", "NECH", "KUN", "EUN"]},
            {"buchstaben": ["B", "R", "O", "T"], "loesungen": ["BROT", "TOR", "ROT", "BOT", "ORT", "BOR"]},
            {"buchstaben": ["B", "U", "T", "T", "E", "R"], "loesungen": ["BUTTER", "BRUT", "BUTE", "RUTE", "TUBE", "BUT"]},
            {"buchstaben": ["K", "A", "E", "S", "E"], "loesungen": ["KAESE", "KASE", "ESEK", "SEE", "KAE", "ASE"]},
            {"buchstaben": ["F", "L", "E", "I", "S", "C", "H"], "loesungen": ["FLEISCH", "FLEIS", "CHEF", "FELS", "SEIL", "ICH"]},
            {"buchstaben": ["F", "I", "S", "C", "H"], "loesungen": ["FISCH", "FICH", "ISH", "ICH", "FIS", "SIH"]},
            {"buchstaben": ["V", "O", "G", "E", "L"], "loesungen": ["VOGEL", "VOLG", "GELO", "LOG", "VOG", "GEL"]},
            {"buchstaben": ["K", "A", "T", "Z", "E"], "loesungen": ["KATZE", "AKTE", "KATE", "ZEIT", "AKT", "ZAT"]},
            {"buchstaben": ["H", "U", "N", "D"], "loesungen": ["HUND", "DUN", "HUD", "UND", "HUN", "NUD"]},
            {"buchstaben": ["P", "F", "E", "R", "D"], "loesungen": ["PFERD", "FRED", "ERDF", "PER", "DER", "RED"]},
            {"buchstaben": ["M", "A", "U", "S"], "loesungen": ["MAUS", "AMUS", "MUSA", "AUS", "SAM", "MAU"]},
            {"buchstaben": ["R", "A", "T", "T", "E"], "loesungen": ["RATTE", "RATE", "TART", "ART", "TAT", "RAT"]},
            {"buchstaben": ["F", "U", "C", "H", "S"], "loesungen": ["FUCHS", "SUCH", "FUSH", "CHUS", "UCH", "SUH"]},
            {"buchstaben": ["W", "O", "L", "F"], "loesungen": ["WOLF", "WLOF", "LOWF", "LOW", "WOL", "OLF"]},
            {"buchstaben": ["B", "A", "E", "R"], "loesungen": ["BAER", "AERB", "BAR", "RAB", "AER", "BAE"]},
            {"buchstaben": ["L", "O", "E", "W", "E"], "loesungen": ["LOEWE", "LOEW", "WELO", "LOE", "WEL", "OWE"]},
            {"buchstaben": ["T", "I", "G", "E", "R"], "loesungen": ["TIGER", "TIER", "REIT", "GERN", "GUT", "TOR"]},
            {"buchstaben": ["E", "L", "E", "F", "A", "N", "T"], "loesungen": ["ELEFANT", "ELF", "FANT", "FALN", "TAL", "ALF"]},
            {"buchstaben": ["G", "I", "R", "A", "F", "F", "E"], "loesungen": ["GIRAFFE", "RAFF", "AFFE", "GRAF", "GIR", "AFI"]},
            {"buchstaben": ["Z", "E", "B", "R", "A"], "loesungen": ["ZEBRA", "BAR", "RAB", "ERA", "ZEB", "RBA"]},
            {"buchstaben": ["A", "F", "F", "E", "N"], "loesungen": ["AFFEN", "AFFE", "NAFF", "FAN", "AFE", "NFA"]},
            {"buchstaben": ["S", "C", "H", "A", "F"], "loesungen": ["SCHAF", "FACH", "SACH", "ASF", "ACH", "FAS"]},
            {"buchstaben": ["Z", "I", "E", "G", "E"], "loesungen": ["ZIEGE", "ZEIG", "EGEL", "GEIZ", "EIG", "ZIE"]},
            {"buchstaben": ["K", "U", "H"], "loesungen": ["KUH", "UHK", "HKU", "UKH", "KHU", "HKU"]},
            {"buchstaben": ["S", "C", "H", "W", "E", "I", "N"], "loesungen": ["SCHWEIN", "WEIN", "SCHI", "NICH", "WEIS", "ICH"]},
            {"buchstaben": ["H", "U", "H", "N"], "loesungen": ["HUHN", "UNH", "HNU", "HUN", "UNH", "NHU"]},
            {"buchstaben": ["E", "N", "T", "E"], "loesungen": ["ENTE", "TEEN", "ETEN", "NET", "TEN", "ENT"]},
            {"buchstaben": ["G", "A", "N", "S"], "loesungen": ["GANS", "SANG", "NAGS", "GAS", "SAG", "NAS"]},
            {"buchstaben": ["T", "A", "U", "B", "E"], "loesungen": ["TAUBE", "TAUB", "TUBE", "BAUT", "TAB", "AUT"]},
            {"buchstaben": ["A", "D", "L", "E", "R"], "loesungen": ["ADLER", "RAD", "DER", "LAD", "ALE", "ERA"]},
            {"buchstaben": ["E", "U", "L", "E"], "loesungen": ["EULE", "LEUE", "EUL", "LEU", "ELE", "UEE"]},
            {"buchstaben": ["A", "M", "S", "E", "L"], "loesungen": ["AMSEL", "MALE", "LEAM", "SAM", "MAL", "ALS"]},
            {"buchstaben": ["M", "E", "I", "S", "E"], "loesungen": ["MEISE", "MIES", "SEIM", "EIS", "MIR", "EMI"]},
            {"buchstaben": ["S", "P", "A", "T", "Z"], "loesungen": ["SPATZ", "SPAT", "PAST", "TAP", "PAS", "SAT"]},
            {"buchstaben": ["F", "L", "I", "E", "G", "E"], "loesungen": ["FLIEGE", "FEIL", "LIEG", "ELF", "GEL", "ILE"]},
            {"buchstaben": ["B", "I", "E", "N", "E"], "loesungen": ["BIENE", "BEIN", "EBEN", "NIE", "BEI", "EIN"]},
            {"buchstaben": ["W", "E", "S", "P", "E", "N"], "loesungen": ["WESPEN", "WESP", "PEWN", "WEN", "PES", "SEN"]},
            {"buchstaben": ["M", "U", "E", "C", "K", "E"], "loesungen": ["MUECKE", "MUEC", "KECM", "MUE", "ECK", "KEM"]},
            {"buchstaben": ["S", "P", "I", "N", "N", "E"], "loesungen": ["SPINNE", "SPIN", "PINE", "PIN", "SIN", "NIE"]},
            {"buchstaben": ["K", "R", "E", "B", "S"], "loesungen": ["KREBS", "KERB", "REBK", "ERB", "REK", "BES"]},
            {"buchstaben": ["F", "I", "S", "C", "H", "E"], "loesungen": ["FISCHE", "FISCH", "CHEF", "SEIL", "ICH", "SIE"]},
            {"buchstaben": ["F", "R", "O", "S", "C", "H"], "loesungen": ["FROSCH", "FORS", "ROCH", "OFR", "ROH", "ORS"]},
            {"buchstaben": ["K", "R", "O", "E", "T", "E"], "loesungen": ["KROETE", "KROT", "ROTE", "TOR", "ROT", "OET"]},
            {"buchstaben": ["E", "C", "H", "S", "E"], "loesungen": ["ECHSE", "ECHS", "SECH", "ECK", "SEC", "EHS"]},
            {"buchstaben": ["S", "C", "H", "L", "A", "N", "G", "E"], "loesungen": ["SCHLANGE", "LANG", "NACH", "GANS", "ELAN", "ACH"]},
            {"buchstaben": ["S", "C", "H", "I", "L", "D", "K", "R", "O", "E", "T", "E"], "loesungen": ["SCHILD", "KROT", "ROTE", "DOCH", "LICH", "DIR"]},
            {"buchstaben": ["H", "A", "I", "F", "I", "S", "C", "H"], "loesungen": ["HAIFISCH", "FISCH", "HAIF", "FACH", "HAIN", "ICH"]},
            {"buchstaben": ["W", "A", "L"], "loesungen": ["WAL", "ALW", "LWA", "AWL", "LAW", "WLA"]},
            {"buchstaben": ["D", "E", "L", "F", "I", "N"], "loesungen": ["DELFIN", "FEIN", "FELD", "LIND", "ELF", "DIN"]},
            {"buchstaben": ["R", "O", "B", "B", "E"], "loesungen": ["ROBBE", "ROBB", "BOBR", "ROB", "BOB", "ORB"]},
            {"buchstaben": ["P", "I", "N", "G", "U", "I", "N"], "loesungen": ["PINGUIN", "PIN", "NIP", "GIN", "ING", "PIG"]},
            {"buchstaben": ["E", "I", "S", "B", "A", "E", "R"], "loesungen": ["EISBAER", "BAER", "REIS", "SIEB", "BAR", "EIS"]},
            {"buchstaben": ["R", "E", "N", "T", "I", "E", "R"], "loesungen": ["RENTIER", "TIER", "REIT", "TEER", "REIN", "NIE"]},
            {"buchstaben": ["T", "R", "A", "U", "M"], "loesungen": ["TRAUM", "MAUT", "RAUM", "ARM"]}
        ]
        self.aktuelles_level_index = 0
        self.gefundene_woerter = []
        self.aktuelles_wort = ""

        # Haupt-Layout
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Level-Anzeige ganz oben
        self.level_titel = Label(text=f"Level {self.aktuelles_level_index + 1}", font_size='24sp', size_hint_y=0.1)
        self.layout.add_widget(self.level_titel)

        # Anzeige für das aktuell getippte Wort
        self.wort_anzeige = Label(text="Tippe Buchstaben...", font_size='30sp', size_hint_y=0.15)
        self.layout.add_widget(self.wort_anzeige)

        # Anzeige der bereits gefundenen Wörter
        self.ergebnis_anzeige = Label(text="Gefunden: 0", font_size='18sp', size_hint_y=0.15)
        self.layout.add_widget(self.ergebnis_anzeige)

        # Behälter für die Buchstaben-Tasten (wird dynamisch geleert und befüllt)
        self.tasten_grid = GridLayout(cols=3, spacing=10, size_hint_y=0.4)
        self.layout.add_widget(self.tasten_grid)

        # Aktions-Tasten (Prüfen & Löschen)
        aktions_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.1)
        
        btn_loeschen = Button(text="Löschen", font_size='18sp', background_color=(1, 0.3, 0.3, 1))
        btn_loeschen.bind(on_press=self.wort_loeschen)
        
        btn_pruefen = Button(text="Prüfen", font_size='18sp', background_color=(0.3, 0.8, 0.3, 1))
        btn_pruefen.bind(on_press=self.wort_pruefen)
        
        aktions_layout.add_widget(btn_loeschen)
        aktions_layout.add_widget(btn_pruefen)
        self.layout.add_widget(aktions_layout)

        # DER NEUE BUTTON: Zum nächsten Level/Buchstaben springen
        btn_naechstes = Button(text="Nächstes Level ➔", font_size='20sp', background_color=(0.9, 0.6, 0.1, 1), size_hint_y=0.1)
        btn_naechstes.bind(on_press=self.naechstes_level)
        self.layout.add_widget(btn_naechstes)

        # Zuerst das erste Level laden
        self.lade_level()

        return self.layout

    def lade_level(self):
        # Setzt das aktuelle Wort und die Funde zurück
        self.aktuelles_wort = ""
        self.gefundene_woerter = []
        self.wort_anzeige.text = "Tippe Buchstaben..."
        self.ergebnis_anzeige.text = "Gefunden: 0"
        self.level_titel.text = f"Level {self.aktuelles_level_index + 1}"

        # Altes Buchstaben-Raster leeren
        self.tasten_grid.clear_widgets()

        # Neue Tasten für das aktuelle Level erzeugen
        aktuelles_level = self.levels[self.aktuelles_level_index]
        for buchstabe in aktuelles_level["buchstaben"]:
            btn = Button(text=buchstabe, font_size='24sp', background_color=(0.2, 0.6, 1, 1))
            btn.bind(on_press=self.buchstabe_getippt)
            self.tasten_grid.add_widget(btn)

    def buchstabe_getippt(self, instance):
        self.aktuelles_wort += instance.text
        self.wort_anzeige.text = self.aktuelles_wort

    def wort_loeschen(self, instance):
        self.aktuelles_wort = ""
        self.wort_anzeige.text = "Tippe Buchstaben..."

    def wort_pruefen(self, instance):
        aktuelles_level = self.levels[self.aktuelles_level_index]
        wort = self.aktuelles_wort
        
        if wort in aktuelles_level["loesungen"] and wort not in self.gefundene_woerter:
            self.gefundene_woerter.append(wort)
            self.ergebnis_anzeige.text = f"Gefunden: {', '.join(self.gefundene_woerter)}"
            self.wort_anzeige.text = "Richtig!"
        elif wort in self.gefundene_woerter:
            self.wort_anzeige.text = "Schon gefunden!"
        else:
            self.wort_anzeige.text = "Falsches Wort!"
        self.aktuelles_wort = ""

    def naechstes_level(self, instance):
        # Zum nächsten Index springen (am Ende fängt es wieder von vorne an)
        self.aktuelles_level_index = (self.aktuelles_level_index + 1) % len(self.levels)
        self.lade_level()

if __name__ == '__main__':
    WortGuruApp().run()
