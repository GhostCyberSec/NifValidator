#!groovy

pipeline {
    agent any
    environment {
        HOME = "${env.WORKSPACE}"
    }

    stages {

        stage('Docker environment') {
            agent {
                docker {
                    image 'python:3.11-slim'
                    reuseNode true
                }
            }
            steps {
                sh"""
                export PIP_DISABLE_PIP_VERSION_CHECK=1
                export PATH="$HOME/.local/bin:${PATH}"
                pip install -r requirements.txt
                pip install -r requirements-test.txt
                """
            }
        }

        stage('Unit test') {
            agent {
               docker {
                    image 'python:3.11-slim'
                    reuseNode true
                }
            }
            steps {
                sh 'python3 -m pytest --junitxml result.xml tests/'
            }
            post {
                always {
                // Archive the test results as artifacts
                archiveArtifacts artifacts: 'result.xml', allowEmptyArchive: true
                // Publish JUnit test results
                junit 'result.xml'
                }
            }
        }

         stage('Coverage report') {
            agent {
                docker {
                    image 'python:3.11-slim'
                    reuseNode true
                }
            }
            steps {
                sh'''
                python3 -m coverage run --source=. --omit=tests/* -m pytest tests
                python3 -m coverage report -m
                python3 -m coverage html
                '''
            }
            post {
                always {
                    publishHTML(target:[
                        allowMissing: false,
                        alwaysLinkToLastBuild: false,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }

         stage('Cyclomatic complexity analysis') {
                    agent {
                        docker {
                            image 'python:3.11-slim'
                            reuseNode true
                        }
                    }
                    steps {
                        sh 'python3 -m radon cc . -a -s --exclude site-packages'
                    }
        }

         stage('Quality Analysis') {
            parallel {
                stage('Integration tests') {
                    agent any
                    steps {
                        echo "TODO Integration tests"
                    }
                }
                stage('User Interface tests') {
                    agent any
                    steps {
                        echo "TODO UI Tests"
                    }
                }
                stage('PEP8 Verification') {
                    agent {
                        docker {
                            image 'python:3.11-slim'
                            reuseNode true
                        }
                    }
                    steps {
                        sh 'python3 -m flake8 . --exclude site-packages --exit-zero'
                    }
                }
            }
        }
        
        stage('Deliver') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'docker-id',
                    passwordVariable: 'passwd', 
                    usernameVariable: 'username')]) {
                    sh"""
                    printenv
                    docker build -t ${username}/${JOB_BASE_NAME} .
                    docker login -u ${username} -p ${passwd}
                    docker push ${username}/${JOB_BASE_NAME}
                    """
                } 
            }
        }

        stage('Beta testing') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'docker-id',
                    passwordVariable: 'passwd', 
                    usernameVariable: 'username')]) {
                    sshagent(credentials: ['cluster-credentials']) {
                        sh"""
                        ssh -o StrictHostKeyChecking=no redhat@172.31.36.26 docker rm -f ${JOB_BASE_NAME} || true
                        ssh -o StrictHostKeyChecking=no redhat@172.31.36.26 docker run -d --name ${JOB_BASE_NAME} -p 8080:9046 --pull always ${username}/${JOB_BASE_NAME}
                        """
                    }
                }
            }
        }
    }
}

