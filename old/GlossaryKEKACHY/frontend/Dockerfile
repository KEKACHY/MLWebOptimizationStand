FROM node:20

WORKDIR /frontend

COPY package.json package-lock.json ./

RUN npm ci --include=dev

COPY . /frontend

ENV HOST=0.0.0.0 

ENV PORT=8080

CMD ["npm", "run", "dev"]
