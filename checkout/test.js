const fs = require('fs');

// Путь к JSON-файлу, где будут храниться данные о пользователях
const usersFilePath = '../db.json';

// Загрузка данных из JSON-файла
let usersData = [];
try {
    const usersFileContent = fs.readFileSync(usersFilePath, 'utf-8');
    usersData = JSON.parse(usersFileContent);
} catch (err) {
    console.error('Error reading or parsing users data:', err.message);
}

// Имитация параметров запроса
const trxId = 'transaction123';
const account_id = 2222222;
const amount = 999;

// Поиск пользователя по account_id
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
        // Вместо отправки сообщения через бота, просто выводим сообщение в консоль
        console.log(`Subscription successfully activated for user ${account_id}`);
    } catch (e) {
        console.error('Error sending message:', e);
    }

    // Редирект
    console.log(`Redirecting to /get-evotor-token/${account_id}`);
} else {
    console.error(`User with user_id ${account_id} not found.`);
}
