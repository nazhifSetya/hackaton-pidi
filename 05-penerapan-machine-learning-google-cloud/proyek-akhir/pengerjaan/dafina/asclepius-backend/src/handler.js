const crypto = require("crypto")
const { predictClassification } = require("./services/inferenceService")
const { storePrediction } = require("./services/storeData")

async function toBuffer(image) {
  if (!image) throw new Error("image field is required")
  if (Buffer.isBuffer(image)) return image
  if (image._data && Buffer.isBuffer(image._data)) return image._data
  if (typeof image.pipe === "function" || image[Symbol.asyncIterator]) {
    const chunks = []
    for await (const chunk of image) chunks.push(chunk)
    return Buffer.concat(chunks)
  }
  throw new Error("unsupported image payload")
}

async function postPredictHandler(request, h) {
  try {
    const { image } = request.payload || {}
    const buffer = await toBuffer(image)

    const { model } = request.server.app
    const { result, suggestion } = await predictClassification(model, buffer)

    const id = crypto.randomUUID()
    const createdAt = new Date().toISOString()
    const data = { id, result, suggestion, createdAt }

    await storePrediction(id, data)

    return h
      .response({
        status: "success",
        message: "Model is predicted successfully",
        data,
      })
      .code(201)
  } catch (error) {
    // Any decode/shape/prediction failure (incl. bad-request.jpg) -> 400 per spec.
    return h
      .response({
        status: "fail",
        message: "Terjadi kesalahan dalam melakukan prediksi",
      })
      .code(400)
  }
}

module.exports = { postPredictHandler }
