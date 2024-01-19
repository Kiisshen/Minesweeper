"""
haravasto - yksinkertainen graafinen käyttöliittymäkirjasto miinaharavalle.

@author: Mika Oja, Oulun yliopisto

Tämä kirjasto tarjoaa nipun funktioita, joilla opiskelijat voivat toteuttaa
graafisen käyttöliittymän miinaharavalle ilman, että heidän tarvitsee erikseen
opetella kokonaista käyttöliittymä- tai pelikirjastoa. Kirjasto toimii Pygletin
päällä, ja avaa pienen osan sen ominaisuuksista yksinkertaisen
funktiorajapinnan kautta. Asiasta enemmän kiinnostuneita opiskelijoita
kehotetaan tutustumaan Pygletiin:

http://pyglet.readthedocs.io

Muokkausnäppäimistä:

Muokkausnäppäimet ovat näppäimistön shift, alt, ctrl jne. näppäimiä. Pyglet
antaa ne syötteenkäsittelijäfunktioille binäärilippumuodossa (ts. kaikkien
nappien tilan yhtenä kokonaislukuna, jossa yksi bitti vastaa yhtä lippua).
Yksittäisten mod-lippujen arvojen saamiseen tarvitaan siis binääristä
AND-operaattoria (&). Operaattoria käytetään tyypillisemmin sulautettujen
ohjelmistojen ohjelmoinnissa. AND-operaatiota ei selitetä tässä, mutta alla
olevan esimerkin perusteella käyttö pitäisi onnistua. Tässä tarkistetaan onko
shift-näppäin pohjassa:

if muokkaus & haravasto.MOD_SHIFT:
    # jotaintapahtuu
"""

import pyglet
from pyglet.gl import glEnable, GL_TEXTURE_2D

HIIRI_VASEN = pyglet.window.mouse.LEFT
HIIRI_KESKI = pyglet.window.mouse.MIDDLE
HIIRI_OIKEA = pyglet.window.mouse.RIGHT

MOD_SHIFT = pyglet.window.key.MOD_SHIFT
MOD_CTRL = pyglet.window.key.MOD_CTRL
MOD_ALT = pyglet.window.key.MOD_ALT

# Grafiikan tarvitsemat muuttujat tallennetaan tähän sanakirjaan, jotta niitä
# voidaan helposti käsitellä kaikissa funktioissa. Vastaavanlainen ratkaisu
# kannattaa toteuttaa myös itse miinaharavassa, jotta käsittelijäfunktioiden
# tarvitsemat tiedot ovat helposti saatavilla.
grafiikka = {
    "ikkuna": None,
    "tausta": None,
    "taustavari": None,
    "puskuri": None,
    "spritet": [],
    "kuvat": {}
}

kasittelijat = {
    "toistuvat": [],
}

glEnable(GL_TEXTURE_2D)

def lataa_kuvat(polku):
    """
    Lataa ohjelman käyttämät oletuskuvat, joilla kuvataan miinakentän ruutuja.
    Kuvat löytyvät oletuksena spritet-kansiosta, ja voit muokata niitä mielesi
    mukaan. Jos haluat lisätä omaa grafiikkaa, voit ottaa mallia sen
    lataamiseksi tästä funktiosta.

    Funktio käyttää Pygletin resource-moduulia, joka lataa kuvat älykkäästi.
    Viittaukset yksittäisiin kuviin talletetaan sanakirjaan, jotta niihin on
    helppo viitata myöhemmin. Sanakirjan avaimissa numerot 0-8 merkkijonoina
    kuvaavat avattuja ruutuja, x miinoja, f lippuja ja välilyönti avaamatonta
    ruutua.

    Oletusgrafiikassa yhden ruudun koko on 40x40 pikseliä.

    Polku kannattaa antaa relatiivisena, eli kooditiedoston sijainnista
    katsottuna (ks. esimerkki).

    :param str polku: sijainti josta kuvat ladataan
    """

    pyglet.resource.path = [polku]
    kuvat = {}
    kuvat["0"] = pyglet.resource.image("ruutu_tyhja.png")
    for i in range(1, 9):
        kuvat[str(i)] = pyglet.resource.image("ruutu_{}.png".format(i))
    kuvat["x"] = pyglet.resource.image("ruutu_miina.png")
    kuvat[" "] = pyglet.resource.image("ruutu_selka.png")
    kuvat["f"] = pyglet.resource.image("ruutu_lippu.png")
    grafiikka["kuvat"].update(kuvat)

