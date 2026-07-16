// Sanity check: run every data-test image through the model and print the
// score + label. Confirms cancer-1.png => Cancer and non-cancer-1.png => Non-cancer
// (the two labels the reviewer's Postman tests assert).
const fs = require("fs")
const path = require("path")
const { loadModel } = require("../src/services/loadModel")
const { predictClassification } = require("../src/services/inferenceService")

const DATA_DIR = path.join(__dirname, "..", "..", "data-test")

async function main() {
  const model = await loadModel()
  const files = fs
    .readdirSync(DATA_DIR)
    .filter((f) => /\.(png|jpe?g)$/i.test(f))
    .sort()

  for (const file of files) {
    const buffer = fs.readFileSync(path.join(DATA_DIR, file))
    try {
      const { result, score } = await predictClassification(model, buffer)
      console.log(`${file.padEnd(20)} score=${score.toFixed(4)}  =>  ${result}`)
    } catch (e) {
      console.log(`${file.padEnd(20)} ERROR: ${e.message}`)
    }
  }
}

main()
