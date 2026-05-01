FROM elasticsearch:8.19.10

USER root

# 直接从 GitHub Release 下载并安装 IK 分词器（构建时需要网络）
RUN /usr/share/elasticsearch/bin/elasticsearch-plugin install --batch \
    https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v8.19.10/elasticsearch-analysis-ik-8.19.10.zip

RUN chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/plugins

USER elasticsearch
