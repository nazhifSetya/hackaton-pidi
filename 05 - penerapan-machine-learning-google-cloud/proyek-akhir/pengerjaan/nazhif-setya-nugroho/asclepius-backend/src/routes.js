const { postPredictHandler } = require("./handler")

const routes = [
  {
    method: "GET",
    path: "/",
    handler: () => ({ status: "success", message: "Asclepius API is running" }),
  },
  {
    method: "POST",
    path: "/predict",
    handler: postPredictHandler,
    options: {
      payload: {
        allow: "multipart/form-data",
        multipart: { output: "stream" },
        maxBytes: 1000000,
        parse: true,
        output: "stream",
      },
    },
  },
]

module.exports = routes
