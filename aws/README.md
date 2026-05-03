# AWS Integration (Future)

This directory is reserved for cloud integration:
- `s3_service.py` — Upload results to S3 instead of local storage
- `lambda_handler.py` — Lambda function to relay parameters to solvers

To enable: swap `storage_service.py` for `s3_service.py` in the routes.
The interface is identical (save/get/list/delete).
