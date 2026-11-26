# TODO

- [ ] Slug generation from show titles / ZIP folder names
- [ ] Seasons and episodes in the `show` table (`S#01`, `S#01#E#01`)
- [ ] Pydantic models for events and items
- [ ] Lambda Powertools (logging, event parsing)
- [ ] Shared library for code used by several functions
- [ ] API Gateway: GET / DELETE / PUT routes
- [ ] PUT → SQS → Lambda
- [x] DELETE show / season / episode (synchronous, `batch_writer`, parent item deleted last)
- [ ] Cascade delete via DynamoDB Streams: API deletes only `META` and returns 204; a stream-triggered
      Lambda deletes the seasons/episodes. Removes the 29 s API Gateway limit and the client retry.
      - table: `stream_enabled`, `stream_view_type = KEYS_ONLY`
      - `aws_lambda_event_source_mapping` with a filter (`REMOVE` events with `sk = META` only), so the
        cascade's own deletes don't trigger it again
      - error handling: `maximum_retry_attempts`, `bisect_batch_on_function_error`, on-failure destination (SQS)
      - at-least-once delivery → the cascade must be idempotent (it is: delete-by-key)
      - emulator 🧪: are streams, event source mappings and filter criteria supported?
- [ ] ZIP upload: S3 → SQS → ingest Lambda (concurrency 1)
- [ ] Input validation and error responses (400 / 404)
- [ ] Paginate list routes: `query` stops at 1 MB and `get_show` ignores `LastEvaluatedKey` (fine for seed data, max 28 episodes)
- [ ] Make `deploy_code.sh` more readable
- [ ] Emulator vs AWS experiments (`~/notes/aws-emulator-vs-real-aws.md`)
