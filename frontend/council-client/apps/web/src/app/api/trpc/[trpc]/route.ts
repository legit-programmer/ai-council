import { createContext } from "@council-client/api/context";
import { appRouter } from "@council-client/api/routers/index";
import { fetchRequestHandler } from "@trpc/server/adapters/fetch";
import { NextRequest } from "next/server";

function handler(req: NextRequest) {
  return fetchRequestHandler({
    endpoint: "/api/trpc",
    req,
    router: appRouter,
    createContext: () => createContext(req),
  });
}
export { handler as GET, handler as POST };
