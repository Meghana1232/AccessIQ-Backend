const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json({ limit: '10mb' }));

const DB_FILE = path.join(__dirname, 'database.json');

const readDB = () => {
  if (!fs.existsSync(DB_FILE)) return {};
  try {
    return JSON.parse(fs.readFileSync(DB_FILE, 'utf8'));
  } catch (err) {
    return {};
  }
};

const writeDB = (data) => {
  fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2));
};

app.post('/api/register', (req, res) => {
  const { descriptor } = req.body;
  if (!descriptor) {
    return res.status(400).json({ success: false, message: 'No face descriptor provided' });
  }

  const db = readDB();
  db.registeredFace = descriptor;
  writeDB(db);

  res.json({ success: true, message: 'Face saved to database successfully!' });
});

app.get('/api/face', (req, res) => {
  const db = readDB();
  if (!db.registeredFace) {
    return res.status(404).json({ success: false, message: 'No registered face found' });
  }
  res.json({ success: true, descriptor: db.registeredFace });
});

app.listen(5000, () => {
  console.log('Backend running on http://localhost:8000');
});