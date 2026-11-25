# TODO

- [ ] Slug generation from show titles / ZIP folder names
- [ ] Seasons and episodes in the `show` table (`S#01`, `S#01#E#01`)
- [ ] Pydantic models for events and items
- [ ] Lambda Powertools (logging, event parsing)
- [ ] Shared library for code used by several functions
- [ ] API Gateway: GET / DELETE / PUT routes
- [ ] PUT → SQS → Lambda
- [ ] DELETE show / season / episode
- [ ] ZIP upload: S3 → SQS → ingest Lambda (concurrency 1)
- [ ] Input validation and error responses (400 / 404)
- [ ] Make `deploy_code.sh` more readable
- [ ] Emulator vs AWS experiments (`~/notes/aws-emulator-vs-real-aws.md`)
