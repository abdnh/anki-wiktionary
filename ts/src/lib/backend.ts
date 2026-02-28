import { createProtoClient } from "ankiutils";

import { BackendService, type GetSupportLinksResponse } from "./generated/backend_pb";

export const client = createProtoClient(BackendService);

export { type GetSupportLinksResponse };
