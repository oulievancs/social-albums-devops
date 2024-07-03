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
        KUBE_ALBUMS_CONSUMER_DEPLOYMENT='kube/albums-consumer/deployment.yaml'
        KUBE_ALBUMS_PRODUCER_DEPLOYMENT='kube/albums-producer/deployment.yaml'
        KUBE_USERS_PRODUCER_DEPLOYMENT='kube/users-producer/deployment.yaml'
        KUBE_API_DEPLOYMENT='kube/api/deployment.yaml'
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
        stage('Building & pushing users-producer Docker images to DockerHub') {
            when {
                expression {
                    def changedFiles = sh(script: "git diff --name-only HEAD~1", returnStdout: true).trim().split('\n')
                    return changedFiles.contains('docker/usersProducer.nonroot.Dockerfile') ||
                           changedFiles.contains('extraction/usersWebApp.py')
                }
            }
            steps {
                script {
                    def imageTag = sh(script: '''
                        HEAD_COMMIT=$(git rev-parse --short HEAD)
                        echo $HEAD_COMMIT-$BUILD_ID
                    ''', returnStdout: true).trim()

                    sh '''
                       docker build --rm -t $USERS_PRODUCER_PREFIX:$imageTag -t $USERS_PRODUCER_PREFIX:latest -f docker/usersProducer.nonroot.Dockerfile .
                       echo $DOCKER_TOKEN | docker login $DOCKER_SERVER -u $DOCKER_USER --password-stdin
                       docker push $USERS_PRODUCER_PREFIX --all-tags
                    '''
                    updateKubeDeployment(KUBE_USERS_PRODUCER_DEPLOYMENT, "$USERS_PRODUCER_PREFIX:$imageTag")
                }
            }
        }
        stage('Building & pushing albums-api Docker images to DockerHub') {
            when {
                expression {
                    def changedFiles = sh(script: "git diff --name-only HEAD~1", returnStdout: true).trim().split('\n')
                    return changedFiles.contains('docker/albumsApi.nonroot.Dockerfile') ||
                           changedFiles.contains('api/apiServer.py')
                }
            }
            steps {
                script {
                    def imageTag = sh(script: '''
                        HEAD_COMMIT=$(git rev-parse --short HEAD)
                        echo $HEAD_COMMIT-$BUILD_ID
                    ''', returnStdout: true).trim()

                    sh '''
                       docker build --rm -t $ALBUMS_API_PREFIX:$imageTag -t $ALBUMS_API_PREFIX:latest -f docker/albumsApi.nonroot.Dockerfile .
                       echo $DOCKER_TOKEN | docker login $DOCKER_SERVER -u $DOCKER_USER --password-stdin
                       docker push $ALBUMS_API_PREFIX --all-tags
                    '''
                    updateKubeDeployment(KUBE_API_DEPLOYMENT, "$ALBUMS_API_PREFIX:$imageTag")
                }
            }
        }
        stage('Building & pushing albums-producer Docker images to DockerHub') {
            when {
                expression {
                    def changedFiles = sh(script: "git diff --name-only HEAD~1", returnStdout: true).trim().split('\n')
                    return changedFiles.contains('docker/albumsProducer.nonroot.Dockerfile') ||
                           changedFiles.contains('extraction/artistsWebApp.py')
                }
            }
            steps {
                script {
                    def imageTag = sh(script: '''
                        HEAD_COMMIT=$(git rev-parse --short HEAD)
                        echo $HEAD_COMMIT-$BUILD_ID
                    ''', returnStdout: true).trim()

                    sh '''
                       docker build --rm -t $ALBUMS_PRODUCER_PREFIX:$imageTag -t $ALBUMS_PRODUCER_PREFIX:latest -f docker/albumsProducer.nonroot.Dockerfile .
                       echo $DOCKER_TOKEN | docker login $DOCKER_SERVER -u $DOCKER_USER --password-stdin
                       docker push $ALBUMS_PRODUCER_PREFIX --all-tags
                    '''
                    updateKubeDeployment(KUBE_ALBUMS_PRODUCER_DEPLOYMENT, "$ALBUMS_PRODUCER_PREFIX:$imageTag")
                }
            }
        }
        stage('Building & pushing albums-consumer Docker images to DockerHub') {
            when {
                expression {
                    def changedFiles = sh(script: "git diff --name-only HEAD~1", returnStdout: true).trim().split('\n')
                    return changedFiles.contains('docker/albumsConsumer.nonroot.Dockerfile') ||
                           changedFiles.contains('transformationLoad/transformationAndLoadApp.py')
                }
            }
            steps {
                script {
                    def imageTag = sh(script: '''
                        HEAD_COMMIT=$(git rev-parse --short HEAD)
                        echo $HEAD_COMMIT-$BUILD_ID
                    ''', returnStdout: true).trim()

                    sh '''
                       docker build --rm -t $ALBUMS_CONSUMER_PREFIX:$imageTag -t $ALBUMS_CONSUMER_PREFIX:latest -f docker/albumsConsumer.nonroot.Dockerfile .
                       echo $DOCKER_TOKEN | docker login $DOCKER_SERVER -u $DOCKER_USER --password-stdin
                       docker push $ALBUMS_CONSUMER_PREFIX --all-tags
                    '''
                    updateKubeDeployment(KUBE_ALBUMS_CONSUMER_DEPLOYMENT, "$ALBUMS_CONSUMER_PREFIX:$imageTag")
                }
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

// Function to update Kubernetes Deployment YAML file with new image tag
def updateKubeDeployment(String yamlFile, String newImage) {
    script {
        sh "sed -i \"s|image:.*|image: $newImage|\" $yamlFile"
    }
}
