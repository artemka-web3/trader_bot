var express = require('express');
var path = require('path');
var sqlite3 = require('sqlite3').verbose();
var db = new sqlite3.Database('../prod.sqlite3');
const TelegramBot = require('node-telegram-bot-api');
const token = '6378365333:AAHvruPmmI-ao7AT3PdXmd0BONVeMbTjc_A';
const cp = require('cloudpayments');
const axios = require('axios');
const fs = require('fs');
const alert = require('alert')

const LOGIN = 'KDeOYMPCsp'
const PASSWORD = 'cgdCYjFcOSWJYHW'
const GROUP_CODE = '9fab4def-2fed-4b05-8b31-a23a3904b043';
const URL = 'https://t.me/RadarMsk_bot'

const usersFilePath = '../db.json';
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
  var account_id = parseInt(req.params.account_id);
  client.getClientApi().getSubscriptionsList({accountId: account_id}).then(
    value=>{
      if (value.getResponse().Model != []){ 
        alert('Вы попали не на ту страницу. Вам нужно обновить подписку, а не создать новую! Вернитесь в телеграм бота и выберите нужную ссылку!')
        return res.redirect('https://t.me/RadarMsk_bot')
      } else{
        return res.render('widget_semiyear', { "account_id": account_id })
      }
    }
  );
  //return res.render('widget_semiyear', { "account_id": account_id })
  // res.sendFile(path.join(__dirname + '/public/widget_semiyear.html'));
});

app.get('/month/:account_id', function (req, res) {
  var account_id = parseInt(req.params.account_id);
  client.getClientApi().getSubscriptionsList({accountId: account_id}).then(
    value=>{
      console.log(value.getResponse().Model)
      if (value.getResponse().Model != []){ 
          alert('Вы попали не на ту страницу. Вам нужно обновить подписку, а не создать новую! Вернитесь в телеграм бота и выберите нужную ссылку!')
          return res.redirect('https://t.me/RadarMsk_bot')
      }
      else{
        return res.render('widget_month', { "account_id": account_id })
      }      
    }
  );



});

app.get('/year/:account_id', function (req, res) {
  var account_id = parseInt(req.params.account_id);
  client.getClientApi().getSubscriptionsList({accountId: account_id}).then(
    value=>{
      if (value.getResponse().Model != []){
        alert('Вы попали не на ту страницу. Вам нужно обновить подписку, а не создать новую! Вернитесь в телеграм бота и выберите нужную ссылку!')
        return res.redirect('https://t.me/RadarMsk_bot')
      }
      else{
        return res.render('widget_year', { "account_id": account_id })
      }
    }
  );

});

app.get('/getTokenMonth/:account_id/:trxId/:price/:email', async (req, res) => {
  var trxId = req.params.trxId;
  var account_id = parseInt(req.params.account_id);
  var amount = parseInt(req.params.price)
  var email = req.params.email
  let usersData = [];
  try {
      const usersFileContent = fs.readFileSync(usersFilePath, 'utf-8');
      usersData = JSON.parse(usersFileContent);
  } catch (err) {
      console.error('Error reading or parsing users data:', err.message);
  }
  const userIndex = usersData.findIndex(user => user.user_id === account_id);
  if (userIndex !== -1) {
    // Обновление данных пользователя
    usersData[userIndex].money_paid += amount;
    usersData[userIndex].trxId = trxId;
    usersData[userIndex].free_sub_end = null;

    // Сохранение обновленных данных в JSON-файл
    try {
        fs.writeFileSync(usersFilePath, JSON.stringify(usersData, null, 2), 'utf-8');
        console.log(`User data updated for user_id: ${account_id}`);
    } catch (err) {
        console.error('Error writing updated users data:', err.message);
    }

    try {
        bot.sendMessage(parseInt(account_id), "Подписка на месяц успешно активирована ✅")
        console.log(`Subscription successfully activated for user ${account_id}`);
        const requestData ={
          "login": LOGIN,
          "pass": PASSWORD,
        };
        const response = await axios.post(
          'https://fiscalization.evotor.ru/possystem/v5/getToken',
          requestData,
          {
            headers: {
              'Content-Type': 'application/json; charset=utf-8',
            },
          }
        );
        await gen_check(email, account_id, amount, response.data.token)
        console.log(`Subscription successfully activated for user ${account_id}`);
        return res.render('thanks')

    } catch (e) {
        console.error('Error sending message:', e);
    }
    console.log(`Redirecting to /get-evotor-token/${account_id}`);
  } else {
      console.error(`User with user_id ${account_id} not found.`);
  }
  // Затем можно использовать это значение для отображения информации о пользователе.
  // редирект на тг бота обратно - res.redirect('')
});

