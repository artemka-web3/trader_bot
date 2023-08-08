var express = require('express');
var path = require('path');
var sqlite3 = require('sqlite3').verbose();
var db = new sqlite3.Database('../prod.sqlite3');
const TelegramBot = require('node-telegram-bot-api');
const token = '6378365333:AAHvruPmmI-ao7AT3PdXmd0BONVeMbTjc_A';
const cp = require('cloudpayments');
const axios = require('axios');

const LOGIN = 'partnerTest1.2'
const PASSWORD = 'partnerTest1.2Pass'
const GROUP_CODE = 'cf0a2212-2e39-463f-9bff-30874b570f75';
const URL = 'https://fiscalization-test.evotor.ru'

const bot = new TelegramBot(token, {polling: false});
const client = new cp.ClientService({
  privateKey: 'd3119d06f156dad88a2ed516957b065b',
  publicId: 'pk_c8695290fec5bcb40f468cca846d2',
});

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

app.get('/getTokenMonth/:account_id/:trxId/:price/:email', function (req, res) {
  var trxId = req.params.trxId;
  var account_id = req.params.account_id;
  var amount = req.params.price
  var email = req.params.email


  db.run("UPDATE users SET money_paid = money_paid + ?, trxId = ?, free_sub_end = ? WHERE user_id = ?", 999, trxId, null, account_id, function (err) {
    if (err) {
      return console.log(err.message);
    }
    console.log(`A row has been inserted with rowid ${this.lastID}`);
    try{
      bot.sendMessage(parseInt(account_id), "Подписка успешно активирована ✅")
    } catch (e){
      console.log(e)
    }
    return res.redirect(`/get-evotor-token/${account_id}/${amount}/${email}`)

  });
  // Затем можно использовать это значение для отображения информации о пользователе.
  // редирект на тг бота обратно - res.redirect('')
});

app.get('/getTokenSemiYear/:account_id/:trxId/:price/:email', function (req, res) {
  var trxId = req.params.trxId;
  var account_id = req.params.account_id;
  var amount = req.params.price
  var email = req.params.email

  db.run("UPDATE users SET money_paid = money_paid + ?, trxId = ?, free_sub_end = ? WHERE user_id = ?", 4999, trxId, null, account_id, function (err) {
    if (err) {
      return console.log(err.message);
    }
    console.log(`A row has been inserted with rowid ${this.lastID}`);
    try{
      bot.sendMessage(parseInt(account_id), "Подписка успешно активирована ✅")
    } catch (e){
      console.log(e)
    }
    return res.redirect(`/get-evotor-token/${account_id}/${amount}/${email}`)
  });
  // Затем можно использовать это значение для отображения информации о пользователе.
  // редирект на тг бота обратно - res.redirect('')
});

app.get('/getTokenYear/:account_id/:trxId/:price/:email', function (req, res) {
  var trxId = req.params.trxId;
  var account_id = req.params.account_id;
  var amount = req.params.price
  var email = req.params.email


  db.run("UPDATE users SET money_paid = money_paid + ?, trxId = ?, free_sub_end = ? WHERE user_id = ?", 7999, trxId, null, account_id, function (err) {
    if (err) {
      return console.log(err.message);
    }
    console.log(`A row has been inserted with rowid ${this.lastID}`);
    try{
      bot.sendMessage(parseInt(account_id), "Подписка успешно активирована ✅")
    } catch (e){
      console.log(e)
    }
    return res.redirect(`/get-evotor-token/${account_id}/${amount}/${email}`)

  });
  // Затем можно использовать это значение для отображения информации о пользователе.
  // редирект на тг бота обратно - res.redirect('')
});

app.get('/paymentWidget/:account_id/:amount', function (req, res) {
  var account_id = req.params.account_id;
  var amount = req.params.amount

  var subs = [];

  res.render('pay', { "account_id": account_id, 'amount': amount })
});

app.get('/pay/:account_id/:amount/:email', function(req, res){
  var account_id = req.params.account_id
  var amount = req.params.amount
  var email = req.params.email

  db.run("UPDATE users SET money_paid = money_paid + ?, free_sub_end = ? WHERE user_id = ?", parseInt(amount), null, account_id, function(err){
    if (err) {
      return console.log(err.message);
    }
    console.log(`A row has been inserted with rowid ${this.lastID}`);
    try{
      client.getClientApi().getSubscriptionsList({accountId: account_id}).then(
        value=>{
          for(let sub of value.getResponse().Model){
              if (sub.Status == "Cancelled"){
                  if (parseInt(amount) == 999) {
                    const now = new Date();
                    const futureDate = new Date(now.getTime() + (30 * 24 * 60 * 60 * 1000));
                    client.getClientApi().updateSubscription({Id: sub.Id, AccountId: account_id, Amount:  10, Interval: "Month", Period: 1, Currency: "RUB", StartDate: futureDate})
                  }
                  else if (parseInt(amount) == 4999){
                    const now = new Date();
                    const futureDate = new Date(now.getTime() + (180 * 24 * 60 * 60 * 1000));
                    client.getClientApi().updateSubscription({Id: sub.Id, AccountId: account_id, Amount: 10, Interval: "Year", Period: 2, Currency: "RUB", StartDate: futureDate})
                  }
                  else if (parseInt(amount) == 7999){
                      const now = new Date();
                      const futureDate = new Date(now.getTime() + (365 * 24 * 60 * 60 * 1000));
                      client.getClientApi().updateSubscription({Id: sub.Id, AccountId: account_id, Amount: 10, Interval: "Year", Period: 1, Currency: "RUB", StartDate: futureDate})
                  }
              }
          }
        } 
      )
      const keyboard = [
        ['ℹ️ О боте. Руководство '],
        ['✅ Подписка '],
      ];
      
      const replyKeyboardMarkup = {
        reply_markup: {
          keyboard: keyboard,
          resize_keyboard: true,
          one_time_keyboard: true,
        },
      };

      bot.sendMessage(parseInt(account_id), "Подписка успешно активирована ✅. Рады видеть вас снова!", replyKeyboardMarkup)
    } catch (e){
      console.log(e)
    }
    return res.redirect(`/get-evotor-token/${account_id}/${amount}/${email}`)
  });

});

