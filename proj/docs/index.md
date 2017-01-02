# System rekomendacji bazujący na Million Song Dataset

Zbiór danych Million Song Dataset to darmowy zbiór jednego miliona utworów muzyki
współczesnej wraz z cechami i danymi metadanymi.

## Co znajduje się w zbiorze danych?

W zbiorze znajdują się podstawowe informacje takie jak:
- Nazwa artysty
- Nazwa piosenki
- Nazwa albumu
- Rok wydania

Ale także i bardziej specyficzne informacje takie jak:
- taneczność (danceability)
- energia (energy)
- gorącość utworu (hotttnesss)

Pełny wykaz pól można znaleźć na stronie: http://labrosa.ee.columbia.edu/millionsong/pages/field-list

Zbiór danych może być wzbogacony przez inne zbiory między innymi:
- SecondHandSongs dataset - nower aranżacje piosenek (cover songs)
- musiXmatch dataset - teksty piosenek
- Last.fm dataset - etykiety i podobieństwa
- Taste Profile subset - dane użytkowników
- thisismyjam-to-MSD mapping - więcej danych użytkowników
- tagtraum genre annotations - etykiety gatunków
- Top MAGD dataset - więcej etykiet gatunków

## Skąd można pobrać zbiór?

Na stronie internetowej MSD jest odnośnik do pobrania podzbioru danych (1.8 GB) oraz informacja, że następujące uniwersytety: Drexel, Ithaca College, QMUL, NYU, UCSD, UPF powinny posiadać całą kopię.
Szybkie wyszukiwanie pokazało jednak, że zbiory te nie są publicznie dostępne na stronach tych uniwersytetów.

Wymieniony został także zasób AWS https://aws.amazon.com/datasets/million-song-dataset/ jednak korzystanie z niego wymaga uiszczenia opłaty w wysokości $0.10 za 1 GB-miesiąc.

Na szczęscie udało się znaleźć źródło nie wymienione na stronie MSD https://www.opensciencedatacloud.org/publicdata/million-song-dataset/ jednak prędkość transferu oraz ilość błędów w przesyłaniu znacząco spowolniła uzyskiwanie całości zbioru.

## Przygotowanie danych

Dane są przechowywane w formacie HDF5 co oznacza, że każdy utwór znajduje się w odddzielnym pliku binarnym.
W sieci znajduje się sporo krytyki na temat formatu HDF5, [tutaj](http://labrosa.ee.columbia.edu/millionsong/blog/11-3-9-hdf5-settling-argument) można przeczytać ostateczne oświadczenie na temat wyboru formatu przez MSD.

Aby odczytać ten format skorzystaliśmy z bibliteki python'owej h5py.
Po załadowaniu pliku można odwołać się do poszczególnych pól za pomocą zagnieżdżonego słownika. Przykłądowo aby uzyskać nazwę artysty:

```python
f['metadata']['songs']['artist_name'][0]
```

Więcej informacji:
- http://www.h5py.org/
- http://labrosa.ee.columbia.edu/millionsong/blog/11-3-9-hdf5-settling-argument
- https://support.hdfgroup.org/HDF5/whatishdf5.html

## Cel projektu

Wraz z prowadzącym przedmiot stwierdziliśmy, że ciekawym pomysłem byłaby próba stworzenia silnika rekomendacji który za pomocą relacji `SIMILAR_TO` wyszukiwałby podobne utwory, zliczał wagę podobności i proponował użytkownikowi piosenki które mają najwyższą sumę wag podobności.

Aby zweryfikować jakość rekomendacji systemu uzgodniliśmy, że wykorzystamy zbiór playlist AoTM http://labrosa.ee.columbia.edu/projects/musicsim/aotm.html który podzielimy na dwie części.
Jedna część zawierać będzie piosenki które przyjmiemy jako wejście do naszego algorytmu i na ich podstawie postaramy się przewidzieć drugą część listy.
Jeśli jakaś piosenka znajdzie się na przewidzianej części oznacza to, że z powodzeniem udało nam się przewidzieć piosenkę która podoba się użytkownikowi.

## Kowersja danych z hdf5 do bazy grafowej

Aby uzyskać prosty sposób wyszukiwania podobnych utworów, załadowaliśmy interesujące nas dane do grafowej bazy danych neo4j.
Przetworzenie 280GB jest zadaniem które wymaga sporo czasu i zasobów obliczeniowych więc zdecydowaliśmy się na skorzystanie z zasobów klastra obliczeniowego zeus.
Jednak po tygodniu wymieniania e-maili z https://helpdesk.plgrid.pl/#/ szybszą ścieżką okazało się przetworzenie danych na lokalnym komputerze.
Wynikiem końcowym jest baza danych o następującym schemacie:

![schema](../../db-schema.png)

## Algorytm rekomendacji

Najważniejszą częścią algorytmu jest pętla licząca wagi podobności piosenek.
Jak widać z zapytania, wybieramy artystę który jest w relacji `:PERFORMS` z piosenką którą otrzymaliśmy jako wejście algorytmu i szukamy piosenki która połączona jest z pierwszą za pomocą relacji `:SIMILAR_TO`.
Następnie mając listę tych piosenek sortujemy ją po sumie wag.

```python
for song in song_list:
  res = session.run("MATCH (a2:ARTIST)-[:PERFORMS]->(n2:SONG)-[w:SIMILAR_TO]-(n:SONG)<-[:PERFORMS]-(a:ARTIST)  where lower(n.title)=\"" + song[1] +
      "\" and lower(a.name)=\"" + song[0] + "\" return n2.title AS title, a2.name AS name, w.weight as weight;")
  for r in res:
    similar[r["name"] + "\t" +  r["title"]] += r["weight"]


sorted_similar = sorted(similar.iteritems(),key=lambda (k,v): v, reverse=True)
```

Całość można zobaczyć w pliku `rec.py`

## Wyniki

Biorąc pod uwagę ogrom zbioru oraz różnorodność gustów i sposób w jaki użytkownicy wybierają swoje playlisty zadowalającym wynikiem jest dokładność silnika na poziomie kilku procent.

Wynik który otrzymaliśmy to: ...