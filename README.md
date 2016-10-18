# eksploracja-danych-2016

## Temat: Analiza danych – Million song dataset - http://labrosa.ee.columbia.edu/millionsong/

### Dostępne dane

Lista pól: http://labrosa.ee.columbia.edu/millionsong/pages/field-list

Dokumentacja echonest zwraca 503 - http://developer.echonest.com/docs/v4/_static/AnalyzeDocumentation_2.2.pdf ale udało się znaleźć wersję na webarchive. Przykładowo:

- https://web.archive.org/web/20111103131846/http://developer.echonest.com/docs/v4/_static/AnalyzeDocumentation_2.2.pdf
- https://web.archive.org/web/20160618002306/http://developer.echonest.com/docs/v4/artist.html

Jest dużo pół które nie są opisane w API a które były generowanie "algorytmicznie" (przynajmniej w wersji z web archive) przykładowo `danceability`.

### Pomysły na zastosowania

- Wykorzystanie cech związanych z charakterystyką dzwięku utworu (bars, sections, segments) w algorytmach redukcji wymiarowości aby zobaczyć czy różne gatunki dzielą podobne cechy
- Hotttnesss vs familarity
