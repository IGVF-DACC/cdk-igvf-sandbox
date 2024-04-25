FROM public.ecr.aws/docker/library/python:3.11.4-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

ENV VIRTUAL_ENV=/opt/venv

ARG VERSION=v0.4.0

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m aft

RUN python -m venv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN chown -R aft:aft $VIRTUAL_ENV

WORKDIR /aft

RUN git clone -b ${VERSION} --depth 1 https://github.com/IGVF-DACC/anvil-file-transfer .

RUN pip install -r requirements.txt

COPY --chown=aft:aft . .

RUN chmod +x *.sh

USER aft

ENTRYPOINT ["./entrypoint.sh"]

CMD ["./run.sh"]
