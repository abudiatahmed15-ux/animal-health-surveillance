const path = require('path');
const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const {
  getAnimals,
  getReports,
  createAnimal,
  createReport
} = require('./db');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const frontendRoot = path.resolve(__dirname, '..');

app.use(cors());
app.use(express.json({ limit: '5mb' }));
app.use(express.urlencoded({ extended: true }));

app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'VetNexa Backend',
    timestamp: new Date().toISOString()
  });
});

app.get('/api/animals', (req, res) => {
  const animals = getAnimals();
  res.json(animals);
});

app.post('/api/animals', (req, res) => {
  try {
    const animal = createAnimal(req.body || {});
    res.status(201).json({ success: true, data: animal });
  } catch (error) {
    res.status(400).json({ success: false, message: error.message });
  }
});

app.get('/api/reports', (req, res) => {
  const reports = getReports();
  res.json(reports);
});

app.post('/api/reports', (req, res) => {
  try {
    const report = createReport(req.body || {});
    res.status(201).json({ success: true, data: report });
  } catch (error) {
    res.status(400).json({ success: false, message: error.message });
  }
});

app.post('/api/ai/predict', (req, res) => {
  const body = req.body || {};
  const symptoms = Array.isArray(body.symptoms) ? body.symptoms : [];
  const animalType = (body.animal_type || 'Cow').toString();
  const confidence = Math.min(0.98, 0.52 + symptoms.length * 0.08 + (animalType ? 0.08 : 0));

  const possibleCondition = symptoms.length > 2 ? 'Infectious Disease Risk' : 'Mild Stress / Monitoring';

  res.json({
    success: true,
    data: {
      possible_condition: possibleCondition,
      confidence: Number(confidence.toFixed(2)),
      recommendations: [
        'Monitor the animal closely for 24 hours',
        'Ensure hydration and isolate if symptoms increase',
        'Schedule a vet follow-up if severity persists'
      ]
    }
  });
});

app.get('/api/docs', (req, res) => {
  res.json({
    message: 'VetNexa API',
    endpoints: {
      health: 'GET /api/health',
      animals: 'GET /api/animals | POST /api/animals',
      reports: 'GET /api/reports | POST /api/reports',
      predict: 'POST /api/ai/predict'
    }
  });
});

app.use(express.static(frontendRoot));

app.get('*', (req, res, next) => {
  if (req.path.startsWith('/api/')) return next();
  res.sendFile(path.join(frontendRoot, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`VetNexa backend running on http://vetnexa:${PORT}`);
  console.log(`Database: ${path.join(__dirname, 'data', 'vatenxa.db')}`);
});
