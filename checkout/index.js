var express = require('express');
var path = require('path');
var sqlite3 = require('sqlite3').verbose();
var db = new sqlite3.Database('../database.db');
var cp = require('cloudpayments')
const client = new cp.ClientService({
  privateKey: '8d3a80672a4985f41060018f3be3ed33',
  publicId: 'pk_a1c3fd07cc4bc56f277ce4ac3f8ed'
});

var clientApi = client.getClientApi()

// Создание приложения
var app = express();

app.set('view engine', 'ejs');
// Установка пути к каталогу для статических файлов
app.set('views', path.join(__dirname, 'views'));


// Маршрут по умолчанию
app.get('/semi_year/:account_id', function (req, res) {
  var account_id = req.params.account_id;
  res.render('widget_semiyear', { "account_id": account_id })
  // res.sendFile(path.join(__dirname + '/public/widget_semiyear.html'));
});

app.get('/month/:account_id', function (req, res) {
  var account_id = req.params.account_id;
  res.render('widget_month', { "account_id": account_id })

});

app.get('/year/:account_id', function (req, res) {
  var account_id = req.params.account_id;
  res.render('widget_year', { "account_id": account_id })
});

app.get('/getTokenMonth/:account_id/:trxId', function (req, res) {
  var trxId = req.params.trxId;
  var account_id = req.params.account_id;


  db.run("UPDATE users SET money_paid = money_paid + ?, trxId = ? WHERE user_id = ?", 500, trxId, account_id, function (err) {
    if (err) {
      return console.log(err.message);
    }
    console.log(`A row has been inserted with rowid ${this.lastID}`);
    return res.send('trxId ' + trxId + ' was successfully added!');
  });
  // Затем можно использовать это значение для отображения информации о пользователе.
  // редирект на тг бота обратно - res.redirect('')
  return res.send('Вы просматриваете информацию о пользователе с trxId ' + trxId);
});

app.get('/getTokenSemiYear/:account_id/:trxId', function (req, res) {
  var trxId = req.params.trxId;
  var account_id = req.params.account_id;


  db.run("UPDATE users SET money_paid = money_paid + ?, trxId = ? WHERE user_id = ?", 500, trxId, account_id, function (err) {
    if (err) {
      return console.log(err.message);
    }
    console.log(`A row has been inserted with rowid ${this.lastID}`);
    return res.send('trxId ' + trxId + ' was successfully added!');
  });
  // Затем можно использовать это значение для отображения информации о пользователе.
  // редирект на тг бота обратно - res.redirect('')
});

app.get('/getTokenYear/:account_id/:trxId', function (req, res) {
  var trxId = req.params.trxId;
  var account_id = req.params.account_id;


  db.run("UPDATE users SET money_paid = money_paid + ?, trxId = ? WHERE user_id = ?", 500, trxId, account_id, function (err) {
    if (err) {
      return console.log(err.message);
    }
    console.log(`A row has been inserted with rowid ${this.lastID}`);
    return res.send('trxId ' + trxId + ' was successfully added!');
  });
  // Затем можно использовать это значение для отображения информации о пользователе.
  // редирект на тг бота обратно - res.redirect('')
  return res.send('Вы просматриваете информацию о пользователе с trxId ' + trxId);
});



// Запуск сервера
app.listen(3000, function () {
  console.log('Сервер запущен на порту 3000!');

});
