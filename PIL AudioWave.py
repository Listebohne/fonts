import pyaudio
import numpy as np
import time
import audioop
import math
import struct
from PIL import Image, ImageDraw, ImageTk, ImageFont
import tkinter as tk

colorMin = 0
dbSum = 0
dbCounter = 0
curSec = 0
prevSec = 0
dbValue = 0

# Funktion, um Audiodaten zu lesen
def read_audio(stream, chunk):
    data = stream.read(chunk)
    return np.frombuffer(data, dtype=np.int16)

def skalieren(wert, klein_min, klein_max, gross_min, gross_max):
    # Berechne den Anteil des Werts im kleineren Bereich
    anteil = (wert - gross_min) / (gross_max - gross_min)

    # Skaliere den Anteil auf den größeren Bereich
    skaliert_wert = klein_min + anteil * (klein_max - klein_min)

    return skaliert_wert

def round_int(x):
    if x in [float("-inf"),float("inf")]: return float("nan")
    return int(round(x))

def calculate_decibel( data ):
    rms = audioop.rms(data,2)
    db = 20 * np.log10(rms)
    if math.isnan(round_int(abs(db))):
        return 0
    return int(round_int(abs(db)))


def update_decibel(_data, _dbValue):
    global dbSum
    global dbCounter
    global curSec
    global prevSec
    db = calculate_decibel(_data)
    #print('db ', rms)

    if not db==0:
        #print('db ',db)
        dbCounter += 1
        #print('Counter ',dbCounter)
        dbSum += db
        #print('Sum ', dbSum)
    curSec = time.time()
    if curSec - prevSec >= 0.5 and not dbCounter == 0:
        prevSec = curSec
        dbMiddle = int(dbSum/dbCounter)
        dbSum = 0
        dbCounter = 0
        return str(dbMiddle)
    else:
        return str(_dbValue)


# Funktion für die Aktualisierung der Audiowave-Anzeige
def update_audio_wave(frame, stream, chunk, image, draw, label):
    global colorMin
    global dbValue
    data = read_audio(stream, chunk)

    draw.rectangle([(0, 0), (chunk / 8 + 44, 240)], fill="WHITE")

    font = ImageFont.truetype(r'C:\Users\liste\Downloads\Mosk Extra-Bold 800.ttf', 50)
    dbValue = update_decibel(data, dbValue)
    draw.text(((chunk / 8 + 44) / 2, (2 * 240) / 3), text=dbValue + ' db', fill='BLACK', anchor="mm", font=font)

    colorVal = 0
    for i in range(int(chunk / 8)):
        colorVal = colorVal + int(data[i])
    r = int(skalieren(abs(colorVal),0,255,0,200000))
    if r>255:
        r=255
    g = 255-r
    b = 255 - abs(r-g)
    if r<10:
        color=(0,0,0)
    else:
        color= (r,g,b)
    for i in range(int(chunk/8)):
        if not i % 5 == 0:
            draw.line([(i+22, 240/3), ((i+22, 240/3 + 1.30*(int(data[i] / 240))))], fill=color)
    photo = ImageTk.PhotoImage(image)
    label.config(image=photo)
    label.image = photo


# Hauptfunktion
def main():
    chunk = 2048  # Anzahl der Frames pro Buffer
    format = pyaudio.paInt16  # Datenformat
    channels = 1  # Mono-Aufnahme
    rate = 88100  # Abtastrate (in Hz)

    p = pyaudio.PyAudio()
    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    # Einrichten des Tkinter-Fensters
    root = tk.Tk()
    root.title("Echtzeit-Audiowave")

    image = Image.new("RGB", (int(chunk/8+44), 240), "black")
    draw = ImageDraw.Draw(image)
    photo = ImageTk.PhotoImage(image)
    label = tk.Label(root, image=photo)
    label.pack()

    def update():
        update_audio_wave(None, stream, chunk, image, draw, label)
        label.after(10, update)

    label.after(10, update)

    root.mainloop()

    stream.stop_stream()
    stream.close()
    p.terminate()


if __name__ == "__main__":
    main()
