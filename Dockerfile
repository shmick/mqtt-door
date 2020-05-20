FROM python:3-alpine

WORKDIR /app

COPY requirements.txt ./

RUN apk update \
    && apk upgrade \
    && apk add --no-cache gcc libc-dev \
    && rm -rf /var/cache/apk/* \
    && pip install --no-cache-dir --extra-index-url https://www.piwheels.org/simple -r requirements.txt \
    && apk del gcc

COPY . .

CMD [ "python", "-u", "./main.py" ]
