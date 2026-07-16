const { Firestore } = require("@google-cloud/firestore")

// Firestore is only wired up in the cloud. Locally (no GCP creds) we skip the
// write so the /predict contract can be tested offline. Set FIRESTORE_ENABLED=true
// (done automatically in the deployed container) to persist predictions.
let db = null
function getDb() {
  if (db) return db
  db = new Firestore({
    projectId: process.env.GOOGLE_CLOUD_PROJECT || undefined,
    databaseId: process.env.FIRESTORE_DATABASE_ID || "(default)",
  })
  return db
}

async function storePrediction(id, data) {
  if (process.env.FIRESTORE_ENABLED !== "true") return
  const predictions = getDb().collection("predictions")
  await predictions.doc(id).set(data)
}

module.exports = { storePrediction }
