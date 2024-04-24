#!/bin/sh
python transfer.py --env sandbox --portal-key ${PORTAL_KEY} --portal-secret-key ${PORTAL_SECRET_KEY} --google-service-account-credentials-base64 ${SA_SECRET}