def lataa_sorsa(polku):
    """
    Lataa sorsapelissä tarvittavat grafiikat annetusta kansiosta. Näihin
    kuuluu itse sorsa (koko 40x40) ja ritsa jota voi käyttää tunnelmaa luovana
    taustana (koko 80x150).
    
    :param str polku: sijainti josta kuvat ladataan
    """

    pyglet.resource.path = [polku]
    sorsa = pyglet.resource.image("sorsa.png")
    ritsa = pyglet.resource.image("ritsa.png")
    grafiikka["kuvat"]["sorsa"] = sorsa
    grafiikka["kuvat"]["ritsa"] = ritsa


def luo_ikkuna(leveys=800, korkeus=600, taustavari=(240, 240, 240, 255)):
    """
    Luo peli-ikkunan grafiikan näyttämistä varten. Funktiota tulee kutsua ennen
    kuin muita tämän moduulin funktioita voidaan käyttää. Oletuksena luo
    800x600 pikselin kokoisen ikkunan vaaleanharmaalla taustalla. Näitä voidaan
    muuttaa funktion valinnaisilla argumenteilla.
    
    Jos ikkuna on jo olemassa, muuttaa ikkunan kokoa uuden luomisen sijaan.

    :param int leveys: ikkunan leveys
    :param int korkeus: ikkunan korkeus
    :param tuple taustavari: taustan väri, neljä kokonaislukua sisältävä
                             monikko (0-255, RGBA)
    """

    if grafiikka["ikkuna"] is None:
        grafiikka["ikkuna"] = pyglet.window.Window(leveys, korkeus, resizable=True)
        grafiikka["taustavari"] = taustavari
        grafiikka["tausta"] = pyglet.sprite.Sprite(
            pyglet.image.SolidColorImagePattern(taustavari).create_image(leveys, korkeus)
        )
        grafiikka["ikkuna"].set_visible(False)
        grafiikka["ikkuna"].on_close = lopeta
    else:
        muuta_ikkunan_koko(leveys, korkeus)

def muuta_ikkunan_koko(leveys, korkeus):
    """
    Muuttaa ikkunan kokoa ohjelman suorituksen aikana.

    :param int leveys: ikkunan uusi leveys
    :param int korkeus: ikkunan uusi korkeus
    """

    grafiikka["ikkuna"].set_size(leveys, korkeus)
    grafiikka["tausta"] = pyglet.sprite.Sprite(
        pyglet.image.SolidColorImagePattern(grafiikka["taustavari"]).create_image(leveys, korkeus)
    )


def aseta_hiiri_kasittelija(kasittelija):
    """
    Asettaa funktion, jota käytetään hiiren klikkausten käsittelyyn.
    Käsittelijää kutsutaan aina, kun hiiren nappi painetaan alas missä tahansa
    peli-ikkunan sisällä. Käsittelijän tulee olla funktio, jolla on tasan neljä
    parametria: x, y, nappi sekä muokkausnäppäimet. Näistä x ja y määrittävät
    klikkauksen sijainnin ruudulla ja nappi kertoo mitä nappia painettiin (saa
    arvoja HIIRI_VASEN, HIIRI_KESKI, HIIRI_OIKEA). Muokkausnäppäimet on
    selitetty moduulin dokumentaatiossa ja niitä ei pitäisi tarvita
    perustoteutuksessa.

    Eli koodissasi sinun tulee määritellä funktio

    def hiiri_kasittelija(x, y, nappi, muokkausnapit):
        # asioita tapahtuu

    ja sen jälkeen rekisteröidä se:

    haravasto.aseta_hiiri_kasittelija(hiiri_kasittelija)

    Tällä tavalla pystyt vastaanottamaan hiiren klikkaukset koodissasi.

    :param function kasittelija: käsittelijäfunktio klikkauksille
    """

    if grafiikka["ikkuna"]:
        grafiikka["ikkuna"].on_mouse_press = kasittelija
    else:
        print("Ikkunaa ei ole luotu!")

