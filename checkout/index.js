var express = require('express');
var path = require('path');
var sqlite3 = require('sqlite3').verbose();
var db = new sqlite3.Database('../prod.sqlite3');
const TelegramBot = require('node-telegram-bot-api');
const token = '6378365333:AAHvruPmmI-ao7AT3PdXmd0BONVeMbTjc_A';
const cp = require('cloudpayments');
const axios = require('axios');
const alert = require('alert')

const LOGIN = 'KDeOYMPCsp'
const PASSWORD = 'cgdCYjFcOSWJYHW'
const GROUP_CODE = '9fab4def-2fed-4b05-8b31-a23a3904b043';
const URL = 'https://t.me/RadarMsk_bot'

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
  client.getClientApi().getSubscriptionsList({accountId: account_id}).then(
    value=>{
      for(let sub of value.getResponse().Model){
        if (sub){
          alert('Вы попали не на ту страницу. Вам нужно обновить подписку, а не создать новую! Вернитесь в телеграм бота и выберите нужную ссылку!')
          res.redirect('https://t.me/RadarMsk_bot')
        }
        else{
          return res.render('widget_semiyear', { "account_id": account_id })
        }
      }
    }
  );
  // res.sendFile(path.join(__dirname + '/public/widget_semiyear.html'));
});

app.get('/month/:account_id', function (req, res) {
  var account_id = req.params.account_id;
  client.getClientApi().getSubscriptionsList({accountId: account_id}).then(
    value=>{
      for(let sub of value.getResponse().Model){
        if (sub){
          alert('Вы попали не на ту страницу. Вам нужно обновить подписку, а не создать новую! Вернитесь в телеграм бота и выберите нужную ссылку!')
          res.redirect('https://t.me/RadarMsk_bot')
        }
        else{
          return res.render('widget_month', { "account_id": account_id })

        }
      }
    }
  );


});

app.get('/year/:account_id', function (req, res) {
  var account_id = req.params.account_id;
  client.getClientApi().getSubscriptionsList({accountId: account_id}).then(
    value=>{
      for(let sub of value.getResponse().Model){
        if (sub){
          alert('Вы попали не на ту страницу. Вам нужно обновить подписку, а не создать новую! Вернитесь в телеграм бота и выберите нужную ссылку!')
          res.redirect('https://t.me/RadarMsk_bot')
        }
        else{
          return res.render('widget_year', { "account_id": account_id })
        }
      }
    }
  );
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
  let params = { "account_id": account_id, 'amount': amount}
  client.getClientApi().getSubscriptionsList({accountId: account_id}).then(
    value=>{
      for(let sub of value.getResponse().Model){
        if (!sub){
          alert('Вы попали не на ту страницу. Вам нужно оформить подписку, так как у вас ее никогда не было! Вернитесь в телеграм бота и выберите нужную ссылку!')
          res.redirect('https://t.me/RadarMsk_bot')
        }
        else{
          return res.render('pay', params)
        }
      }
    }
  );
  var subs = [];
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

// РАБОТА С ЧЕКАМИ
app.get('/get-evotor-token/:account_id/:email/:price', async (req, res) => {
  let account_id = req.params.account_id
  let email = req.params.email
  let price = req.params.price
  try {
    // Prepare the request data
    const requestData ={
      "login": LOGIN,
      "pass": PASSWORD,
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
    //await axios.post(`/generate-receipt/${response.data.token}/${account_id}/${email}/${price}`)
    res.redirect(`/generate-receipt/${response.data.token}/${account_id}/${email}/${price}`)
    // Return the token from the response
    //res.json({ token: response.data.token });
  } catch (error) {
    // Handle any errors that occurred during the API call
    console.log(error)
    res.status(error.response ? error.response.status : 500).json({
      error: 'Something went wrong.',
    });
  }
});

app.get('/generate-receipt/:token/:account_id/:email/:price', async (req, res) => {
  let token_evotor = req.params.token;
  let email = req.params.email;
  let account_id = req.params.account_id;
  let price = req.params.price;
  const currentDate = new Date();
  const year = currentDate.getFullYear();
  const month = (currentDate.getMonth() + 1).toString().padStart(2, '0');
  const day = currentDate.getDate().toString().padStart(2, '0');
  const hours = currentDate.getHours().toString().padStart(2, '0');
  const minutes = currentDate.getMinutes().toString().padStart(2, '0');
  const seconds = currentDate.getSeconds().toString().padStart(2, '0');  
  const formattedDate = `${day}.${month}.${year} ${hours}:${minutes}:${seconds}`;
  const timestampInSeconds = Math.floor(currentDate.getTime() / 1000);

  const apiUrl = 'https://fiscalization.evotor.ru/possystem/v5';
  const groupCode = GROUP_CODE;
  const option = 'sell';
  const token_ev = token_evotor;
  const urlWithParams = `${apiUrl}/${groupCode}/${option}?token=${token_ev}`;
  const receiptData = {
    timestamp: formattedDate,
    external_id: `${account_id}${timestampInSeconds}`,
    receipt: {
      client: {
        email: email,
        name: `${(await bot.getChat(account_id)).first_name} ${(await bot.getChat(account_id)).last_name}`
      },
      company: {
        email: "romanovcapi@gmail.com",
        sno: "usn_income",
        inn: "434586393116",
        payment_address: 'https://t.me/RadarMsk_bot'
      },
      items: [
        {
          name: "Подписка на телеграм-бота",
          price: parseInt(price), // Interpolate the price value
          quantity: 1.0,
          measure: 0,
          sum: parseInt(price), // Interpolate the price value
          payment_method: "full_payment",
          payment_object: 4, // Change to the appropriate payment object type
          vat: {
            type: "vat20",
          },
        }
      ],
      payments: [
        {
          type: 2,
          sum: parseInt(price), // Interpolate the price value
        }
      ],
      total: parseInt(price), // Interpolate the price value
    }
  };

  headers = {
    'Content-Type': 'application/json',
  };  
  await axios.post(urlWithParams, receiptData, {headers})
    .then(response => function(){
      res.redirect('https://t.me/RadarMsk_bot')})
    .catch(error => console.error('Ошибка:', error));
});

app.get("/thanks", function(req, res){
  res.render('thanks')
});

// Запуск сервера
app.listen(3000, function () {
  console.log('Сервер запущен на порту 3000!');

});
