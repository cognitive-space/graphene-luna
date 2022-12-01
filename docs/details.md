# Implementation Details

## GraphQL Requests and Context

In Django websockets, a request object is not built in. Luna thus built in a `GraphQLRequest` object that works similar to a Django request object. In your subscriptions this request object can be accessed in the info objects context (`info.context`). In the GraphQL middleware provided by Luna this is accessed via the websocket request attribute (`ws.request`).

