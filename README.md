# article-service
Service for articles recommendations

У нас будет несколько основных сущностей - пользователь и статья. Остальные добавим позже. 
Возможно, появятся права и роли пользователей. Для статей можно идти в сторону расширения "категорий".

В качестве базы данных выбрана MongoDB, так как нам важно быстро вносить изменения в схему от спринта к спринту и уметь гибко работать с массивами в качестве полей.

Полнотекстовый поиск, поиск по элементам массива поддерживают в MongoDB, так что инструмент подойдет для использования в текущем проекте

## Поиск статей
Поиск статей по полям осуществляется через ручку GET /articles с соответствующими параметрами.
Поля для поиска : year, authors, abstract,  keywords и другие.
Для эффективного поиска по базе были добавлены несколько композитных индексов по полям поиска.
Так как при фильтре `{field1: value1, field2: value2, field3: value3}` должен существовать композитный индекс
`(field1, field2, field3, ... )`, то количество композитных индексов равно количеству полей поиска.

То есть для трех полей `year, authors, keywords` созданы индексы:
1. `(authors, keywords, year)`
2. `(keywords, year)`
3. `(year)`

## User

```json
{
  "id": UUID('6ce75daa-304c-4abb-842e-69d69a98b9e8'),
  "login": "cucumber",
  "password_hash": "5f4dcc3b5aa765d61d8327deb882cf99", // just md5 hash of password
  "created": "2022-09-24T00:00:00.000Z",
  "updated" : "2022-09-24T00:00:00.000Z"
}
```
Идентификаторы статей - ObjectId

## Article
```json
{
  "id": ObjectId("53a7258520f7420be8b514a9"),
  "title": "Semantic Wikipedia.",
  "authors": [
    ObjectId("53f47915dabfaefedbbb728f"),
    ObjectId("53f44a27dabfaedf435dbf2e"),
    ObjectId("5433f551dabfaebba5832602"),
    ObjectId("53f322dddabfae9a84460560"),
    ObjectId("53f556b9dabfaea7cd1d5e32")
  ],
  "venue": {
    "_id": "53a7257a20f7420be8b50425",
    "type": 0,
    "raw": "WWW"
  },
  "year": 2006,
  "n_citation": 647,
  "page_start": "585",
  "page_end": "594",
  "lang": "en",
  "volume": "",
  "issue": "",
  "issn": "",
  "isbn": "",
  "doi": "10.1145/1135777.1135863",
  "pdf": null,
  "url": [
    "http://doi.acm.org/10.1145/1135777.1135863",
    "db/conf/www/www2006.html#VolkelKVHS06",
    "https://doi.org/10.1145/1135777.1135863",
    "https://www.wikidata.org/entity/Q27680376"
  ],
  "created": "2022-09-24T00:00:00.000Z",
  "updated" : "2022-09-24T00:00:00.000Z"
}
```
## Author
Данные были собраны из датасета статей
```json
{
  "_id": ObjectId('53f47915dabfaefedbbb728f'),
  "name": "Perakakis M.",
  "created": "2022-09-24T00:00:00.000Z",
  "updated" : "2022-09-24T00:00:00.000Z"
}
```
## Как поднять локально
```docker-compose up -d```

После этого можно запустить тесты
```docker-compose run web pytest```
