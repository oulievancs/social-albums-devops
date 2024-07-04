def subject = "${env.JOB_NAME} - Build #${env.BUILD_NUMBER}"
def content = '${JELLY_SCRIPT,template="html"}'

pipeline {
    agent any
    environment {
        DOCKER_TOKEN=credentials('registry-creds')
        DOCKER_USER='angelosnm'
        DOCKER_SERVER='docker.io'
        USERS_PRODUCER_PREFIX='docker.io/angelosnm/users-producer'
        ALBUMS_API_PREFIX='docker.io/angelosnm/albums-api'
        ALBUMS_PRODUCER_PREFIX='docker.io/angelosnm/albums-producer'
        ALBUMS_CONSUMER_PREFIX='docker.io/angelosnm/albums-consumer'
    }
    stages {
        stage('Check for relevant changes') {
            steps {
                script {
                    def changedFiles = sh(script: "git diff --name-only HEAD~1", returnStdout: true).trim().split('\n')
                    def usersProducerChanges = changedFiles.any { file -> 
                        file == 'docker/usersProducer.nonroot.Dockerfile' || 
                        file == 'extraction/usersWebApp.py' 
                    }
                    def albumsApiChanges = changedFiles.any { file -> 
                        file == 'docker/albumsApi.nonroot.Dockerfile' || 
                        file == 'api/apiServer.py' 
                    }
                    def albumsProducerChanges = changedFiles.any { file -> 
                        file == 'docker/albumsProducer.nonroot.Dockerfile' || 
                        file == 'extraction/artistsWebApp.py' 
                    }
                    def albumsConsumerChanges = changedFiles.any { file -> 
                        file == 'docker/albumsConsumer.nonroot.Dockerfile' || 
                        file == 'transformationLoad/transformationAndLoadApp.py' 
                    }
                    def commonChanges = changedFiles.any { file -> 
                        file.startsWith('common/')
                    }
                    if (!usersProducerChanges && !albumsApiChanges && !albumsProducerChanges && !albumsConsumerChanges && !commonChanges) {
                        currentBuild.result = 'NOT_BUILT'
                        error('No relevant changes detected. Skipping build.')
                    }
                }
            }
        }
        stage('Building, pushing & deploying users-producer container image') {
            when {
                expression {
                    def changedFiles = sh(script: "git diff --name-only HEAD~1", returnStdout: true).trim().split('\n')
                    return changedFiles.contains('docker/usersProducer.nonroot.Dockerfile') ||
                           changedFiles.contains('extraction/usersWebApp.py')
                }
            }
            steps {
                sh '''
                   HEAD_COMMIT=$(git rev-parse --short HEAD)
                   TAG=$HEAD_COMMIT-$BUILD_ID
                   docker build --rm -t $USERS_PRODUCER_PREFIX:$TAG -t $USERS_PRODUCER_PREFIX:latest -f docker/usersProducer.nonroot.Dockerfile .
                '''
                sh '''
                    echo $DOCKER_TOKEN | docker login $DOCKER_SERVER -u $DOCKER_USER --password-stdin
                    docker push $USERS_PRODUCER_PREFIX --all-tags
                '''
                sh """
                    sed -i 's|image: ${env.USERS_PRODUCER_PREFIX}:.*|image: ${env.USERS_PRODUCER_PREFIX}:${TAG}|g' kube/users-producer/deployment.yaml
                    kubectl apply -f kube/users-producer/deployment.yaml
                """
            }
        }
        stage('Building, pushing & deploying albums-api container image') {
            when {
                expression {
                    def changedFiles = sh(script: "git diff --name-only HEAD~1", returnStdout: true).trim().split('\n')
                    return changedFiles.contains('docker/albumsApi.nonroot.Dockerfile') ||
                           changedFiles.contains('api/apiServer.py')
                }
            }
            steps {
                sh '''
                   HEAD_COMMIT=$(git rev-parse --short HEAD)
                   TAG=$HEAD_COMMIT-$BUILD_ID
                   docker build --rm -t $ALBUMS_API_PREFIX:$TAG -t $ALBUMS_API_PREFIX:latest -f docker/albumsApi.nonroot.Dockerfile .
                '''
                sh '''
                    echo $DOCKER_TOKEN | docker login $DOCKER_SERVER -u $DOCKER_USER --password-stdin
                    docker push $ALBUMS_API_PREFIX --all-tags
                '''
            }
        }
        stage('Building, pushing & deploying albums-producer container image') {
            when {
                expression {
                    def changedFiles = sh(script: "git diff --name-only HEAD~1", returnStdout: true).trim().split('\n')
                    return changedFiles.contains('docker/albumsProducer.nonroot.Dockerfile') ||
                           changedFiles.contains('extraction/artistsWebApp.py')
                }
            }
            steps {
                sh '''
                   HEAD_COMMIT=$(git rev-parse --short HEAD)
                   TAG=$HEAD_COMMIT-$BUILD_ID
                   docker build --rm -t $ALBUMS_PRODUCER_PREFIX:$TAG -t $ALBUMS_PRODUCER_PREFIX:latest -f docker/albumsProducer.nonroot.Dockerfile .
                '''
                sh '''
                    echo $DOCKER_TOKEN | docker login $DOCKER_SERVER -u $DOCKER_USER --password-stdin
                    docker push $ALBUMS_PRODUCER_PREFIX --all-tags
                '''
            }
        }
        stage('Building, pushing & deploying albums-consumer container image') {
            when {
                expression {
                    def changedFiles = sh(script: "git diff --name-only HEAD~1", returnStdout: true).trim().split('\n')
                    return changedFiles.contains('docker/albumsConsumer.nonroot.Dockerfile') ||
                           changedFiles.contains('transformationLoad/transformationAndLoadApp.py')
                }
            }
            steps {
                sh '''
                   HEAD_COMMIT=$(git rev-parse --short HEAD)
                   TAG=$HEAD_COMMIT-$BUILD_ID
                   docker build --rm -t $ALBUMS_CONSUMER_PREFIX:$TAG -t $ALBUMS_CONSUMER_PREFIX:latest -f docker/albumsConsumer.nonroot.Dockerfile .
                '''
                sh '''
                    echo $DOCKER_TOKEN | docker login $DOCKER_SERVER -u $DOCKER_USER --password-stdin
                    docker push $ALBUMS_CONSUMER_PREFIX --all-tags
                '''
            }
        }
        stage('Building, pushing & deploying all container images') {
            when {
                expression {
                    def changedFiles = sh(script: "git diff --name-only HEAD~1", returnStdout: true).trim().split('\n')
                    return changedFiles.any { file -> file.startsWith('common/') }
                }
            }
            steps {
                sh '''
                    HEAD_COMMIT=$(git rev-parse --short HEAD)
                    TAG=$HEAD_COMMIT-$BUILD_ID
                    docker build --rm -t $USERS_PRODUCER_PREFIX:$TAG -t $USERS_PRODUCER_PREFIX:latest -f docker/usersProducer.nonroot.Dockerfile .
                    docker build --rm -t $ALBUMS_API_PREFIX:$TAG -t $ALBUMS_API_PREFIX:latest -f docker/albumsApi.nonroot.Dockerfile .
                    docker build --rm -t $ALBUMS_PRODUCER_PREFIX:$TAG -t $ALBUMS_PRODUCER_PREFIX:latest -f docker/albumsProducer.nonroot.Dockerfile .
                    docker build --rm -t $ALBUMS_CONSUMER_PREFIX:$TAG -t $ALBUMS_CONSUMER_PREFIX:latest -f docker/albumsConsumer.nonroot.Dockerfile .
                '''
                sh '''
                    echo $DOCKER_TOKEN | docker login $DOCKER_SERVER -u $DOCKER_USER --password-stdin
                    docker push $USERS_PRODUCER_PREFIX --all-tags
                    docker push $ALBUMS_API_PREFIX --all-tags
                    docker push $ALBUMS_PRODUCER_PREFIX --all-tags
                    docker push $ALBUMS_CONSUMER_PREFIX --all-tags
                '''
            }
        }
    }

    post {
        always {
            script {
                if (currentBuild.result != 'NOT_BUILT') {
                    sh 'docker image prune -a -f'
                }
            }
            emailext(body: content, mimeType: 'text/html',
            replyTo: '$DEFAULT_REPLYTO', subject: subject,
            to: 'itp23108@hua.gr', attachLog: true )
            cleanWs()
        }
    }
}
