# article-service
Service for articles recommendations

У нас будет несколько основных сущностей - пользователь и статья. Остальные добавим позже. 
Возможно, появятся права и роли пользователей. Для статей можно идти в сторону расширения "категорий".

## User

```json
{
  "_id": UUID('6ce75daa-304c-4abb-842e-69d69a98b9e8'),
  "login": "cucumber",
  "password_hash": "5f4dcc3b5aa765d61d8327deb882cf99", // just md5 hash of password
  "created": "2022-09-24T00:00:00.000Z",
  "updated" : "2022-09-24T00:00:00.000Z"
}
```
Идентификаторы статей - UUID-ы (для удобства добавления новых статей)

## Article
```json
{
  "_id": UUID('badaaff9-3e12-49cc-9dc3-ec1d1368db1d'),
  "title": "some title",
  "authors": [UUID('2904b054-6b4f-4fdc-b249-50de68f8bf62'), UUID('48750366-f950-4744-b4fc-d5d7ebcb2406')],
  "abstract": "abstract",
  "conference" : "Proceedings of the 10th international conference",
  "year" : 2006,
  "references" : [UUID('1dcc3c5d-3cd6-40b7-8a40-7427b78eda03'), UUID('22bed3de-b248-4877-85c8-ed2acf469373'), UUID('d944a6dc-2844-4757-9966-e6ee611a0adc')],
  "created": "2022-09-24T00:00:00.000Z",
  "updated" : "2022-09-24T00:00:00.000Z"
}
```
## Author
Предлагается уницифировать все имена авторов до вида A.B. Jones (например, из John Joseph Nicholson получится J.J. Nicholson)
Другой вариант - оставить только фамилию на случай, если где-либо не указано имя или среднее имя. 
```json
{
  "_id": UUID('2904b054-6b4f-4fdc-b249-50de68f8bf62'),
  "name": "M.", // it was Manolis, let's reduce to one letter everything apart from surname
  "surname": "Perakakis",
  "created": "2022-09-24T00:00:00.000Z",
  "updated" : "2022-09-24T00:00:00.000Z"
}
```