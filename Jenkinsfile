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
        PATH = "%PATH%;C:\\Windows\\System32;C:\\Users\\prapu\\AppData\\Local\\Programs\\Python\\Python38;\
        C:\\Users\\prapu\\AppData\\Local\\Programs\\Python\\Python38\\Scripts"
        WORKON_HOME = "C:\\Program Files (x86)\\Jenkins\\workspace\\local-library_master"
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
                    bat 'echo %WORKSPACE%'
                    bat 'echo %WORKON_HOME%'
                    bat 'echo %BUILD_TAG%'
                    bat 'python --version'
                    bat 'python -m pip list'
                    bat 'python -m virtualenv --version'
                    bat 'call virtualenvwrapper-win.bat'
                    bat '''python -m mkvirtualenv myenv'''
                }
            }
        }
        stage('Test environment') {
            steps {
                echo 'Testing'
                script {
                    bat 'virtualenv --version'

                }
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