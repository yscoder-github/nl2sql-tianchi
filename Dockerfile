# Base Images
FROM registry.cn-shanghai.aliyuncs.com/tcc-public/tensorflow:latest-cuda10.0-py3-ys-base
ADD . /competition
WORKDIR /competition
# CMD ["sh", "run.sh"]