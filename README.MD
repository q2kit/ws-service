# WS Service



## Run with Docker Compose:

```bash
docker-compose up --build -d
```


## Run without Docker Compose:


### 1. Create network:

```bash
docker network create wss
```


### 2. Run backend:

#### 2.1. Pull image:

```bash
docker pull q2kit/wss-backend:TAG
```

#### 2.2. Create container:

```bash
docker run --publish 18080:80 --network wss --name wss-backend -e CSRF_TRUSTED_ORIGINS="['http://localhost:18080']" q2kit/wss-backend:TAG
```


### 3. Run database:

#### 3.1. Pull image:

```bash
docker pull postgres:14.0
```

#### 3.2. Create container:

```bash
docker run --network wss --name wss-db -e POSTGRES_DB=wsservice -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres postgres:14.0
```


### 4. Run redis:

#### 4.1. Pull image:

```bash
docker pull redis:6.2.6
```

#### 4.2. Create container:

```bash
docker run --network wss --name wss-redis redis:6.2.6
```
