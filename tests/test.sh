docker build -t ppt-to-txt-ppt-converter . && \
docker run --name ppt-to-txt-container ppt-to-txt-ppt-converter uv run pytest && \
docker rm -f ppt-to-txt-container && \
docker image prune -f
