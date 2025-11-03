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
                pip install -r requirements.txt
                """
            }
        }

        stage('Build') {
            steps {
                sh"""
                docker build -t carvalhoigor/nif-validator .
                """
            }
        }
    }

}

