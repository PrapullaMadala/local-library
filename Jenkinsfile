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
        WORKON_HOME = ".\\Envs"
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
                    bat 'echo %BUILD_TAG%'
                    bat '''cmd /c "mkvirtualenv %BUILD_TAG% & workon %BUILD_TAG% & pip install -r requirements.txt"
                           '''
                }
            }
        }
        stage('Test environment') {
            steps {
                echo 'Testing'
                script {
                    bat 'lsvirtualenv'
                    bat '''cmd /k "workon %BUILD_TAG% & cd library & "'''
                }
            }
        }
        stage('Static code metrics') {
            steps {
                echo "Raw metrics"
                script {
                    bat '''cmd /k "workon %BUILD_TAG% & cd library & pytest --cov=.\\catalogapp --cov-report html"'''
                }
                echo "Code Coverage"
                script {
                    bat '''cmd /k "workon %BUILD_TAG% & cd library & pytest --cov=.\\catalogapp --cov-report xml"'''
                }
                echo "Style check"
                script {
                    bat '''cmd /k "workon %BUILD_TAG% & cd library & pylint --load-plugins pylint_django -v\
                    --rcfile=.pylintrc catalogapp > pylint.log || true"'''
                }
            }
            post{
                always{
                    step([$class: 'CoberturaPublisher',
                                   autoUpdateHealth: false,
                                   autoUpdateStability: false,
                                   coberturaReportFile: 'library\\coverage.xml',
                                   failNoReports: false,
                                   failUnhealthy: false,
                                   failUnstable: false,
                                   maxNumberOfBuilds: 10,
                                   onlyStable: false,
                                   sourceEncoding: 'ASCII',
                                   zoomCoverageChart: false])
                    publishHTML(target:[
                             allowMissing: false,
                             alwaysLinkToLastBuild: false,
                             keepAll: true,
                             reportDir: 'library\\htmlcov',
                             reportFiles: 'index.html',
                             reportName: 'HTML Report'])
                    recordIssues(
                        tool: pyLint('**\\pylint.log')
                        unstableTotalAll: 100,
                        )
                }
            }
        }
        stage('Unit tests') {
            steps {
                script {
                    bat '''cmd /k "workon %BUILD_TAG% & cd library & pytest --verbose --junit-xml pytest_reports.xml"'''
                }
            }
            post {
                always {
                    // Archive unit tests for the future
                    junit (allowEmptyResults: true,
                          testResults: '.\\pytest_reports.xml')
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
            bat 'rmvirtualenv %BUILD_TAG%'
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