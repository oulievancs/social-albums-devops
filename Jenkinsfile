def subject = "${env.JOB_NAME} - Build #${env.BUILD_NUMBER}"
def content = '${JELLY_SCRIPT,template="html"}'

pipeline {
    agent any
    environment {
        DOCKER_TOKEN=credentials('registry-creds')
        DOCKER_USER='angelosnm'
        DOCKER_SERVER='docker.io'
        DOCKER_PREFIX='docker.io/angelosnm/users-producer'
    }
    stages {
        stage('Building & pushing docker images to DockerHub') {
            steps {
                sh '''
                   HEAD_COMMIT=$(git rev-parse --short HEAD)
                   TAG=$HEAD_COMMIT-$BUILD_ID
                   docker build --rm -t $DOCKER_PREFIX:$TAG -t $DOCKER_PREFIX:latest -f docker/usersProducer.nonroot.Dockerfile .
                '''

                sh '''
                    echo $DOCKER_TOKEN | docker login $DOCKER_SERVER -u $DOCKER_USER --password-stdin
                    docker push $DOCKER_PREFIX --all-tags
                '''
            }
        }
    }
    
    post {
        always {
            sh 'docker image prune -a -f' // remove built images
            emailext(body: content, mimeType: 'text/html',
            replyTo: '$DEFAULT_REPLYTO', subject: subject,
            to: 'itp23108@hua.gr', attachLog: true )
            cleanWs()
        }
    }
}