app.get('/getTokenSemiYear/:account_id/:trxId/:price/:email', async (req, res) => {
  var trxId = req.params.trxId;
  var account_id = parseInt(req.params.account_id);
  var amount = parseInt(req.params.price)
  var email = req.params.email
  let usersData = [];
  try {
      const usersFileContent = fs.readFileSync(usersFilePath, 'utf-8');
      usersData = JSON.parse(usersFileContent);
  } catch (err) {
      console.error('Error reading or parsing users data:', err.message);
  }
  const userIndex = usersData.findIndex(user => user.user_id === account_id);
  if (userIndex !== -1) {
    // Обновление данных пользователя
    usersData[userIndex].money_paid += amount;
    usersData[userIndex].trxId = trxId;
    usersData[userIndex].free_sub_end = null;

    // Сохранение обновленных данных в JSON-файл
    try {
        fs.writeFileSync(usersFilePath, JSON.stringify(usersData, null, 2), 'utf-8');
        console.log(`User data updated for user_id: ${account_id}`);
    } catch (err) {
        console.error('Error writing updated users data:', err.message);
    }

    try {
        bot.sendMessage(parseInt(account_id), "Подписка на полгода успешно активирована ✅")
        console.log(`Subscription successfully activated for user ${account_id}`);
        const requestData ={
          "login": LOGIN,
          "pass": PASSWORD,
        };
        const response = await axios.post(
          'https://fiscalization.evotor.ru/possystem/v5/getToken',
          requestData,
          {
            headers: {
              'Content-Type': 'application/json; charset=utf-8',
            },
          }
        );
        await gen_check(email, account_id, amount, response.data.token)
        
        console.log(`Subscription successfully activated for user ${account_id}`);
        return res.render('thanks')

    } catch (e) {
        console.error('Error sending message:', e);
    }
    console.log(`Redirecting to /get-evotor-token/${account_id}`);
  } else {
      console.error(`User with user_id ${account_id} not found.`);
  }

  // Затем можно использовать это значение для отображения информации о пользователе.
  // редирект на тг бота обратно - res.redirect('')
});

app.get('/getTokenYear/:account_id/:trxId/:price/:email', async (req, res) => {
  var trxId = req.params.trxId;
  var account_id = parseInt(req.params.account_id);
  var amount = parseInt(req.params.price)
  var email = req.params.email
  let usersData = [];
  try {
      const usersFileContent = fs.readFileSync(usersFilePath, 'utf-8');
      usersData = JSON.parse(usersFileContent);
  } catch (err) {
      console.error('Error reading or parsing users data:', err.message);
  }
  const userIndex = usersData.findIndex(user => user.user_id === account_id);
  if (userIndex !== -1) {
    // Обновление данных пользователя
    usersData[userIndex].money_paid += amount;
    usersData[userIndex].trxId = trxId;
    usersData[userIndex].free_sub_end = null;

    // Сохранение обновленных данных в JSON-файл
    try {
        fs.writeFileSync(usersFilePath, JSON.stringify(usersData, null, 2), 'utf-8');
        console.log(`User data updated for user_id: ${account_id}`);
    } catch (err) {
        console.error('Error writing updated users data:', err.message);
    }

    try {
        bot.sendMessage(parseInt(account_id), "Подписка на год успешно активирована ✅")
        console.log(`Subscription successfully activated for user ${account_id}`);
        const requestData ={
          "login": LOGIN,
          "pass": PASSWORD,
        };
        const response = await axios.post(
          'https://fiscalization.evotor.ru/possystem/v5/getToken',
          requestData,
          {
            headers: {
              'Content-Type': 'application/json; charset=utf-8',
            },
          }
        );
        await gen_check(email, account_id, amount, response.data.token)
        return res.render('thanks')
    } catch (e) {
        console.error('Error sending message:', e);
    }
  } else {
      console.error(`User with user_id ${account_id} not found.`);
  }
  // Затем можно использовать это значение для отображения информации о пользователе.
  // редирект на тг бота обратно - res.redirect('')
});

app.get('/paymentWidget/:account_id/:amount', function (req, res) {
  var account_id = parseInt(req.params.account_id);
  var amount = parseInt(req.params.amount)
  let params = { "account_id": account_id, 'amount': amount}
  client.getClientApi().getSubscriptionsList({accountId: account_id}).then(
    value=>{
      if (value.getResponse().Model != []){
          return res.render('pay', params)
      } else{
        alert('Вы попали не на ту страницу. Вам нужно оформить подписку, так как у вас ее никогда не было! Вернитесь в телеграм бота и выберите нужную ссылку!')
        return res.redirect('https://t.me/RadarMsk_bot')
      }
      
    }
  );
});

