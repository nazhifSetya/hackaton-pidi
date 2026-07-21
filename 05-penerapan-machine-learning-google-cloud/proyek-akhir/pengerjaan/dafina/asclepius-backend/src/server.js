const Hapi = require("@hapi/hapi")
const routes = require("./routes")
const { loadModel } = require("./services/loadModel")

async function init() {
  const server = Hapi.server({
    port: process.env.PORT || 3000,
    host: "0.0.0.0",
    routes: {
      cors: { origin: ["*"] },
    },
  })

  // Load the model once at startup and hand it to every request via server.app.
  server.app.model = await loadModel()

  server.route(routes)

  // Reshape Hapi/Boom errors (e.g. the 413 for payloads > 1MB) into the
  // { status: "fail", message } envelope the reviewer's Postman tests expect.
  // The 413 message is Hapi's own default and matches the spec exactly.
  server.ext("onPreResponse", (request, h) => {
    const response = request.response
    if (response.isBoom) {
      return h
        .response({ status: "fail", message: response.message })
        .code(response.output.statusCode)
    }
    return h.continue
  })

  await server.start()
  console.log(`Server running on ${server.info.uri}`)
}

process.on("unhandledRejection", (err) => {
  console.error(err)
  process.exit(1)
})

init()
