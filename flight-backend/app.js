// server.js
const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
const app = express();
const port = 4000; // Choose a port for your backend

app.use(cors());
app.use(express.json());

const mongoURI = 'mongodb://localhost:27017/';
const databaseName = 'BoeingTaxiCommands';
const collectionName = 'commands';

// Connect to MongoDB
mongoose.connect(mongoURI + databaseName, {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

const Flight = mongoose.model('Flight', {
  flightID: String,
  runway: String,
  commands: String,
  date: String,
  time: String,
  controlTower: String
}, collectionName);

// Route to fetch flights
app.get('/commands', async (req, res) => {
  try {
    const flights = await Flight.find();
    res.json(flights);
  } catch (error) {
    console.error('Error fetching flights:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