app.get('/pay/:account_id/:amount/:email', async (req, res) => {
  var account_id = parseInt(req.params.account_id)
  var amount = parseInt(req.params.amount)
  var email = req.params.email
  let usersData = [];

  try {
      const usersFileContent = fs.readFileSync(usersFilePath, 'utf-8');
      usersData = JSON.parse(usersFileContent);
  } catch (err) {
      console.error('Error reading or parsing users data:', err.message);
  }
  const userIndex = usersData.findIndex(user => user.user_id === account_id);
  if (userIndex !== -1) {
    // Обновление данных пользователя
    usersData[userIndex].money_paid += amount;
    usersData[userIndex].free_sub_end = null;

    // Сохранение обновленных данных в JSON-файл
    try {
        fs.writeFileSync(usersFilePath, JSON.stringify(usersData, null, 2), 'utf-8');
        console.log(`User data updated for user_id: ${account_id}`);

    } catch (err) {
        console.error('Error writing updated users data:', err.message);
    }
    answer = "Что-то пошло не так, вернитесь в телеграм бот"
    try {
        client.getClientApi().getSubscriptionsList({accountId: account_id}).then(
          async(value)=>{
            console.log(value.getResponse().Model)
            for(let sub of value.getResponse().Model){
                if (sub.Status == "Cancelled"){
                    if (parseInt(amount) == 999) {
                      //sub, account_id, amount, days, email
                      await process_check_handling(sub, account_id, amount, 30, email)
                      res.render('thanks')
                    }
                    else if (parseInt(amount) == 4999){
                      await process_check_handling(sub, account_id, amount, 180, email)
                      res.render('thanks')
                    }
                    else if (parseInt(amount) == 7999){
                      await process_check_handling(sub, account_id, amount, 180, email)
                      res.render('thanks')
                    }
                }
            }
          } 
        );
        
    } catch (e) {
      alert('Ошибка отправки')
        console.error('Error sending message:', e);
    }
  } else {
      alert('Пользователь не найден')
      console.error(`User with user_id ${account_id} not found.`);
  }  
  
});

app.get("/thanks", function(req, res){
  res.render('thanks')
});



async function process_check_handling(sub, account_id, amount, days, email){
  const keyboard = [
    ['ℹ️ О боте. Руководство '],
    ['✅ Подписка '],
  ];

  const replyKeyboardMarkup = {
    reply_markup: {
      keyboard: keyboard,
      resize_keyboard: true,
      one_time_keyboard: true,
    }
  };
  const now = new Date();
  const futureDate = new Date(now.getTime() + (days * 24 * 60 * 60 * 1000));
  client.getClientApi().updateSubscription({Id: sub.Id, AccountId: account_id, Amount:  10, Interval: "Month", Period: 1, Currency: "RUB", StartDate: futureDate})
  bot.sendMessage(parseInt(account_id), "Подписка успешно активирована ✅. Рады видеть вас снова!", replyKeyboardMarkup)

  console.log(`Subscription successfully activated for user ${account_id}`);
  answer = `Перейдите по этой ссылке чтобы сгенерировать чек! http://localhost:3000/get-evotor-token/${account_id}/${email}/${amount}`
  let params = { "account_id": account_id, 'amount': amount, 'email': email}
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
    await gen_check(email, account_id, amount, response.data.token)

  } catch (error) {
    // Handle any errors that occurred during the API call
      console.log(error)
      res.status(error.response ? error.response.status : 500).json({
        error: 'Something went wrong.',
      });
  }
}

async function gen_check(email,  account_id, amount, token_evotor){
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
          price: parseInt(amount), // Interpolate the price value
          quantity: 1.0,
          measure: 0,
          sum: parseInt(amount), // Interpolate the price value
          payment_method: "full_payment",
          payment_object: 4, // Change to the appropriate payment object type
          vat: {
            type: "none",
          },
        }
      ],
      payments: [
        {
          type: 2,
          sum: parseInt(amount), // Interpolate the price value
        }
      ],
      total: parseInt(amount), // Interpolate the price value
    }
  };

  headers = {
    'Content-Type': 'application/json',
  };  
  await axios.post(urlWithParams, receiptData, {headers})
    .then(response => function(){
      return res.redirect('http://localhost:3000/thanks')})
    .catch(error => console.error('Ошибка:', error));
}

// Запуск сервера
app.listen(80, function () {
  console.log('Сервер запущен на порту 80!');

});
