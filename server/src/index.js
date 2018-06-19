require("dotenv").config();
require("dotenv-safe").config();
const express = require("express");
const graphqlHTTP = require("express-graphql");
// middleware express pour ajouter les headers CORS
const cors = require("cors");
const graphql = require("graphql");
const { buildSchema, GraphQLSchema } = require("graphql");
const mongoose = require("mongoose");
const logger = require("./services/logger");
const ipfilter = require("express-ipfilter").IpFilter;
const { getUserFromJwt } = require("./services/user");
// mongoose.set("debug", true);

connectToMongodb()
  .then(() => {
    console.log(`connected successfully to ${process.env.MONGODB_URL} ! `);
    const schema = buildGraphQLSchema();
    startExpressServer(schema);
  })
  .catch(e => console.error(e));

function connectToMongodb() {
  mongoose.Promise = global.Promise;
  return mongoose.connect(process.env.MONGODB_URL);
}

function buildGraphQLSchema() {
  const schema = new graphql.GraphQLSchema({
    // "query" type contains all our queries types
    query: new graphql.GraphQLObjectType({
      name: "Query",
      fields: {
        ...require("./graphql/queries/hello"),
        ...require("./graphql/queries/aide"),
        ...require("./graphql/queries/user")
      }
    }),
    // "mutation" type contains all our mutations types
    mutation: new graphql.GraphQLObjectType({
      name: "Mutation",
      fields: {
        ...require("./graphql/mutations/email"),
        ...require("./graphql/mutations/aide"),
        ...require("./graphql/mutations/user")
      }
    })
  });
  return schema;
}

function auth() {
  return async (req, res, next) => {
    try {
      if (!req.headers.authorization) return next();

      const [type, jwt] = req.headers.authorization.split(" ");
      if (type !== "Bearer") return next();

      req.user = await getUserFromJwt(jwt);
      next();
    } catch (err) {
      next(err);
    }
  };
}

function startExpressServer(schema) {
  const app = express();
  app.use(cors());
  // to support JSON-encoded bodies
  // app.use(express.json());

  app.use(auth());

  app.use(
    "/graphql",
    graphqlHTTP(req => ({
      schema,
      rootValue: {},
      context: {
        user: req.user
      },
      // always display graphiql explorer for now
      graphiql: true,
      formatError: error => {
        console.log(error);
        return {
          message: error.message,
          stack:
            process.env.NODE_ENV === "development"
              ? error.stack.split("\n")
              : null
        };
      }
    }))
  );

  app.use("/", (req, res) => {
    res.json("server is running. Go to /graphql.");
  });

  if (!process.env.PORT) {
    logger.error("warning : MISSING PORT VARIABLE");
  }
  const port = process.env.PORT ? process.env.PORT : 8100;

  app.listen(port);
  logger.info(`Running a GraphQL API server at localhost:${port}/graphql`);
}
