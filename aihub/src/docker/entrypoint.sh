#!/bin/bash

mkdir -p /data/log/nginx/
pip install pysnooper requests Flask==2.1.3 kubernetes celery redis cryptography tqdm pyarrow celery redis fsspec aiohttp librosa pandarallel requests_toolbelt multiprocess --index-url https://mirrors.cloud.tencent.com/pypi/simple/  --extra-index-url https://mirrors.tencent.com/repository/pypi/tencent_pypi/simple/

cp /src/docker/nginx.conf /etc/nginx/nginx.conf
cp /src/docker/default.conf /etc/nginx/conf.d/default.conf
service nginx stop
nginx -g "daemon off;" &
echo "started nginx"

if [ "$#" -ne 0 ]; then
    exec "$@"
fi

