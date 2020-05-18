import random as rand
import numpy as np
import xlwt
import odslib


##########################
def create_missionsfeld(blau, rot, neut, att):
    total = blau + rot + neut + att
    print
    'total', total
    list = []
    for i in range(blau):
        list.append('blau')
    for i in range(rot):
        list.append('rot')
    for i in range(neut):
        list.append('neut')
    for i in range(att):
        list.append('att')
    rand.shuffle(list)
    return list


############################ Einlesen
def woerter_einlesen(anzahl, filename):
    save = open(filename, 'r')
    next(save)
    list = []
    for i, line in enumerate(save):  # i zeilennummer, line is inhalt der zeile
        line = line.strip()
        list.append(line)
    save.close()
    # print list

    auswahl = []
    for i in range(anzahl):
        temp = rand.choice(list)
        list.remove(temp)  # keine doppelung
        auswahl.append(temp)

    return auswahl


############################### Spiel-Parameter
blau = 10  # Team blau
rot = 10  # Team rot
neut = 4  # neutrale Felder
att = 1  # Attentaeter

laenge = 5
breite = 5
anzahl = 25

# feld = (length, width)

############################### Hauptprogramm
### mission schema fuer spieler erzeugen
mission = create_missionsfeld(blau, rot, neut, att)
mission = np.array(mission)

mission_print = mission.reshape((laenge, breite))
print
'Missionfeld: \n', mission_print

### Spielfeld erzeugen
woerterbuch = 'dic.dat'
# woerterbuch = 'dic_eng.dat'

spielfeld = woerter_einlesen(anzahl, woerterbuch)
spielfeld = np.array(spielfeld)

spielfeld_print = spielfeld.reshape((laenge, breite))
print
spielfeld_print

####################### export nach excel
doc = odslib.ODS()


def write_cell(x, y, inhalt):
    doc.content.getCell(x, y).stringValue(inhalt)
    doc.content.getCell(x, y).setCellColor('red')


for i, wort in enumerate(spielfeld):
    # print i,wort
    # print 'x', i%breite
    x = i % breite
    y = i / int(laenge)
    # print 'y', i/int(laenge)
    doc.content.getCell(x, y).stringValue(wort)

doc.save("spielfeld.ods")

doc = odslib.ODS()
for i, wort in enumerate(mission):
    # print i,wort
    # print 'x', i%breite
    x = i % breite
    y = i / int(laenge)
    # print 'y', i/int(laenge)
    doc.content.getCell(x, y).stringValue(wort)
    if wort == 'blau': doc.content.getCell(x, y).setCellColor('#0000FF')  # team blau
    if wort == 'rot': doc.content.getCell(x, y).setCellColor('#FF0000')  # team rot
    if wort == 'neut': doc.content.getCell(x, y).setCellColor('#FF00FF')  # neutral
    if wort == 'att': doc.content.getCell(x, y).setCellColor('#00FF00')  # attentat
    doc.content.getCell(x, y).stringValue(spielfeld[i])

doc.save("nicht_anklicken_missionsfeld.ods")