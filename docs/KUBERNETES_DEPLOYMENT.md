# Kubernetes Deployment Guide

This guide provides comprehensive instructions for deploying the GenAI Chatbot application on Kubernetes.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Cluster Setup](#cluster-setup)
- [Configuration Management](#configuration-management)
- [Deployment](#deployment)
- [Scaling and High Availability](#scaling-and-high-availability)
- [Monitoring and Observability](#monitoring-and-observability)
- [Maintenance and Updates](#maintenance-and-updates)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

## Prerequisites

- **Kubernetes Cluster**: Version 1.24 or higher
- **kubectl**: Configured to connect to your cluster
- **Helm**: Version 3.0 or higher (recommended)
- **Docker Registry Access**: To thingxcloud Docker Hub account
- **Cert-Manager**: For TLS certificate management (optional)
- **Nginx Ingress Controller**: For ingress management

### Required Kubernetes Resources

- **Minimum**: 4 CPU cores, 8GB RAM, 100GB storage
- **Recommended**: 8 CPU cores, 16GB RAM, 200GB storage
- **Storage Classes**: For persistent volumes

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/nithinmohantk/genai-boilerplate-python.git
cd genai-boilerplate-python/deployments/kubernetes
```

### 2. Create Namespace and Resources

```bash
# Create namespace and basic resources
kubectl apply -f namespace.yaml

# Create secrets (update with your values first)
kubectl apply -f secrets.yaml

# Create ConfigMaps
kubectl apply -f configmap.yaml
```

### 3. Deploy Database and Cache

```bash
# Deploy PostgreSQL
kubectl apply -f postgres.yaml

# Deploy Redis
kubectl apply -f redis.yaml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n genai-chatbot --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n genai-chatbot --timeout=300s
```

### 4. Deploy Application

```bash
# Deploy backend
kubectl apply -f backend.yaml

# Deploy frontend
kubectl apply -f frontend.yaml

# Configure ingress
kubectl apply -f ingress.yaml
```

### 5. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n genai-chatbot

# Check services
kubectl get svc -n genai-chatbot

# Check ingress
kubectl get ingress -n genai-chatbot
```

## Cluster Setup

### Local Development Cluster

#### Using Kind

```bash
# Create kind cluster
cat << EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: genai-cluster
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
- role: worker
- role: worker
EOF

# Install nginx ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```

#### Using Minikube

```bash
# Start minikube
minikube start --memory=8192 --cpus=4

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard
```

### Cloud Providers

#### Amazon EKS

```bash
# Create EKS cluster
eksctl create cluster \
  --name genai-cluster \
  --version 1.28 \
  --region us-west-2 \
  --nodegroup-name standard-workers \
  --node-type m5.large \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 4 \
  --managed

# Install AWS Load Balancer Controller
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=genai-cluster
```

#### Google GKE

```bash
# Create GKE cluster
gcloud container clusters create genai-cluster \
  --zone us-central1-a \
  --machine-type n1-standard-2 \
  --num-nodes 3 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 5

# Get credentials
gcloud container clusters get-credentials genai-cluster --zone us-central1-a
```

#### Azure AKS

```bash
# Create resource group
az group create --name genai-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group genai-rg \
  --name genai-cluster \
  --node-count 3 \
  --node-vm-size Standard_DS2_v2 \
  --enable-addons monitoring

# Get credentials
az aks get-credentials --resource-group genai-rg --name genai-cluster
```

## Configuration Management

### Secrets Configuration

Update the secrets file with your actual values:

```bash
# Generate base64 encoded secrets
echo -n "your_postgres_password" | base64
echo -n "your_redis_password" | base64
echo -n "your_secret_key" | base64

# Edit secrets.yaml with actual values
vim deployments/kubernetes/secrets.yaml
```

### Environment-Specific Configurations

Create environment-specific overlays:

```bash
mkdir -p deployments/kubernetes/overlays/{development,staging,production}
```

#### Development Overlay

```yaml
# deployments/kubernetes/overlays/development/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

patchesStrategicMerge:
- deployment-dev.yaml

images:
- name: thingxcloud/genai-chatbot-backend
  newTag: develop
- name: thingxcloud/genai-chatbot-frontend
  newTag: develop

replicas:
- name: backend
  count: 1
- name: frontend
  count: 1
```

### ConfigMap Updates

To update configuration without rebuilding:

```bash
# Update ConfigMap
kubectl patch configmap backend-config -n genai-chatbot \
  --patch='{"data":{"LOG_LEVEL":"DEBUG"}}'

# Restart deployments to pick up changes
kubectl rollout restart deployment/backend -n genai-chatbot
```

## Deployment

### Deployment Strategies

#### Rolling Updates (Default)

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

#### Blue-Green Deployment

```bash
# Deploy new version with different label
kubectl patch deployment backend -n genai-chatbot \
  -p '{"spec":{"selector":{"matchLabels":{"version":"v2"}},"template":{"metadata":{"labels":{"version":"v2"}}}}}'

# Update service to point to new version
kubectl patch service backend-service -n genai-chatbot \
  -p '{"spec":{"selector":{"version":"v2"}}}'
```

#### Canary Deployment

Use Istio or Flagger for advanced canary deployments:

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: backend-canary
  namespace: genai-chatbot
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  service:
    port: 8000
  analysis:
    interval: 30s
    threshold: 5
    maxWeight: 50
    stepWeight: 10
```

### Database Migrations

```bash
# Run database migrations
kubectl run migration-job \
  --image=thingxcloud/genai-chatbot-backend:latest \
  --rm -i --tty \
  --restart=Never \
  --namespace=genai-chatbot \
  --env="DATABASE_URL=postgresql://..." \
  -- python -m alembic upgrade head
```

### Initialization Jobs

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: theme-init-job
  namespace: genai-chatbot
spec:
  template:
    spec:
      containers:
      - name: theme-init
        image: thingxcloud/genai-chatbot-backend:latest
        command: ["python", "-m", "backend.startup.theme_init"]
        envFrom:
        - configMapRef:
            name: backend-config
        - secretRef:
            name: app-secrets
      restartPolicy: Never
  backoffLimit: 3
```

## Scaling and High Availability

### Horizontal Pod Autoscaling

HPA is already configured in the deployment files:

```bash
# Check HPA status
kubectl get hpa -n genai-chatbot

# Describe HPA for details
kubectl describe hpa backend-hpa -n genai-chatbot

# Manual scaling override
kubectl scale deployment backend --replicas=5 -n genai-chatbot
```

### Vertical Pod Autoscaling

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: backend-vpa
  namespace: genai-chatbot
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  updatePolicy:
    updateMode: "Auto"
```

### Cluster Autoscaling

Configure cluster autoscaling based on your cloud provider:

```bash
# AWS EKS
eksctl create nodegroup \
  --cluster=genai-cluster \
  --region=us-west-2 \
  --name=autoscaling-group \
  --node-type=m5.large \
  --nodes=2 \
  --nodes-min=2 \
  --nodes-max=8 \
  --asg-access
```

### Multi-Zone Deployment

```yaml
spec:
  template:
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - backend
              topologyKey: kubernetes.io/hostname
```

## Monitoring and Observability

### Prometheus and Grafana

Deploy monitoring stack:

```bash
# Add Prometheus community helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=admin123 \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
```

### Application Metrics

Add ServiceMonitor for your application:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: backend-metrics
  namespace: genai-chatbot
spec:
  selector:
    matchLabels:
      app: backend
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

### Logging

Deploy EFK stack:

```bash
# Install Elasticsearch
helm repo add elastic https://helm.elastic.co
helm install elasticsearch elastic/elasticsearch \
  --namespace logging \
  --create-namespace

# Install Fluent Bit
helm repo add fluent https://fluent.github.io/helm-charts
helm install fluent-bit fluent/fluent-bit \
  --namespace logging \
  --set config.outputs[0].name=es \
  --set config.outputs[0].match="*" \
  --set config.outputs[0].host=elasticsearch-master

# Install Kibana
helm install kibana elastic/kibana \
  --namespace logging \
  --set service.type=LoadBalancer
```

### Health Checks and Alerts

Configure Prometheus alerts:

```yaml
groups:
- name: genai-chatbot
  rules:
  - alert: BackendDown
    expr: up{job="backend-service"} == 0
    for: 1m
    annotations:
      summary: Backend service is down
      
  - alert: HighMemoryUsage
    expr: container_memory_usage_bytes{pod=~"backend-.*"} / container_spec_memory_limit_bytes > 0.9
    for: 5m
    annotations:
      summary: High memory usage detected
```

## Maintenance and Updates

### Rolling Updates

```bash
# Update backend image
kubectl set image deployment/backend backend=thingxcloud/genai-chatbot-backend:v1.2.0 -n genai-chatbot

# Check rollout status
kubectl rollout status deployment/backend -n genai-chatbot

# Rollback if needed
kubectl rollout undo deployment/backend -n genai-chatbot
```

### Backup Strategies

#### Database Backup

```bash
# Create backup CronJob
cat << EOF | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: genai-chatbot
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: postgres-backup
            image: postgres:15-alpine
            command:
            - /bin/bash
            - -c
            - |
              BACKUP_FILE="/backup/postgres-\$(date +%Y%m%d%H%M%S).sql"
              pg_dump -h postgres-service -U \$POSTGRES_USER -d \$POSTGRES_DB > \$BACKUP_FILE
              # Upload to S3 or other storage
            env:
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: postgres-credentials
                  key: username
            - name: POSTGRES_DB
              valueFrom:
                secretKeyRef:
                  name: postgres-credentials
                  key: database
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-credentials
                  key: password
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
EOF
```

#### Application State Backup

Use Velero for cluster backup:

```bash
# Install Velero
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.7.0 \
  --bucket my-backup-bucket \
  --secret-file ./credentials-velero

# Create backup
velero backup create genai-chatbot-backup --include-namespaces genai-chatbot

# Schedule regular backups
velero schedule create genai-chatbot-daily --schedule="0 2 * * *" --include-namespaces genai-chatbot
```

### Certificate Management

Using cert-manager for TLS:

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for cert-manager to be ready
kubectl wait --for=condition=ready pod -l app=cert-manager -n cert-manager --timeout=300s

# Create ClusterIssuer (already in ingress.yaml)
kubectl apply -f ingress.yaml
```

## Troubleshooting

### Common Issues

#### Pod Stuck in Pending State

```bash
# Check pod events
kubectl describe pod <pod-name> -n genai-chatbot

# Common causes:
# 1. Insufficient resources
kubectl top nodes
kubectl describe node <node-name>

# 2. Image pull issues
kubectl describe pod <pod-name> -n genai-chatbot | grep -A 5 "Events:"

# 3. PVC binding issues
kubectl get pvc -n genai-chatbot
kubectl describe pvc <pvc-name> -n genai-chatbot
```

#### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints backend-service -n genai-chatbot

# Test service connectivity
kubectl run test-pod --image=busybox -i --tty --rm -- /bin/sh
# Inside pod: wget -O- http://backend-service:8000/health

# Check ingress configuration
kubectl describe ingress genai-chatbot-ingress -n genai-chatbot
```

#### Database Connection Issues

```bash
# Test database connectivity
kubectl exec -it deployment/backend -n genai-chatbot -- \
  psql -h postgres-service -U genai_user -d genai_chatbot -c "SELECT version();"

# Check database logs
kubectl logs deployment/postgres -n genai-chatbot

# Verify secrets
kubectl get secret postgres-credentials -n genai-chatbot -o yaml
```

### Debug Commands

```bash
# Get comprehensive cluster information
kubectl cluster-info dump --output-directory=./cluster-dump

# Check resource usage
kubectl top nodes
kubectl top pods -n genai-chatbot

# View events
kubectl get events -n genai-chatbot --sort-by=.metadata.creationTimestamp

# Port forward for debugging
kubectl port-forward svc/backend-service 8000:8000 -n genai-chatbot
kubectl port-forward svc/frontend-service 3000:8080 -n genai-chatbot
```

### Performance Troubleshooting

```bash
# Check HPA metrics
kubectl describe hpa backend-hpa -n genai-chatbot

# Resource utilization
kubectl top pods -n genai-chatbot --containers

# Network policies (if enabled)
kubectl describe networkpolicy -n genai-chatbot
```

## Security Best Practices

### RBAC Configuration

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: genai-chatbot
  name: genai-app-role
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: genai-app-rolebinding
  namespace: genai-chatbot
subjects:
- kind: ServiceAccount
  name: genai-backend-sa
  namespace: genai-chatbot
roleRef:
  kind: Role
  name: genai-app-role
  apiGroup: rbac.authorization.k8s.io
```

### Pod Security Standards

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: genai-chatbot
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
  namespace: genai-chatbot
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    - podSelector: {} # Allow from pods in same namespace
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

### Secret Management

Consider using external secret management:

```bash
# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets-system --create-namespace

# Example with AWS Secrets Manager
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: genai-chatbot
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-west-2
      auth:
        secretRef:
          accessKeyIDSecretRef:
            name: aws-creds
            key: access-key-id
          secretAccessKeySecretRef:
            name: aws-creds
            key: secret-access-key
```

## Advanced Topics

### GitOps with ArgoCD

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Create Application
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: genai-chatbot
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/nithinmohantk/genai-boilerplate-python
    targetRevision: HEAD
    path: deployments/kubernetes
  destination:
    server: https://kubernetes.default.svc
    namespace: genai-chatbot
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Service Mesh with Istio

```bash
# Install Istio
istioctl install --set values.defaultRevision=default

# Enable sidecar injection
kubectl label namespace genai-chatbot istio-injection=enabled

# Create VirtualService for traffic management
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: backend-vs
  namespace: genai-chatbot
spec:
  http:
  - match:
    - uri:
        prefix: "/api/"
    route:
    - destination:
        host: backend-service
        port:
          number: 8000
```

---

For more information, see:
- [Docker Deployment Guide](./DOCKER_DEPLOYMENT.md)
- [Architecture Documentation](./ARCHITECTURE.md)
- [Security Guide](./SECURITY.md)