app.get("/cancel/:account_id", function(req, res){
    account_id = req.params.account_id
    res.render('cancel', { "account_id": account_id})
});
app.get("/cancel_result/:account_id", function(req, res){
  var account_id = req.params.account_id
  try{
    client.getClientApi().getSubscriptionsList({accountId: account_id}).then(
      value=>{
        let counter = 0
        for(let sub of value.getResponse().Model){
            if (sub.Status == "Active"){  
              counter+=1
              client.getClientApi().cancelSubscription({Id: sub.Id})
            }
        }
        if(counter>0){
          const keyboard = [
            ['ℹ️ О боте. Руководство '],
            ['Купить подписку'],
          ];
          
          const replyKeyboardMarkup = {
            reply_markup: {
              keyboard: keyboard,
              resize_keyboard: true,
              one_time_keyboard: true,
            },
          };
          bot.sendMessage(parseInt(account_id), "Подписка успешно отменена!", replyKeyboardMarkup)
          return res.redirect('https://t.me/RadarMsk_bot')
        } else {
          const keyboard = [
            ['ℹ️ О боте. Руководство '],
            ['Купить подписку'],
          ];
          
          const replyKeyboardMarkup = {
            reply_markup: {
              keyboard: keyboard,
              resize_keyboard: true,
              one_time_keyboard: true,
            },
          };
          bot.sendMessage(parseInt(account_id), "У вас нет активных подписок!", replyKeyboardMarkup)
          return res.redirect('https://t.me/RadarMsk_bot')
        }

      }
    )
  } catch(error){
    console.log(error)
  }

});

// РАБОТА С ЧЕКАМИ
app.get('/get-evotor-token/:account_id/:email/:price', async (req, res) => {
  let account_id = req.params.account_id
  let email = req.params.email
  let price = req.params.price
  try {
    // Prepare the request data
    const requestData = {
      login: LOGIN,
      pass: PASSWORD,
    };

    // Make the POST request to obtain the token
    const response = await axios.post(
      'https://fiscalization.evotor.ru/possystem/v5/getToken',
      requestData,
      {
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
        },
      }
    );
    res.redirect(`/generate-receipt/${response.data.token}/${account_id}/${email}/${price}`)
    // Return the token from the response
    //res.json({ token: response.data.token });
  } catch (error) {
    // Handle any errors that occurred during the API call
    res.status(error.response ? error.response.status : 500).json({
      error: 'Something went wrong.',
    });
  }
});

app.get('/generate-receipt/:token/:account_id/:email/:price', async (req, res) => {
  let token_p = req.params.token 
  let email = req.params.email
  let account_id = req.params.account_id
  let price = req.params.price
  try {
    const operation = 'sell'; // Change this to the desired operation type
    const currentDateISO = new Date();

    const options = {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false, // Use 24-hour format
    };
    
    const formattedDate = new Intl.DateTimeFormat('en-US', options).format(currentDateISO);
    const currentDate = new Date();
    const timestampInSeconds = Math.floor(currentDate.getTime() / 1000);
    // Prepare the receipt data from the request body
    const receiptData = 
      {
        "timestamp": `${formattedDate}`,
        "external_id": `${account_id}${timestampInSeconds}`,
        "receipt": {
          "client": {
              "email": `${email}`,
              "name": `${(await bot.getChat(account_id)).first_name} ${(await bot.getChat(account_id)).last_name}`
          },
          "company": {
              "email": "email@evotor.ru",
              "sno": "osn",
              "inn": "5010051677",
              "payment_address": `${URL}`
          },
          "items": [
              {
                "name": "Ваш любимый товар1",
                "price": {price},
                "quantity": 1.0,
                "measure": 0,
                "sum": {price},
                "payment_method": "full_payment",
                "payment_object": 4,
                "vat": {
                    "type": "vat20",
                    "sum": 20.0
                },
              }
          ],
          "payments":[
              {
                "type": 1,
                "sum": {price}
              }
          ],
          "total": {price},
        }
    }; 

    // Make the request to the API
    const response = await axios.post(
      `https://fiscalization.evotor.ru/possystem/v5/${GROUP_CODE}/${operation}?token=${token_p}`,
      receiptData,
      {
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
        },
      }
    );

    // Return the response from the API
    res.redirect('https://t.me/RadarMsk_bot')
    // res.json(response.data);
  } catch (error) {
    // Handle any errors that occurred during the API call
    res.status(error.response ? error.response.status : 500).json({
      error: 'Something went wrong.',
    });
  }
});

// Запуск сервера
app.listen(3000, function () {
  console.log('Сервер запущен на порту 3000!');

});