def aseta_raahaus_kasittelija(kasittelija):
    """
    Asettaa funktion, jota käytetään kun hiiren kursoria raahataan napin
    ollessa pohjassa. Käsittelijän tulee olla funktion, jolla on kaiken
    kaikkiaan kuusi parametria: x, y, dx, dy, nappi sekä muokkausnäppäimet.
    Näistä x ja y määrittävät kursorin sijainnin, kun taas dx ja dy edellisestä
    sijainnista liikutun matkan. Nappi kertaa mitä hiiren nappia pidetään
    pohjassa (mahdolliset arvot HIIRI_VASEN, HIIRI_KESKI, HIIRI_OIKEA).
    Muokkausnäppäimet on selitetty moduulin dokumentaatiossa ja niitä ei pitäisi
    tarvita perustoteutuksessa.
    
    Eli koodissasi sinun tulee määritellä funktio
    
    def raahaus_kasittelija(x, y, dx, dy, nappi, muokkausnapit):
        # asioita tapahtuu
        
    ja sen jälkeen rekisteröidä se:
    
    haravasto.aseta_raahaus_kasittelija(raahaus_kasittelija)
    
    Tällä tavalla voit toteuttaa ikkunassa olevien objektien liikuttelun hiirellä.
    
    :param function kasittelija: käsittelijäfunktio raahaukselle
    """

    if grafiikka["ikkuna"]:
        grafiikka["ikkuna"].on_mouse_drag = kasittelija
    else:
        print("Ikkunaa ei ole luotu!")

def aseta_vapautus_kasittelija(kasittelija):
    """
    Asettaa funktion, jota käytetään kun hiiren nappi vapautetaan.
    Tyypillisesti tarpeellinen jos raahauksen päätteeksi halutaan tehdä jotain.
    Käsittelijäksi kelpaa samanlainen funktion kuin 
    aseta_hiiri_kasittelija-funktiolle. Eli määrittele sopiva funktio:
    
    def vapautus_kasittelija(x, y, nappi, muokkausnapit):
        # asioita tapahtuu
        
    ja rekisteröi se:
    
    haravasto.aseta_vapautus_kasittelija(vapautus_kasittelija)
    
    Tällä tavalla koodisi voi tehdä asioita kun hiiren nappi vapautetaan.
    
    :param function kasittelija: käsittelijäfunktio hiiren vapautukselle
    """

    if grafiikka["ikkuna"]:
        grafiikka["ikkuna"].on_mouse_release = kasittelija
    else:
        print("Ikkunaa ei ole luotu!")



def aseta_nappain_kasittelija(kasittelija):
    """
    Asettaa funktion, jota käytetään näppäimistöpainallusten käsittelyyn.
    Tarvitaan vain jos haluat pelisi käyttävän näppäimistöä johonkin.
    Käsittelijäfunktiolla tulee olla kaksi parametria: symboli ja
    muokkausnapit. Symboli on vakio, joka on asetettu pyglet.window.key-
    moduulissa (esim. pyglet.window.key.A on A-näppäin). Käytä alla olevaa
    importia jotta pääset näihin helposti käsiksi:

    from pyglet.window import key

    jonka jälkeen pääset näppäinkoodeihin kiinni key-nimen kautta, esim. key.A.
    Muokkausnapit on selitetty tämän moduulin dokumentaatiossa.

    Käyttääksesi näppäimistöä sinun tulee määritellä funktio:

    def nappain_kasittelija(symboli, muokkausnapit):
        # asioita tapahtuu

    ja sen jälkeen rekisteröidä se:

    haravasto.aseta_nappain_kasittelija(nappain_kasittelija)

    :param function kasittelija: käsittelijäfunktio näppäimistölle
    """

    if grafiikka["ikkuna"]:
        grafiikka["ikkuna"].on_key_press = kasittelija
    else:
        print("Ikkunaa ei ole luotu!")

