    #!/bin/sh

    if [ "$DATABASE" = "postgres" ]; then
        echo "Waiting for postgres..."

        while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
        sleep 0.1
        done

        echo "PostgreSQL started"
    fi

    # Make migrations and migrate the database.
    echo "Making migrations and migrating the database. "
    python manage.py makemigrations main --noinput 
    python manage.py migrate --noinput 
    exec "$@"apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    run: dealership
  name: dealership
spec:
  replicas: 1
  selector:
    matchLabels:
      run: dealership
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
  template:
    metadata:
      labels:
        run: dealership
    spec:
      containers:
      - image: us.icr.io/$MY_NAMESPACE/dealership:latest
        imagePullPolicy: Always
        name: dealership
        ports:
        - containerPort: 8000
          protocol: TCP
      restartPolicy: Always
  replicas: 1apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    run: dealership
  name: dealership
spec:
  replicas: 1
  selector:
    matchLabels:
      run: dealership
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
  template:
    metadata:
      labels:
        run: dealership
    spec:
      containers:
      - image: us.icr.io/$MY_NAMESPACE/dealership:latest
        imagePullPolicy: Always
        name: dealership
        ports:
        - containerPort: 8000
          protocol: TCP
      restartPolicy: Always
  replicas: 