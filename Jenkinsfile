pipeline {
  agent any
  environment {
    WSS_TAG = "1.3"
    credentialsId = credentials('WSS_GIT_CREDENTIALS_ID')
  }
  stages {
    stage('Checkout') {
      steps {
        script {
          echo 'Checking out code from git...'
          git credentialsId: credentialsId, url: 'git@github.com:q2kit/ws-service.git'
          checkout([
            $class: 'GitSCM',
            branches: [[name: 'master']],
            doGenerateSubmoduleConfigurations: false,
          ])
        }
      }
    }

    stage('Build') {
      steps {
        script {
          echo 'Building docker image...'
          sh 'cp .env.example .env'
          sh 'docker build -t q2kit/wss-backend:${WSS_TAG} .'
        }
      }
    }

    stage('Test') {
      steps {
        script {
          echo 'Running tests...'
          sh 'docker run --rm --name wss-backend-test --network ws-service_default q2kit/wss-backend:1.0 python manage.py test'
        }
      }
    }

    stage('Deploy') {
      steps {
        script {
          echo 'Deploying docker image...'
          sh 'docker push q2kit/wss-backend:${WSS_TAG}'
        }
      }
    }

    stage('Cleanup') {
      steps {
        script {
          echo 'Cleaning up...'
          sh 'docker rmi q2kit/wss-backend:${WSS_TAG}'
        }
      }
    }
  }

  post {
    success {
      echo 'Build and deployment successful!'
      emailext subject: 'Project $PROJECT_NAME - Build # $BUILD_NUMBER - $BUILD_STATUS!',
        body: 'Project $PROJECT_NAME - Build # $BUILD_NUMBER - $BUILD_STATUS:\n\nCheck console output at $BUILD_URL to view the results.',
        to: 'dhq1440p@gmail.com'
    }
    failure {
      echo 'Build or deployment failed!'
      emailext subject: 'Project $PROJECT_NAME - Build # $BUILD_NUMBER - $BUILD_STATUS!',
        body: 'Project $PROJECT_NAME - Build # $BUILD_NUMBER - $BUILD_STATUS:\n\nCheck console output at $BUILD_URL to view the results.',
        to: 'dhq1440p@gmail.com'
    }
  }
}