def aseta_piirto_kasittelija(kasittelija):
    """
    Asettaa funktion, joka piirtää peli-ikkunan grafiikat. Jokseenkin tärkeä.
    Käsittelijä on funktio, jolla ei ole parametreja, ja sen tulisi piirtää
    ikkunan sisältö käyttäen seuraavia funktiota:

    tyhjaa_ikkuna (pyyhkii edellisen kierroksen grafiikat pois)
    piirra_tausta (asettaa ikkunan taustavärin)
    piirra_tekstia (kirjoittaa ruudulle tekstiä)
    aloita_ruutujen_piirto (kutsutaan ennen varsinaisen ruudukon piirtoa)
    lisaa_piirrettava_ruutu (lisää piirrettävän ruudun)
    piirra_ruudut (piirtää kaikki aloituksen jälkeen lisätyt ruudut)

    :param function kasittelija: käsittelijäfunktio piirtämiselle
    """

    if grafiikka["ikkuna"]:
        grafiikka["ikkuna"].on_draw = kasittelija
    else:
        print("Ikkunaa ei ole luotu!")

def aseta_toistuva_kasittelija(kasittelija, toistovali=1/60):
    """
    Asettaa funktion, jota kutsutaan periodisesti käyttäen annettua toistoväliä.
    Käytetään mm. animaatioihin, ruudulla näkyvään ajanottoon jne. Toistoväli
    annetaan sekunteina, ja on ohjeellinen, eli ei välttämättä aina toteudu
    millisekunnin tarkkuudella. Todellinen kulunut aika kutsujen välissä annetaan
    käsittelijäfunktiolle parametrina. Käsittelijäfunktio on siis muotoa:

    def paivitys_kasittelija(kulunut_aika):
        # asioita tapahtuu

    Ja se rekisteröidään kutsumalla tätä funktiota: 

    haravasto.aseta_toistuva_kasittelija(paivitys_kasittelija, 1/60)

    Toistovälin oletusarvo vastaa 60 FPS ruudunpäivitystä.

    :param function kasittelija: periodisesti kutsuttava käsittelijäfunktio
    :param float toistovali: kutsujen periodi, oletusarvo 1/60
    """

    pyglet.clock.schedule_interval(kasittelija, toistovali)
    kasittelijat["toistuvat"].append(kasittelija)

def aloita():
    """
    Käynnistää pelin. Ennen tämän kutsumista sinun tulee luoda ikkuna sekä
    asettaa tarvitsemasi käsittelijäfunktiot. 
    """

    grafiikka["ikkuna"].set_visible(True)
    pyglet.app.run()

def lopeta():
    """
    Piilottaa ikkunan ja sammuttaa pelisilmukan. Tätä käyttämällä voit esim.
    palata takaisin tekstipohjaiseen valikkoon. Irrottaa myös kaikki toistuvat
    käsittelijät - ne pitää siis asettaa uudestaan kun ikkuna avataan
    uudestaan.
    """

    for kasittelija in kasittelijat["toistuvat"]:
        pyglet.clock.unschedule(kasittelija)
    pyglet.app.exit()
    grafiikka["ikkuna"].set_visible(False)

def tyhjaa_ikkuna():
    """
    Siivoaa edellisen piirtokerran tuotokset pois ikkunasta.
    """

    grafiikka["ikkuna"].clear()

def piirra_tausta():
    """
    Piirtää ikkunan taustagrafiikan (taustavärin). Hyvä kutsua ennen muiden
    asioiden piirtämistä, koska muuten taustaväri peittää ne.
    """

    grafiikka["tausta"].draw()

