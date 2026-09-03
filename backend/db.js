const fs = require('fs');
const path = require('path');
const Database = require('better-sqlite3');

const dbDir = path.join(__dirname, 'data');
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir, { recursive: true });
}

const dbPath = path.join(dbDir, 'vatenxa.db');
const db = new Database(dbPath);

db.pragma('journal_mode = WAL');

db.exec(`
  CREATE TABLE IF NOT EXISTS animals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    breed TEXT,
    age INTEGER,
    gender TEXT,
    location TEXT,
    status TEXT DEFAULT 'healthy',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER,
    title TEXT NOT NULL,
    symptoms TEXT,
    severity TEXT,
    status TEXT DEFAULT 'pending',
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(animal_id) REFERENCES animals(id)
  );
`);

const seedAnimals = [
  {
    name: 'Maya',
    type: 'Cow',
    breed: 'Holstein',
    age: 4,
    gender: 'Female',
    location: 'Nashik',
    status: 'healthy'
  },
  {
    name: 'Bharat',
    type: 'Goat',
    breed: 'Jamunapari',
    age: 2,
    gender: 'Male',
    location: 'Pune',
    status: 'monitoring'
  },
  {
    name: 'Sundar',
    type: 'Buffalo',
    breed: 'Murrah',
    age: 5,
    gender: 'Male',
    location: 'Nagpur',
    status: 'critical'
  }
];

const seedReports = [
  {
    animal_id: 1,
    title: 'Mild fever observed',
    symptoms: 'Low appetite, slight fever',
    severity: 'medium',
    status: 'reviewing',
    notes: 'Recommended hydration and rest.'
  },
  {
    animal_id: 3,
    title: 'Respiratory distress',
    symptoms: 'Coughing, laboured breathing',
    severity: 'high',
    status: 'urgent',
    notes: 'Vet follow-up required within 24 hours.'
  }
];

const animalCount = db.prepare('SELECT COUNT(*) as total FROM animals').get();
if (!animalCount.total) {
  const insertAnimal = db.prepare(`
    INSERT INTO animals (name, type, breed, age, gender, location, status)
    VALUES (@name, @type, @breed, @age, @gender, @location, @status)
  `);
  const insertReport = db.prepare(`
    INSERT INTO reports (animal_id, title, symptoms, severity, status, notes)
    VALUES (@animal_id, @title, @symptoms, @severity, @status, @notes)
  `);

  const animals = seedAnimals.map((animal) => ({ ...animal }));

  const insertAnimals = db.transaction((rows) => {
    rows.forEach((row) => insertAnimal.run(row));
  });
  insertAnimals(animals);

  const reportRows = seedReports.map((report) => ({ ...report }));
  const insertReports = db.transaction((rows) => {
    rows.forEach((row) => insertReport.run(row));
  });
  insertReports(reportRows);
}

function getAnimals() {
  return db.prepare('SELECT * FROM animals ORDER BY id DESC').all();
}

function getReports() {
  return db.prepare(`
    SELECT r.*, a.name AS animal_name, a.type AS animal_type
    FROM reports r
    LEFT JOIN animals a ON a.id = r.animal_id
    ORDER BY r.id DESC
  `).all();
}

function createAnimal(payload) {
  const stmt = db.prepare(`
    INSERT INTO animals (name, type, breed, age, gender, location, status)
    VALUES (@name, @type, @breed, @age, @gender, @location, @status)
  `);

  const result = stmt.run({
    name: payload.name,
    type: payload.type,
    breed: payload.breed || 'Unknown',
    age: Number(payload.age || 0),
    gender: payload.gender || 'Unknown',
    location: payload.location || 'Unknown',
    status: payload.status || 'healthy'
  });

  return getAnimalById(result.lastInsertRowid);
}

function createReport(payload) {
  const stmt = db.prepare(`
    INSERT INTO reports (animal_id, title, symptoms, severity, status, notes)
    VALUES (@animal_id, @title, @symptoms, @severity, @status, @notes)
  `);

  const result = stmt.run({
    animal_id: payload.animal_id || null,
    title: payload.title || 'New report',
    symptoms: payload.symptoms || '',
    severity: payload.severity || 'low',
    status: payload.status || 'pending',
    notes: payload.notes || ''
  });

  return getReportById(result.lastInsertRowid);
}

function getAnimalById(id) {
  return db.prepare('SELECT * FROM animals WHERE id = ?').get(id);
}

function getReportById(id) {
  return db.prepare(`
    SELECT r.*, a.name AS animal_name, a.type AS animal_type
    FROM reports r
    LEFT JOIN animals a ON a.id = r.animal_id
    WHERE r.id = ?
  `).get(id);
}

module.exports = {
  db,
  getAnimals,
  getReports,
  createAnimal,
  createReport,
  getAnimalById,
  getReportById
};
