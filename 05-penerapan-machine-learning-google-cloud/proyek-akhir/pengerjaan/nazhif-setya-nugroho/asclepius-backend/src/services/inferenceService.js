const tf = require("@tensorflow/tfjs")
const sharp = require("sharp")

// Decode -> resize to the model's 224x224x3 input -> predict.
// The Melly/Dicoding model outputs a single sigmoid value in [0,1];
// > 0.5 => Cancer, <= 0.5 => Non-cancer.
async function predictClassification(model, imageBuffer) {
  // Reject anything that isn't a natively 3-channel RGB image. sharp would
  // otherwise happily promote a grayscale (1-channel) or CMYK image to 3
  // channels, but the model expects real RGB and the spec wants a 400 for
  // "format/shape yang tidak sesuai" (e.g. the grayscale bad-request.jpg).
  // sharp also throws here on non-image payloads -> caller maps both to 400.
  const meta = await sharp(imageBuffer).metadata()
  if (meta.channels !== 3) {
    throw new Error(
      `unsupported image: expected 3-channel RGB, got ${meta.channels} channel(s)`,
    )
  }

  // Decode -> resize -> raw RGB pixel bytes [0..255].
  const { data } = await sharp(imageBuffer)
    .resize(224, 224, { fit: "fill", kernel: sharp.kernel.nearest })
    .raw()
    .toBuffer({ resolveWithObject: true })

  const score = tf.tidy(() => {
    const input = tf
      .tensor3d(new Uint8Array(data), [224, 224, 3])
      .toFloat()
      .expandDims(0)
    const prediction = model.predict(input)
    return prediction.dataSync()[0]
  })

  const result = score > 0.5 ? "Cancer" : "Non-cancer"
  const suggestion =
    result === "Cancer"
      ? "Segera periksa ke dokter!"
      : "Penyakit kanker tidak terdeteksi."

  return { result, suggestion, score }
}

module.exports = { predictClassification }
