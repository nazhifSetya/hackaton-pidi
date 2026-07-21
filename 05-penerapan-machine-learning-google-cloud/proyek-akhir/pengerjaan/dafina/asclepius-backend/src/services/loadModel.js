const fs = require("fs")
const path = require("path")
const tf = require("@tensorflow/tfjs")
require("@tensorflow/tfjs-backend-cpu")

// Reads a TensorFlow.js graph-model (model.json + shard .bin files) straight
// from the local filesystem. Pure @tensorflow/tfjs has no filesystem IO handler
// (that lives in tfjs-node, which is painful to build on Apple Silicon), so we
// hand it the ModelArtifacts ourselves.
function fileIOHandler(modelDir) {
  return {
    load: async () => {
      const modelJSON = JSON.parse(
        fs.readFileSync(path.join(modelDir, "model.json"), "utf8"),
      )

      const weightSpecs = []
      const buffers = []
      for (const group of modelJSON.weightsManifest) {
        for (const w of group.weights) weightSpecs.push(w)
        for (const p of group.paths) {
          buffers.push(fs.readFileSync(path.join(modelDir, p)))
        }
      }
      const merged = Buffer.concat(buffers)
      const weightData = merged.buffer.slice(
        merged.byteOffset,
        merged.byteOffset + merged.byteLength,
      )

      return {
        modelTopology: modelJSON.modelTopology,
        weightSpecs,
        weightData,
        format: modelJSON.format,
        generatedBy: modelJSON.generatedBy,
        convertedBy: modelJSON.convertedBy,
      }
    },
  }
}

// MODEL_URL (https, e.g. a Cloud Storage object) wins in production; otherwise
// fall back to the local ./model directory for offline development.
async function loadModel() {
  await tf.setBackend("cpu")
  await tf.ready()

  const modelUrl = process.env.MODEL_URL
  if (modelUrl) {
    return tf.loadGraphModel(modelUrl)
  }

  const localDir = process.env.MODEL_DIR || path.join(__dirname, "..", "..", "..", "model")
  return tf.loadGraphModel(fileIOHandler(localDir))
}

module.exports = { loadModel, fileIOHandler }
