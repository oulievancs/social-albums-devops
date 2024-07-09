def subject = "${env.JOB_NAME} - Build #${env.BUILD_NUMBER}"
def content = '${JELLY_SCRIPT,template="html"}'

pipeline {
    agent any
    environment {        
        DOCKER_TOKEN=credentials('registry-creds')
        DOCKER_USER='angelosnm'
        DOCKER_SERVER='docker.io'
        USERS_PRODUCER_PREFIX='users-producer'
        ALBUMS_API_PREFIX='albums-api'
        ALBUMS_PRODUCER_PREFIX='albums-producer'
        ALBUMS_CONSUMER_PREFIX='albums-consumer'
        USERS_CONSUMER_PREFIX='users-consumer'
    }
    stages {
        stage('Building, pushing & deploying all container images') {          
            steps {
                sh '''
                   HEAD_COMMIT=$(git rev-parse --short HEAD)
                   TAG=$HEAD_COMMIT-$BUILD_ID
                   docker build --rm -t $DOCKER_USER/$USERS_PRODUCER_PREFIX:$TAG -t $DOCKER_USER/$USERS_PRODUCER_PREFIX:latest -f docker/usersProducer.nonroot.Dockerfile .
                   docker build --rm -t $DOCKER_USER/$ALBUMS_API_PREFIX:$TAG -t $DOCKER_USER/$ALBUMS_API_PREFIX:latest -f docker/albumsApi.nonroot.Dockerfile .
                   docker build --rm -t $DOCKER_USER/$ALBUMS_PRODUCER_PREFIX:$TAG -t $DOCKER_USER/$ALBUMS_PRODUCER_PREFIX:latest -f docker/albumsProducer.nonroot.Dockerfile .
                   docker build --rm -t $DOCKER_USER/$ALBUMS_CONSUMER_PREFIX:$TAG -t $DOCKER_USER/$ALBUMS_CONSUMER_PREFIX:latest -f docker/albumsConsumer.nonroot.Dockerfile .
                   docker build --rm -t $DOCKER_USER/$USERS_CONSUMER_PREFIX:$TAG -t $DOCKER_USER/$USERS_CONSUMER_PREFIX:latest -f docker/usersConsumer.nonroot.Dockerfile .
                   echo $DOCKER_TOKEN | docker login $DOCKER_SERVER -u $DOCKER_USER --password-stdin
                   docker push $DOCKER_USER/$USERS_PRODUCER_PREFIX --all-tags
                   docker push $DOCKER_USER/$ALBUMS_API_PREFIX --all-tags
                   docker push $DOCKER_USER/$ALBUMS_PRODUCER_PREFIX --all-tags
                   docker push $DOCKER_USER/$ALBUMS_CONSUMER_PREFIX --all-tags
                   kubectl set image -f kube/users-producer/deployment.yaml social-users-producer=$DOCKER_USER/$USERS_PRODUCER_PREFIX:$TAG              
                   kubectl set image -f kube/api/deployment.yaml social-albums-api=$DOCKER_USER/$ALBUMS_API_PREFIX:$TAG
                   kubectl set image -f kube/albums-producer/deployment.yaml social-albums-producer=$DOCKER_USER/$ALBUMS_PRODUCER_PREFIX:$TAG
                   kubectl set image -f kube/albums-consumer/deployment.yaml social-albums-consumer=$DOCKER_USER/$ALBUMS_CONSUMER_PREFIX:$TAG
                   kubectl set image -f kube/users-consumer/deployment.yaml social-users-consumer=$DOCKER_USER/$USERS_CONSUMER_PREFIX:$TAG
                '''
            }
        }
    }
}