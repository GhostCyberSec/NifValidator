#!groovy

pipeline {
    agent any

    environment {
        // Não definir HOME aqui — será definido por stage
        DOCKER_IMAGE = "${env.JOB_BASE_NAME.toLowerCase()}"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    stages {

        // ====================================================================
        // 1. Preparar ambiente Docker com dependências
        // ====================================================================
        stage('Setup Environment') {
            agent {
                docker {
                    image 'python:3.11-slim'
                    reuseNode true
                    args "-v ${env.WORKSPACE}:${env.WORKSPACE} -w ${env.WORKSPACE}"
                }
            }
            steps {
                sh '''
                    export HOME="${WORKSPACE}"
                    export PATH="$HOME/.local/bin:$PATH"
                    export PIP_DISABLE_PIP_VERSION_CHECK=1
                    export PIP_USER=1

                    echo "Instalando dependências..."
                    pip install --user -r requirements.txt
                    pip install --user -r requirements-test.txt

                    echo "Dependências instaladas em $HOME/.local"
                '''
            }
        }

        // ====================================================================
        // 2. Testes Unitários + Cobertura
        // ====================================================================
        stage('Test & Coverage') {
            agent {
                docker {
                    image 'python:3.11-slim'
                    reuseNode true
                    args "-v ${env.WORKSPACE}:${env.WORKSPACE} -w ${env.WORKSPACE}"
                }
            }
            steps {
                sh '''
                    export HOME="${WORKSPACE}"
                    export PATH="$HOME/.local/bin:$PATH"

                    echo "Executando testes com cobertura..."
                    python3 -m coverage run --source=. --omit=tests/*,*/site-packages/* -m pytest tests/ -q --junitxml=result.xml

                    echo "Gerando relatórios..."
                    python3 -m coverage report -m
                    python3 -m coverage html -d htmlcov
                '''
            }
            post {
                always {
                    // Arquivar XML de resultados (mesmo se vazio)
                    archiveArtifacts artifacts: 'result.xml', allowEmptyArchive: true, fingerprint: true

                    // Publicar resultados JUnit
                    junit testResults: 'result.xml', allowEmptyResults: true

                    // Publicar relatório HTML de cobertura
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report',
                        reportTitles: 'Cobertura de Código'
                    ])
                }
            }
        }

        // ====================================================================
        // 3. Análise de Complexidade Ciclomática
        // ====================================================================
        stage('Cyclomatic Complexity') {
            agent {
                docker {
                    image 'python:3.11-slim'
                    reuseNode true
                    args "-v ${env.WORKSPACE}:${env.WORKSPACE} -w ${env.WORKSPACE}"
                }
            }
            steps {
                sh '''
                    export HOME="${WORKSPACE}"
                    export PATH="$HOME/.local/bin:$PATH"

                    echo "Analisando complexidade ciclomatica..."
                    python3 -m radon cc . -a -s --exclude "tests/*,htmlcov/*,site-packages/*"
                '''
            }
        }

        // ====================================================================
        // 4. Análise de Qualidade (Paralelo)
        // ====================================================================
        stage('Quality Analysis') {
            parallel {

                stage('Integration Tests') {
                    agent any
                    steps {
                        echo "TODO: Implementar testes de integração"
                        // sh 'your-integration-test-command'
                    }
                }

                stage('UI Tests') {
                    agent any
                    steps {
                        echo "TODO: Implementar testes de interface"
                        // sh 'your-ui-test-command'
                    }
                }

                stage('PEP8 Style Check') {
                    agent {
                        docker {
                            image 'python:3.11-slim'
                            reuseNode true
                            args "-v ${env.WORKSPACE}:${env.WORKSPACE} -w ${env.WORKSPACE}"
                        }
                    }
                    steps {
                        sh '''
                            export HOME="${WORKSPACE}"
                            export PATH="$HOME/.local/bin:$PATH"

                            echo "Verificando conformidade PEP8..."
                            python3 -m flake8 . --exclude=tests,htmlcov,venv,build,dist,site-packages --max-line-length=88 --exit-zero
                        '''
                    }
                }
            }
        }

        // ====================================================================
        // 5. Build e Push da Imagem Docker
        // ====================================================================
        stage('Build & Push Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'docker-id',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo "Construindo imagem Docker..."
                        docker build -t ${DOCKER_USER}/${DOCKER_IMAGE}:${IMAGE_TAG} .
                        docker tag ${DOCKER_USER}/${DOCKER_IMAGE}:${IMAGE_TAG} ${DOCKER_USER}/${DOCKER_IMAGE}:latest

                        echo "Fazendo login no Docker Hub..."
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin

                        echo "Enviando imagem..."
                        docker push ${DOCKER_USER}/${DOCKER_IMAGE}:${IMAGE_TAG}
                        docker push ${DOCKER_USER}/${DOCKER_IMAGE}:latest
                    '''
                }
            }
        }

        // ====================================================================
        // 6. Deploy em Ambiente Beta
        // ====================================================================
        stage('Deploy to Beta') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'docker-id',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    sshagent(credentials: ['cluster-credentials']) {
                        sh '''
                            set +e  # Evitar falha se container não existir

                            echo "Parando e removendo container antigo..."
                            ssh -o StrictHostKeyChecking=no redhat@172.31.36.26 \
                                "docker rm -f ${DOCKER_IMAGE} || true"

                            echo "Puxando nova imagem..."
                            ssh -o StrictHostKeyChecking=no redhat@172.31.36.26 \
                                "echo '$DOCKER_PASS' | docker login -u '$DOCKER_USER' --password-stdin"

                            echo "Iniciando novo container..."
                            ssh -o StrictHostKeyChecking=no redhat@172.31.36.26 \
                                "docker run -d --name ${DOCKER_IMAGE} -p 8080:9046 --pull always ${DOCKER_USER}/${DOCKER_IMAGE}:latest"

                            echo "Deploy concluído com sucesso!"
                        '''
                    }
                }
            }
        }
    }

    // ====================================================================
    // Post-build actions
    // ====================================================================
    post {
        always {
            echo "Pipeline concluído."
        }
        success {
            echo "Build #${env.BUILD_NUMBER} concluído com sucesso!"
        }
        failure {
            echo "Falha no build #${env.BUILD_NUMBER}. Verifique os logs."
        }
        cleanup {
            // Limpar imagens antigas (opcional)
            sh '''
                docker image prune -f || true
            '''
        }
    }
}