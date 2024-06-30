# social-albums
Regarding a project on HUA University about Backend development of MSc. Presenting a social
network ETL project consuming two datasets from two databases *MongoDB* and *Neo4J*. Using
the *Kafka*, datasources are extracted and transformed into a relational database *MySQL*,
creating the associations between music albums and artists that was located into the *MongoDB*
and users that was located into the *Neo4J DB*.

*API*s are configured in order to provide intelligent ideas, that create recommendations
of music albums and artists to users regarding its associations into the social network.

---

## Modules Containing
### List of Modules

* Flask API that starts `extraction/artistsWebApp.py` the extraction of artists from the
*MongoDB* into a *Kafka* topic.

* Flask API that starts `extraction/usersWebApp.py` the extraction of users from the *Neo4J*
into a *Kafka* topic.

* The *Kafka* consumers `transformationLoad/transformationAndLoadApp.py` that defining
two *Kafka* consumers into isolated threads, each consumer regarding into each *Kafka*
topic and load the consumed data's into a *MySQL* database.

* A *Flask* API that provides intelligent recommendation of music albums and artists on
a requested user, regarding its associations in the social network and the preferences 
of its friends. This module, located on `api/apiServer.py`.


Finally, an extra, out of scope module presented on `api/workProjectBackend.py`
that regarding an example of the FR - front end exercise, and how
data regarding a *Workplan* can be stored on a *Neo4J* database.

### Docker images
Each module has its own Dockerfile inside the `docker` directory of the project.
In order to build them, you will need to be on the root directory and specify the Dockferfile

##### albums-api
```
docker build . -f ./docker/albumsApi.nonroot.Dockerfile -t albums-api
```

##### albums-consumer
```
docker build . -f ./docker/albumsConsumer.nonroot.Dockerfile -t albums-consumer
```

##### albums-producer
```
docker build . -f ./docker/albumsProducer.nonroot.Dockerfile -t albums-producer
```

##### users-producer
```
docker build . -f ./docker/usersProducer.nonroot.Dockerfile -t users-producer
```

### Kubernetes

#### mysql-config-secrets

```
kubectl create secret generic mysql-config-secrets -n social-albums \
  --from-literal=MYSQL_ROOT_PASSWORD=kx12kx12 \
  --from-literal=MYSQL_DATABASE=social-music \
  --from-literal=MYSQL_USER=koukos \
  --from-literal=MYSQL_PASSWORD=kx12kx12
```

#### mongo-config-secrets

```
kubectl create secret generic mongo-config-secrets -n social-albums \
  --from-literal=MONGO_INITDB_ROOT_USERNAME=koukos \
  --from-literal=MONGO_INITDB_ROOT_PASSWORD=kx12kx12
```

#### neo4j-config-secrets

```
kubectl create secret generic neo4j-config-secrets -n social-albums \
  --from-literal=NEO4J_AUTH=neo4j/fysalida
```

#### keycloak-config-secrets

```
kubectl create secret generic keycloak-config-secrets -n social-albums \
  --from-literal=KC_PROXY_ADDRESS_FORWARDING=true \
  --from-literal=KC_DB=mysql \
  --from-literal=KC_DB_USERNAME=koukos \
  --from-literal=KC_DB_PASSWORD=kx12kx12 \
  --from-literal=KC_DB_URL_HOST=social-albums-mysql \
  --from-literal=KC_DB_URL_PORT=3306 \
  --from-literal=KC_DB_URL_DATABASE=keycloak \
  --from-literal=KEYCLOAK_ADMIN=admin \
  --from-literal=KEYCLOAK_ADMIN_PASSWORD=password
```

#### social-albums-config (configMap)

```
kubectl create configmap my-config -n social-albums --from-env-file=.env.kube
```