def piirra_tekstia(teksti, x, y, vari=(0, 0, 0, 255), fontti="serif", koko=32):
    """
    Piirtää tekstiä ruudulle. Voit käyttää tätä funktiota jos haluat kirjoittaa
    käyttöliittymään jotain (esim. laskureita tai ohjeita). Oletusfontti on
    serif, koko 32 ja väri musta. Voit muuttaa näitä käyttämällä funktiokutsun
    valinnaisia argumentteja. Tekstin sijainnissa x- ja y-koordinaatti
    määrittävät vasemman alakulman sijainnin.

    Tekstit tulee piirtää ikkunaan viimeisenä.

    :param str teksti: esitettävä merkkijono
    :param int x: tekstin vasemman laidan x-koordinaatti
    :param int y: tekstin alalaidan y-koordinaatti
    :param tuple vari: väriarvo, neljä kokonaisluku sisältävä monikko (RGBA)
    :param str fontti: käytettävän fonttiperheen nimi
    :param int koko: fontin koko pisteinä
    """

    tekstilaatikko = pyglet.text.Label(teksti,
        font_name=fontti,
        font_size=koko,
        color=vari,
        x=x, y=y,
        anchor_x="left", anchor_y="bottom"
    )
    tekstilaatikko.draw()

def aloita_ruutujen_piirto():
    """
    Aloittaa ruutujen piirtämisen alustamalla eräänlaisen puskuriin, johon
    piirrettävät ruudut kerätään. Ruutuja ei siis piirretä yksitellen, koska
    se ei ole erityisen tehokasta. Sen sijaan keräämme fiksusti piirrettävät
    ruudut yhteen nippuun, joka piirretään lopuksi yhdellä kertaa. Jotta tämä
    onnistuisi, tulee tätä funktiota kutsua ennen ruutujen piirtämistä.
    """

    grafiikka["puskuri"] = pyglet.graphics.Batch()

def lisaa_piirrettava_ruutu(avain, x, y):
    """
    Lisää piirrettävän ruudun auki olevaan piirtopuskuriin. Ennen kuin tätä
    funktiota kutsutaan, tulee kutsua aloita_ruutujen_piirto-funktiota kerran.
    Ensimmäinen argumentti kertoo mikä ruutu piirretään. Mahdolliset arvot ovat
    numerot 0-8 merkkijonoina, "x" miinoille, "f" lipuille ja " "
    avaamattomille ruuduille. Sorsapelissä voidaan piirtää myös avaimilla
    "sorsa" ja "ritsa". 

    Ruutujen sijainnit ikkunassa joudut laskemaan. Yhden ruudun oletuskoko on
    40x40 pikseliä.

    :param str avain: avain, joka valitsee piirrettävän ruudun
    :param int x: ruudun vasemman laidan x-koordinaatti
    :param int y: ruudun alalaidan y-koordinaatti
    """

    grafiikka["spritet"].append(pyglet.sprite.Sprite(
        grafiikka["kuvat"][str(avain).lower()],
        x,
        y,
        batch=grafiikka["puskuri"]
    ))

def piirra_ruudut():
    """
    Piirtää kaikki auki olevaan puskuriin lisätyt ruudut. Kutsu tätä funktiota
    kun olet lisännyt kaikki ruudut piirtopuskuriin.
    """

    grafiikka["puskuri"].draw()
    grafiikka["spritet"].clear()

if __name__ == "__main__":
    # Poistetaan kaksi pylint-varoitusta pois käytöstä, koska testikoodi
    # antaa ne aiheettomasti
    # pylint: disable=missing-docstring,unused-argument

    # kuvat ladataan spritet-alikansiosta, jonka tulee sijaita samassa
    # kansiossa kuin tämä kooditiedosto
    lataa_kuvat("spritet")
    luo_ikkuna()

    def piirra():
        tyhjaa_ikkuna()
        piirra_tausta()
        aloita_ruutujen_piirto()
        for i, avain in enumerate(grafiikka["kuvat"].keys()):
            lisaa_piirrettava_ruutu(avain, i * 40, 10)

        piirra_ruudut()

    def sulje(x, y, nappi, modit):
        lopeta()

    aseta_piirto_kasittelija(piirra)
    aseta_hiiri_kasittelija(sulje)

    aloita()
