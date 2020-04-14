pipeline {
    agent any

    triggers {
        pollSCM('*/5 * * * 1-5')
    }
    options {
        skipDefaultCheckout(true)
        // Keep the 10 most recent builds
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }
    environment {
        PATH = "%PATH%;c:\\Windows\\System32"
        PATH = 'C:\\Users\\prapu\\AppData\\Local\\Programs\\Python\\Python38\\python.exe:%PATH%'
    }

    stages {
        stage ("Code pull"){
            steps{
                checkout scm
            }
        }
        stage('Build environment') {
            steps {
                echo 'Building virtual environment'

                script {
                    bat 'echo %PATH%'
                    bat '''virtualenv %BUILD_TAG%
                           cmd /k ".\\%BUILD_TAG%\\Scripts\\activate.bat"'''
                }
            }
        }
        stage('Test') {
            steps {
                echo 'Testing'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying'
            }
        }
    }
    post {
        always {
            echo 'This will always run'
        }
        success {
            echo 'This will run only if successful'
        }
        failure {
            echo 'This will run only if failed'
        }
        unstable {
            echo 'This will run only if the run was marked as unstable'
        }
        changed {
            echo 'This will run only if the state of the Pipeline has changed'
            echo 'For example, if the Pipeline was previously failing but is now successful'
        }
    }
}